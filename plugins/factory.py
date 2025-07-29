"""
Framework detection plugin factory
"""

from typing import List, Dict, Any, Optional
from .base import BaseFrameworkPlugin, FrameworkDetection
from .react import ReactPlugin
from .angular import AngularPlugin
from .vue import VuePlugin
from .webpack import WebpackPlugin

class FrameworkDetectionEngine:
    """Engine for detecting JavaScript frameworks and tools"""
    
    def __init__(self):
        self.plugins: List[BaseFrameworkPlugin] = [
            ReactPlugin(),
            AngularPlugin(),
            VuePlugin(),
            WebpackPlugin(),
        ]
    
    def detect_frameworks(self, content: str, js_results: Dict[str, Any], url: str) -> List[FrameworkDetection]:
        """
        Detect all frameworks in the given content
        
        Args:
            content: HTML content of the page
            js_results: JavaScript execution results from injection
            url: Target URL
            
        Returns:
            List of detected frameworks
        """
        detections = []
        
        for plugin in self.plugins:
            try:
                detection = plugin.detect(content, js_results, url)
                if detection:
                    detections.append(detection)
            except Exception as e:
                print(f"Error in {plugin.get_name()} plugin: {e}")
        
        detections.sort(key=lambda x: x.confidence, reverse=True)
        
        return detections
    
    def get_framework_summary(self, detections: List[FrameworkDetection]) -> Dict[str, Any]:
        """Get a summary of detected frameworks"""
        if not detections:
            return {"frameworks": [], "primary_framework": None, "total_confidence": 0.0}
        
        frameworks = []
        total_confidence = 0.0
        
        for detection in detections:
            frameworks.append({
                "name": detection.name,
                "version": detection.version,
                "confidence": detection.confidence,
                "indicators_count": len(detection.indicators),
                "files_count": len(detection.files)
            })
            total_confidence += detection.confidence
        
        return {
            "frameworks": frameworks,
            "primary_framework": frameworks[0] if frameworks else None,
            "total_confidence": min(total_confidence, 1.0),
            "framework_count": len(frameworks)
        }
