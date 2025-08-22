
"""
Модуль для патчинга функций MLflow

Этот модуль содержит функции для патчинга оригинальных функций MLflow
при использовании Greenplum. Выделение патчинга в отдельный модуль
помогает избежать циклических импортов.
"""
import sqlalchemy
import logging
from functools import wraps
from typing import Dict, Any, Callable, Optional, Tuple, List
import os

from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import BAD_REQUEST, INTERNAL_ERROR, TEMPORARILY_UNAVAILABLE
from mlflow.store.db.db_types import SQLITE
from mlflow.store.model_registry.dbmodels.models import (
    SqlModelVersion,
    SqlModelVersionTag,
    SqlRegisteredModel,
    SqlRegisteredModelAlias,
    SqlRegisteredModelTag,
)
from mlflow.store.tracking.dbmodels.initial_models import Base as InitialBase

from mlflow.store.tracking.dbmodels.models import (
    SqlDataset,
    SqlExperiment,
    SqlExperimentTag,
    SqlInput,
    SqlInputTag,
    SqlLatestMetric,
    SqlMetric,
    SqlParam,
    SqlRun,
    SqlTag,
    SqlTraceInfo,
    SqlTraceRequestMetadata,
    SqlTraceTag,
)

logger = logging.getLogger(__name__)

# Оригинальные функции, которые мы заменяем
original_functions = {}

