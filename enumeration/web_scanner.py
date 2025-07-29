import asyncio
from typing import Dict, List, Set
from playwright.async_api import async_playwright
from .base import BaseEnumerator
from ..models.scan_result import EnumerationResult
from ..core.config import Config

class WebScannerEnumerator(BaseEnumerator):
    """Web scanner enumeration strategy - migrated from existing site_analyzer"""
    
    def get_name(self) -> str:
        return "web_scanner"
    
    def enumerate(self, target: str) -> EnumerationResult:
        """Perform web scanning enumeration"""
        data = {
            'emails': [],
            'urls': [],
            'endpoints': [],
            'keywords': [],
            'sourcemap_matches': [],
            'js_paths': []
        }
        errors = []
        
        try:
            result = asyncio.run(self._scan_website(target))
            data.update(result)
        except Exception as e:
            errors.append(f"Web scanning failed: {e}")
        
        return self._create_result(target, data, errors)
    
    async def _scan_website(self, url: str) -> Dict:
        """Perform web scanning using Playwright"""
        result = {
            'emails': set(),
            'urls': set(),
            'endpoints': set(),
            'keywords': set(),
            'sourcemap_matches': set(),
            'js_paths': set()
        }
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.config.headless)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=self.config.timeout)
                
                content = await page.content()
                
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, content)
                result['emails'].update(emails)
                
                url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'
                urls = re.findall(url_pattern, content)
                result['urls'].update(urls)
                
                endpoint_pattern = r'/api/[^\s<>"\']+|/v\d+/[^\s<>"\']+|/rest/[^\s<>"\']+|/graphql[^\s<>"\']*'
                endpoints = re.findall(endpoint_pattern, content)
                result['endpoints'].update(endpoints)
                
                js_elements = await page.query_selector_all('script[src]')
                for element in js_elements:
                    src = await element.get_attribute('src')
                    if src:
                        result['js_paths'].add(src)
                
                sourcemap_pattern = r'//# sourceMappingURL=([^\s]+)'
                sourcemaps = re.findall(sourcemap_pattern, content)
                result['sourcemap_matches'].update(sourcemaps)
                
                sensitive_keywords = ['password', 'token', 'api_key', 'secret', 'auth', 'login']
                for keyword in sensitive_keywords:
                    if keyword.lower() in content.lower():
                        result['keywords'].add(keyword)
                
            except Exception as e:
                raise Exception(f"Failed to scan {url}: {e}")
            finally:
                await browser.close()
        
        return {k: list(v) if isinstance(v, set) else v for k, v in result.items()}
