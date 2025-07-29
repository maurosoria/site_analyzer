"""
React framework detection plugin
"""

import re
from typing import Dict, Any, Optional
from .base import BaseFrameworkPlugin, FrameworkDetection

class ReactPlugin(BaseFrameworkPlugin):
    """React framework detection"""
    
    def get_name(self) -> str:
        return "React"
    
    def detect(self, content: str, js_results: Dict[str, Any], url: str) -> Optional[FrameworkDetection]:
        """Detect React framework"""
        indicators = []
        files = []
        confidence = 0.0
        version = None
        
        script_sources = js_results.get('script_sources', [])
        for src in script_sources:
            if 'react' in src.lower():
                indicators.append(f"React script: {src}")
                files.append(src)
                confidence += 0.3
        
        react_globals = ['React', '__REACT_DEVTOOLS_GLOBAL_HOOK__', '__REACT_HOT_LOADER__']
        found_globals = self._check_js_globals(js_results, react_globals)
        if found_globals:
            indicators.extend([f"React global: {g}" for g in found_globals])
            confidence += 0.4
        
        if 'React.createElement' in content or 'react.createElement' in content:
            indicators.append("React.createElement found")
            confidence += 0.3
        
        jsx_patterns = [
            r'<[A-Z][a-zA-Z0-9]*[^>]*>',  # JSX components
            r'className\s*=',              # JSX className
            r'onClick\s*=\s*\{',          # JSX event handlers
        ]
        
        for pattern in jsx_patterns:
            if re.search(pattern, content):
                indicators.append(f"JSX pattern: {pattern}")
                confidence += 0.2
        
        if '__NEXT_DATA__' in content or '__NEXT_DATA__' in str(js_results):
            indicators.append("Next.js detected (__NEXT_DATA__)")
            confidence += 0.5
            files.extend([f for f in script_sources if 'next' in f.lower()])
        
        if '/static/js/' in content and 'react' in content.lower():
            indicators.append("Create React App structure detected")
            confidence += 0.3
        
        version_patterns = [
            r'react["\']?\s*:\s*["\']([0-9]+\.[0-9]+\.[0-9]+)',
            r'React\s+([0-9]+\.[0-9]+\.[0-9]+)',
            r'"react":\s*"([^"]+)"'
        ]
        version = self._extract_version(content, version_patterns)
        
        if 'react-router' in content.lower() or 'ReactRouter' in str(js_results):
            indicators.append("React Router detected")
            confidence += 0.2
        
        redux_globals = ['__REDUX_DEVTOOLS_EXTENSION__', 'Redux']
        found_redux = self._check_js_globals(js_results, redux_globals)
        if found_redux:
            indicators.extend([f"Redux: {g}" for g in found_redux])
            confidence += 0.2
        
        if confidence > 0.3:
            return FrameworkDetection(
                name=self.get_name(),
                version=version,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                files=files
            )
        
        return None
