"""
Base framework detection plugin
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class FrameworkDetection:
    """Framework detection result"""
    name: str
    version: Optional[str] = None
    confidence: float = 0.0
    indicators: Optional[List[str]] = None
    files: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.indicators is None:
            self.indicators = []
        if self.files is None:
            self.files = []

class BaseFrameworkPlugin(ABC):
    """Base class for framework detection plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the framework name this plugin detects"""
        pass
    
    @abstractmethod
    def detect(self, content: str, js_results: Dict[str, Any], url: str) -> Optional[FrameworkDetection]:
        """
        Detect framework in the given content and JS execution results
        
        Args:
            content: HTML content of the page
            js_results: JavaScript execution results from injection
            url: Target URL
            
        Returns:
            FrameworkDetection if framework is detected, None otherwise
        """
        pass
    
    def _extract_version(self, content: str, patterns: List[str]) -> Optional[str]:
        """Extract version from content using regex patterns"""
        import re
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _check_js_globals(self, js_results: Dict[str, Any], globals_to_check: List[str]) -> List[str]:
        """Check for JavaScript global variables in execution results"""
        found_globals = []
        window_props = js_results.get('window_properties', [])
        
        for global_var in globals_to_check:
            if global_var in window_props:
                found_globals.append(global_var)
        
        return found_globals
