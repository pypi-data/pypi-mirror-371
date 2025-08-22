from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    Float,
    ForeignKey,
    Text,
    ForeignKeyConstraint,
    text,
    Boolean,
    create_engine,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.engine import Connection, Engine
import logging
import time
from typing import List, Union

# NOTE: InitialBase не используется – убрано для чистоты

Base = declarative_base()
logger = logging.getLogger(__name__)



class Experiment(Base):
    __tablename__ = 'experiments'
    
    # SERIAL автоматически создает sequence в нужной схеме
    experiment_id = Column(Integer, primary_key=True, autoincrement=True)
    
    name = Column(String(255), nullable=False, index=True) 
    artifact_location = Column(String(500))
    lifecycle_stage = Column(String(50), default='active')
    creation_time = Column(BigInteger, default=lambda: int(time.time() * 1000))
    last_update_time = Column(BigInteger, default=lambda: int(time.time() * 1000))
    
    # Relationships
    runs = relationship("Run", back_populates="experiment")
    tags = relationship("ExperimentTag", back_populates="experiment", cascade="all, delete-orphan")

class Run(Base):
    __tablename__ = 'runs'
    run_uuid = Column(String(36), primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiments.experiment_id"))
    user_id = Column(String(255))
    status = Column(String(50), default='RUNNING')
    start_time = Column(BigInteger)
    end_time = Column(BigInteger, nullable=True)
    # Поле появилось в новых версиях MLflow для мягкого удаления
    deleted_time = Column(BigInteger, nullable=True)
    lifecycle_stage = Column(String(50), default='active')
    artifact_uri = Column(String(500))
    name = Column(String(255))
    source_type = Column(String(50))
    source_name = Column(String(500))
    entry_point_name = Column(String(255))
    source_version = Column(String(50))
    
    # Relationships
    experiment = relationship("Experiment", back_populates="runs")
    params = relationship("Param", back_populates="run", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="run", cascade="all, delete-orphan")
    latest_metrics = relationship("LatestMetric", back_populates="run", cascade="all, delete-orphan")
    inputs = relationship("Input", primaryjoin="Run.run_uuid==foreign(Input.destination_id)")
    traces = relationship("TraceInfo", back_populates="run")

class Param(Base):
    __tablename__ = 'params'
    # Используем составной ключ только из обязательных полей
    run_uuid = Column(String(36), ForeignKey("runs.run_uuid"), primary_key=True)
    key = Column(String(255), primary_key=True)
    value = Column(Text)
    
    # Relationships
    run = relationship("Run", back_populates="params")

class Metric(Base):
    __tablename__ = 'metrics'
    # Для метрик используем составной ключ с timestamp
    run_uuid = Column(String(36), ForeignKey("runs.run_uuid"), primary_key=True)
    key = Column(String(255), primary_key=True)
    timestamp = Column(BigInteger, primary_key=True)
    step = Column(BigInteger, default=0)
    value = Column(Float, nullable=False)
    is_nan = Column(Boolean, default=False, nullable=False)
    # Relationships
    run = relationship("Run", back_populates="metrics")

class Tag(Base):
    __tablename__ = 'tags'
    # Для тегов простой составной ключ
    run_uuid = Column(String(36), ForeignKey("runs.run_uuid"), primary_key=True)
    key = Column(String(255), primary_key=True)
    value = Column(Text)
    
    # Relationships
    run = relationship("Run", back_populates="tags")


# Dataset tracking (минимально необходимые таблицы для новых версий MLflow)
class Dataset(Base):
    __tablename__ = 'datasets'

    dataset_uuid = Column(String(36), primary_key=True)
    experiment_id = Column(Integer, nullable=True)
    name = Column(String(500), nullable=True)
    digest = Column(String(64), nullable=True)
    dataset_source_type = Column(String(50), nullable=True)
    dataset_source = Column(Text, nullable=True)
    dataset_schema = Column(Text, nullable=True)
    dataset_profile = Column(Text, nullable=True)


class Input(Base):
    __tablename__ = 'inputs'

    input_uuid = Column(String(36), primary_key=True)
    destination_type = Column(String(20), nullable=True)  # RUN
    destination_id = Column(String(36), nullable=True)    # run_uuid
    source_type = Column(String(20), nullable=True)       # DATASET
    source_id = Column(String(36), nullable=True)         # dataset_uuid
    # Простейшая модель без FK чтобы избежать проблем совместимости разных версий


class InputTag(Base):
    __tablename__ = 'input_tags'
    input_uuid = Column(String(36), primary_key=True)
    name = Column(String(255), primary_key=True)
    value = Column(Text)


class LatestMetric(Base):
    __tablename__ = 'latest_metrics'
    run_uuid = Column(String(36), ForeignKey("runs.run_uuid"), primary_key=True)
    key = Column(String(255), primary_key=True)
    value = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    step = Column(BigInteger, default=0, nullable=False)
    is_nan = Column(Boolean, default=False, nullable=False)
    run = relationship("Run", back_populates="latest_metrics")
    


class RegisteredModelAlias(Base):
    __tablename__ = 'registered_model_aliases'
    name = Column(String(255), ForeignKey("registered_models.name"), primary_key=True)
    alias = Column(String(255), primary_key=True)
    version = Column(Integer, nullable=False)
    registered_model = relationship("RegisteredModel")


class TraceInfo(Base):
    __tablename__ = 'trace_info'
    request_id = Column(String(36), primary_key=True)
    experiment_id = Column(Integer, nullable=True)
    run_uuid = Column(String(36), ForeignKey("runs.run_uuid"), nullable=True)
    timestamp_ms = Column(BigInteger, default=lambda: int(time.time() * 1000))
    execution_time_ms = Column(BigInteger, nullable=True)
    status = Column(String(50), nullable=True)
    status_message = Column(Text, nullable=True)
    run = relationship("Run", back_populates="traces")
    tags = relationship("TraceTag", back_populates="trace", cascade="all, delete-orphan")
    request_metadata = relationship("TraceRequestMetadata", back_populates="trace", cascade="all, delete-orphan")


class TraceRequestMetadata(Base):
    __tablename__ = 'trace_request_metadata'
    request_id = Column(String(36), ForeignKey("trace_info.request_id"), primary_key=True)
    key = Column(String(255), primary_key=True)
    value = Column(Text)
    trace = relationship("TraceInfo", back_populates="request_metadata")


class TraceTag(Base):
    __tablename__ = 'trace_tags'
    request_id = Column(String(36), ForeignKey("trace_info.request_id"), primary_key=True)
    key = Column(String(255), primary_key=True)
    value = Column(Text)
    trace = relationship("TraceInfo", back_populates="tags")





# Model Registry Tables
class RegisteredModel(Base):
    __tablename__ = 'registered_models'
    
    name = Column(String(255), primary_key=True)
    creation_time = Column(BigInteger, default=lambda: int(time.time() * 1000))
    last_updated_time = Column(BigInteger, default=lambda: int(time.time() * 1000))
    description = Column(Text, nullable=True)
    
    # Relationships
    model_versions = relationship("ModelVersion", back_populates="registered_model", cascade="all, delete-orphan")
    tags = relationship("RegisteredModelTag", back_populates="registered_model", cascade="all, delete-orphan")

class ExperimentTag(Base):
    """
    Таблица тегов экспериментов.
    """
    __tablename__ = 'experiment_tags'
    
    key = Column(String(250), primary_key=True)
    value = Column(String(5000), nullable=True)
    experiment_id = Column(Integer, ForeignKey('experiments.experiment_id'), primary_key=True)
    
    # Отношение к эксперименту
    experiment = relationship("Experiment", back_populates="tags")

class ModelVersion(Base):
    __tablename__ = 'model_versions'
    
    name = Column(String(255), ForeignKey("registered_models.name"), primary_key=True)
    version = Column(Integer, primary_key=True)  # Версия задается вручную, не через sequence
    creation_time = Column(BigInteger, default=lambda: int(time.time() * 1000))
    last_updated_time = Column(BigInteger, default=lambda: int(time.time() * 1000))
    description = Column(Text, nullable=True)
    user_id = Column(String(255), nullable=True)
    current_stage = Column(String(50), default='None')
    source = Column(String(500), nullable=True)
    run_id = Column(String(36), nullable=True)
    status = Column(String(50), default='READY')
    status_message = Column(Text, nullable=True)
    run_link = Column(String(500), nullable=True)
    storage_location = Column(String(500), nullable=True)

    # Relationships
    registered_model = relationship("RegisteredModel", back_populates="model_versions")
    tags = relationship("ModelVersionTag", back_populates="model_version", cascade="all, delete-orphan")


class RegisteredModelTag(Base):
    __tablename__ = 'registered_model_tags'
    
    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=True)
    name = Column(String(255), ForeignKey("registered_models.name"), primary_key=True)
    
    # Relationships
    registered_model = relationship("RegisteredModel", back_populates="tags")




