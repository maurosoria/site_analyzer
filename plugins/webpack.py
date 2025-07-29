"""
Webpack bundler detection plugin
"""

import re
from typing import Dict, Any, Optional
from .base import BaseFrameworkPlugin, FrameworkDetection

class WebpackPlugin(BaseFrameworkPlugin):
    """Webpack bundler detection"""
    
    def get_name(self) -> str:
        return "Webpack"
    
    def detect(self, content: str, js_results: Dict[str, Any], url: str) -> Optional[FrameworkDetection]:
        """Detect Webpack bundler"""
        indicators = []
        files = []
        confidence = 0.0
        version = None
        
        script_sources = js_results.get('script_sources', [])
        for src in script_sources:
            if any(webpack_pattern in src.lower() for webpack_pattern in ['webpack', 'chunk', 'bundle']):
                indicators.append(f"Webpack file: {src}")
                files.append(src)
                confidence += 0.3
        
        webpack_patterns = [
            r'__webpack_require__',
            r'webpackJsonp',
            r'__webpack_exports__',
            r'__webpack_modules__',
            r'webpack_require\.r',
            r'webpack_require\.d',
            r'/\*\* webpack version: ([0-9]+\.[0-9]+\.[0-9]+) \*/',
        ]
        
        for pattern in webpack_patterns:
            matches = re.findall(pattern, content)
            if matches:
                indicators.append(f"Webpack pattern: {pattern}")
                confidence += 0.4
                
                if 'webpack version:' in pattern and matches:
                    version = matches[0]
        
        if 'webpackChunkName' in content:
            indicators.append("Webpack dynamic imports detected")
            confidence += 0.3
        
        if '__webpack_hmr' in content or 'webpackHotUpdate' in content:
            indicators.append("Webpack HMR detected")
            confidence += 0.2
        
        webpack_file_patterns = [
            r'[a-f0-9]{8,}\.js',      # Webpack hash files
            r'chunk\.[a-f0-9]+\.js',  # Webpack chunks
            r'vendor\.[a-f0-9]+\.js', # Vendor bundles
            r'runtime\.[a-f0-9]+\.js' # Runtime chunks
        ]
        
        for pattern in webpack_file_patterns:
            matches = re.findall(pattern, content)
            if matches:
                indicators.append(f"Webpack file pattern: {pattern} ({len(matches)} files)")
                confidence += 0.2
        
        if 'webpack-dev-server' in content or '__webpack_dev_server__' in content:
            indicators.append("Webpack Dev Server detected")
            confidence += 0.2
        
        if '//# sourceMappingURL=' in content:
            indicators.append("Source maps detected (likely Webpack)")
            confidence += 0.1
        
        if confidence > 0.3:
            return FrameworkDetection(
                name=self.get_name(),
                version=version,
                confidence=min(confidence, 1.0),
                indicators=indicators,
                files=files
            )
        
        return None
