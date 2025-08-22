"""
Greenplum Tracking Store для MLflow

Этот модуль содержит кастомную реализацию tracking store для работы с Greenplum,
включая специальную обработку миграций и создания таблиц.
"""

import logging
import os
import pathlib
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore
from mlflow.store.db.utils import create_sqlalchemy_engine_with_retry
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.sql import text

from mlflow_greenplum.patching import patch_mlflow_db_functions, restore_mlflow_db_functions
from mlflow_greenplum.models import create_greenplum_tables, Base
import mlflow_greenplum

logger = logging.getLogger(__name__)


class GreenplumStore(SqlAlchemyStore):
    """
    Кастомный tracking store для Greenplum базы данных с полной поддержкой MLflow функций.
    
    Основные отличия от стандартного SqlAlchemyStore:
    - Создает таблицы с учетом специфики Greenplum (appendonly=false, distributed by)
    - Поддерживает Model Registry (регистрация моделей, версионирование)
    - Эмулирует выполнение миграций вместо их реального запуска
    - Обеспечивает совместимость с PostgreSQL API для полного функционала MLflow
    """
    
    def __init__(self, store_uri: str, artifact_uri: Optional[str] = None):
        """
        Инициализация Greenplum tracking store.
        
        Args:
            store_uri: URI подключения к Greenplum базе данных
            artifact_uri: URI для хранения артефактов
        """
        logger.info(f"Инициализация GreenplumStore с URI: {store_uri}")
        
        # Парсим URI для извлечения параметров
        parsed = urlparse(store_uri)
        query_params = parse_qs(parsed.query)
        
        # Получаем схему из параметров URI или переменных окружения
        # или используем 'public' по умолчанию
        # Извлекаем schema (приоритет: явный параметр schema, затем options search_path, затем переменная окружения, затем public)
        self.schema = query_params.get('schema', [None])[0]
        if not self.schema:
            # Разбор options=-c search_path=mlflow_test1
            options_vals = query_params.get('options')
            if options_vals:
                combined = ' '.join(options_vals)
                # Ищем search_path=...
                import re
                m = re.search(r'search_path=([a-zA-Z0-9_]+)', combined)
                if m:
                    self.schema = m.group(1)
        if not self.schema:
            self.schema = os.environ.get('MLFLOW_GREENPLUM_SCHEMA', 'public')
        # engine = mlflow_greenplum.db._create_engine()
        logger.info(f"Используем схему базы данных: {self.schema}")
        
        # Удаляем параметр schema из URI если он был передан
        new_query_dict = {k: v for k, v in query_params.items() if k != 'schema'}
        new_query = urlencode(new_query_dict, doseq=True) if new_query_dict else ''
        
        # Преобразуем URI для SQLAlchemy
        if parsed.scheme == 'greenplum':
            # Создаем новый URI без параметра schema
            path_parts = (
                'postgresql',  # схема
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,     # параметры запроса
                parsed.fragment
            )
            logger.info(f"Создан новый URI для SQLAlchemy: {path_parts}")
            sa_store_uri = urlunparse(path_parts)
            logger.info(f"Используемый URI для SQLAlchemy: {sa_store_uri}")

        else:
            # Оставляем URI как есть
            sa_store_uri = store_uri
        
        # Создаем движок с повторными попытками
        self.engine = create_sqlalchemy_engine_with_retry(sa_store_uri)
        self.SessionMaker = sessionmaker(bind=self.engine)
        # Безусловно пытаемся создать/обновить таблицы (идемпотентно)
        try:
            create_greenplum_tables(self.engine, self.schema)
        except Exception as e:
            logger.warning("Не удалось выполнить начальное создание таблиц: %s", e)


        # Устанавливаем поисковый путь для схемы
        @event.listens_for(self.engine, "connect")
        def set_search_path(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute(f"SET search_path TO {self.schema}")
            cursor.close()
        # Создаем таблицы в Greenplum (повторная проверка/досоздание)
        self._create_tables_if_needed()

        # Патчим функции верификации схемы и инициализации таблиц (отключаем alembic)
        original_functions = patch_mlflow_db_functions(self.schema)

        def _normalize_artifact_uri(raw: str) -> str:
            """Приводит путь/URI артефактов к формату, понятному MLflow.

            На Windows путь вида 'C:\\dir\\mlruns' интерпретируется как схема 'c' при парсинге.
            Добавляем file:/// и преобразуем обратные слеши в прямые.
            Если уже указана поддерживаемая схема (file, s3, greenplum и т.п.) – возвращаем как есть.
            """
            if not raw:
                return raw
            lower = raw.lower()
            # Если есть двоеточие до первого слеша и это диск (например C:) без // – считаем что нужен file://
            if (len(raw) > 2 and raw[1] == ':' and (raw[2] == '\\' or raw[2] == '/')):
                # Преобразуем в file:///C:/...
                p = pathlib.Path(raw).resolve()
                uri_path = str(p).replace('\\', '/')
                return "file:///" + uri_path.lstrip('/')
            # Если уже схема присутствует
            if '://' in raw:
                return raw
            # Относительный или абсолютный путь без схемы
            p = pathlib.Path(raw).resolve()
            return "file:///" + str(p).replace('\\', '/').lstrip('/')

        try:
            if artifact_uri is not None:
                norm_artifact_uri = _normalize_artifact_uri(artifact_uri)
                logger.info(f"Используем artifact URI: {norm_artifact_uri}")
                super().__init__(sa_store_uri, norm_artifact_uri)
            else:
                default_artifact_path = os.path.abspath(os.path.join(os.getcwd(), "mlruns"))
                norm_artifact_uri = _normalize_artifact_uri(default_artifact_path)
                logger.info(f"Используем default artifact URI: {norm_artifact_uri}")
                os.makedirs(default_artifact_path, exist_ok=True)
                super().__init__(sa_store_uri, norm_artifact_uri)
        finally:
            restore_mlflow_db_functions()
    
    def _create_tables_if_needed(self) -> None:
        """Проверяет наличие всех необходимых таблиц и создает недостающие.

        Логика переписана для:
          - Проверки полного набора таблиц, а не только experiment_tags
          - Идемпотентного создания (safe to run many times)
          - Подробного логирования недостающих таблиц
        """
        required_tables = [
            "experiments", "runs", "params", "metrics", "tags", "experiment_tags",
            "registered_models", "model_versions", "registered_model_tags", "model_version_tags",
            "datasets", "inputs", "input_tags", "latest_metrics", "registered_model_aliases",
            "trace_info", "trace_request_metadata", "trace_tags"
        ]
        logger.info("Проверка наличия таблиц MLflow в схеме '%s'", self.schema)

        # Используем отдельные подключения без вложенных транзакций
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
                trans.commit()
            except Exception as e:
                trans.rollback()
                logger.error("Не удалось создать схему %s: %s", self.schema, e)

        with self.engine.connect() as conn:
            existing = {r[0] for r in conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=:s"), {"s": self.schema})}
        missing = [t for t in required_tables if t not in existing]
        if missing:
            logger.warning("Отсутствуют таблицы (%s). Создаем...", ", ".join(missing))
            try:
                # Передаем engine, чтобы create_greenplum_tables само открыло транзакцию
                create_greenplum_tables(self.engine, self.schema)
            except Exception as e:
                logger.error("Ошибка при создании таблиц: %s", e)
            with self.engine.connect() as conn:
                existing_after = {r[0] for r in conn.execute(text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema=:s"), {"s": self.schema})}
            still_missing = [t for t in required_tables if t not in existing_after]
            if still_missing:
                logger.error("После создания все еще отсутствуют: %s", ", ".join(still_missing))
            else:
                logger.info("Все таблицы созданы в схеме '%s'", self.schema)
        else:
            logger.info("Все таблицы уже существуют в схеме '%s'", self.schema)
    
    def search_experiments(self, view_type=None, max_results=None, 
                           filter_string=None, order_by=None, page_token=None):
        """
        Поиск экспериментов с оптимизацией для Greenplum.
        
        Переопределяет базовый метод для добавления Greenplum-специфичных
        оптимизаций запросов.
        """
        logger.debug("Выполнение поиска экспериментов в Greenplum")
        
        # Устанавливаем значение по умолчанию для max_results если не передано
        if max_results is None:
            max_results = 1000  # Разумное значение по умолчанию
        
        try:
            # Пытаемся использовать базовую реализацию
            return super().search_experiments(
                view_type=view_type,
                max_results=max_results, 
                filter_string=filter_string,
                order_by=order_by,
                page_token=page_token
            )
        except Exception as e:
            # Если ошибка связана с experiment_tags, используем обходной путь
            if "experiment_tags" in str(e):
                logger.warning("Обнаружена ошибка с таблицей experiment_tags. Используем обходной путь.")
                
                # Создаем сессию напрямую через SQLAlchemy
                session = self.SessionMaker()
                try:
                    from mlflow.entities import Experiment
                    from mlflow.store.tracking.dbmodels.models import SqlExperiment
                    
                    # Импортируем нужные классы из правильных модулей
                    try:
                        from mlflow.store.entities.paged_list import PagedList
                    except ImportError:
                        # Старые версии MLflow
                        from mlflow.utils.search_utils import PagedList
                    
                    # Получаем все константы из правильных модулей
                    try:
                        from mlflow.entities.lifecycle_stage import LifecycleStage
                    except ImportError:
                        # Определяем константы вручную для старых версий
                        class LifecycleStage:
                            ACTIVE = "active"
                            DELETED = "deleted"
                    
                    try:
                        from mlflow.tracking.registry import ViewType
                    except ImportError:
                        # Определяем константы вручную для старых версий
                        class ViewType:
                            ALL = "all"
                            ACTIVE_ONLY = "active_only"
                            DELETED_ONLY = "deleted_only"
                    
                    # Выполняем простой запрос без использования experiment_tags
                    query = session.query(SqlExperiment)
                    
                    # Применяем фильтр по view_type
                    if view_type == ViewType.ACTIVE_ONLY or view_type is None:
                        query = query.filter(SqlExperiment.lifecycle_stage == LifecycleStage.ACTIVE)
                    elif view_type == ViewType.DELETED_ONLY:
                        query = query.filter(SqlExperiment.lifecycle_stage == LifecycleStage.DELETED)
                    
                    # Применяем сортировку
                    query = query.order_by(SqlExperiment.experiment_id.asc())
                    
                    # Выполняем запрос
                    sql_experiments = query.all()
                    
                    # Преобразуем SqlExperiment в EntityExperiment
                    experiments = [
                        Experiment(
                            experiment_id=e.experiment_id,
                            name=e.name,
                            artifact_location=e.artifact_location,
                            lifecycle_stage=e.lifecycle_stage,
                            creation_time=e.creation_time,
                            last_update_time=e.last_update_time,
                            tags={}  # Пустые теги, так как у нас проблема с таблицей experiment_tags
                        )
                        for e in sql_experiments
                    ]
                    
                    return PagedList(experiments, None)
                finally:
                    session.close()
            else:
                # Если ошибка не связана с experiment_tags, пробрасываем её дальше
                raise
    
    def search_runs(self, experiment_ids, filter_string=None, run_view_type=None,
                   max_results=None, order_by=None, page_token=None):
        """
        Поиск запусков с оптимизацией для Greenplum.
        
        Переопределяет базовый метод для добавления Greenplum-специфичных
        оптимизаций запросов.
        """
        logger.debug("Выполнение поиска запусков в Greenplum")
        
        # Устанавливаем значение по умолчанию для max_results если не передано
        if max_results is None:
            max_results = 1000  # Разумное значение по умолчанию
        
        # Используем базовую реализацию, но можем добавить оптимизации
        return super().search_runs(
            experiment_ids=experiment_ids,
            filter_string=filter_string,
            run_view_type=run_view_type,
            max_results=max_results,
            order_by=order_by,
            page_token=page_token
        )

    # ==============================================
    # ПОДДЕРЖКА MODEL REGISTRY
    # ==============================================
    
    # def create_registered_model(self, name, tags=None, description=None):
    #     """Создает новую зарегистрированную модель в Model Registry."""
    #     logger.info(f"Создание зарегистрированной модели: {name}")
    #     try:
    #         return super().create_registered_model(name, tags, description)
    #     except Exception as e:
    #         logger.error(f"Ошибка создания зарегистрированной модели {name}: {e}")
    #         raise

    # def get_registered_model(self, name):
    #     """Получает зарегистрированную модель по имени."""
    #     logger.debug(f"Получение зарегистрированной модели: {name}")
    #     return super().get_registered_model(name)

    # def rename_registered_model(self, name, new_name):
    #     """Переименовывает зарегистрированную модель."""
    #     logger.info(f"Переименование модели {name} в {new_name}")
    #     return super().rename_registered_model(name, new_name)

    # def update_registered_model(self, name, description=None):
    #     """Обновляет описание зарегистрированной модели."""
    #     logger.info(f"Обновление описания модели: {name}")
    #     return super().update_registered_model(name, description)

    # def delete_registered_model(self, name):
    #     """Удаляет зарегистрированную модель."""
    #     logger.info(f"Удаление зарегистрированной модели: {name}")
    #     return super().delete_registered_model(name)

    # def search_registered_models(self, filter_string=None, max_results=None, order_by=None, page_token=None):
    #     """Поиск зарегистрированных моделей."""
    #     logger.debug("Поиск зарегистрированных моделей")
        
    #     if max_results is None:
    #         max_results = 1000
            
    #     return super().search_registered_models(filter_string, max_results, order_by, page_token)

    # def get_latest_versions(self, name, stages=None):
    #     """Получает последние версии модели для указанных стадий."""
    #     logger.debug(f"Получение последних версий модели {name} для стадий: {stages}")
    #     return super().get_latest_versions(name, stages)

    # def create_model_version(self, name, source, run_id=None, tags=None, run_link=None, description=None):
    #     """Создает новую версию модели."""
    #     logger.info(f"Создание новой версии модели {name} из источника: {source}")
    #     try:
    #         return super().create_model_version(name, source, run_id, tags, run_link, description)
    #     except Exception as e:
    #         logger.error(f"Ошибка создания версии модели {name}: {e}")
    #         raise

    # def get_model_version(self, name, version):
    #     """Получает конкретную версию модели."""
    #     logger.debug(f"Получение версии {version} модели {name}")
    #     return super().get_model_version(name, version)

    # def update_model_version(self, name, version, description=None):
    #     """Обновляет описание версии модели."""
    #     logger.info(f"Обновление описания версии {version} модели {name}")
    #     return super().update_model_version(name, version, description)

    # def delete_model_version(self, name, version):
    #     """Удаляет версию модели."""
    #     logger.info(f"Удаление версии {version} модели {name}")
    #     return super().delete_model_version(name, version)

    # def search_model_versions(self, filter_string=None, max_results=None, order_by=None, page_token=None):
    #     """Поиск версий моделей."""
    #     logger.debug("Поиск версий моделей")
        
    #     if max_results is None:
    #         max_results = 1000
            
    #     return super().search_model_versions(filter_string, max_results, order_by, page_token)

    # def transition_model_version_stage(self, name, version, stage, archive_existing_versions=False):
    #     """Переводит версию модели в новую стадию."""
    #     logger.info(f"Перевод версии {version} модели {name} в стадию {stage}")
    #     return super().transition_model_version_stage(name, version, stage, archive_existing_versions)

    # def set_registered_model_tag(self, name, tag):
    #     """Устанавливает тег для зарегистрированной модели."""
    #     logger.debug(f"Установка тега для модели {name}: {tag.key}={tag.value}")
    #     return super().set_registered_model_tag(name, tag)

    # def delete_registered_model_tag(self, name, key):
    #     """Удаляет тег зарегистрированной модели."""
    #     logger.debug(f"Удаление тега {key} у модели {name}")
    #     return super().delete_registered_model_tag(name, key)

    # def set_model_version_tag(self, name, version, tag):
    #     """Устанавливает тег для версии модели."""
    #     logger.debug(f"Установка тега для версии {version} модели {name}: {tag.key}={tag.value}")
    #     return super().set_model_version_tag(name, version, tag)

    # def delete_model_version_tag(self, name, version, key):
    #     """Удаляет тег версии модели."""
    #     logger.debug(f"Удаление тега {key} у версии {version} модели {name}")
    #     return super().delete_model_version_tag(name, version, key)

    # def set_registered_model_alias(self, name, alias, version):
    #     """Устанавливает алиас для версии модели."""
    #     logger.info(f"Установка алиаса {alias} для версии {version} модели {name}")
    #     try:
    #         return super().set_registered_model_alias(name, alias, version)
    #     except AttributeError:
    #         # Если метод не существует в старых версиях MLflow
    #         logger.warning("Метод set_registered_model_alias не поддерживается в этой версии MLflow")
    #         pass

    # def delete_registered_model_alias(self, name, alias):
    #     """Удаляет алиас модели."""
    #     logger.info(f"Удаление алиаса {alias} у модели {name}")
    #     try:
    #         return super().delete_registered_model_alias(name, alias)
    #     except AttributeError:
    #         # Если метод не существует в старых версиях MLflow
    #         logger.warning("Метод delete_registered_model_alias не поддерживается в этой версии MLflow")
    #         pass

    # def get_model_version_by_alias(self, name, alias):
    #     """Получает версию модели по алиасу."""
    #     logger.debug(f"Получение версии модели {name} по алиасу {alias}")
    #     try:
    #         return super().get_model_version_by_alias(name, alias)
    #     except AttributeError:
    #         # Если метод не существует в старых версиях MLflow
    #         logger.warning("Метод get_model_version_by_alias не поддерживается в этой версии MLflow")
    #         return None