class ModelVersionTag(Base):
    __tablename__ = 'model_version_tags'
    __table_args__ = (
        ForeignKeyConstraint(['name', 'version'], ['model_versions.name', 'model_versions.version']),
    )
    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=True)
    name = Column(String(255), primary_key=True)
    version = Column(Integer, primary_key=True)
    
    # Relationships
    model_version = relationship("ModelVersion", back_populates="tags")


# --- Greenplum DDL helpers ---
def _run_distribution_statements(conn: Connection, statements: List[str]) -> None:
    for stmt in statements:
        try:
            conn.execute(text(stmt))
        except Exception as e:
            # Логируем и продолжаем, чтобы не падать из-за отсутствия расширений/прав
            logger.warning(f"Не удалось применить распределение таблицы: {stmt} — {e}")


def set_schema_for_models(schema_name: str) -> None:
    """
    Устанавливает схему для всех моделей SQLAlchemy.
    
    Args:
        schema_name: Имя схемы в PostgreSQL/Greenplum
    """
    for table in Base.metadata.tables.values():
        table.schema = schema_name
    logger.info(f"Установлена схема '{schema_name}' для всех моделей SQLAlchemy")


def set_gp_storage_options_for_models(options: dict) -> None:
    """Помечает таблицы для добавления WITH (...) при генерации DDL.

    Мы не полагаемся на postgresql_with (не везде поддерживается). Вместо этого
    через компилятор CreateTable добавляем суффикс WITH (...), если table.info['gp_with'] задан.
    Пример options: {"appendonly": False}
    """
    for table in Base.metadata.tables.values():
        table.info.setdefault('gp_with', options)
    logger.info(f"[GP] Помечены таблицы для WITH {options}")


