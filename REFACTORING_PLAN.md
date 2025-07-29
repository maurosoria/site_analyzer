# Site Analyzer Refactoring Plan

## Current Analysis

### Mohiverse Functions Analysis
The notebook contains several key enumeration strategies:

1. **SecurityTrails API Wrapper** - Comprehensive domain intelligence
   - Domain information gathering (`get_domain`)
   - Subdomain enumeration (`get_subdomain`) 
   - WHOIS data collection (`get_whois`, `get_history_whois`)
   - Historical DNS records (`get_history_dns`)
   - IP neighborhood analysis (`ip_explorer`)
   - Advanced domain filtering (`domain_searcher`)
   - Virtual host discovery (`get_vhosts`, `get_domains`)

2. **DNS Enumeration Functions**
   - Batch subdomain collection (`get_securitytrails_subdomains`)
   - Historical DNS analysis (`get_securitytrails_history_dns`)
   - DNS reconnaissance via DNSDumpster (`get_dns_dumpster`)

3. **Service Detection & Utilities**
   - String filtering by prefixes (`filter_strings`)
   - Automated service scanning (phpMyAdmin detection)
   - Domain filtering and validation

### Problems Solved
- **Reconnaissance**: Comprehensive domain and subdomain discovery
- **Intelligence Gathering**: Historical data analysis for security assessment
- **Infrastructure Mapping**: Virtual host and IP neighborhood discovery
- **Service Detection**: Automated scanning for specific web services
- **Data Correlation**: Cross-referencing multiple data sources

## Proposed Class Structure

Based on dirsearch patterns and Mohiverse functionality:

```
site_analyzer/
├── core/
│   ├── __init__.py
│   ├── analyzer.py          # Main SiteAnalyzer orchestrator
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Custom exceptions
│   └── decorators.py        # Utility decorators
├── interfaces/
│   ├── __init__.py
│   ├── cli.py               # Command line interface
│   ├── grpc_server.py       # gRPC server implementation
│   ├── rest_api.py          # Flask REST API
│   └── base.py              # Base interface class
├── enumeration/
│   ├── __init__.py
│   ├── base.py              # Base enumerator class
│   ├── security_trails.py   # SecurityTrails API integration
│   ├── dns_enumeration.py   # DNS enumeration strategies
│   ├── web_scanner.py       # Playwright-based web scanning
│   ├── service_detection.py # Service detection modules
│   └── factory.py           # Enumerator factory
├── storage/
│   ├── __init__.py
│   ├── base.py              # Base storage interface
│   ├── file_storage.py      # File-based storage
│   ├── mongodb_storage.py   # MongoDB storage
│   ├── sql_storage.py       # SQL database storage
│   └── factory.py           # Storage factory
├── models/
│   ├── __init__.py
│   ├── scan_result.py       # Scan result models
│   ├── domain_info.py       # Domain information models
│   └── enums.py             # Enumeration types
├── utils/
│   ├── __init__.py
│   ├── logging_utils.py     # Logging utilities
│   ├── validators.py        # Input validators
│   ├── filters.py           # Data filtering utilities
│   └── correlation.py       # Data correlation utilities
└── proto/                   # gRPC protocol definitions
    ├── __init__.py
    ├── site_analyzer.proto
    └── generated/           # Generated gRPC code
```

## Key Classes Design

### 1. Core Classes

#### SiteAnalyzer (core/analyzer.py)
```python
class SiteAnalyzer:
    """Main orchestrator for site analysis operations"""
    def __init__(self, config: Config):
        self.config = config
        self.enumerators = []
        self.storage_manager = StorageFactory.create(config.storage_type)
        
    def analyze(self, target: str) -> ScanResult:
        """Main analysis entry point"""
        
    def add_enumerator(self, enumerator: BaseEnumerator):
        """Add enumeration strategy"""
        
    def correlate_results(self, results: List[EnumerationResult]) -> ScanResult:
        """Correlate and merge results from different enumerators"""
```

