"""
Vue.js framework detection plugin
"""

import re
from typing import Dict, Any, Optional
from .base import BaseFrameworkPlugin, FrameworkDetection

class VuePlugin(BaseFrameworkPlugin):
    """Vue.js framework detection"""
    
    def get_name(self) -> str:
        return "Vue.js"
    
    def detect(self, content: str, js_results: Dict[str, Any], url: str) -> Optional[FrameworkDetection]:
        """Detect Vue.js framework"""
        indicators = []
        files = []
        confidence = 0.0
        version = None
        
        script_sources = js_results.get('script_sources', [])
        for src in script_sources:
            if 'vue' in src.lower():
                indicators.append(f"Vue script: {src}")
                files.append(src)
                confidence += 0.4
        
        vue_globals = ['Vue', '__VUE__', '__VUE_DEVTOOLS_GLOBAL_HOOK__', '__VUE_OPTIONS_API__']
        found_globals = self._check_js_globals(js_results, vue_globals)
        if found_globals:
            indicators.extend([f"Vue global: {g}" for g in found_globals])
            confidence += 0.5
        
        vue_patterns = [
            r'v-[a-z]+\s*=',           # Vue directives
            r'@[a-z]+\s*=',            # Vue event shortcuts
            r':[a-z]+\s*=',            # Vue property binding shortcuts
            r'{{[^}]+}}',              # Vue interpolation
            r'<template[^>]*>',        # Vue templates
        ]
        
        for pattern in vue_patterns:
            matches = re.findall(pattern, content)
            if matches:
                indicators.append(f"Vue pattern: {pattern} ({len(matches)} matches)")
                confidence += 0.3
        
        if 'vue-router' in content.lower() or 'router-view' in content.lower():
            indicators.append("Vue Router detected")
            confidence += 0.3
        
        if 'vuex' in content.lower() or '$store' in content:
            indicators.append("Vuex detected")
            confidence += 0.2
        
        if '__NUXT__' in content or 'nuxt' in content.lower():
            indicators.append("Nuxt.js detected")
            confidence += 0.4
        
        vue_cli_files = ['app.js', 'vendor.js', 'chunk-vendors.js']
        found_cli_files = [f for f in script_sources if any(cli_file in f for cli_file in vue_cli_files)]
        if found_cli_files:
            indicators.append(f"Vue CLI structure detected: {found_cli_files}")
            confidence += 0.3
        
        version_patterns = [
            r'vue["\']?\s*:\s*["\']([0-9]+\.[0-9]+\.[0-9]+)',
            r'Vue\s+([0-9]+\.[0-9]+\.[0-9]+)',
            r'"vue":\s*"([^"]+)"'
        ]
        version = self._extract_version(content, version_patterns)
        
        if 'createApp' in content or 'Vue.createApp' in content:
            indicators.append("Vue 3 composition API detected")
            confidence += 0.3
        
        if 'new Vue(' in content:
            indicators.append("Vue 2 instance detected")
            confidence += 0.3
        
        if confidence > 0.3:
            return FrameworkDetection(
                name=self.get_name(),
                version=version,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                files=files
            )
        
        return None
