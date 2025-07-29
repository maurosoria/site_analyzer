import grpc
from concurrent import futures
import asyncio
from typing import Dict, Any
from .base import BaseInterface
from ..core.config import Config
from ..core.analyzer import SiteAnalyzer
from ..storage.factory import StorageFactory
from ..enumeration.factory import EnumeratorFactory
from ..models.scan_result import ScanResults


class SiteAnalyzerServicer:
    """gRPC service implementation for site analyzer"""
    
    def __init__(self, config: Config):
        self.config = config
        self.analyzer = SiteAnalyzer(config)
        
        storage = StorageFactory.create(config)
        self.analyzer.set_storage(storage)
        
        enumerators = EnumeratorFactory.create_enumerators(config)
        for enumerator in enumerators:
            self.analyzer.add_enumerator(enumerator)
    
    def Analyze(self, request, context):
        """Handle gRPC analysis request"""
        try:
            target = request.target
            results = self.analyzer.analyze(target)
            
            response = self._convert_to_grpc_response(results)
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Analysis failed: {str(e)}")
            return None
    
    def GetScanResult(self, request, context):
        """Get scan result by ID"""
        try:
            scan_id = request.scan_id
            results = self.analyzer.get_scan_result(scan_id)
            
            if not results:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Scan {scan_id} not found")
                return None
                
            response = self._convert_to_grpc_response(results)
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get scan result: {str(e)}")
            return None
    
    def ListScans(self, request, context):
        """List recent scans"""
        try:
            limit = getattr(request, 'limit', 100)
            scans = self.analyzer.list_scans(limit)
            
            response = self._convert_scan_list_to_grpc(scans)
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list scans: {str(e)}")
            return None
    
    def _convert_to_grpc_response(self, results: ScanResults):
        """Convert ScanResults to gRPC response format"""
        return {
            'scan_id': results.scan_id,
            'target': results.target,
            'status': results.status.value,
            'start_time': results.start_time.isoformat(),
            'end_time': results.end_time.isoformat() if results.end_time else None,
            'emails': list(results.emails),
            'subdomains': list(results.subdomains),
            'urls': list(results.urls),
            'endpoints': list(results.endpoints),
            'ip_addresses': list(results.ip_addresses),
            'virtual_hosts': list(results.virtual_hosts)
        }
    
    def _convert_scan_list_to_grpc(self, scans: list):
        """Convert scan list to gRPC response format"""
        return {'scans': scans}

class GRPCInterface(BaseInterface):
    """gRPC server interface"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.server = None
        self.servicer = SiteAnalyzerServicer(config)
    
    def run(self, *args, **kwargs):
        """Start gRPC server"""
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        
        listen_addr = f'[::]:{self.config.grpc_port}'
        self.server.add_insecure_port(listen_addr)
        
        print(f"Starting gRPC server on {listen_addr}")
        self.server.start()
        
        try:
            self.server.wait_for_termination()
        except KeyboardInterrupt:
            print("Shutting down gRPC server...")
            self.server.stop(0)
    
    def display_results(self, results: ScanResults):
        """Display results (not used in gRPC interface)"""
        pass
    
    def stop(self):
        """Stop the gRPC server"""
        if self.server:
            self.server.stop(0)
