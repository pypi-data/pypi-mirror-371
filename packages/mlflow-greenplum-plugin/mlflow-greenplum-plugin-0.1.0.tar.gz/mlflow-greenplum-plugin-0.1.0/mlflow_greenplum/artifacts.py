"""
Artifact Repository для Greenplum

Этот модуль обеспечивает хранение артефактов MLflow с учетом особенностей Greenplum.
Может использовать как файловую систему, так и специальные хранилища.
"""

import logging
import os
from typing import Optional, List
from mlflow.entities.file_info import FileInfo
from mlflow.store.artifact.artifact_repo import ArtifactRepository

logger = logging.getLogger(__name__)


class GreenplumArtifactRepository(ArtifactRepository):
    """
    Кастомный artifact repository для работы с Greenplum.
    
    Расширяет базовую функциональность для интеграции с Greenplum
    и оптимизации хранения артефактов.
    """
    
    def __init__(self, artifact_uri: str):
        """
        Инициализация repository для артефактов.
        
        Args:
            artifact_uri: URI для хранения артефактов
        """
        logger.info(f"Инициализация GreenplumArtifactRepository с URI: {artifact_uri}")
        super().__init__(artifact_uri)
        
    def log_artifact(self, local_file: str, artifact_path: Optional[str] = None):
        """
        Загружает локальный файл как артефакт.
        
        Args:
            local_file: Путь к локальному файлу
            artifact_path: Относительный путь в хранилище артефактов
        """
        logger.debug(f"Загрузка артефакта: {local_file} -> {artifact_path}")
        
        # Используем базовую реализацию с возможными оптимизациями
        super().log_artifact(local_file, artifact_path)
        
    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None):
        """
        Загружает директорию как артефакты.
        
        Args:
            local_dir: Путь к локальной директории
            artifact_path: Относительный путь в хранилище артефактов
        """
        logger.debug(f"Загрузка артефактов из директории: {local_dir} -> {artifact_path}")
        
        # Используем базовую реализацию с возможными оптимизациями
        super().log_artifacts(local_dir, artifact_path)
        
    def list_artifacts(self, path: Optional[str] = None) -> List[FileInfo]:
        """
        Возвращает список артефактов по указанному пути.
        
        Args:
            path: Путь для поиска артефактов
            
        Returns:
            Список артефактов
        """
        logger.debug(f"Получение списка артефактов для пути: {path}")
        
        # Используем базовую реализацию
        return super().list_artifacts(path)
        
    def download_artifacts(self, artifact_path: str, dst_path: Optional[str] = None) -> str:
        """
        Скачивает артефакты из хранилища.
        
        Args:
            artifact_path: Путь к артефакту в хранилище
            dst_path: Локальный путь для сохранения
            
        Returns:
            Путь к скачанному артефакту
        """
        logger.debug(f"Скачивание артефакта: {artifact_path} -> {dst_path}")
        
        # Используем базовую реализацию
        return super().download_artifacts(artifact_path, dst_path)
