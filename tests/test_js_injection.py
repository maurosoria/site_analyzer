import pytest
from unittest.mock import AsyncMock, patch, mock_open
from ..lib.site_analyzer import load_scripts, load_payloads, get_url_content
from ..lib.extractors import (
    extract_emails_from_js, extract_urls_from_js, 
    extract_keywords_from_js, extract_endpoints,
    extract_js_paths, extract_sourcemap_matches
)

class TestJavaScriptInjection:
    """Test JavaScript injection functionality"""
    
    @pytest.mark.asyncio
    async def test_load_scripts(self):
        """Test loading JavaScript injection scripts"""
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['test.js', 'other.txt']), \
             patch('builtins.open', mock_open(read_data='console.log("test");')):
            
            scripts = await load_scripts('./js')
            assert 'test.js' in scripts
            assert scripts['test.js'] == 'console.log("test");'
            assert 'other.txt' not in scripts
    
    @pytest.mark.asyncio
    async def test_load_payloads(self):
        """Test loading JavaScript payload scripts"""
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['payload.js']), \
             patch('builtins.open', mock_open(read_data='window.hook = true;')):
            
            payloads = await load_payloads('./db/js_payloads')
            assert 'payload.js' in payloads
            assert payloads['payload.js'] == 'window.hook = true;'
    
    @pytest.mark.asyncio
    async def test_get_url_content(self, mock_browser, mock_page, scan_results):
        """Test URL content retrieval with JS injection"""
        mock_browser.new_page.return_value = mock_page
        mock_page.content.return_value = "<html>Test</html>"
        mock_page.evaluate.return_value = {"test": "data"}
        
        js_injects = {'test.js': 'console.log("test");'}
        
        with patch('..lib.site_analyzer.load_payloads', return_value={}):
            content, assets = await get_url_content(mock_browser, 'https://test.com', scan_results, js_injects)
            
            assert content == "<html>Test</html>"
            assert 'test.js' in assets
            mock_page.goto.assert_called_once()
            mock_page.evaluate.assert_called()

class TestDataExtractors:
    """Test data extraction from JavaScript results"""
    
    def test_extract_emails_from_js(self, sample_js_results):
        """Test email extraction from JS results"""
        emails = extract_emails_from_js(sample_js_results)
        assert 'test@example.com' in emails
    
    def test_extract_urls_from_js(self, sample_js_results):
        """Test URL extraction from JS results"""
        urls = extract_urls_from_js(sample_js_results)
        assert 'https://example.com/page1' in urls
        assert 'https://example.com/submit' in urls
        assert 'https://cdn.example.com/app.js' in urls
    
    def test_extract_keywords_from_js(self, sample_js_results):
        """Test keyword extraction from JS results"""
        keywords = extract_keywords_from_js(sample_js_results)
        assert 'api' in keywords or 'token' in keywords
    
    def test_extract_endpoints(self, sample_html_content):
        """Test endpoint extraction from content"""
        endpoints = extract_endpoints(sample_html_content)
        assert any('/api/' in endpoint for endpoint in endpoints)
    
    def test_extract_js_paths(self, sample_html_content):
        """Test JS path extraction from content"""
        js_paths = extract_js_paths(sample_html_content)
        assert '/js/app.js' in js_paths
    
    def test_extract_sourcemap_matches(self, sample_html_content):
        """Test sourcemap extraction from content"""
        sourcemaps = extract_sourcemap_matches(sample_html_content)
        assert 'app.js.map' in sourcemaps

class TestJSInjectionIntegration:
    """Integration tests for JS injection workflow"""
    
    @pytest.mark.asyncio
    async def test_full_js_injection_workflow(self, mock_browser, mock_page, scan_results):
        """Test complete JS injection workflow"""
        mock_browser.new_page.return_value = mock_page
        mock_page.content.return_value = "<html><script>var api_key='test';</script></html>"
        mock_page.evaluate.return_value = {"localStorage": [("email", "test@example.com")]}
        
        js_injects = {'extract.js': 'return document.body.innerHTML;'}
        
        with patch('..lib.site_analyzer.load_payloads', return_value={}):
            content, assets = await get_url_content(mock_browser, 'https://test.com', scan_results, js_injects)
            
            assert scan_results.content == content
            assert scan_results.js_execution_results == assets
            
            emails = extract_emails_from_js(assets)
            keywords = extract_keywords_from_js(assets)
            
            assert len(emails) > 0 or len(keywords) > 0
