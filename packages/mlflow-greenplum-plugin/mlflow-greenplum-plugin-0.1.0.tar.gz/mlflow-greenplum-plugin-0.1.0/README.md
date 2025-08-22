# MLflow Greenplum Plugin

Плагин для MLflow, который обеспечивает поддержку Greenplum базы данных с кастомными методами создания таблиц и обработки миграций.

## Описание

Этот плагин решает проблему работы MLflow с Greenplum, где стандартные миграции PostgreSQL могут не работать корректно. Вместо выполнения пошаговых миграций, плагин:

1. **Эмулирует миграции** - создает записи о выполненных миграциях в таблице `alembic_version`
2. **Создает финальные таблицы** - сразу создает таблицы в их итоговом виде, минуя промежуточные миграции
3. **Поддерживает Greenplum** - использует специфические для Greenplum функции и ограничения
4. **Совместимость с PostgreSQL** - работает как с Greenplum, так и с обычной PostgreSQL

## Установка

```bash
pip install -e .
```

Или установите из репозитория:

```bash
pip install git+https://github.com/yourusername/mlflow-greenplum-plugin.git
```

## Конфигурация

Настройте MLflow для использования Greenplum:

```python
import mlflow
mlflow.set_tracking_uri("greenplum://user:password@host:port/database")
```

Или запустите MLflow сервер:

```bash
mlflow server --backend-store-uri "greenplum://gpadmin:gpadmin@localhost:5432/mlflow_ai?schema=public" --default-artifact-root ./mlruns --host 127.0.0.1 --port 5000
```

## Использование

После установки плагин автоматически регистрируется в MLflow и будет использоваться при подключении к Greenplum базе данных.

### Пример базового использования:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

# Настройка подключения к Greenplum
mlflow.set_tracking_uri("greenplum://gpadmin:gpadmin@localhost:5432/mlflow_db?options=-csearch_path%3Dmlflow_schema")

# Создание эксперимента
experiment_id = mlflow.create_experiment("my_experiment")

# Запуск эксперимента
with mlflow.start_run(experiment_id=experiment_id):
    # Ваш код машинного обучения
    model = RandomForestClassifier()
    # ... обучение модели ...
    
    # Логирование параметров, метрик и модели
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.sklearn.log_model(model, "model")
```

## Особенности реализации

### Архитектура плагина:

- **GreenplumStore** - кастомный tracking store для работы с Greenplum
- **GreenplumMigrationManager** - управление миграциями (эмуляция)
- **create_greenplum_tables** - создание таблиц в финальном виде
- **Утилиты** - вспомогательные функции для работы с Greenplum

### Ключевые особенности:

- **Патчинг функций MLflow** - перехватывает процесс инициализации и верификации схемы
- **Эмуляция миграций** - вместо реального выполнения миграций создает записи в alembic_version
- **Оптимизация для Greenplum** - поддержка распределенных таблиц и оптимизация запросов
- **Совместимость** - работает с pg8000 драйвером для избежания проблем с psycopg2 на Windows

### Особенности Greenplum:

- **Распределенные таблицы** - оптимизация таблиц с помощью DISTRIBUTED BY
- **Хеш-объединения** - использование хеш-объединений вместо слияния
- **Параллельное выполнение** - выполнение запросов на всех сегментах
- **Секционирование** - поддержка секционированных таблиц для больших объемов данных

### Поддерживаемые драйверы:

- **pg8000** - основной рекомендуемый драйвер (устанавливается автоматически)
- **psycopg2** - поддерживается, но может требовать дополнительной настройки на Windows

## Структура проекта

- `mlflow_greenplum/` - основной пакет плагина
  - `store.py` - кастомный tracking store для Greenplum
  - `migrations.py` - управление миграциями
  - `models.py` - модели данных и DDL запросы
  - `utils.py` - вспомогательные функции
  - `artifacts.py` - repository для артефактов

## Разработка

Для разработки установите зависимости:

```bash
pip install -r requirements-dev.txt
```

Запустите тесты:

```bash
pytest
```

## Примеры

В директории `examples/` находятся примеры использования:

- `basic_usage.py` - базовый пример использования с scikit-learn
- `setup_and_test.py` - пример настройки и тестирования соединения с Greenplum

## Поддерживаемые версии

- Python 3.8+
- MLflow 2.0.0+
- Greenplum 6+
- PostgreSQL 10+

## Лицензия

Apache License 2.0

Запуск тестов:

```bash
pytest tests/
```

Быстрая проверка установки:

```bash
python quick_test.py
```

## Устранение неполадок

### Ошибки подключения:

1. Убедитесь что Greenplum/PostgreSQL сервер запущен и доступен
2. Проверьте правильность параметров подключения в URI
3. Убедитесь что база данных существует и у пользователя есть права на создание таблиц

### Проблемы с миграциями:

Если MLflow сообщает о проблемах со схемой БД, попробуйте:

```sql
-- Очистить таблицу миграций (ОСТОРОЖНО: удалит данные о миграциях)
DROP TABLE IF EXISTS alembic_version;
```

Затем перезапустите приложение - плагин пересоздаст таблицы и миграции.

## Примеры

Смотрите директорию `examples/` для примеров использования:

- `basic_usage.py` - базовый пример с scikit-learn
- `setup_and_test.py` - настройка и тестирование подключения

## Технологии

- **MLflow** >= 2.0.0 - основной фреймворк
- **SQLAlchemy** >= 1.4.0 - ORM и подключение к БД  
- **pg8000** >= 1.29.0 - драйвер PostgreSQL/Greenplum
- **Alembic** >= 1.7.0 - миграции (для эмуляции)

## Лицензия

Apache License 2.0

## Поддержка

При возникновении проблем создайте issue в репозитории с подробным описанием проблемы и логами.
