# Google Gemini 2.5 Flash-Lite Integration

This guide explains how to use Google Gemini 2.5 Flash-Lite with the site_analyzer framework for intelligent website analysis and navigation.

## Why Gemini 2.5 Flash-Lite?

- **Cost-effective**: Significantly cheaper than other LLM providers
- **Fast**: Optimized for quick responses
- **Powerful**: Excellent for website analysis, security scanning, and navigation
- **Easy to use**: Simple API integration

## Setup Instructions

### 1. Get Your API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key (starts with `AIza...`)

### 2. Set Environment Variable

```bash
export GEMINI_API_KEY="AIzaSy..."
```

Or add to your `.env` file:
```
GEMINI_API_KEY=AIzaSy...
```

### 3. Install Dependencies

```bash
pip install google-generativeai>=0.3.0
```

## Usage Examples

### Basic Website Analysis

```python
import asyncio
import os
from example_usage import SiteAnalyzerFramework, FrameworkConfig

async def analyze_website():
    config = FrameworkConfig(
        domains=["example.com"],
        num_playwright_instances=2,
        
        # Gemini configuration
        llm_provider="gemini",
        gemini_api_key=os.getenv('GEMINI_API_KEY'),
        llm_model="gemini-2.0-flash-exp",
        
        # Storage
        storage_type="file",
        output_dir="./analysis_results"
    )
    
    framework = SiteAnalyzerFramework(config)
    results = await framework.analyze_domains()
    
    print(f"Analysis complete! Results saved to {config.output_dir}")
    return results

# Run the analysis
results = asyncio.run(analyze_website())
```

### Intelligent Navigation with Prompts

```python
import asyncio
import os
from example_usage import SiteAnalyzerFramework, FrameworkConfig

async def navigate_with_ai():
    config = FrameworkConfig(
        domains=["example.com"],
        
        # Gemini configuration
        llm_provider="gemini",
        gemini_api_key=os.getenv('GEMINI_API_KEY'),
        llm_model="gemini-2.0-flash-exp",
        
        # Captcha solving
        capsolver_api_key=os.getenv('CAPSOLVER_API_KEY')
    )
    
    framework = SiteAnalyzerFramework(config)
    
    # AI-powered navigation
    result = await framework.navigate_with_prompt(
        url="https://example.com/register",
        prompt="register in this website with predefined credentials",
        credentials={
            "email": "test@example.com",
            "password": "SecurePass123",
            "username": "testuser"
        }
    )
    
    print(f"Navigation completed: {result.success}")
    print(f"Screenshots saved: {len(result.screenshots)}")
    return result

# Run the navigation
result = asyncio.run(navigate_with_ai())
```

## Configuration Options

### Framework Configuration

```python
config = FrameworkConfig(
    # Target domains
    domains=["example.com", "test.com"],
    num_playwright_instances=3,
    
    # LLM Provider
    llm_provider="gemini",                    # Use Gemini
    gemini_api_key="AIzaSy...",              # Your API key
    llm_model="gemini-2.0-flash-exp",        # Model version
    
    # Storage
    storage_type="file",                      # or "mongodb", "sql"
    output_dir="./results",
    
    # Optional integrations
    security_trails_api_key="your-key",       # For DNS enumeration
    capsolver_api_key="your-key",            # For captcha solving
    
    # Browser settings
    headless=True,
    timeout=30000
)
```

### Environment Variables

```bash
# Required
export GEMINI_API_KEY="AIzaSy..."

# Optional
export SECURITY_TRAILS_API_KEY="your-key"
export CAPSOLVER_API_KEY="your-key"
export STORAGE_TYPE="file"
export OUTPUT_DIR="./results"
```

## Features

### 1. Website Content Analysis

Gemini can analyze website content to detect:

- **Frameworks**: React, Angular, Vue, etc.
- **Libraries**: jQuery, Bootstrap, etc.
- **Build Tools**: Webpack, Vite, etc.
- **Security Issues**: Exposed secrets, vulnerabilities
- **API Endpoints**: REST APIs, GraphQL endpoints

### 2. Security Analysis

- Detect hardcoded API keys and secrets
- Find potential XSS vulnerabilities
- Identify insecure configurations
- Analyze authentication mechanisms
- Check for common security misconfigurations

### 3. Intelligent Navigation

- Generate automation steps from natural language prompts
- Handle complex user flows (registration, login, etc.)
- Adapt to different website structures
- Solve captchas automatically (with Capsolver integration)

### 4. Framework Detection

- Identify JavaScript frameworks and versions
- Detect build tools and bundlers
- Find lazy-loaded modules and routes
- Analyze SPA (Single Page Application) structures

## Testing

### Run Integration Tests

```bash
# Set your API key
export GEMINI_API_KEY="AIzaSy..."

# Run comprehensive tests
python test_gemini_real.py
```

### Run Captcha Tests

```bash
# Set API keys
export GEMINI_API_KEY="AIzaSy..."
export CAPSOLVER_API_KEY="CAP-..."

# Test captcha solving with Gemini navigation
python test_captcha_comprehensive.py
```

## Cost Optimization

Gemini 2.5 Flash-Lite is designed to be cost-effective:

- **Input tokens**: ~$0.075 per 1M tokens
- **Output tokens**: ~$0.30 per 1M tokens
- **Typical analysis**: $0.01-0.05 per website
- **Navigation session**: $0.02-0.10 per session

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: Invalid API key
   ```
   - Verify your API key is correct
   - Check that it starts with `AIza`
   - Ensure the key has proper permissions

2. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   ```
   - Reduce the number of concurrent requests
   - Add delays between requests
   - Check your quota limits

3. **Model Not Found**
   ```
   Error: Model not found
   ```
   - Use `gemini-2.0-flash-exp` for latest features
   - Check available models in Google AI Studio

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your framework code here
```

## Best Practices

1. **Use Environment Variables**: Never hardcode API keys
2. **Handle Errors**: Implement proper error handling for API calls
3. **Rate Limiting**: Respect API rate limits
4. **Content Size**: Limit content size for analysis (4KB recommended)
5. **Caching**: Cache results to avoid redundant API calls

## Migration from AWS Bedrock

If you're migrating from AWS Bedrock:

```python
# Old configuration
config = FrameworkConfig(
    llm_provider="bedrock",
    aws_bedrock_url="your-bedrock-url",
    aws_region="us-east-1"
)

# New configuration
config = FrameworkConfig(
    llm_provider="gemini",
    gemini_api_key=os.getenv('GEMINI_API_KEY'),
    llm_model="gemini-2.0-flash-exp"
)
```

## Support

For issues with Gemini integration:

1. Check the [Google AI documentation](https://ai.google.dev/)
2. Review the test files: `test_gemini_real.py`
3. Run the example: `gemini_example.py`
4. Check the logs for detailed error messages
