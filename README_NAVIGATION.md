# Prompt-Based Navigation Module

## Overview

The navigation module provides intelligent website navigation capabilities using natural language prompts, automatic screenshot capture, and captcha solving integration.

## Features

### 🎯 **Prompt-Based Navigation**
- Natural language prompts for website interaction
- Automatic form detection and filling
- Smart element selection and clicking
- Support for registration, login, and search workflows

### 📸 **Screenshot Management**
- Automatic screenshot capture at each step
- Organized storage by domain and date
- Session-based organization with unique IDs
- JSON reports with step details

### 🤖 **Captcha Solving**
- Integration with Capsolver API
- Support for reCAPTCHA v2/v3, hCaptcha, and FunCaptcha
- Automatic detection and solving
- Fallback handling for unsupported captchas

## Quick Start

### Basic Usage

```python
from navigation.prompt_navigator import PromptNavigator
from core.config import Config

# Configure
config = Config(headless=False, timeout=30000)
navigator = PromptNavigator(config, "your-capsolver-api-key")

# Navigate with prompt
result = await navigator.navigate_with_prompt(
    url="https://example.com",
    prompt="register in this website with some predefined credentials",
    credentials={
        "email": "test@example.com",
        "username": "testuser123",
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
)

print(f"Navigation completed: {result.successful_steps}/{result.total_steps} steps")
```

### Registration Example

```python
credentials = {
    "email": "user@example.com",
    "username": "myusername",
    "password": "MySecurePassword123!",
    "confirm_password": "MySecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
}

result = await navigator.navigate_with_prompt(
    url="https://site.com/register",
    prompt="register in this website with predefined credentials",
    credentials=credentials
)
```

### Login Example

```python
credentials = {
    "email": "user@example.com",
    "password": "MyPassword123!"
}

result = await navigator.navigate_with_prompt(
    url="https://site.com/login",
    prompt="login to this website with credentials",
    credentials=credentials
)
```

### Search Example

```python
result = await navigator.navigate_with_prompt(
    url="https://site.com",
    prompt="search for python tutorials on this website"
)
```

## Screenshot Storage

Screenshots are automatically organized in the following structure:

```
navigation_screenshots/
├── example.com/
│   ├── 2025-01-29/
│   │   ├── 20250129_143022/
│   │   │   ├── step_001_navigate_to_url.png
│   │   │   ├── step_002_page_loaded.png
│   │   │   ├── step_003_click_register.png
│   │   │   ├── step_004_fill_email.png
│   │   │   ├── step_005_solve_captcha.png
│   │   │   └── navigation_report.json
│   │   └── 20250129_150315/
│   └── 2025-01-30/
└── another-site.com/
```

### Managing Screenshots

```python
from navigation.screenshot_storage import ScreenshotStorage

storage = ScreenshotStorage()

# List all sessions
sessions = storage.list_sessions()

# List sessions for specific domain
sessions = storage.list_sessions(domain="example.com")

# Get screenshots for a session
screenshots = storage.get_session_screenshots("example.com", "20250129_143022")

# Cleanup old sessions (older than 30 days)
storage.cleanup_old_sessions(days_to_keep=30)
```

## Captcha Integration

### Supported Captcha Types

- **reCAPTCHA v2**: Standard checkbox captcha
- **reCAPTCHA v3**: Invisible captcha with score
- **hCaptcha**: Alternative to reCAPTCHA
- **FunCaptcha**: Arkose Labs captcha

### Capsolver Setup

1. Sign up at [capsolver.com](https://capsolver.com)
2. Get your API key from the dashboard
3. Add credits to your account
4. Use the API key in your navigator configuration

```python
# Check balance
from navigation.captcha_solver import CaptchaSolver

solver = CaptchaSolver("your-api-key")
balance = await solver.get_balance()
print(f"Account balance: ${balance}")
```

## Configuration

### Navigator Configuration

```python
from core.config import Config

config = Config(
    headless=False,        # Set to True for headless mode
    timeout=30000,         # Page timeout in milliseconds
    # ... other config options
)
```

### Environment Variables

```bash
# Optional: Set capsolver API key as environment variable
export CAPSOLVER_API_KEY="your-api-key-here"
```

## Advanced Usage

### Custom Prompt Handling

The navigator supports various prompt patterns:

- **Registration**: "register", "sign up", "create account"
- **Login**: "login", "sign in", "authenticate"
- **Search**: "search", "find", "look for"
- **Custom**: Any other prompt will use basic heuristics

### Error Handling

```python
result = await navigator.navigate_with_prompt(url, prompt, credentials)

# Check for errors
failed_steps = [step for step in result.steps if not step.success]
if failed_steps:
    print("Failed steps:")
    for step in failed_steps:
        print(f"  {step.action}: {step.error_message}")
```

### Session Reports

Each navigation session generates a detailed JSON report:

```json
{
  "domain": "example.com",
  "prompt": "register in this website with predefined credentials",
  "total_steps": 8,
  "successful_steps": 7,
  "session_id": "20250129_143022",
  "start_time": "2025-01-29T14:30:22.123456",
  "end_time": "2025-01-29T14:31:45.789012",
  "steps": [
    {
      "step_number": 1,
      "action": "navigate_to_url",
      "description": "Navigating to https://example.com",
      "screenshot_path": "/path/to/step_001_navigate_to_url.png",
      "success": true,
      "timestamp": "2025-01-29T14:30:22.123456"
    }
  ]
}
```

## Integration with Site Analyzer

The navigation module integrates seamlessly with the main site analyzer framework:

```python
from example_usage import FrameworkConfig, SiteAnalyzerFramework
from navigation.prompt_navigator import PromptNavigator

# Combine analysis with navigation
config = FrameworkConfig(
    domains=["example.com"],
    capsolver_api_key="your-api-key"
)

framework = SiteAnalyzerFramework(config)

# First analyze the site
analysis_results = await framework.analyze_domains()

# Then navigate based on findings
navigator = PromptNavigator(framework.core_config, config.capsolver_api_key)
navigation_result = await navigator.navigate_with_prompt(
    url="https://example.com/register",
    prompt="register with test credentials"
)
```

## Troubleshooting

### Common Issues

1. **Captcha not detected**: Ensure the site uses supported captcha types
2. **Form fields not found**: Check if the site uses non-standard field names
3. **Navigation timeout**: Increase timeout in config for slow sites
4. **Screenshot storage errors**: Check directory permissions

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Capsolver Issues

- Check API key validity
- Verify account balance
- Ensure captcha type is supported
- Check rate limits

## Examples

See `navigation_example.py` for complete working examples of:
- Website registration with captcha solving
- User login automation
- Search functionality
- Session management
- Error handling
