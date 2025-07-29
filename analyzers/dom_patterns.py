"""
DOM pattern analysis for security and functionality detection
"""

import re
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DOMPatternMatch:
    """DOM pattern match result"""
    name: str
    description: str
    severity: str
    matches: List[str]
    count: int
    file_source: Optional[str] = None

class DOMPatternAnalyzer:
    """Analyzer for DOM patterns in JavaScript code"""
    
    def __init__(self, patterns_file: str = "./db/dom_patterns.json"):
        self.patterns_file = patterns_file
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load DOM patterns from JSON file"""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading DOM patterns: {e}")
        
        return [
            {
                "name": "html_sink",
                "description": "Potential XSS sink - innerHTML usage",
                "regex": "(innerHTML|insertAdjacentHTML)\\s*[+*/\\-=]*\\s*",
                "severity": "high"
            },
            {
                "name": "eval_usage",
                "description": "Eval function usage - code injection risk",
                "regex": "\\beval\\s*\\(",
                "severity": "high"
            }
        ]
    
    def analyze_content(self, content: str, source_file: Optional[str] = None) -> List[DOMPatternMatch]:
        """
        Analyze content for DOM patterns
        
        Args:
            content: JavaScript/HTML content to analyze
            source_file: Optional source file name
            
        Returns:
            List of pattern matches found
        """
        matches = []
        
        for pattern in self.patterns:
            try:
                regex_matches = re.findall(pattern['regex'], content, re.IGNORECASE | re.MULTILINE)
                
                if regex_matches:
                    match = DOMPatternMatch(
                        name=pattern['name'],
                        description=pattern['description'],
                        severity=pattern['severity'],
                        matches=regex_matches,
                        count=len(regex_matches),
                        file_source=source_file
                    )
                    matches.append(match)
                    
            except re.error as e:
                print(f"Invalid regex pattern '{pattern['name']}': {e}")
        
        return matches
    
    def analyze_js_results(self, js_results: Dict[str, Any]) -> List[DOMPatternMatch]:
        """
        Analyze JavaScript execution results for DOM patterns
        
        Args:
            js_results: JavaScript execution results from injection
            
        Returns:
            List of pattern matches found
        """
        all_matches = []
        
        for script_name, script_result in js_results.items():
            if isinstance(script_result, dict):
                content = str(script_result)
                matches = self.analyze_content(content, script_name)
                all_matches.extend(matches)
            elif isinstance(script_result, str):
                matches = self.analyze_content(script_result, script_name)
                all_matches.extend(matches)
        
        return all_matches
    
    def get_security_score(self, matches: List[DOMPatternMatch]) -> Dict[str, Any]:
        """
        Calculate security score based on pattern matches
        
        Args:
            matches: List of DOM pattern matches
            
        Returns:
            Security score and breakdown
        """
        severity_weights = {
            'high': 10,
            'medium': 5,
            'info': 1
        }
        
        total_score = 0
        severity_counts = {'high': 0, 'medium': 0, 'info': 0}
        
        for match in matches:
            weight = severity_weights.get(match.severity, 1)
            total_score += weight * match.count
            severity_counts[match.severity] += match.count
        
        max_possible_score = len(matches) * 10  # Assuming all high severity
        normalized_score = min((total_score / max(max_possible_score, 1)) * 100, 100) if max_possible_score > 0 else 0
        
        return {
            'total_score': total_score,
            'normalized_score': normalized_score,
            'severity_breakdown': severity_counts,
            'total_patterns': len(matches),
            'risk_level': self._get_risk_level(normalized_score)
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score"""
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def generate_report(self, matches: List[DOMPatternMatch]) -> Dict[str, Any]:
        """Generate comprehensive DOM pattern analysis report"""
        security_score = self.get_security_score(matches)
        
        by_severity = {}
        for match in matches:
            if match.severity not in by_severity:
                by_severity[match.severity] = []
            by_severity[match.severity].append({
                'name': match.name,
                'description': match.description,
                'count': match.count,
                'file_source': match.file_source,
                'sample_matches': match.matches[:3]  # First 3 matches as samples
            })
        
        return {
            'security_score': security_score,
            'patterns_by_severity': by_severity,
            'total_matches': len(matches),
            'recommendations': self._get_recommendations(matches)
        }
    
    def _get_recommendations(self, matches: List[DOMPatternMatch]) -> List[str]:
        """Generate security recommendations based on matches"""
        recommendations = []
        
        high_severity_patterns = [m for m in matches if m.severity == 'high']
        if high_severity_patterns:
            recommendations.append("🚨 High severity patterns detected - immediate review recommended")
            
            for match in high_severity_patterns:
                if 'html_sink' in match.name:
                    recommendations.append("• Review innerHTML usage for XSS vulnerabilities")
                elif 'eval' in match.name:
                    recommendations.append("• Replace eval() with safer alternatives")
                elif 'document_write' in match.name:
                    recommendations.append("• Replace document.write with safer DOM manipulation")
        
        medium_severity_patterns = [m for m in matches if m.severity == 'medium']
        if medium_severity_patterns:
            recommendations.append("⚠️ Medium severity patterns found - security review suggested")
        
        if not recommendations:
            recommendations.append("✅ No high-risk patterns detected")
        
        return recommendations
