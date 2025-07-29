from abc import ABC, abstractmethod
from typing import Any, Dict
from ..core.config import Config
from ..models.scan_result import ScanResults

class BaseInterface(ABC):
    """Base interface for all user interfaces"""
    
    def __init__(self, config: Config):
        self.config = config
        
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Run the interface"""
        pass
        
    @abstractmethod
    def display_results(self, results: ScanResults):
        """Display scan results"""
        pass
