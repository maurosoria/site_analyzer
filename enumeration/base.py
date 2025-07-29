from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
from ..models.scan_result import EnumerationResult
from ..core.config import Config

class BaseEnumerator(ABC):
    """Base class for all enumeration strategies"""
    
    def __init__(self, config: Config):
        self.config = config
        
    @abstractmethod
    def get_name(self) -> str:
        """Get enumerator name"""
        pass
        
    @abstractmethod
    def enumerate(self, target: str) -> EnumerationResult:
        """Perform enumeration on target"""
        pass
        
    def is_enabled(self) -> bool:
        """Check if this enumerator is enabled in config"""
        return self.get_name() in self.config.enabled_enumerators
        
    def _create_result(self, target: str, data: Dict, errors: Optional[list] = None) -> EnumerationResult:
        """Helper to create enumeration result"""
        return EnumerationResult(
            enumerator_name=self.get_name(),
            target=target,
            timestamp=datetime.now(),
            data=data,
            errors=errors or []
        )
