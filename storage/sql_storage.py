import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from .base import BaseStorage, SQLStorageMixin
from ..models.scan_result import ScanResults, ScanStatus, EnumerationResult
from ..core.config import Config

class SQLStorage(BaseStorage, SQLStorageMixin):
    """SQL database storage implementation (SQLite)"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self._reuse_connection = True
        self._init_database()
    
    def _create_connection(self, database_path: Optional[str] = None):
        """Create SQLite connection"""
        if database_path is None:
            database_path = self.config.storage_config.get('database_path', './scans.db')
        return sqlite3.connect(str(database_path))
    
    def _init_database(self):
        """Initialize database tables"""
        database_path = self.config.storage_config.get('database_path', './scans.db')
        conn = self.get_connection(database_path)
        cursor = conn.cursor()
        
        cursor.execute(self.get_create_table_query())
        conn.commit()
        
        if not self._reuse_connection:
            conn.close()
    
    def get_create_table_query(self) -> str:
        """Get SQL query to create scans table"""
        return """
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            target TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            status TEXT NOT NULL,
            result_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    def save(self, result: ScanResults) -> str:
        """Save scan result to SQL database"""
        database_path = self.config.storage_config.get('database_path', './scans.db')
        conn = self.get_connection(database_path)
        cursor = conn.cursor()
        
        result_dict = {
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
        
        cursor.execute("""
            INSERT OR REPLACE INTO scans 
            (scan_id, target, start_time, end_time, status, result_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            result.scan_id,
            result.target,
            result.start_time.isoformat(),
            result.end_time.isoformat() if result.end_time else None,
            result.status.value,
            json.dumps(result_dict)
        ))
        
        conn.commit()
        
        if not self._reuse_connection:
            conn.close()
            
        return result.scan_id
    
    def load(self, scan_id: str) -> Optional[ScanResults]:
        """Load scan result from SQL database"""
        database_path = self.config.storage_config.get('database_path', './scans.db')
        conn = self.get_connection(database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT scan_id, target, start_time, end_time, status, result_data
            FROM scans WHERE scan_id = ?
        """, (scan_id,))
        
        row = cursor.fetchone()
        
        if not self._reuse_connection:
            conn.close()
            
        if not row:
            return None
            
        scan_id, target, start_time, end_time, status, result_data = row
        
        data = json.loads(result_data) if result_data else {}
        
        result = ScanResults(
            scan_id=scan_id,
            target=target,
            start_time=datetime.fromisoformat(start_time),
            end_time=datetime.fromisoformat(end_time) if end_time else None,
            status=ScanStatus(status)
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
    
    def list_scans(self, limit: int = 100) -> List[Dict]:
        """List recent scans"""
        database_path = self.config.storage_config.get('database_path', './scans.db')
        conn = self.get_connection(database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT scan_id, target, start_time, status
            FROM scans 
            ORDER BY start_time DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        if not self._reuse_connection:
            conn.close()
            
        return [
            {
                'scan_id': row[0],
                'target': row[1],
                'start_time': row[2],
                'status': row[3]
            }
            for row in rows
        ]
    
    def delete(self, scan_id: str) -> bool:
        """Delete scan result from SQL database"""
        database_path = self.config.storage_config.get('database_path', './scans.db')
        conn = self.get_connection(database_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        
        if not self._reuse_connection:
            conn.close()
            
        return deleted
