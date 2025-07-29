from typing import Dict, Type, List
from .base import BaseEnumerator
from .security_trails import SecurityTrailsEnumerator
from .dns_enumeration import DNSEnumerator
from .web_scanner import WebScannerEnumerator
from ..core.config import Config
from ..core.exceptions import ConfigurationException

class EnumeratorFactory:
    """Factory for creating enumeration strategies"""
    
    _enumerator_types = {
        'security_trails': SecurityTrailsEnumerator,
        'dns_enumeration': DNSEnumerator,
        'web_scanner': WebScannerEnumerator,
    }
    
    @classmethod
    def create_enumerators(cls, config: Config) -> List[BaseEnumerator]:
        """Create all enabled enumerators based on config"""
        enumerators = []
        
        for enumerator_name in config.enabled_enumerators:
            if enumerator_name in cls._enumerator_types:
                try:
                    enumerator_class = cls._enumerator_types[enumerator_name]
                    enumerator = enumerator_class(config)
                    if enumerator.is_enabled():
                        enumerators.append(enumerator)
                except Exception as e:
                    print(f"Failed to create {enumerator_name} enumerator: {e}")
            else:
                print(f"Unknown enumerator type: {enumerator_name}")
        
        return enumerators
    
    @classmethod
    def create_enumerator(cls, enumerator_type: str, config: Config) -> BaseEnumerator:
        """Create a single enumerator"""
        if enumerator_type not in cls._enumerator_types:
            raise ConfigurationException(f"Unknown enumerator type: {enumerator_type}")
            
        enumerator_class = cls._enumerator_types[enumerator_type]
        return enumerator_class(config)
    
    @classmethod
    def register_enumerator(cls, name: str, enumerator_class: Type[BaseEnumerator]):
        """Register a new enumerator type"""
        cls._enumerator_types[name] = enumerator_class
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available enumerator types"""
        return list(cls._enumerator_types.keys())
