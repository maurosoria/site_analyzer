import requests
import socket
from typing import Dict, List, Set
from .base import BaseEnumerator
from ..models.scan_result import EnumerationResult
from ..core.config import Config

class DNSEnumerator(BaseEnumerator):
    """DNS enumeration strategy"""
    
    def get_name(self) -> str:
        return "dns_enumeration"
    
    def enumerate(self, target: str) -> EnumerationResult:
        """Perform DNS enumeration"""
        data = {
            'subdomains': [],
            'dns_records': {},
            'dns_dumpster_data': {}
        }
        errors = []
        
        try:
            data['dns_records'] = self._get_basic_dns_records(target)
        except Exception as e:
            errors.append(f"Failed to get basic DNS records: {e}")
        
        try:
            dns_dumpster_data = self._get_dns_dumpster(target)
            data['dns_dumpster_data'] = dns_dumpster_data
            if 'subdomains' in dns_dumpster_data:
                data['subdomains'].extend(dns_dumpster_data['subdomains'])
        except Exception as e:
            errors.append(f"Failed to get DNS Dumpster data: {e}")
        
        return self._create_result(target, data, errors)
    
    def _get_basic_dns_records(self, domain: str) -> Dict:
        """Get basic DNS records"""
        records = {}
        
        try:
            a_records = socket.gethostbyname_ex(domain)
            records['a'] = a_records[2]
        except Exception:
            records['a'] = []
        
        try:
            records['hostname'] = socket.gethostbyaddr(records['a'][0])[0] if records['a'] else None
        except Exception:
            records['hostname'] = None
        
        return records
    
    def _get_dns_dumpster(self, domain: str) -> Dict:
        """Get DNS information from DNSDumpster - adapted from Mohiverse notebook"""
        try:
            session = requests.Session()
            
            url = "https://dnsdumpster.com/"
            response = session.get(url)
            response.raise_for_status()
            
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    csrf_token = line.split('value="')[1].split('"')[0]
                    break
            
            if not csrf_token:
                raise Exception("Could not find CSRF token")
            
            data = {
                'csrfmiddlewaretoken': csrf_token,
                'targetip': domain,
                'user': 'free'
            }
            
            headers = {
                'Referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = session.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            result = self._parse_dns_dumpster_response(response.text, domain)
            return result
            
        except Exception as e:
            raise Exception(f"DNS Dumpster query failed: {e}")
    
    def _parse_dns_dumpster_response(self, html: str, domain: str) -> Dict:
        """Parse DNS Dumpster HTML response"""
        import re
        
        result = {
            'subdomains': [],
            'dns_servers': [],
            'mx_records': [],
            'txt_records': []
        }
        
        subdomain_pattern = r'([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*' + re.escape(domain)
        subdomains = re.findall(subdomain_pattern, html)
        
        clean_subdomains = set()
        for match in subdomains:
            if isinstance(match, tuple):
                subdomain = match[0] + domain if match[0] else domain
            else:
                subdomain = match
            
            if subdomain and subdomain != domain:
                clean_subdomains.add(subdomain)
        
        result['subdomains'] = list(clean_subdomains)
        
        dns_pattern = r'DNS Servers.*?<td[^>]*>([^<]+)</td>'
        dns_matches = re.findall(dns_pattern, html, re.DOTALL | re.IGNORECASE)
        result['dns_servers'] = [dns.strip() for dns in dns_matches if dns.strip()]
        
        mx_pattern = r'MX Records.*?<td[^>]*>([^<]+)</td>'
        mx_matches = re.findall(mx_pattern, html, re.DOTALL | re.IGNORECASE)
        result['mx_records'] = [mx.strip() for mx in mx_matches if mx.strip()]
        
        return result

def get_dns_dumpster(domain: str) -> Dict:
    """Standalone DNS Dumpster function - adapted from Mohiverse notebook"""
    enumerator = DNSEnumerator(None)
    return enumerator._get_dns_dumpster(domain)

def filter_strings(strings: List[str], prefixes: List[str]) -> List[str]:
    """Filter strings by prefixes - adapted from Mohiverse notebook"""
    filtered = []
    for string in strings:
        for prefix in prefixes:
            if string.startswith(prefix):
                filtered.append(string)
                break
    return filtered
