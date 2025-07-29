"""
Angular framework detection plugin
"""

import re
from typing import Dict, Any, Optional
from .base import BaseFrameworkPlugin, FrameworkDetection

class AngularPlugin(BaseFrameworkPlugin):
    """Angular framework detection"""
    
    def get_name(self) -> str:
        return "Angular"
    
    def detect(self, content: str, js_results: Dict[str, Any], url: str) -> Optional[FrameworkDetection]:
        """Detect Angular framework"""
        indicators = []
        files = []
        confidence = 0.0
        version = None
        
        script_sources = js_results.get('script_sources', [])
        for src in script_sources:
            if any(angular_file in src.lower() for angular_file in ['angular', 'ng-', '@angular']):
                indicators.append(f"Angular script: {src}")
                files.append(src)
                confidence += 0.4
        
        angular_globals = ['ng', 'angular', '__NG_DEVTOOLS_GLOBAL_HOOK__', 'getAllAngularRootElements']
        found_globals = self._check_js_globals(js_results, angular_globals)
        if found_globals:
            indicators.extend([f"Angular global: {g}" for g in found_globals])
            confidence += 0.5
        
        angular_patterns = [
            r'ng-[a-z]+\s*=',           # AngularJS directives
            r'\*ng[A-Z][a-zA-Z]*',      # Angular structural directives
            r'\[ng[A-Z][a-zA-Z]*\]',    # Angular property binding
            r'\(ng[A-Z][a-zA-Z]*\)',    # Angular event binding
            r'{{[^}]+}}',               # Angular interpolation
            r'ng:///',                  # Angular inline templates
        ]
        
        for pattern in angular_patterns:
            matches = re.findall(pattern, content)
            if matches:
                indicators.append(f"Angular pattern: {pattern} ({len(matches)} matches)")
                confidence += 0.3
        
        if 'router-outlet' in content.lower() or 'routerLink' in content:
            indicators.append("Angular Router detected")
            confidence += 0.3
        
        if 'mat-' in content or '@angular/material' in content:
            indicators.append("Angular Material detected")
            confidence += 0.2
        
        if 'main.js' in script_sources and 'polyfills.js' in script_sources:
            indicators.append("Angular CLI structure detected")
            confidence += 0.3
        
        version_patterns = [
            r'@angular/core["\']?\s*:\s*["\']([0-9]+\.[0-9]+\.[0-9]+)',
            r'Angular\s+([0-9]+\.[0-9]+\.[0-9]+)',
            r'"@angular/core":\s*"([^"]+)"'
        ]
        version = self._extract_version(content, version_patterns)
        
        if 'angular.js' in content.lower() or 'angularjs' in content.lower():
            indicators.append("AngularJS (legacy) detected")
            confidence += 0.4
        
        if '__ANGULAR_UNIVERSAL__' in content or 'ng-state' in content:
            indicators.append("Angular Universal (SSR) detected")
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
