"""MLflow Greenplum Plugin

Этот пакет предоставляет поддержку Greenplum базы данных для MLflow,
включая кастомные методы создания таблиц и обработки миграций.

Пример использования (создание таблиц в целевой схеме):
    from mlflow_greenplum import create_greenplum_tables
    from sqlalchemy import create_engine
    engine = create_engine("postgresql+psycopg2://user:pass@host:5432/db")
    create_greenplum_tables(engine, schema="mlflow")
"""

import logging

__version__ = "0.1.0"
__author__ = "Your Name"

# Настройка логирования
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Импортируем основной API
from .models import create_greenplum_tables

# Классы импортируются MLflow через entry points (см. pyproject.toml / setup.py)
# Не импортируем классы здесь, чтобы избежать циклических импортов

__all__ = ['create_greenplum_tables']
