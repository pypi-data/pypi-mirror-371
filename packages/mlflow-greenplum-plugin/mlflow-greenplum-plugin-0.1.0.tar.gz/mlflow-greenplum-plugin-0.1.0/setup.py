from setuptools import setup, find_packages

setup(
    name="mlflow-greenplum-plugin",
    version="0.1.0",
    description="MLflow plugin for Greenplum database support",
    author="Russ Russell",
    author_email="625ruslan@gmail.com",
    packages=find_packages(),
    install_requires=[
        "mlflow>=2.0.0",
        "sqlalchemy>=1.4.0,<2.0.0",
        "alembic>=1.7.0",
        "psycopg2>=2.8.6"
    ],
    entry_points={
        "mlflow.tracking_store": [
            "greenplum=mlflow_greenplum.store:GreenplumStore"
        ],
        "mlflow.model_registry_store": [
            "greenplum=mlflow_greenplum.registry:GreenplumModelRegistryStore"
        ],
        "mlflow.artifact_repository": [
            "greenplum=mlflow_greenplum.artifacts:GreenplumArtifactRepository"
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
