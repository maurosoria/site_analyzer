import uuid
from datetime import datetime
from typing import List, Optional
from .config import Config
from .exceptions import SiteAnalyzerException
from ..models.scan_result import ScanResults, ScanStatus
from ..enumeration.base import BaseEnumerator
from ..storage.base import BaseStorage

class SiteAnalyzer:
    """Main orchestrator for site analysis operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.enumerators: List[BaseEnumerator] = []
        self.storage: Optional[BaseStorage] = None
        
    def add_enumerator(self, enumerator: BaseEnumerator):
        """Add enumeration strategy"""
        if enumerator.is_enabled():
            self.enumerators.append(enumerator)
            
    def set_storage(self, storage: BaseStorage):
        """Set storage backend"""
        self.storage = storage
        
    def analyze(self, target: str) -> ScanResults:
        """Main analysis entry point"""
        scan_id = str(uuid.uuid4())
        
        results = ScanResults(
            scan_id=scan_id,
            target=target,
            start_time=datetime.now(),
            status=ScanStatus.RUNNING
        )
        
        try:
            for enumerator in self.enumerators:
                try:
                    enum_result = enumerator.enumerate(target)
                    results.add_enumeration_result(enum_result)
                except Exception as e:
                    print(f"Error in {enumerator.get_name()}: {e}")
                    
            results.merge_results()
            results.status = ScanStatus.COMPLETED
            results.end_time = datetime.now()
            
            if self.storage:
                self.storage.save(results)
                
        except Exception as e:
            results.status = ScanStatus.FAILED
            results.end_time = datetime.now()
            if self.storage:
                self.storage.save(results)
            raise SiteAnalyzerException(f"Analysis failed: {e}")
            
        return results
        
    def get_scan_result(self, scan_id: str) -> Optional[ScanResults]:
        """Get scan result by ID"""
        if not self.storage:
            raise SiteAnalyzerException("No storage backend configured")
        return self.storage.load(scan_id)
        
    def list_scans(self, limit: int = 100) -> List[dict]:
        """List recent scans"""
        if not self.storage:
            raise SiteAnalyzerException("No storage backend configured")
        return self.storage.list_scans(limit)
