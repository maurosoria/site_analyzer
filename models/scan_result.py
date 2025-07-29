from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum

class ScanStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class EnumerationResult:
    """Result from a single enumeration strategy"""
    enumerator_name: str
    target: str
    timestamp: datetime
    data: Dict
    errors: List[str] = field(default_factory=list)
    
@dataclass
class ScanResults:
    """Comprehensive scan results container"""
    scan_id: str
    target: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: ScanStatus = ScanStatus.PENDING
    
    emails: Set[str] = field(default_factory=set)
    urls: Set[str] = field(default_factory=set)
    endpoints: Set[str] = field(default_factory=set)
    keywords: Set[str] = field(default_factory=set)
    sourcemap_matches: Set[str] = field(default_factory=set)
    js_paths: Set[str] = field(default_factory=set)
    
    subdomains: Set[str] = field(default_factory=set)
    dns_records: Dict[str, List[str]] = field(default_factory=dict)
    historical_dns: Dict[str, List[Dict]] = field(default_factory=dict)
    
    whois_data: Dict = field(default_factory=dict)
    domain_info: Dict = field(default_factory=dict)
    
    ip_addresses: Set[str] = field(default_factory=set)
    virtual_hosts: Set[str] = field(default_factory=set)
    
    detected_services: Dict[str, List[str]] = field(default_factory=dict)
    
    enumeration_results: List[EnumerationResult] = field(default_factory=list)
    
    def add_enumeration_result(self, result: EnumerationResult):
        """Add result from an enumerator"""
        self.enumeration_results.append(result)
        
    def merge_results(self):
        """Merge all enumeration results into consolidated fields"""
        for result in self.enumeration_results:
            if result.enumerator_name == "web_scanner":
                self._merge_web_results(result.data)
            elif result.enumerator_name == "dns_enumeration":
                self._merge_dns_results(result.data)
            elif result.enumerator_name == "security_trails":
                self._merge_security_trails_results(result.data)
                
    def _merge_web_results(self, data: Dict):
        """Merge web scanning results"""
        self.emails.update(data.get('emails', []))
        self.urls.update(data.get('urls', []))
        self.endpoints.update(data.get('endpoints', []))
        self.keywords.update(data.get('keywords', []))
        self.sourcemap_matches.update(data.get('sourcemap_matches', []))
        self.js_paths.update(data.get('js_paths', []))
        
    def _merge_dns_results(self, data: Dict):
        """Merge DNS enumeration results"""
        self.subdomains.update(data.get('subdomains', []))
        self.dns_records.update(data.get('dns_records', {}))
        
    def _merge_security_trails_results(self, data: Dict):
        """Merge SecurityTrails results"""
        self.subdomains.update(data.get('subdomains', []))
        self.historical_dns.update(data.get('historical_dns', {}))
        self.whois_data.update(data.get('whois_data', {}))
        self.domain_info.update(data.get('domain_info', {}))
        self.ip_addresses.update(data.get('ip_addresses', []))
        self.virtual_hosts.update(data.get('virtual_hosts', []))