@compiles(CreateTable, 'postgresql')
def _compile_create_table_with_gp(create, compiler, **kw):
    """Расширяем CREATE TABLE: добавляем WITH (...) для таблиц, где указан table.info['gp_with']."""
    stmt = compiler.visit_create_table(create, **kw)
    tbl = create.element
    opts = getattr(tbl, 'info', {}).get('gp_with')
    if opts:
        # Преобразуем словарь в 'k=v' вид с true/false
        parts = []
        for k, v in opts.items():
            if isinstance(v, bool):
                parts.append(f"{k}={'true' if v else 'false'}")
            else:
                parts.append(f"{k}={v}")
        return stmt + " WITH (" + ", ".join(parts) + ")"
    return stmt


def create_greenplum_tables(connection: Union[Connection, Engine], schema: str = 'public') -> None:
    """Создает таблицы и применяет DISTRIBUTED BY для Greenplum.

    Args:
        connection: Engine или Connection
        schema: имя схемы
    """
    logger.info(f"[GP] Создание таблиц в схеме '{schema}'")

    # 0. Обеспечиваем создание схемы вне общей транзакции, чтобы не откатить её позже
    try:
        if isinstance(connection, Engine):
            with connection.connect() as c:
                c = c.execution_options(isolation_level="AUTOCOMMIT")
                c.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        else:
            # Connection: используем AUTOCOMMIT, если поддерживается
            try:
                connection.execution_options(isolation_level="AUTOCOMMIT").execute(
                    text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
                )
            except Exception:
                # Фолбэк: обычная транзакция
                with connection.begin():
                    connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
    except Exception as e:
        logger.warning("[GP] Не удалось создать схему %s: %s", schema, e)

    # 1. Продолжаем основную работу в транзакции
    if isinstance(connection, Engine):
        begin_cm = connection.begin()
        engine_mode = True
    else:
        begin_cm = connection.begin()
        engine_mode = False

    with begin_cm as _ctx:
        conn = _ctx if engine_mode else connection
        logger.info("[GP] Вызван create_greenplum_tables(schema=%s)", schema)

        # 1. Прописываем схему в моделях перед create_all
        set_schema_for_models(schema)

        # 1.0. Принудительно задаем WITH (appendonly=false) на уровне каждой таблицы
        try:
            set_gp_storage_options_for_models({"appendonly": False})
        except Exception as e:
            logger.warning("[GP] Не удалось проставить WITH (appendonly=false) через диалектные опции: %s", e)

        # 1.0.1 Диагностика: показать DDL (первые 3 таблицы)
        try:
            preview = list(Base.metadata.sorted_tables)[:3]
            for t in preview:
                opts = t.info.get('gp_with', None)
                logger.info("[GP][DDL] table=%s, gp_with=%s", t.name, opts)
                ddl = str(CreateTable(t).compile(dialect=conn.dialect))
                logger.info("[GP][DDL] %s => %s", t.name, ddl.replace('\n', ' '))
        except Exception as e:
            logger.warning("[GP] Не удалось получить диагностический DDL: %s", e)

        # 1.1. Создаём таблицы вручную с гарантированным WITH (appendonly=false)
        created_tables: List[str] = []
        failed_tables: List[str] = []

        for table in Base.metadata.sorted_tables:
            table_created = False
            # Каждую таблицу создаём в отдельной транзакции
            with connection.begin() as sub_conn:
                try:
                    exists = sub_conn.execute(text(
                        "SELECT 1 FROM information_schema.tables WHERE table_schema=:s AND table_name=:t"),
                        {"s": schema, "t": table.name}
                    ).fetchone()

                    if not exists:
                        ddl = str(CreateTable(table).compile(dialect=sub_conn.dialect))
                        if 'WITH (' not in ddl:
                            ddl = ddl.rstrip(';') + ' WITH (appendonly=false)'
                        logger.info("[GP] Создание таблицы %s с appendonly=false", table.name)
                        sub_conn.execute(text(ddl))
                    table_created = True
                except Exception as e:
                    logger.warning("[GP] Не удалось создать таблицу %s: %s", table.name, e)
                    failed_tables.append(f"{table.name}({e})")
                    continue

            if table_created:
                created_tables.append(table.name)

        if created_tables:
            logger.info("[GP] Успешно созданы/проверены таблицы: %s", ", ".join(created_tables))
        if failed_tables:
            logger.error("[GP] Не удалось создать таблицы: %s", ", ".join(failed_tables))

        # 1.2. Добавляем недостающие новые колонки (идемпотентно)
        try:
            # Проверяем наличие deleted_time в runs
            col_exists = conn.execute(text(
                "SELECT 1 FROM information_schema.columns WHERE table_schema=:s AND table_name='runs' AND column_name='deleted_time'"), {"s": schema}).fetchone()
            if not col_exists:
                logger.info("[GP] Добавляем колонку runs.deleted_time")
                try:
                    conn.execute(text(f"ALTER TABLE {schema}.runs ADD COLUMN deleted_time BIGINT"))
                except Exception as e:
                    logger.warning("[GP] Не удалось добавить колонку deleted_time: %s", e)

            # Приводим input_tags: ожидается колонка name (а не key)
            input_tags_cols = conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_schema=:s AND table_name='input_tags'"), {"s": schema}).fetchall()
            input_cols = {r[0] for r in input_tags_cols}
            if 'input_tags' in {t.name for t in Base.metadata.sorted_tables}:  # таблица объявлена
                if 'name' not in input_cols and 'key' in input_cols:
                    try:
                        logger.info("[GP] Переименовываем input_tags.key -> name")
                        conn.execute(text(f"ALTER TABLE {schema}.input_tags RENAME COLUMN key TO name"))
                    except Exception as e:
                        logger.warning("[GP] Не удалось переименовать key->name в input_tags: %s", e)
                elif 'name' not in input_cols and 'key' not in input_cols:
                    try:
                        logger.info("[GP] Добавляем колонку name в input_tags")
                        conn.execute(text(f"ALTER TABLE {schema}.input_tags ADD COLUMN name VARCHAR(255)"))
                    except Exception as e:
                        logger.warning("[GP] Не удалось добавить name в input_tags: %s", e)
        except Exception as e:
            logger.warning("[GP] Ошибка при проверке/добавлении дополнительных колонок: %s", e)

        # 2. DISTRIBUTED BY – используем ключи бизнес-идентификаторов
        distribution_sql = [
            f"ALTER TABLE IF EXISTS {schema}.experiments SET DISTRIBUTED BY (experiment_id)",
            f"ALTER TABLE IF EXISTS {schema}.runs SET DISTRIBUTED BY (run_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.params SET DISTRIBUTED BY (run_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.metrics SET DISTRIBUTED BY (run_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.tags SET DISTRIBUTED BY (run_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.experiment_tags SET DISTRIBUTED BY (experiment_id)",
            f"ALTER TABLE IF EXISTS {schema}.registered_models SET DISTRIBUTED BY (name)",
            f"ALTER TABLE IF EXISTS {schema}.model_versions SET DISTRIBUTED BY (name, version)",
            f"ALTER TABLE IF EXISTS {schema}.registered_model_tags SET DISTRIBUTED BY (name)",
            f"ALTER TABLE IF EXISTS {schema}.model_version_tags SET DISTRIBUTED BY (name, version)",
            f"ALTER TABLE IF EXISTS {schema}.datasets SET DISTRIBUTED BY (dataset_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.inputs SET DISTRIBUTED BY (input_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.input_tags SET DISTRIBUTED BY (input_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.latest_metrics SET DISTRIBUTED BY (run_uuid)",
            f"ALTER TABLE IF EXISTS {schema}.registered_model_aliases SET DISTRIBUTED BY (name)",
            f"ALTER TABLE IF EXISTS {schema}.trace_info SET DISTRIBUTED BY (request_id)",
            f"ALTER TABLE IF EXISTS {schema}.trace_request_metadata SET DISTRIBUTED BY (request_id)",
            f"ALTER TABLE IF EXISTS {schema}.trace_tags SET DISTRIBUTED BY (request_id)",
        ]
        logger.info("[GP] Применение DISTRIBUTED BY")
        _run_distribution_statements(conn, distribution_sql)

        # 3. Проверка
        existing = {r[0] for r in conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema=:s"), {"s": schema})}
        required = {t.name for t in Base.metadata.sorted_tables}
        missing = required - existing
        if missing:
            logger.error(f"[GP] После создания отсутствуют таблицы: {sorted(missing)}")
        else:
            logger.info("[GP] Все таблицы успешно созданы")

 
def main():
    try:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
        con = r'postgresql+psycopg2://gpadmin:gpadmin@localhost:5432/mlflow_ai'
        engine = create_engine(con)
        schema = 'mlflow_test10'

        create_greenplum_tables(engine, schema)
        with engine.connect() as c:
            rows = c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema=:s"), {"s": schema}).fetchall()
            print("Таблицы в схеме:", [r[0] for r in rows])
        logger.info("Проверка завершена")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()