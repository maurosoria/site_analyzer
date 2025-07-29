from typing import Type
from storage.base import BaseStorage
from storage.file_storage import FileStorage
from storage.mongodb_storage import MongoDBStorage
from storage.sql_storage import SQLStorage
from core.config import Config
from core.exceptions import ConfigurationException

class StorageFactory:
    """Factory for creating storage backends"""
    
    _storage_types = {
        'file': FileStorage,
        'mongodb': MongoDBStorage,
        'sql': SQLStorage,
    }
    
    @classmethod
    def create(cls, config) -> BaseStorage:
        """Create storage backend based on config"""
        if isinstance(config, dict):
            storage_type = config.get('type', '').lower()
        else:
            storage_type = config.storage_type.lower()
        
        if storage_type not in cls._storage_types:
            raise ConfigurationException(f"Unknown storage type: {storage_type}")
            
        storage_class = cls._storage_types[storage_type]
        return storage_class(config)
    
    @classmethod
    def register_storage(cls, name: str, storage_class: Type[BaseStorage]):
        """Register a new storage backend"""
        cls._storage_types[name] = storage_class
    
    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available storage types"""
        return list(cls._storage_types.keys())
