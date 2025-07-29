import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from storage.base import BaseStorage, FileStorageMixin
from models.scan_result import ScanResults
from core.config import Config

class FileStorage(BaseStorage, FileStorageMixin):
    """File-based storage implementation"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        storage_dir = self.config.storage_config.get('directory', './scans')
        os.makedirs(storage_dir, exist_ok=True)
    
    def save(self, result: ScanResults) -> str:
        """Save scan result to JSON file"""
        file_path = self._get_file_path(result.scan_id)
        self._ensure_directory(file_path)
        
        result_dict = {
            'scan_id': result.scan_id,
            'target': result.target,
            'start_time': result.start_time.isoformat(),
            'end_time': result.end_time.isoformat() if result.end_time else None,
            'status': result.status.value,
            'emails': list(result.emails),
            'urls': list(result.urls),
            'endpoints': list(result.endpoints),
            'keywords': list(result.keywords),
            'sourcemap_matches': list(result.sourcemap_matches),
            'js_paths': list(result.js_paths),
            'subdomains': list(result.subdomains),
            'dns_records': result.dns_records,
            'historical_dns': result.historical_dns,
            'whois_data': result.whois_data,
            'domain_info': result.domain_info,
            'ip_addresses': list(result.ip_addresses),
            'virtual_hosts': list(result.virtual_hosts),
            'detected_services': result.detected_services,
            'enumeration_results': [
                {
                    'enumerator_name': er.enumerator_name,
                    'target': er.target,
                    'timestamp': er.timestamp.isoformat(),
                    'data': er.data,
                    'errors': er.errors
                }
                for er in result.enumeration_results
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(result_dict, f, indent=2)
            
        return result.scan_id
    
    def load(self, scan_id: str) -> Optional[ScanResults]:
        """Load scan result from JSON file"""
        file_path = self._get_file_path(scan_id)
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            from models.scan_result import ScanStatus, EnumerationResult
            
            result = ScanResults(
                scan_id=data['scan_id'],
                target=data['target'],
                start_time=datetime.fromisoformat(data['start_time']),
                end_time=datetime.fromisoformat(data['end_time']) if data['end_time'] else None,
                status=ScanStatus(data['status'])
            )
            
            result.emails = set(data.get('emails', []))
            result.urls = set(data.get('urls', []))
            result.endpoints = set(data.get('endpoints', []))
            result.keywords = set(data.get('keywords', []))
            result.sourcemap_matches = set(data.get('sourcemap_matches', []))
            result.js_paths = set(data.get('js_paths', []))
            result.subdomains = set(data.get('subdomains', []))
            result.dns_records = data.get('dns_records', {})
            result.historical_dns = data.get('historical_dns', {})
            result.whois_data = data.get('whois_data', {})
            result.domain_info = data.get('domain_info', {})
            result.ip_addresses = set(data.get('ip_addresses', []))
            result.virtual_hosts = set(data.get('virtual_hosts', []))
            result.detected_services = data.get('detected_services', {})
            
            for er_data in data.get('enumeration_results', []):
                enum_result = EnumerationResult(
                    enumerator_name=er_data['enumerator_name'],
                    target=er_data['target'],
                    timestamp=datetime.fromisoformat(er_data['timestamp']),
                    data=er_data['data'],
                    errors=er_data['errors']
                )
                result.enumeration_results.append(enum_result)
                
            return result
            
        except Exception as e:
            print(f"Error loading scan {scan_id}: {e}")
            return None
    
    def list_scans(self, limit: int = 100) -> List[Dict]:
        """List recent scans"""
        storage_dir = self.config.storage_config.get('directory', './scans')
        scans = []
        
        if not os.path.exists(storage_dir):
            return scans
            
        for filename in os.listdir(storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(storage_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    scans.append({
                        'scan_id': data['scan_id'],
                        'target': data['target'],
                        'start_time': data['start_time'],
                        'status': data['status']
                    })
                except Exception:
                    continue
                    
        scans.sort(key=lambda x: x['start_time'], reverse=True)
        return scans[:limit]
    
    def delete(self, scan_id: str) -> bool:
        """Delete scan result file"""
        file_path = self._get_file_path(scan_id)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False
