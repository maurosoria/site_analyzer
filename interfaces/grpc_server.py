import grpc
from concurrent import futures
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
from interfaces.base import BaseInterface
from core.config import Config
from core.analyzer import SiteAnalyzer
from storage.factory import StorageFactory
from enumeration.factory import EnumeratorFactory
from models.scan_result import ScanResults
import sys
import os
import importlib.util

proto_dir = os.path.join(os.path.dirname(__file__), '..', 'proto')
pb2_spec = importlib.util.spec_from_file_location("site_analyzer_pb2", os.path.join(proto_dir, "site_analyzer_pb2.py"))
pb2 = importlib.util.module_from_spec(pb2_spec)
pb2_spec.loader.exec_module(pb2)

pb2_grpc_spec = importlib.util.spec_from_file_location("site_analyzer_pb2_grpc", os.path.join(proto_dir, "site_analyzer_pb2_grpc.py"))
pb2_grpc = importlib.util.module_from_spec(pb2_grpc_spec)
pb2_grpc_spec.loader.exec_module(pb2_grpc)


class SiteAnalyzerServicer(pb2_grpc.SiteAnalyzerServicer):
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
            
            specific_enumerators = list(request.enumerators) if request.enumerators else None
            
            results = self.analyzer.analyze(target)
            
            response = pb2.AnalyzeResponse(
                scan_id=results.scan_id,
                target=results.target,
                status=self._convert_status_to_enum(results.status.value),
                start_time=results.start_time.isoformat()
            )
            
            if results:
                response.initial_results.CopyFrom(self._convert_to_scan_result_pb(results))
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Analysis failed: {str(e)}")
            return pb2.AnalyzeResponse()
    
    def GetScanResult(self, request, context):
        """Get scan result by ID"""
        try:
            scan_id = request.scan_id
            results = self.analyzer.get_scan_result(scan_id)
            
            if not results:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Scan {scan_id} not found")
                return pb2.ScanResult()
                
            return self._convert_to_scan_result_pb(results)
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get scan result: {str(e)}")
            return pb2.ScanResult()
    
    def ListScans(self, request, context):
        """List recent scans"""
        try:
            limit = request.limit if request.limit > 0 else 100
            offset = request.offset if request.offset > 0 else 0
            target_filter = request.target_filter if request.target_filter else None
            
            scans = self.analyzer.list_scans(limit)
            
            if target_filter:
                scans = [s for s in scans if target_filter.lower() in s.get('target', '').lower()]
            
            response = pb2.ListScansResponse(
                total_count=len(scans),
                has_more=len(scans) >= limit
            )
            
            for scan in scans:
                summary = pb2.ScanSummary(
                    scan_id=scan.get('scan_id', ''),
                    target=scan.get('target', ''),
                    status=self._convert_status_to_enum(scan.get('status', 'unknown')),
                    start_time=scan.get('start_time', ''),
                    end_time=scan.get('end_time', '')
                )
                
                if 'stats' in scan:
                    stats = scan['stats']
                    summary.stats.email_count = stats.get('email_count', 0)
                    summary.stats.url_count = stats.get('url_count', 0)
                    summary.stats.endpoint_count = stats.get('endpoint_count', 0)
                    summary.stats.subdomain_count = stats.get('subdomain_count', 0)
                    summary.stats.ip_count = stats.get('ip_count', 0)
                    summary.stats.framework_count = stats.get('framework_count', 0)
                
                response.scans.append(summary)
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list scans: {str(e)}")
            return pb2.ListScansResponse()
    
    def _convert_to_scan_result_pb(self, results: ScanResults) -> pb2.ScanResult:
        """Convert ScanResults to protobuf ScanResult message"""
        scan_result = pb2.ScanResult(
            scan_id=results.scan_id,
            target=results.target,
            status=self._convert_status_to_enum(results.status.value),
            start_time=results.start_time.isoformat(),
            end_time=results.end_time.isoformat() if results.end_time else ""
        )
        
        scan_result.emails.extend(list(results.emails))
        scan_result.urls.extend(list(results.urls))
        scan_result.endpoints.extend(list(results.endpoints))
        scan_result.keywords.extend(list(results.keywords))
        scan_result.subdomains.extend(list(results.subdomains))
        scan_result.ip_addresses.extend(list(results.ip_addresses))
        scan_result.virtual_hosts.extend(list(results.virtual_hosts))
        scan_result.js_paths.extend(list(results.js_paths))
        scan_result.sourcemap_matches.extend(list(results.sourcemap_matches))
        
        if results.dns_records:
            for k, v in results.dns_records.items():
                scan_result.dns_records[k] = str(v)
                
        if results.historical_dns:
            for k, v in results.historical_dns.items():
                scan_result.historical_dns[k] = str(v)
                
        if results.whois_data:
            for k, v in results.whois_data.items():
                scan_result.whois_data[k] = str(v)
                
        if results.domain_info:
            for k, v in results.domain_info.items():
                scan_result.domain_info[k] = str(v)
                
        if results.detected_services:
            for k, v in results.detected_services.items():
                scan_result.detected_services[k] = str(v)
        
        for er in results.enumeration_results:
            enum_result = pb2.EnumerationResult(
                enumerator_name=er.enumerator_name,
                target=er.target,
                timestamp=er.timestamp.isoformat(),
                execution_time_ms=int(er.execution_time * 1000) if hasattr(er, 'execution_time') else 0
            )
            
            enum_result.errors.extend(er.errors)
            
            for k, v in er.data.items():
                if isinstance(v, (list, set)):
                    enum_result.data[k] = str(list(v))
                elif isinstance(v, dict):
                    enum_result.data[k] = str(v)
                else:
                    enum_result.data[k] = str(v)
            
            scan_result.enumeration_results.append(enum_result)
        
        return scan_result
    
    def _convert_status_to_enum(self, status_str: str) -> pb2.ScanStatus:
        """Convert status string to protobuf enum value"""
        status_map = {
            'pending': pb2.ScanStatus.SCAN_STATUS_PENDING,
            'running': pb2.ScanStatus.SCAN_STATUS_RUNNING,
            'completed': pb2.ScanStatus.SCAN_STATUS_COMPLETED,
            'failed': pb2.ScanStatus.SCAN_STATUS_FAILED,
            'cancelled': pb2.ScanStatus.SCAN_STATUS_CANCELLED
        }
        return status_map.get(status_str.lower(), pb2.ScanStatus.SCAN_STATUS_UNKNOWN)
    
    def DeleteScan(self, request, context):
        """Delete scan result"""
        try:
            scan_id = request.scan_id
            success = self.analyzer.storage.delete(scan_id)
            
            if success:
                return pb2.DeleteScanResponse(success=True)
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Scan {scan_id} not found")
                return pb2.DeleteScanResponse(success=False, error_message="Scan not found")
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to delete scan: {str(e)}")
            return pb2.DeleteScanResponse(success=False, error_message=str(e))
    
    def GetEnumerators(self, request, context):
        """Get available enumerators"""
        try:
            enumerators = EnumeratorFactory.get_available_types()
            
            response = pb2.GetEnumeratorsResponse()
            for enum in enumerators:
                info = pb2.EnumeratorInfo(
                    name=enum.get('name', ''),
                    description=enum.get('description', ''),
                    enabled=enum.get('enabled', False)
                )
                
                if 'required_config' in enum:
                    info.required_config.extend(enum['required_config'])
                    
                response.enumerators.append(info)
                
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get enumerators: {str(e)}")
            return pb2.GetEnumeratorsResponse()
    
    def GetStorageTypes(self, request, context):
        """Get available storage types"""
        try:
            storage_types = StorageFactory.get_available_types()
            
            response = pb2.GetStorageTypesResponse()
            for st in storage_types:
                info = pb2.StorageTypeInfo(
                    name=st.get('name', ''),
                    description=st.get('description', ''),
                    supported=st.get('supported', False)
                )
                
                if 'required_config' in st:
                    info.required_config.extend(st['required_config'])
                    
                response.storage_types.append(info)
                
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get storage types: {str(e)}")
            return pb2.GetStorageTypesResponse()
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        try:
            start_time = getattr(self.analyzer, 'start_time', datetime.now())
            uptime = int((datetime.now() - start_time).total_seconds())
            
            return pb2.HealthCheckResponse(
                status="healthy",
                service="site_analyzer_grpc",
                version="1.0.0",
                uptime=uptime
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Health check failed: {str(e)}")
            return pb2.HealthCheckResponse(status="unhealthy")

class GRPCInterface(BaseInterface):
    """gRPC server interface"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.server = None
        self.servicer = SiteAnalyzerServicer(config)
    
    def run(self, *args, **kwargs):
        """Start gRPC server"""
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        pb2_grpc.add_SiteAnalyzerServicer_to_server(self.servicer, self.server)
        
        try:
            from grpc_reflection.v1alpha import reflection
            SERVICE_NAMES = (
                pb2.DESCRIPTOR.services_by_name['SiteAnalyzer'].full_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, self.server)
            print("gRPC reflection enabled")
        except ImportError:
            print("grpc_reflection not available, skipping reflection setup")
        
        try:
            from grpc_health.v1 import health_pb2, health_pb2_grpc
            from grpc_health.v1 import health
            health_servicer = health.HealthServicer()
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.server)
            health_servicer.set(pb2.DESCRIPTOR.services_by_name['SiteAnalyzer'].full_name, health_pb2.HealthCheckResponse.SERVING)
            print("gRPC health service enabled")
        except ImportError:
            print("grpc_health not available, skipping health service setup")
        
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