### 2. Enumeration Classes

#### BaseEnumerator (enumeration/base.py)
```python
from abc import ABC, abstractmethod

class BaseEnumerator(ABC):
    """Base class for all enumeration strategies"""
    
    @abstractmethod
    def enumerate(self, target: str) -> EnumerationResult:
        """Perform enumeration on target"""
        
    @abstractmethod
    def get_name(self) -> str:
        """Get enumerator name"""
```

#### SecurityTrailsEnumerator (enumeration/security_trails.py)
```python
class SecurityTrailsEnumerator(BaseEnumerator):
    """SecurityTrails API integration"""
    
    def __init__(self, api_key: str):
        self.api = SecurityTrails(api_key)
        
    def enumerate(self, target: str) -> EnumerationResult:
        """Perform SecurityTrails enumeration"""
        subdomains = self._get_subdomains(target)
        dns_history = self._get_dns_history(target)
        whois_data = self._get_whois_data(target)
        return EnumerationResult(subdomains, dns_history, whois_data)
```

### 3. Storage Classes (Following dirsearch pattern)

#### BaseStorage (storage/base.py)
```python
from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    def save(self, result: ScanResult):
        """Save scan result"""
        
    @abstractmethod
    def load(self, scan_id: str) -> ScanResult:
        """Load scan result"""
```

#### StorageMixins (storage/base.py)
```python
class FileStorageMixin:
    """File-based storage operations"""
    
class SQLStorageMixin:
    """SQL database storage operations"""
    
class MongoStorageMixin:
    """MongoDB storage operations"""
```

### 4. Interface Classes

#### CLIInterface (interfaces/cli.py)
```python
class CLIInterface:
    """Command line interface"""
    
    def run(self, args):
        """Run CLI analysis"""
        analyzer = SiteAnalyzer(self._parse_config(args))
        result = analyzer.analyze(args.target)
        self._display_results(result)
```

#### GRPCServer (interfaces/grpc_server.py)
```python
class SiteAnalyzerServicer(site_analyzer_pb2_grpc.SiteAnalyzerServicer):
    """gRPC service implementation"""
    
    def Analyze(self, request, context):
        """Handle gRPC analysis request"""
```

#### RestAPI (interfaces/rest_api.py)
```python
from flask import Flask, request, jsonify

class RestAPI:
    """Flask REST API"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self._setup_routes()
        
    def _setup_routes(self):
        @self.app.route('/analyze', methods=['POST'])
        def analyze():
            """REST endpoint for analysis"""
```

## Integration Strategy

### 1. Mohiverse Functions Integration
- **SecurityTrails API**: Direct integration as SecurityTrailsEnumerator
- **DNS Functions**: Integrated into DNSEnumerator with multiple providers
- **Service Detection**: Separate ServiceDetectionEnumerator
- **Filtering Utilities**: Integrated into utils/filters.py

### 2. Storage Strategy
- **File Storage**: JSON, CSV, XML formats
- **MongoDB**: Document-based storage for complex nested data
- **SQL**: Relational storage for structured data and reporting

### 3. Interface Strategy
- **CLI**: Maintains current command-line compatibility
- **gRPC**: High-performance API for service integration
- **REST**: Web-friendly API for dashboard integration

## Implementation Phases

### Phase 1: Core Infrastructure
1. Create base classes and interfaces
2. Implement configuration management
3. Set up logging and error handling

### Phase 2: Enumeration Modules
1. Implement SecurityTrails integration
2. Create DNS enumeration module
3. Migrate existing Playwright scanner

### Phase 3: Storage Backends
1. Implement file storage
2. Add MongoDB support
3. Add SQL database support

### Phase 4: Interface Implementation
1. Refactor CLI interface
2. Implement gRPC server
3. Create Flask REST API

### Phase 5: Integration & Testing
1. Integrate all components
2. Add comprehensive testing
3. Performance optimization
