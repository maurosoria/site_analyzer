import asyncio
from typing import Dict, List, Set
from playwright.async_api import async_playwright
from .base import BaseEnumerator
from ..models.scan_result import EnumerationResult
from ..core.config import Config
from ..lib.site_analyzer import load_scripts, get_url_content
from ..lib.extractors import (
    extract_emails_from_js, extract_urls_from_js, 
    extract_keywords_from_js, extract_endpoints,
    extract_js_paths, extract_sourcemap_matches
)
from ..lib.scan_result import ScanResults
from ..plugins.factory import FrameworkDetectionEngine
from ..analyzers.dom_patterns import DOMPatternAnalyzer

class WebScannerEnumerator(BaseEnumerator):
    """Web scanner enumeration strategy with JavaScript injection"""
    
    def get_name(self) -> str:
        return "web_scanner"
    
    def enumerate(self, target: str) -> EnumerationResult:
        """Perform web scanning enumeration with JS injection"""
        data = {
            'emails': [],
            'urls': [],
            'endpoints': [],
            'keywords': [],
            'sourcemap_matches': [],
            'js_paths': [],
            'storage_data': {},
            'frameworks': [],
            'dom_patterns': [],
            'security_score': {}
        }
        errors = []
        
        try:
            result = asyncio.run(self._scan_website_with_injection(target))
            data.update(result)
        except Exception as e:
            errors.append(f"Web scanning with JS injection failed: {e}")
        
        return self._create_result(target, data, errors)
    
    async def _scan_website_with_injection(self, url: str) -> Dict:
        """Perform web scanning using Playwright with JavaScript injection"""
        result = {
            'emails': set(),
            'urls': set(),
            'endpoints': set(),
            'keywords': set(),
            'sourcemap_matches': set(),
            'js_paths': set(),
            'storage_data': {},
            'frameworks': [],
            'dom_patterns': [],
            'security_score': {}
        }
        
        scan_results = ScanResults()
        scan_results.target = url
        
        js_injects = await load_scripts('./js')
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.config.headless)
            
            try:
                content, assets = await get_url_content(browser, url, scan_results, js_injects)
                
                result['emails'].update(extract_emails_from_js(assets))
                result['urls'].update(extract_urls_from_js(assets))
                result['keywords'].update(extract_keywords_from_js(assets, './db/keywords.txt'))
                result['endpoints'].update(extract_endpoints(content))
                result['sourcemap_matches'].update(extract_sourcemap_matches(content))
                result['js_paths'].update(extract_js_paths(content))
                
                result['storage_data'] = assets
                
                framework_engine = FrameworkDetectionEngine()
                frameworks = framework_engine.detect_frameworks(content, assets, url)
                result['frameworks'] = [
                    {
                        'name': f.name,
                        'version': f.version,
                        'confidence': f.confidence,
                        'indicators': f.indicators,
                        'files': f.files
                    }
                    for f in frameworks
                ]
                
                dom_analyzer = DOMPatternAnalyzer()
                dom_matches = dom_analyzer.analyze_content(content, url)
                dom_matches.extend(dom_analyzer.analyze_js_results(assets))
                
                result['dom_patterns'] = [
                    {
                        'name': m.name,
                        'description': m.description,
                        'severity': m.severity,
                        'count': m.count,
                        'file_source': m.file_source
                    }
                    for m in dom_matches
                ]
                
                result['security_score'] = dom_analyzer.get_security_score(dom_matches)
                
            except Exception as e:
                raise Exception(f"Failed to scan {url} with JS injection: {e}")
            finally:
                await browser.close()
        
        return {k: list(v) if isinstance(v, set) else v for k, v in result.items()}
