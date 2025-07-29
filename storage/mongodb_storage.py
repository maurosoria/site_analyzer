from typing import Dict, List, Optional
from datetime import datetime
from .base import BaseStorage, MongoStorageMixin
from ..models.scan_result import ScanResults, ScanStatus, EnumerationResult
from ..core.config import Config

class MongoDBStorage(BaseStorage, MongoStorageMixin):
    """MongoDB storage implementation"""
    
    def save(self, result: ScanResults) -> str:
        """Save scan result to MongoDB"""
        collection = self._get_collection()
        
        result_dict = {
            '_id': result.scan_id,
            'scan_id': result.scan_id,
            'target': result.target,
            'start_time': result.start_time,
            'end_time': result.end_time,
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
                    'timestamp': er.timestamp,
                    'data': er.data,
                    'errors': er.errors
                }
                for er in result.enumeration_results
            ],
            'created_at': datetime.now()
        }
        
        collection.replace_one(
            {'_id': result.scan_id},
            result_dict,
            upsert=True
        )
        
        return result.scan_id
    
    def load(self, scan_id: str) -> Optional[ScanResults]:
        """Load scan result from MongoDB"""
        collection = self._get_collection()
        data = collection.find_one({'_id': scan_id})
        
        if not data:
            return None
            
        result = ScanResults(
            scan_id=data['scan_id'],
            target=data['target'],
            start_time=data['start_time'],
            end_time=data['end_time'],
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
                timestamp=er_data['timestamp'],
                data=er_data['data'],
                errors=er_data['errors']
            )
            result.enumeration_results.append(enum_result)
            
        return result
    
    def list_scans(self, limit: int = 100) -> List[Dict]:
        """List recent scans"""
        collection = self._get_collection()
        
        cursor = collection.find(
            {},
            {'scan_id': 1, 'target': 1, 'start_time': 1, 'status': 1}
        ).sort('start_time', -1).limit(limit)
        
        return list(cursor)
    
    def delete(self, scan_id: str) -> bool:
        """Delete scan result from MongoDB"""
        collection = self._get_collection()
        result = collection.delete_one({'_id': scan_id})
        return result.deleted_count > 0
