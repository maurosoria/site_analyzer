import requests
from typing import Dict, List, Optional
from datetime import datetime
from enumeration.base import BaseEnumerator
from models.scan_result import EnumerationResult
from core.config import Config
from core.exceptions import APIException

class SecurityTrails:
    """SecurityTrails API wrapper - adapted from Mohiverse notebook"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.securitytrails.com/v1"
        self.headers = {
            "APIKEY": api_key,
            "Content-Type": "application/json"
        }
    
    def get_domain(self, domain: str) -> Dict:
        """Get domain information"""
        url = f"{self.base_url}/domain/{domain}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_subdomain(self, domain: str) -> Dict:
        """Get subdomains for domain"""
        url = f"{self.base_url}/domain/{domain}/subdomains"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_whois(self, domain: str) -> Dict:
        """Get WHOIS information"""
        url = f"{self.base_url}/domain/{domain}/whois"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_history_dns(self, domain: str, record_type: str = "a") -> Dict:
        """Get historical DNS records"""
        url = f"{self.base_url}/history/{domain}/dns/{record_type}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_history_whois(self, domain: str) -> Dict:
        """Get historical WHOIS data"""
        url = f"{self.base_url}/history/{domain}/whois"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def ip_explorer(self, ip: str) -> Dict:
        """Explore IP neighborhood"""
        url = f"{self.base_url}/ips/nearby/{ip}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def domain_searcher(self, query: str, filter_type: str = "keyword") -> Dict:
        """Search domains by keyword"""
        url = f"{self.base_url}/domains/list"
        params = {
            "filter": {filter_type: query}
        }
        response = requests.post(url, headers=self.headers, json=params)
        response.raise_for_status()
        return response.json()
    
    def get_vhosts(self, ip: str) -> Dict:
        """Get virtual hosts for IP"""
        url = f"{self.base_url}/ips/{ip}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_domains(self, ip: str) -> Dict:
        """Get domains hosted on IP"""
        url = f"{self.base_url}/ips/{ip}/domains"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

class SecurityTrailsEnumerator(BaseEnumerator):
    """SecurityTrails enumeration strategy"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        if not config.security_trails_api_key:
            raise APIException("SecurityTrails API key not configured")
        self.api = SecurityTrails(config.security_trails_api_key)
    
    def get_name(self) -> str:
        return "security_trails"
    
    def enumerate(self, target: str) -> EnumerationResult:
        """Perform SecurityTrails enumeration"""
        data = {
            'subdomains': [],
            'historical_dns': {},
            'whois_data': {},
            'domain_info': {},
            'ip_addresses': [],
            'virtual_hosts': []
        }
        errors = []
        
        try:
            domain_info = self.api.get_domain(target)
            data['domain_info'] = domain_info
            
            if 'current_dns' in domain_info:
                for record_type, records in domain_info['current_dns'].items():
                    if record_type == 'a':
                        for record in records:
                            if 'ip' in record:
                                data['ip_addresses'].append(record['ip'])
            
        except Exception as e:
            errors.append(f"Failed to get domain info: {e}")
        
        try:
            subdomain_data = self.api.get_subdomain(target)
            if 'subdomains' in subdomain_data:
                data['subdomains'] = [f"{sub}.{target}" for sub in subdomain_data['subdomains']]
            
        except Exception as e:
            errors.append(f"Failed to get subdomains: {e}")
        
        try:
            whois_data = self.api.get_whois(target)
            data['whois_data'] = whois_data
            
        except Exception as e:
            errors.append(f"Failed to get WHOIS data: {e}")
        
        try:
            for record_type in ['a', 'aaaa', 'mx', 'ns', 'txt']:
                try:
                    history = self.api.get_history_dns(target, record_type)
                    data['historical_dns'][record_type] = history
                except Exception as e:
                    errors.append(f"Failed to get {record_type} history: {e}")
            
        except Exception as e:
            errors.append(f"Failed to get DNS history: {e}")
        
        for ip in data['ip_addresses']:
            try:
                vhosts = self.api.get_vhosts(ip)
                if 'hostnames' in vhosts:
                    data['virtual_hosts'].extend(vhosts['hostnames'])
                    
                domains = self.api.get_domains(ip)
                if 'domains' in domains:
                    data['virtual_hosts'].extend(domains['domains'])
                    
            except Exception as e:
                errors.append(f"Failed to get virtual hosts for {ip}: {e}")
        
        return self._create_result(target, data, errors)

def get_securitytrails_subdomains(domains: List[str], api_key: str) -> List[str]:
    """Batch subdomain collection - adapted from Mohiverse notebook"""
    api = SecurityTrails(api_key)
    all_subdomains = []
    
    for domain in domains:
        try:
            result = api.get_subdomain(domain)
            if 'subdomains' in result:
                subdomains = [f"{sub}.{domain}" for sub in result['subdomains']]
                all_subdomains.extend(subdomains)
        except Exception as e:
            print(f"Error getting subdomains for {domain}: {e}")
    
    return list(set(all_subdomains))

def get_securitytrails_history_dns(domains: List[str], api_key: str) -> Dict:
    """Get historical DNS for multiple domains - adapted from Mohiverse notebook"""
    api = SecurityTrails(api_key)
    history_data = {}
    
    for domain in domains:
        history_data[domain] = {}
        for record_type in ['a', 'aaaa', 'mx', 'ns']:
            try:
                history = api.get_history_dns(domain, record_type)
                history_data[domain][record_type] = history
            except Exception as e:
                print(f"Error getting {record_type} history for {domain}: {e}")
    
    return history_data
