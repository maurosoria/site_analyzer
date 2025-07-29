# Site Analyzer Framework - Usage Guide

## Simple and Elegant Usage Examples

### 1. Basic Single Domain Analysis

```python
from example_usage import FrameworkConfig, SiteAnalyzerFramework

# Simple configuration
config = FrameworkConfig(
    domains=["example.com"],
    num_playwright_instances=2,
    storage_type="file",
    output_dir="./results"
)

# Run analysis
framework = SiteAnalyzerFramework(config)
results = await framework.analyze_domains()
```

### 2. Multiple Domains with Load Balancing

```python
# Analyze multiple domains with load balancing
config = FrameworkConfig(
    domains=["site1.com", "site2.com", "site3.com"],
    num_playwright_instances=5,  # 5 concurrent browser instances
    storage_type="file",
    output_dir="./multi_results"
)

framework = SiteAnalyzerFramework(config)
results = await framework.analyze_domains()

# Get summary
summary = framework.get_results_summary()
print(f"Analyzed {summary['total_domains']} domains")
print(f"Found {summary['total_emails']} emails total")
```

### 3. Advanced Configuration with API Tokens

```python
config = FrameworkConfig(
    domains=["target1.com", "target2.com"],
    num_playwright_instances=3,
    
    # Storage configuration
    storage_type="mongodb",  # or "file", "sql"
    
    # API tokens
    security_trails_api_key="your-securitytrails-key",
    
    # LLM integration (Gemini recommended for cost-effectiveness)
    llm_provider="gemini",  # or "bedrock"
    gemini_api_key=os.getenv('GEMINI_API_KEY'),  # Google AI API key
    llm_model="gemini-2.0-flash-exp",
    
    # Alternative: AWS Bedrock LLM integration
    # aws_bedrock_url="https://bedrock-runtime.us-east-1.amazonaws.com",
    # aws_region="us-east-1",
    
    # Enumeration strategies
    enumerators=["web_scanner", "dns_enumeration", "security_trails"]
)
```

### 4. BrowserUse + LLM Integration

```python
from browseruse_integration import BrowserUseSiteAnalyzer, BrowserUseConfig

# Configure LLM-driven analysis
browseruse_config = BrowserUseConfig(
    llm_provider="aws_bedrock",
    aws_bedrock_url="https://bedrock-runtime.us-east-1.amazonaws.com",
    aws_region="us-east-1",
    max_actions_per_page=10
)

analyzer = BrowserUseSiteAnalyzer(config, browseruse_config)

# Define analysis goals for the LLM agent
analysis_goals = [
    "security_assessment",
    "ui_analysis", 
    "behavioral_analysis"
]

# Run LLM-driven analysis
results = await analyzer.analyze_with_llm_agent("https://target.com", analysis_goals)
```

## Key Features

### 🎭 Multiple Playwright Instances
- Automatic load balancing across browser instances
- Configurable concurrency limits
- Efficient resource management

### 💾 Flexible Storage Options
- **File Storage**: JSON files in specified directory
- **MongoDB**: NoSQL document storage
- **SQL**: Relational database storage (SQLite, PostgreSQL, MySQL)

### 🤖 LLM Integration
- **Google Gemini 2.5 Flash-Lite**: Cost-effective, fast LLM analysis (Recommended)
- **AWS Bedrock**: Enterprise-grade LLM integration
- **BrowserUse**: LLM-driven browser automation
- Combines traditional scanning with AI insights

### ⚖️ Load Balancing
- Semaphore-based concurrency control
- Automatic distribution of work across instances
- Configurable instance limits

## Running the Examples

### Quick Start
```bash
# Install dependencies
pip install -r requirements_refactored.txt

# Install Playwright browsers
playwright install

# Run simple example
python example_usage.py
```

### With Environment Variables
```bash
# Set API keys
export SECURITY_TRAILS_API_KEY="your-key"
export GEMINI_API_KEY="your-gemini-key"  # Get from https://aistudio.google.com/app/apikey
export AWS_BEDROCK_URL="https://bedrock-runtime.us-east-1.amazonaws.com"  # Optional

# Run advanced example
python -c "from example_usage import advanced_example_with_llm; advanced_example_with_llm()"
```

### Load Balanced Analysis
```bash
# Analyze 20 domains with 8 concurrent instances
python -c "from example_usage import load_balanced_example; load_balanced_example()"
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `domains` | List of domains to analyze | Required |
| `num_playwright_instances` | Concurrent browser instances | 3 |
| `storage_type` | Storage backend (file/mongodb/sql) | "file" |
| `output_dir` | Output directory for results | "./results" |
| `security_trails_api_key` | SecurityTrails API key | None |
| `llm_provider` | LLM provider (gemini/bedrock) | "gemini" |
| `gemini_api_key` | Google Gemini API key | None |
| `llm_model` | Gemini model version | "gemini-2.0-flash-exp" |
| `aws_bedrock_url` | AWS Bedrock endpoint URL | None |
| `enumerators` | List of enumeration strategies | ["web_scanner", "dns_enumeration"] |

## Framework Architecture

```
SiteAnalyzerFramework
├── Load Balancing (Semaphore-based)
├── Multiple Playwright Instances
├── JavaScript Injection Engine
├── Data Extraction & Analysis
├── LLM Integration (Optional)
└── Flexible Storage Backends
```

This framework provides a simple, elegant interface while maintaining powerful capabilities for comprehensive site analysis with modern browser automation and AI integration.

## Docker Support

For easy deployment and consistent environments, the framework supports Docker:

```bash
# Pull the Docker image
docker pull maurosoria/site_analyzer:latest

# Run with CLI interface
docker run -e GEMINI_API_KEY=your-key -e SECURITY_TRAILS_API_KEY=your-key -e CAPSOLVER_API_KEY=your-key \
  maurosoria/site_analyzer:latest --target example.com
```

For a complete setup with all services (REST API, gRPC, CLI):

```bash
# Clone the repository
git clone https://github.com/maurosoria/site_analyzer.git
cd site_analyzer

# Configure environment variables
cp .env.example .env.rest
cp .env.example .env.grpc
cp .env.example .env.cli

# Edit the .env files to add your API keys
# Then start the services
docker-compose up -d
```

See [README_DOCKER.md](README_DOCKER.md) for detailed Docker setup instructions.

## Additional Documentation

- [API Documentation](docs/API.md): Comprehensive REST API documentation
- [gRPC Documentation](docs/GRPC.md): Detailed gRPC service documentation and client examples
- [Gemini Integration](README_GEMINI.md): Guide for using Google Gemini 2.5 Flash-Lite
- [Navigation Guide](README_NAVIGATION.md): Instructions for prompt-based navigation and captcha solving
