"""
Greenplum Model Registry Store для MLflow

Этот модуль содержит кастомную реализацию model registry store для работы с Greenplum,
обеспечивая полную поддержку MLflow Model Registry функций.
"""

import logging
import os
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from mlflow.store.model_registry.sqlalchemy_store import SqlAlchemyStore
from mlflow.store.db.utils import create_sqlalchemy_engine_with_retry
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.sql import text

from mlflow_greenplum.patching import patch_mlflow_db_functions, restore_mlflow_db_functions
from mlflow_greenplum.models import create_greenplum_tables

logger = logging.getLogger(__name__)


class GreenplumModelRegistryStore(SqlAlchemyStore):
    """
    Кастомный Model Registry store для Greenplum базы данных.
    
    Обеспечивает полную поддержку MLflow Model Registry функций:
    - Регистрация и управление моделями
    - Версионирование моделей  
    - Управление стадиями жизненного цикла
    - Теги и алиасы моделей
    - Совместимость с PostgreSQL API
    """
    
    def __init__(self, store_uri: str):
        """
        Инициализация Greenplum Model Registry store.
        
        Args:
            store_uri: URI подключения к Greenplum базе данных
        """
        logger.info(f"Инициализация GreenplumModelRegistryStore с URI: {store_uri}")
        
        # Парсим URI для извлечения параметров
        parsed = urlparse(store_uri)
        query_params = parse_qs(parsed.query)
        
        # Получаем схему из параметров URI
        self.schema = self._extract_schema_from_uri(query_params)
        logger.info(f"Используем схему базы данных: {self.schema}")
        
        

        # Преобразуем URI для SQLAlchemy
        sa_store_uri = self._convert_uri_for_sqlalchemy(parsed, query_params)
        self.engine = create_sqlalchemy_engine_with_retry(sa_store_uri)
        logger.info(f"Используемый URI для SQLAlchemy: {sa_store_uri}")
        
        # Патчим функции MLflow для работы с Greenplum
        self._apply_greenplum_patches()
        
        try:
            # Инициализируем родительский класс
            super().__init__(sa_store_uri)
            
            # Создаем таблицы если нужно
            self._create_tables_if_needed()
            
            # Устанавливаем поисковый путь для схемы
            self._setup_search_path()
        finally:
            # Восстанавливаем оригинальные функции
            restore_mlflow_db_functions()
    
    def _extract_schema_from_uri(self, query_params: Dict) -> str:
        """Извлекает схему из параметров URI."""
        # Приоритет: явный параметр schema, затем options search_path, затем переменная окружения, затем public
        schema = query_params.get('schema', [None])[0]
        
        if not schema:
            # Разбор options=-c search_path=mlflow_test5
            options_vals = query_params.get('options')
            if options_vals:
                combined = ' '.join(options_vals)
                import re
                m = re.search(r'search_path=([a-zA-Z0-9_]+)', combined)
                if m:
                    schema = m.group(1)
        
        if not schema:
            schema = os.environ.get('MLFLOW_GREENPLUM_SCHEMA', 'public')
        
        return schema
    
    def _convert_uri_for_sqlalchemy(self, parsed, query_params: Dict) -> str:
        """Преобразует greenplum:// URI в postgresql:// для SQLAlchemy."""
        # Удаляем параметр schema из URI если он был передан
        new_query_dict = {k: v for k, v in query_params.items() if k != 'schema'}
        new_query = urlencode(new_query_dict, doseq=True) if new_query_dict else ''
        
        if parsed.scheme == 'greenplum':
            # Преобразуем схему в postgresql
            path_parts = (
                'postgresql',  # схема
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,     # параметры запроса
                parsed.fragment
            )
            return urlunparse(path_parts)
        else:
            # Оставляем URI как есть
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                             parsed.params, new_query, parsed.fragment))
    
    def _create_tables_if_needed(self) -> None:
        """Создает таблицы Model Registry если они не существуют."""
        logger.info("Проверка наличия таблиц Model Registry в схеме '%s'", self.schema)
        
        # Таблицы необходимые для Model Registry
        registry_tables = [
            "registered_models", 
            "model_versions", 
            "registered_model_tags", 
            "model_version_tags",
            "registered_model_aliases"
        ]
        
        with self.engine.connect() as conn:
            # Создаем схему если не существует
            trans = conn.begin()
            try:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
                trans.commit()
            except Exception as e:
                trans.rollback()
                logger.error("Не удалось создать схему %s: %s", self.schema, e)
        
        # Проверяем какие таблицы существуют
        with self.engine.connect() as conn:
            existing = {r[0] for r in conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=:s"), 
                {"s": self.schema})}
        
        missing = [t for t in registry_tables if t not in existing]
        
        if missing:
            logger.warning("Отсутствуют таблицы Model Registry (%s). Создаем...", ", ".join(missing))
            try:
                # Вызываем функцию создания таблиц для отсутствующих
                create_greenplum_tables(self.engine, self.schema)
                logger.info("Таблицы Model Registry созданы в схеме '%s'", self.schema)
            except Exception as e:
                logger.error("Ошибка при создании таблиц Model Registry: %s", e)
        else:
            # Проверяем наличие всех необходимых колонок в таблицах
            try:
                self._verify_table_structure()
                logger.info("Все таблицы Model Registry существуют в схеме '%s' и имеют корректную структуру", self.schema)
            except Exception as e:
                logger.error("Ошибка при проверке структуры таблиц: %s", e)
                # При ошибке пытаемся пересоздать таблицы
                try:
                    create_greenplum_tables(self.engine, self.schema)
                    logger.info("Таблицы Model Registry пересозданы в схеме '%s'", self.schema)
                except Exception as re:
                    logger.error("Не удалось пересоздать таблицы: %s", re)
    
    def _verify_table_structure(self) -> None:
        """Проверяет наличие всех необходимых колонок в таблицах Model Registry."""
        # Проверяем наличие критичных полей в таблицах
        with self.engine.connect() as conn:
            # Проверка registered_models
            result = conn.execute(text(
                """SELECT column_name FROM information_schema.columns 
                   WHERE table_schema=:s AND table_name='registered_models'"""), 
                {"s": self.schema}).fetchall()
            
            cols = {r[0] for r in result}
            required_cols = {"name", "creation_time", "last_updated_time", "description"}
            
            if not required_cols.issubset(cols):
                missing = required_cols - cols
                logger.warning(f"В таблице registered_models отсутствуют колонки: {missing}")
                raise Exception(f"Неполная структура таблицы registered_models, отсутствуют: {missing}")
            
            # Проверка model_versions
            result = conn.execute(text(
                """SELECT column_name FROM information_schema.columns 
                   WHERE table_schema=:s AND table_name='model_versions'"""), 
                {"s": self.schema}).fetchall()
            
            cols = {r[0] for r in result}
            required_cols = {"name", "version", "current_stage", "creation_time", "last_updated_time", 
                            "source", "run_id", "description", "run_link"}
            
            if not required_cols.issubset(cols):
                missing = required_cols - cols
                logger.warning(f"В таблице model_versions отсутствуют колонки: {missing}")
                raise Exception(f"Неполная структура таблицы model_versions, отсутствуют: {missing}")
    
    def _setup_search_path(self) -> None:
        """Настраивает поисковый путь для схемы."""
        logger.info(f"Настройка search_path для схемы {self.schema}")
        
        @event.listens_for(self.engine, "connect")
        def set_search_path(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute(f"SET search_path TO {self.schema}")
            cursor.close()
    
    def _apply_greenplum_patches(self) -> None:
        """Применяет патчи MLflow для работы с Greenplum."""
        # Патчим функции MLflow для работы с Greenplum
        patch_mlflow_db_functions(self.schema)
    # Важно: НЕ вызываем _setup_search_path здесь, так как self.engine
    # создаётся в SqlAlchemyStore.__init__. Настройка search_path
    # выполняется позже, после super().__init__().
    
    # ==============================================
    # ПЕРЕОПРЕДЕЛЕНИЕ МЕТОДОВ MODEL REGISTRY
    # ==============================================
    
    def create_registered_model(self, name, tags=None, description=None):
        """Создает новую зарегистрированную модель в Model Registry."""
        logger.info(f"[GP Registry] Создание зарегистрированной модели: {name}")
        try:
            result = super().create_registered_model(name, tags, description)
            logger.info(f"[GP Registry] Модель {name} успешно зарегистрирована")
            return result
        except Exception as e:
            logger.error(f"[GP Registry] Ошибка создания зарегистрированной модели {name}: {e}")
            raise

    def get_registered_model(self, name):
        """Получает зарегистрированную модель по имени."""
        logger.debug(f"[GP Registry] Получение зарегистрированной модели: {name}")
        return super().get_registered_model(name)

    def rename_registered_model(self, name, new_name):
        """Переименовывает зарегистрированную модель."""
        logger.info(f"[GP Registry] Переименование модели {name} в {new_name}")
        return super().rename_registered_model(name, new_name)

    def update_registered_model(self, name, description=None):
        """Обновляет описание зарегистрированной модели."""
        logger.info(f"[GP Registry] Обновление описания модели: {name}")
        return super().update_registered_model(name, description)

    def delete_registered_model(self, name):
        """Удаляет зарегистрированную модель."""
        logger.info(f"[GP Registry] Удаление зарегистрированной модели: {name}")
        return super().delete_registered_model(name)

    def search_registered_models(self, filter_string=None, max_results=None, order_by=None, page_token=None):
        """Поиск зарегистрированных моделей с оптимизациями для Greenplum."""
        logger.debug("[GP Registry] Поиск зарегистрированных моделей")
        
        if max_results is None:
            max_results = 1000  # Разумное значение по умолчанию
            
        try:
            return super().search_registered_models(filter_string, max_results, order_by, page_token)
        except Exception as e:
            logger.error(f"[GP Registry] Ошибка поиска зарегистрированных моделей: {e}")
            raise

    def get_latest_versions(self, name, stages=None):
        """Получает последние версии модели для указанных стадий."""
        logger.debug(f"[GP Registry] Получение последних версий модели {name} для стадий: {stages}")
        return super().get_latest_versions(name, stages)

    def create_model_version(self, name, source, run_id=None, tags=None, run_link=None, description=None):
        """Создает новую версию модели."""
        logger.info(f"[GP Registry] Создание новой версии модели {name} из источника: {source}")
        try:
            result = super().create_model_version(name, source, run_id, tags, run_link, description)
            logger.info(f"[GP Registry] Версия модели {name} успешно создана: {result.version}")
            return result
        except Exception as e:
            logger.error(f"[GP Registry] Ошибка создания версии модели {name}: {e}")
            raise

    def get_model_version(self, name, version):
        """Получает конкретную версию модели."""
        logger.debug(f"[GP Registry] Получение версии {version} модели {name}")
        return super().get_model_version(name, version)

    def update_model_version(self, name, version, description=None):
        """Обновляет описание версии модели."""
        logger.info(f"[GP Registry] Обновление описания версии {version} модели {name}")
        return super().update_model_version(name, version, description)

    def delete_model_version(self, name, version):
        """Удаляет версию модели."""
        logger.info(f"[GP Registry] Удаление версии {version} модели {name}")
        return super().delete_model_version(name, version)

    def search_model_versions(self, filter_string=None, max_results=None, order_by=None, page_token=None):
        """Поиск версий моделей с оптимизациями для Greenplum."""
        logger.debug("[GP Registry] Поиск версий моделей")
        
        if max_results is None:
            max_results = 1000
            
        try:
            return super().search_model_versions(filter_string, max_results, order_by, page_token)
        except Exception as e:
            logger.error(f"[GP Registry] Ошибка поиска версий моделей: {e}")
            raise

    def transition_model_version_stage(self, name, version, stage, archive_existing_versions=False):
        """Переводит версию модели в новую стадию."""
        logger.info(f"[GP Registry] Перевод версии {version} модели {name} в стадию {stage}")
        return super().transition_model_version_stage(name, version, stage, archive_existing_versions)

    def set_registered_model_tag(self, name, tag):
        """Устанавливает тег для зарегистрированной модели."""
        logger.debug(f"[GP Registry] Установка тега для модели {name}: {tag.key}={tag.value}")
        return super().set_registered_model_tag(name, tag)

    def delete_registered_model_tag(self, name, key):
        """Удаляет тег зарегистрированной модели."""
        logger.debug(f"[GP Registry] Удаление тега {key} у модели {name}")
        return super().delete_registered_model_tag(name, key)

    def set_model_version_tag(self, name, version, tag):
        """Устанавливает тег для версии модели."""
        logger.debug(f"[GP Registry] Установка тега для версии {version} модели {name}: {tag.key}={tag.value}")
        return super().set_model_version_tag(name, version, tag)

    def delete_model_version_tag(self, name, version, key):
        """Удаляет тег версии модели."""
        logger.debug(f"[GP Registry] Удаление тега {key} у версии {version} модели {name}")
        return super().delete_model_version_tag(name, version, key)

    def set_registered_model_alias(self, name, alias, version):
        """Устанавливает алиас для версии модели."""
        logger.info(f"[GP Registry] Установка алиаса {alias} для версии {version} модели {name}")
        try:
            return super().set_registered_model_alias(name, alias, version)
        except AttributeError:
            # Если метод не существует в старых версиях MLflow
            logger.warning("[GP Registry] Метод set_registered_model_alias не поддерживается в этой версии MLflow")
            pass

    def delete_registered_model_alias(self, name, alias):
        """Удаляет алиас модели."""
        logger.info(f"[GP Registry] Удаление алиаса {alias} у модели {name}")
        try:
            return super().delete_registered_model_alias(name, alias)
        except AttributeError:
            # Если метод не существует в старых версиях MLflow
            logger.warning("[GP Registry] Метод delete_registered_model_alias не поддерживается в этой версии MLflow")
            pass

    def get_model_version_by_alias(self, name, alias):
        """Получает версию модели по алиасу."""
        logger.debug(f"[GP Registry] Получение версии модели {name} по алиасу {alias}")
        try:
            return super().get_model_version_by_alias(name, alias)
        except AttributeError:
            # Если метод не существует в старых версиях MLflow
            logger.warning("[GP Registry] Метод get_model_version_by_alias не поддерживается в этой версии MLflow")
            return None
