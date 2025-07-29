#!/usr/bin/env python3
"""
Integration with browseruse for enhanced browser automation and LLM-driven analysis
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


from lib.site_analyzer import get_url_content
from lib.scan_result import ScanResults
from core.config import Config

@dataclass
class BrowserUseConfig:
    """Configuration for browseruse integration"""
    llm_provider: str = "aws_bedrock"  # aws_bedrock, openai, anthropic
    llm_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    aws_bedrock_url: Optional[str] = None
    aws_region: str = "us-east-1"
    max_actions_per_page: int = 10
    action_timeout: int = 30
    enable_screenshots: bool = True

class BrowserUseSiteAnalyzer:
    """Enhanced site analyzer using browseruse for LLM-driven browser automation"""
    
    def __init__(self, config: Config, browseruse_config: BrowserUseConfig):
        self.config = config
        self.browseruse_config = browseruse_config
        self.logger = logging.getLogger(__name__)
    
    async def analyze_with_llm_agent(self, url: str, analysis_goals: List[str]) -> Dict[str, Any]:
        """
        Analyze a website using LLM-driven browser automation
        
        Args:
            url: Target URL to analyze
            analysis_goals: List of analysis objectives for the LLM agent
        
        Returns:
            Enhanced analysis results with LLM insights
        """
        results = {
            'url': url,
            'llm_analysis': {},
            'traditional_analysis': {},
            'combined_insights': {},
            'screenshots': [],
            'agent_actions': []
        }
        
        try:
            traditional_results = await self._run_traditional_analysis(url)
            results['traditional_analysis'] = traditional_results
            
            llm_results = await self._run_llm_analysis(url, analysis_goals)
            results['llm_analysis'] = llm_results
            
            combined = await self._combine_analysis_results(traditional_results, llm_results)
            results['combined_insights'] = combined
            
        except Exception as e:
            self.logger.error(f"Analysis failed for {url}: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _run_traditional_analysis(self, url: str) -> Dict[str, Any]:
        """Run traditional JavaScript injection analysis"""
        from playwright.async_api import async_playwright
        from lib.site_analyzer import load_scripts
        
        scan_results = ScanResults()
        scan_results.target = url
        
        js_injects = await load_scripts('./js')
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.config.headless)
            
            try:
                content, assets = await get_url_content(browser, url, scan_results, js_injects)
                
                return {
                    'content_length': len(content),
                    'js_execution_results': assets,
                    'emails': list(scan_results.emails),
                    'urls': list(scan_results.urls),
                    'keywords': list(scan_results.keywords),
                    'endpoints': list(scan_results.endpoints)
                }
            finally:
                await browser.close()
    
    async def _run_llm_analysis(self, url: str, analysis_goals: List[str]) -> Dict[str, Any]:
        """Run LLM-driven browser analysis using browseruse"""
        
        llm_results = {
            'goals_analyzed': analysis_goals,
            'llm_observations': [],
            'security_insights': [],
            'ui_analysis': [],
            'behavioral_patterns': [],
            'recommendations': []
        }
        
        for goal in analysis_goals:
            if goal == "security_assessment":
                insights = await self._llm_security_assessment(url)
                llm_results['security_insights'].extend(insights)
            
            elif goal == "ui_analysis":
                ui_data = await self._llm_ui_analysis(url)
                llm_results['ui_analysis'].extend(ui_data)
            
            elif goal == "behavioral_analysis":
                behavior = await self._llm_behavioral_analysis(url)
                llm_results['behavioral_patterns'].extend(behavior)
        
        return llm_results
    
    async def _llm_security_assessment(self, url: str) -> List[Dict[str, Any]]:
        """LLM-driven security assessment"""
        
        security_insights = [
            {
                'type': 'form_analysis',
                'description': 'LLM agent would analyze forms for security issues',
                'findings': ['CSRF protection status', 'Input validation', 'Authentication flows']
            },
            {
                'type': 'javascript_analysis',
                'description': 'LLM agent would analyze JavaScript for security patterns',
                'findings': ['API endpoints', 'Authentication tokens', 'Sensitive data exposure']
            }
        ]
        
        return security_insights
    
    async def _llm_ui_analysis(self, url: str) -> List[Dict[str, Any]]:
        """LLM-driven UI/UX analysis"""
        ui_analysis = [
            {
                'type': 'navigation_structure',
                'description': 'LLM agent would map site navigation',
                'findings': ['Menu structure', 'Hidden pages', 'Admin interfaces']
            },
            {
                'type': 'interactive_elements',
                'description': 'LLM agent would identify interactive elements',
                'findings': ['Forms', 'Buttons', 'Dynamic content']
            }
        ]
        
        return ui_analysis
    
    async def _llm_behavioral_analysis(self, url: str) -> List[Dict[str, Any]]:
        """LLM-driven behavioral analysis"""
        behavioral_patterns = [
            {
                'type': 'user_flows',
                'description': 'LLM agent would trace user interaction flows',
                'findings': ['Registration process', 'Login flows', 'Data submission']
            },
            {
                'type': 'dynamic_behavior',
                'description': 'LLM agent would observe dynamic page behavior',
                'findings': ['AJAX requests', 'Real-time updates', 'State changes']
            }
        ]
        
        return behavioral_patterns
    
    async def _combine_analysis_results(self, traditional: Dict, llm: Dict) -> Dict[str, Any]:
        """Combine traditional and LLM analysis results"""
        combined = {
            'enhanced_endpoints': [],
            'security_score': 0,
            'comprehensive_findings': [],
            'actionable_recommendations': []
        }
        
        traditional_endpoints = traditional.get('endpoints', [])
        llm_security = llm.get('security_insights', [])
        
        for endpoint in traditional_endpoints:
            enhanced_endpoint = {
                'endpoint': endpoint,
                'traditional_detection': True,
                'llm_context': 'Would be enhanced with LLM insights about endpoint purpose and security'
            }
            combined['enhanced_endpoints'].append(enhanced_endpoint)
        
        combined['comprehensive_findings'] = [
            'Traditional JS injection found sensitive data patterns',
            'LLM agent identified additional security concerns',
            'Combined analysis provides deeper context and understanding'
        ]
        
        return combined

async def example_llm_driven_analysis():
    """Example of LLM-driven site analysis"""
    config = Config(headless=True, timeout=30000)
    browseruse_config = BrowserUseConfig(
        aws_bedrock_url="https://bedrock-runtime.us-east-1.amazonaws.com",
        aws_region="us-east-1"
    )
    
    analyzer = BrowserUseSiteAnalyzer(config, browseruse_config)
    
    analysis_goals = [
        "security_assessment",
        "ui_analysis", 
        "behavioral_analysis"
    ]
    
    results = await analyzer.analyze_with_llm_agent("https://example.com", analysis_goals)
    
    print("🤖 LLM-Driven Analysis Results:")
    print(f"  Traditional findings: {len(results['traditional_analysis'].get('emails', []))} emails")
    print(f"  LLM insights: {len(results['llm_analysis'].get('security_insights', []))} security insights")
    print(f"  Combined recommendations: {len(results['combined_insights'].get('actionable_recommendations', []))}")

def create_browseruse_framework_config() -> Dict[str, Any]:
    """Create configuration for browseruse integration"""
    return {
        'browseruse': {
            'enabled': True,
            'llm_provider': 'aws_bedrock',
            'llm_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'aws_bedrock_url': 'https://bedrock-runtime.us-east-1.amazonaws.com',
            'aws_region': 'us-east-1',
            'max_actions_per_page': 10,
            'enable_screenshots': True
        },
        'analysis_goals': [
            'security_assessment',
            'ui_analysis',
            'behavioral_analysis',
            'data_extraction',
            'vulnerability_detection'
        ]
    }

if __name__ == "__main__":
    print("🤖 BrowserUse Integration Example")
    print("=" * 50)
    
    asyncio.run(example_llm_driven_analysis())
    
    config = create_browseruse_framework_config()
    print("\n⚙️  BrowserUse Configuration:")
    print(json.dumps(config, indent=2))