def patch_mlflow_db_functions(schema: Optional[str] = None) -> Dict[str, Callable]:
    """Патчит внутренние функции MLflow для работы с Greenplum без Alembic миграций.

    Параметр schema позволяет избежать жёстко захардкоженной схемы. Если не передан,
    используется переменная окружения MLFLOW_GREENPLUM_SCHEMA или 'public'.

    Args:
        schema: Имя схемы, в которой находятся (или будут созданы) таблицы MLflow.

    Returns:
        Dict[str, Callable]: Словарь оригинальных функций (для возможного восстановления).
    """
    if not schema:
        schema = os.getenv("MLFLOW_GREENPLUM_SCHEMA", "public")
    # Нормализуем (убираем кавычки) – при необходимости можно расширить.
    schema_unquoted = schema.strip('"')
    
    import mlflow.store.tracking.sqlalchemy_store as sa_store
    import mlflow.store.db.utils as db_utils
    
    # 1. Патчим функцию _verify_schema для пропуска проверки версии схемы
    if '_verify_schema' in dir(db_utils):
        original_functions['_verify_schema'] = db_utils._verify_schema
        
    @wraps(db_utils._verify_schema)
    def patched_verify_schema(engine):
            """
            Патч для пропуска проверки версии схемы базы данных.
            
            В Greenplum мы создаем таблицы напрямую в финальном виде,
            поэтому нам не нужно проверять версию схемы.
            """
            logger.info("Пропускаем проверку версии схемы базы данных для Greenplum")
            
            # Проверяем, существует ли таблица alembic_version
            from sqlalchemy.sql import text
            with engine.connect() as conn:
                from sqlalchemy.sql import text
                try:
                    exists_sql = text(
                        """
                        SELECT EXISTS (
                          SELECT 1 FROM information_schema.tables
                          WHERE table_name = 'alembic_version' AND table_schema = :schema
                        )
                        """
                    )
                    result = conn.execute(exists_sql, {"schema": schema_unquoted}).scalar()

                    if not result:
                        conn.execute(text(f"CREATE TABLE {schema_unquoted}.alembic_version (version_num VARCHAR(32) NOT NULL, PRIMARY KEY (version_num))"))
                        latest_version = 'f5a4f2784254'
                        conn.execute(text(f"INSERT INTO {schema_unquoted}.alembic_version (version_num) VALUES (:v)"), {"v": latest_version})
                        logger.info("Создана таблица и запись alembic_version=%s в схеме %s", latest_version, schema_unquoted)
                    else:
                        count_sql = text(f"SELECT COUNT(*) FROM {schema_unquoted}.alembic_version")
                        count = conn.execute(count_sql).scalar()
                        if count == 0:
                            latest_version = 'f5a4f2784254'
                            conn.execute(text(f"INSERT INTO {schema_unquoted}.alembic_version (version_num) VALUES (:v)"), {"v": latest_version})
                            logger.info("Добавлена запись alembic_version=%s в схему %s", latest_version, schema_unquoted)
                except Exception as e:
                    logger.warning("Ошибка при проверке/создании alembic_version в схеме %s: %s", schema_unquoted, e)
            
            # Пропускаем оригинальную функцию, которая может вызвать ошибку
            # Так как все необходимые таблицы уже созданы
            return None
        
    # Применяем патч
    db_utils._verify_schema = patched_verify_schema
    
    # 2. Патчим функцию _initialize_tables, чтобы использовать наш метод создания таблиц
    if '_initialize_tables' in dir(db_utils):
        original_functions['_initialize_tables'] = db_utils._initialize_tables
        
    @wraps(db_utils._initialize_tables)
    def patched_initialize_tables(engine):
            """
            Патч для инициализации таблиц без использования Alembic миграций.
            
            Вместо запуска миграций через Alembic, мы просто проверяем существуют ли 
            таблицы и создаем их в финальном виде, если они не существуют.
            """
            logger.info("=== НАЧАЛО patched_initialize_tables ===")
            logger.info("Используем патч для инициализации таблиц в Greenplum, схема: %s", schema_unquoted)
            
            # Проверим какие таблицы уже существуют
            from sqlalchemy.sql import text
            with engine.connect() as conn:
                try:
                    # Получаем все таблицы в схеме
                    all_tables_sql = text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = :schema AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """)
                    result = conn.execute(all_tables_sql, {"schema": schema_unquoted})
                    existing_tables = [row[0] for row in result.fetchall()]
                    logger.info("Существующие таблицы в схеме %s: %s", schema_unquoted, existing_tables)
                    
                    # Проверим MLflow таблицы отдельно  
                    REQUIRED_MLFLOW_TABLES = {
                        'experiments', 'runs', 'params', 'metrics', 'tags', 'experiment_tags',
                        'registered_models', 'model_versions', 'registered_model_tags', 
                        'model_version_tags', 'latest_metrics', 'datasets', 'inputs', 
                        'input_tags', 'trace_info', 'trace_request_metadata', 'trace_tags',
                        'registered_model_aliases'
                    }
                    
                    mlflow_tables = [t for t in existing_tables if t in REQUIRED_MLFLOW_TABLES]
                    missing_mlflow = REQUIRED_MLFLOW_TABLES - set(mlflow_tables)
                    other_tables = [t for t in existing_tables if t not in REQUIRED_MLFLOW_TABLES]
                    
                    logger.info("MLflow таблицы в схеме: %s", sorted(mlflow_tables))
                    logger.info("Недостающие MLflow таблицы: %s", sorted(missing_mlflow))
                    logger.info("Другие таблицы в схеме: %s", sorted(other_tables))
                    
                    if missing_mlflow:
                        logger.warning("Обнаружены недостающие MLflow таблицы, вызов оригинальной функции может попытаться их создать")
                    else:
                        logger.info("Все MLflow таблицы присутствуют")
                        
                except Exception as e:
                    logger.error("Ошибка при анализе таблиц: %s", e)
            
            # Проверяем, существует ли таблица alembic_version
            with engine.connect() as conn:
                try:
                    from sqlalchemy.sql import text
                    exists_sql = text(
                        """
                        SELECT EXISTS (
                          SELECT 1 FROM information_schema.tables
                          WHERE table_name = 'alembic_version' AND table_schema = :schema
                        )
                        """
                    )
                    result = conn.execute(exists_sql, {"schema": schema_unquoted}).scalar()
                    if not result:
                        logger.info("Создаем таблицу alembic_version")
                        conn.execute(text(f"CREATE TABLE {schema_unquoted}.alembic_version (version_num VARCHAR(32) NOT NULL, PRIMARY KEY (version_num))"))
                        latest_version = 'f5a4f2784254'
                        conn.execute(text(f"INSERT INTO {schema_unquoted}.alembic_version (version_num) VALUES (:v)"), {"v": latest_version})
                        conn.commit()
                        logger.info("Создана таблица alembic_version и запись версии %s в схеме %s", latest_version, schema_unquoted)
                    else:
                        logger.info("Таблица alembic_version уже существует")
                except Exception as e:
                    logger.warning("Ошибка при проверке/создании alembic_version в схеме %s: %s", schema_unquoted, e)
            
            # Вызываем оригинальную функцию с дополнительным логированием
            logger.info("Вызываем оригинальную _initialize_tables...")
            try:
                result = original_functions['_initialize_tables'](engine)
                logger.info("Оригинальная _initialize_tables завершена успешно")
                return result
            except Exception as e:
                logger.error("Ошибка в оригинальной _initialize_tables: %s", e)
                raise
            finally:
                logger.info("=== КОНЕЦ patched_initialize_tables ===")
        
    # Применяем патч
    db_utils._initialize_tables = patched_initialize_tables
    
    # 3. Полностью заменяем функцию _upgrade_db, чтобы предотвратить выполнение миграций
    if '_upgrade_db' in dir(db_utils):
        original_functions['_upgrade_db'] = db_utils._upgrade_db
        
    @wraps(db_utils._upgrade_db)
    def patched_upgrade_db(engine):
            """
            Полная замена функции _upgrade_db для предотвращения запуска Alembic миграций.
            
            Вместо запуска миграций просто логируем информацию и ничего не делаем.
            """
            logger.info("Пропускаем выполнение миграций Alembic для Greenplum")
            # Не выполняем никаких действий с миграциями
            return None
        
    # Применяем патч
    db_utils._upgrade_db = patched_upgrade_db
    
    # 4. Патчим функцию _search_experiments
    if '_search_experiments' in dir(sa_store.SqlAlchemyStore):
        original_functions['_search_experiments'] = sa_store.SqlAlchemyStore._search_experiments
        
        # Переопределяем функцию _search_experiments
        @wraps(sa_store.SqlAlchemyStore._search_experiments)
        def patched_search_experiments(self, *args, **kwargs):
            try:
                # Пытаемся выполнить оригинальную функцию
                return original_functions['_search_experiments'](self, *args, **kwargs)
            except Exception as e:
                # Если ошибка связана с experiment_tags, используем обходной путь
                if "experiment_tags" in str(e):
                    logger.warning("Обнаружена ошибка с таблицей experiment_tags в _search_experiments. Используем обходной путь.")
                    
                    # Используем встроенную функцию управления сессиями в соответствии с версией MLflow
                    # Для newer MLflow версий она может быть в другом месте
                    try:
                        # Сначала пытаемся импортировать непосредственно
                        from mlflow.store.db.utils import make_managed_session
                    except ImportError:
                        # Если не получилось, пробуем найти функцию в других местах
                        # В зависимости от версии MLflow
                        from contextlib import contextmanager
                        
                        @contextmanager
                        def make_managed_session(session_maker):
                            """
                            Создает и управляет сессией SQLAlchemy для MLflow.
                            
                            Эта функция используется, если встроенная функция недоступна.
                            """
                            session = session_maker()
                            try:
                                yield session
                                session.commit()
                            except Exception as e:
                                session.rollback()
                                raise
                            finally:
                                session.close()
                    
                    # Создаем свои собственные результаты запроса
                    from mlflow.entities import Experiment
                    try:
                        from mlflow.store.entities.paged_list import PagedList
                    except Exception:
                        from mlflow.utils.search_utils import PagedList
                    
                    filter_string = kwargs.get('filter_string', None)
                    order_by = kwargs.get('order_by', None)
                    page_token = kwargs.get('page_token', None)
                    max_results = kwargs.get('max_results', 1000)
                    
                    # Создаем SQL-запрос напрямую, чтобы избежать проблем с experiment_tags
                    with make_managed_session(self.SessionMaker) as session:
                        # Строим запрос вручную
                        from sqlalchemy.sql import text
                        
                        # Простой запрос к таблице experiments без JOIN
                        try:
                            query = """
                            SELECT experiment_id, name, artifact_location, lifecycle_stage, 
                                   creation_time, last_update_time
                            FROM experiments
                            WHERE lifecycle_stage IN (:active, :deleted)
                            ORDER BY creation_time DESC, experiment_id ASC
                            LIMIT :limit OFFSET :offset
                            """
                            
                            result = session.execute(
                                text(query), 
                                {
                                    'active': 'active', 
                                    'deleted': 'deleted',
                                    'limit': max_results,
                                    'offset': 0 if page_token is None else int(page_token)
                                }
                            )
                            
                            # Преобразуем результат в список экспериментов
                            experiments = []
                            for row in result:
                                exp = Experiment(
                                    experiment_id=row.experiment_id,
                                    name=row.name,
                                    artifact_location=row.artifact_location,
                                    lifecycle_stage=row.lifecycle_stage,
                                    creation_time=row.creation_time,
                                    last_update_time=row.last_update_time,
                                    tags={}  # Пустые теги
                                )
                                experiments.append(exp)
                            
                            # Вычисляем next_page_token
                            next_page_token = None
                            if len(experiments) == max_results:
                                next_page_token = str(0 if page_token is None else int(page_token) + max_results)
                            
                            return PagedList(experiments, next_page_token)
                        
                        except Exception as inner_e:
                            logger.error(f"Ошибка при выполнении запроса: {str(inner_e)}")
                            # Возвращаем пустой список в случае ошибки
                            return PagedList([], None)
                else:
                    # Если ошибка не связана с experiment_tags, пробрасываем её дальше
                    raise
        
        # Применяем патч
        sa_store.SqlAlchemyStore._search_experiments = patched_search_experiments
    
    # 5. Патчим функцию _all_tables_exist для безопасной работы с None
    if '_all_tables_exist' in dir(db_utils):
        original_functions['_all_tables_exist'] = db_utils._all_tables_exist
        
    @wraps(db_utils._all_tables_exist)
    def patched_all_tables_exist(engine):
            """
            Патч для полного отключения проверки таблиц.
            
            Всегда возвращает True, чтобы отключить миграции Alembic.
            """
            logger.info("Полное отключение проверки существования таблиц для Greenplum")
            # Просто возвращаем True, что означает "все таблицы существуют"
            return True
        
    # Применяем патч
    db_utils._all_tables_exist = patched_all_tables_exist
    
    # 6. Патчим функцию _get_alembic_config, чтобы предотвратить использование Alembic
    if '_get_alembic_config' in dir(db_utils):
        original_functions['_get_alembic_config'] = db_utils._get_alembic_config
        
    @wraps(db_utils._get_alembic_config)
    def patched_get_alembic_config(db_url):
            """
            Патч для предотвращения создания конфигурации Alembic.
            
            Возвращает пустой объект, который не вызовет ошибок при доступе к базовым атрибутам.
            """
            logger.info("Пропускаем создание конфигурации Alembic для Greenplum")
            
            # Создаем минимальный объект конфигурации
            from alembic.config import Config
            config = Config()
            config.set_main_option("script_location", "")
            return config
        
    # Применяем патч
    db_utils._get_alembic_config = patched_get_alembic_config
    
    # 7. Патчим Inspector.get_table_names для фильтрации только таблиц MLflow
    REQUIRED_MLFLOW_TABLES = {
        'experiments', 'runs', 'params', 'metrics', 'tags', 'experiment_tags',
        'registered_models', 'model_versions', 'registered_model_tags', 
        'model_version_tags', 'latest_metrics', 'datasets', 'inputs', 
        'input_tags', 'trace_info', 'trace_request_metadata', 'trace_tags',
        'registered_model_aliases', 'alembic_version'
    }
    
    original_functions['get_table_names'] = sqlalchemy.engine.reflection.Inspector.get_table_names
    
    @wraps(sqlalchemy.engine.reflection.Inspector.get_table_names)
    def patched_get_table_names(self, schema=None, **kwargs):
        """Возвращает только таблицы MLflow, фильтруя остальные таблицы в схеме."""
        # Получаем все таблицы из схемы
        all_tables = original_functions['get_table_names'](self, schema=schema, **kwargs)
        
        # Определяем текущую схему
        current_schema = schema or schema_unquoted
        
        logger.info("=== get_table_names вызван ===")
        logger.info("Запрошена схема: %s, текущая схема: %s", schema, current_schema)
        logger.info("Все таблицы в схеме %s: %s", current_schema, sorted(all_tables))
        
        # Если это наша целевая схема, фильтруем только таблицы MLflow
        if current_schema == schema_unquoted:
            mlflow_tables = [table for table in all_tables if table in REQUIRED_MLFLOW_TABLES]
            logger.info("ФИЛЬТРАЦИЯ: возвращаем только MLflow таблицы: %s", sorted(mlflow_tables))
            logger.info("СКРЫТО: %d других таблиц: %s", 
                       len(all_tables) - len(mlflow_tables),
                       sorted([t for t in all_tables if t not in REQUIRED_MLFLOW_TABLES]))
            return mlflow_tables
        else:
            logger.info("Схема %s не равна целевой %s - возвращаем все таблицы", current_schema, schema_unquoted)
            return all_tables
    
    sqlalchemy.engine.reflection.Inspector.get_table_names = patched_get_table_names
    
    return original_functions

def restore_mlflow_db_functions() -> None:
    """
    Восстанавливает оригинальные функции MLflow.
    """
    import mlflow.store.tracking.sqlalchemy_store as sa_store
    import mlflow.store.db.utils as db_utils
    
    # Восстанавливаем оригинальную функцию _verify_schema
    if '_verify_schema' in original_functions:
        db_utils._verify_schema = original_functions['_verify_schema']
    
    # Восстанавливаем оригинальную функцию _initialize_tables
    if '_initialize_tables' in original_functions:
        db_utils._initialize_tables = original_functions['_initialize_tables']
    
    # Восстанавливаем оригинальную функцию _upgrade_db
    if '_upgrade_db' in original_functions:
        db_utils._upgrade_db = original_functions['_upgrade_db']
    
    # Восстанавливаем оригинальную функцию _search_experiments
    if '_search_experiments' in original_functions:
        sa_store.SqlAlchemyStore._search_experiments = original_functions['_search_experiments']
    
    # Восстанавливаем оригинальную функцию _all_tables_exist
    if '_all_tables_exist' in original_functions:
        db_utils._all_tables_exist = original_functions['_all_tables_exist']
    
    # Восстанавливаем оригинальную функцию _get_alembic_config
    if '_get_alembic_config' in original_functions:
        db_utils._get_alembic_config = original_functions['_get_alembic_config']
    
    # Восстанавливаем оригинальную функцию get_table_names
    if 'get_table_names' in original_functions:
        sqlalchemy.engine.reflection.Inspector.get_table_names = original_functions['get_table_names']
    
    logger.info("Восстановлены оригинальные функции MLflow")