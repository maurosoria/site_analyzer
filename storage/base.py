from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from ..models.scan_result import ScanResults
from ..core.config import Config

class BaseStorage(ABC):
    """Base storage interface"""
    
    def __init__(self, config: Config):
        self.config = config
        
    @abstractmethod
    def save(self, result: ScanResults) -> str:
        """Save scan result and return scan ID"""
        pass
        
    @abstractmethod
    def load(self, scan_id: str) -> Optional[ScanResults]:
        """Load scan result by ID"""
        pass
        
    @abstractmethod
    def list_scans(self, limit: int = 100) -> List[Dict]:
        """List recent scans"""
        pass
        
    @abstractmethod
    def delete(self, scan_id: str) -> bool:
        """Delete scan result"""
        pass

class FileStorageMixin:
    """File-based storage operations mixin"""
    
    def _get_file_path(self, scan_id: str, extension: str = "json") -> str:
        """Get file path for scan ID"""
        storage_dir = getattr(self, 'config').storage_config.get('directory', './scans')
        return f"{storage_dir}/{scan_id}.{extension}"
        
    def _ensure_directory(self, path: str):
        """Ensure directory exists"""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)

class SQLStorageMixin:
    """SQL database storage operations mixin"""
    
    _conn = None
    _reuse_connection = True
    
    def get_connection(self, database_url: str):
        """Get database connection"""
        if not self._reuse_connection:
            return self._create_connection(database_url)
            
        if not self._conn:
            self._conn = self._create_connection(database_url)
            
        return self._conn
        
    def _create_connection(self, database_url: str):
        """Create new database connection - to be implemented by subclasses"""
        raise NotImplementedError
        
    def get_create_table_query(self) -> str:
        """Get SQL query to create scans table"""
        return """
        CREATE TABLE IF NOT EXISTS scans (
            scan_id VARCHAR(255) PRIMARY KEY,
            target VARCHAR(255) NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            status VARCHAR(50) NOT NULL,
            result_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

class MongoStorageMixin:
    """MongoDB storage operations mixin"""
    
    def _get_collection(self):
        """Get MongoDB collection"""
        from pymongo import MongoClient
        
        mongo_config = getattr(self, 'config').storage_config
        client = MongoClient(mongo_config.get('connection_string', 'mongodb://localhost:27017'))
        db = client[mongo_config.get('database', 'site_analyzer')]
        return db[mongo_config.get('collection', 'scans')]
