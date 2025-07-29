import pytest
from unittest.mock import AsyncMock, patch
from enumeration.web_scanner import WebScannerEnumerator
from enumeration.security_trails import SecurityTrailsEnumerator
from enumeration.dns_enumeration import DNSEnumerator

class TestWebScannerEnumerator:
    """Test WebScannerEnumerator with JS injection"""
    
    def test_get_name(self, config):
        """Test enumerator name"""
        enumerator = WebScannerEnumerator(config)
        assert enumerator.get_name() == "web_scanner"
    
    @patch('..enumeration.web_scanner.async_playwright')
    @patch('..enumeration.web_scanner.load_scripts')
    @patch('..enumeration.web_scanner.get_url_content')
    def test_enumerate_success(self, mock_get_url_content, mock_load_scripts, mock_playwright, config):
        """Test successful enumeration with JS injection"""
        mock_load_scripts.return_value = {'test.js': 'console.log("test");'}
        mock_get_url_content.return_value = (
            "<html>Test content</html>",
            {
                'test.js': {'emails': ['test@example.com']},
                'cookies': [{'name': 'session', 'value': 'abc123'}]
            }
        )
        
        mock_browser = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        
        enumerator = WebScannerEnumerator(config)
        result = enumerator.enumerate('https://test.com')
        
        assert result.success
        assert result.target == 'https://test.com'
        assert 'storage_data' in result.data
    
    def test_enumerate_failure(self, config):
        """Test enumeration failure handling"""
        with patch('..enumeration.web_scanner.asyncio.run', side_effect=Exception("Test error")):
            enumerator = WebScannerEnumerator(config)
            result = enumerator.enumerate('https://test.com')
            
            assert not result.success
            assert len(result.errors) > 0
            assert "Web scanning with JS injection failed" in result.errors[0]

class TestSecurityTrailsEnumerator:
    """Test SecurityTrails enumeration"""
    
    def test_get_name(self, config):
        """Test enumerator name"""
        enumerator = SecurityTrailsEnumerator(config)
        assert enumerator.get_name() == "security_trails"
    
    @patch('requests.get')
    def test_enumerate_success(self, mock_get, config):
        """Test successful SecurityTrails enumeration"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'subdomains': ['api', 'www', 'mail'],
            'records': [{'type': 'A', 'values': ['1.2.3.4']}]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        enumerator = SecurityTrailsEnumerator(config)
        result = enumerator.enumerate('example.com')
        
        assert result.success
        assert result.target == 'example.com'
        assert 'subdomains' in result.data
    
    def test_enumerate_no_api_key(self, config):
        """Test enumeration without API key"""
        config.security_trails_api_key = None
        enumerator = SecurityTrailsEnumerator(config)
        result = enumerator.enumerate('example.com')
        
        assert not result.success
        assert "SecurityTrails API key not configured" in result.errors[0]

class TestDNSEnumerator:
    """Test DNS enumeration"""
    
    def test_get_name(self, config):
        """Test enumerator name"""
        enumerator = DNSEnumerator(config)
        assert enumerator.get_name() == "dns_enumeration"
    
    @patch('dns.resolver.resolve')
    def test_enumerate_success(self, mock_resolve, config):
        """Test successful DNS enumeration"""
        mock_answer = AsyncMock()
        mock_answer.__iter__.return_value = [AsyncMock(address='1.2.3.4')]
        mock_resolve.return_value = mock_answer
        
        enumerator = DNSEnumerator(config)
        result = enumerator.enumerate('example.com')
        
        assert result.success
        assert result.target == 'example.com'
        assert 'a_records' in result.data
    
    def test_enumerate_dns_failure(self, config):
        """Test DNS enumeration failure"""
        with patch('dns.resolver.resolve', side_effect=Exception("DNS error")):
            enumerator = DNSEnumerator(config)
            result = enumerator.enumerate('invalid.domain')
            
            assert not result.success
            assert len(result.errors) > 0

class TestEnumeratorIntegration:
    """Integration tests for enumerators"""
    
    def test_multiple_enumerators(self, config):
        """Test running multiple enumerators"""
        enumerators = [
            WebScannerEnumerator(config),
            DNSEnumerator(config)
        ]
        
        target = 'example.com'
        results = []
        
        for enumerator in enumerators:
            with patch.object(enumerator, 'enumerate') as mock_enumerate:
                mock_enumerate.return_value = enumerator._create_result(target, {}, [])
                result = enumerator.enumerate(target)
                results.append(result)
        
        assert len(results) == 2
        assert all(result.target == target for result in results)
