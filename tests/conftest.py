import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from playwright.async_api import Browser, Page
from ..core.config import Config
from ..lib.scan_result import ScanResults

@pytest.fixture
def config():
    """Provide test configuration"""
    return Config(
        headless=True,
        timeout=10000,
        debug=False
    )

@pytest.fixture
def scan_results():
    """Provide empty scan results for testing"""
    return ScanResults()

@pytest.fixture
def mock_browser():
    """Mock Playwright browser for testing"""
    browser = AsyncMock(spec=Browser)
    return browser

@pytest.fixture
def mock_page():
    """Mock Playwright page for testing"""
    page = AsyncMock(spec=Page)
    page.content.return_value = "<html><body>Test content</body></html>"
    page.evaluate.return_value = {"test": "data"}
    return page

@pytest.fixture
def sample_js_results():
    """Sample JavaScript execution results for testing extractors"""
    return {
        'extract_urls.js': {
            'links': [{'href': 'https://example.com/page1'}],
            'forms': [{'action': 'https://example.com/submit'}]
        },
        'hook_storage.js': {
            'localStorage': [('user_email', 'test@example.com')],
            'sessionStorage': [('api_token', 'abc123')]
        },
        'script_sources': ['https://cdn.example.com/app.js'],
        'external_resources': ['https://api.example.com/data'],
        'cookies': [{'name': 'session', 'value': 'xyz789', 'domain': 'example.com'}],
        'window_properties': ['apiConfig', 'userData']
    }

@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing content extractors"""
    return """
    <html>
    <head>
        <script src="/js/app.js"></script>
        <script>
            // sourceMappingURL=app.js.map
        </script>
    </head>
    <body>
        <a href="mailto:contact@example.com">Contact</a>
        <form action="/api/submit">
            <input type="email" value="user@test.com">
        </form>
        <script>
            fetch('/api/users');
            const config = {api_key: 'secret123'};
        </script>
    </body>
    </html>
    """

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_mock_context():
    """Async context manager mock for testing"""
    context = AsyncMock()
    context.__aenter__ = AsyncMock(return_value=context)
    context.__aexit__ = AsyncMock(return_value=None)
    return context
