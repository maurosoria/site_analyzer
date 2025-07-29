#!/usr/bin/env python3
"""
Example gRPC client for Site Analyzer
This demonstrates how to connect to and use the Site Analyzer gRPC service.
"""

import grpc
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import site_analyzer_pb2 as pb2
from proto import site_analyzer_pb2_grpc as pb2_grpc


def analyze_target(stub, target):
    """Analyze a target website using the gRPC service"""
    print(f"Analyzing target: {target}")
    
    request = pb2.AnalyzeRequest(target=target)
    
    response = stub.Analyze(request)
    
    print(f"Scan ID: {response.scan_id}")
    print(f"Status: {get_status_name(response.status)}")
    print(f"Start time: {response.start_time}")
    
    return response.scan_id


def get_scan_result(stub, scan_id):
    """Get scan result by ID"""
    print(f"Getting scan result for ID: {scan_id}")
    
    request = pb2.GetScanResultRequest(scan_id=scan_id)
    
    result = stub.GetScanResult(request)
    
    print(f"Target: {result.target}")
    print(f"Status: {get_status_name(result.status)}")
    print(f"Start time: {result.start_time}")
    print(f"End time: {result.end_time}")
    print(f"Emails found: {len(result.emails)}")
    print(f"URLs found: {len(result.urls)}")
    print(f"Endpoints found: {len(result.endpoints)}")
    print(f"Subdomains found: {len(result.subdomains)}")
    
    return result


def list_scans(stub, limit=10):
    """List recent scans"""
    print(f"Listing up to {limit} recent scans")
    
    request = pb2.ListScansRequest(limit=limit)
    
    response = stub.ListScans(request)
    
    print(f"Total scans: {response.total_count}")
    print(f"Has more: {response.has_more}")
    
    for i, scan in enumerate(response.scans):
        print(f"\nScan {i+1}:")
        print(f"  ID: {scan.scan_id}")
        print(f"  Target: {scan.target}")
        print(f"  Status: {get_status_name(scan.status)}")
        print(f"  Start time: {scan.start_time}")
    
    return response


def get_enumerators(stub):
    """Get available enumerators"""
    print("Getting available enumerators")
    
    request = pb2.GetEnumeratorsRequest()
    
    response = stub.GetEnumerators(request)
    
    for i, enum in enumerate(response.enumerators):
        print(f"\nEnumerator {i+1}:")
        print(f"  Name: {enum.name}")
        print(f"  Description: {enum.description}")
        print(f"  Enabled: {enum.enabled}")
        if enum.required_config:
            print(f"  Required config: {', '.join(enum.required_config)}")
    
    return response


def get_storage_types(stub):
    """Get available storage types"""
    print("Getting available storage types")
    
    request = pb2.GetStorageTypesRequest()
    
    response = stub.GetStorageTypes(request)
    
    for i, st in enumerate(response.storage_types):
        print(f"\nStorage type {i+1}:")
        print(f"  Name: {st.name}")
        print(f"  Description: {st.description}")
        print(f"  Supported: {st.supported}")
        if st.required_config:
            print(f"  Required config: {', '.join(st.required_config)}")
    
    return response


def health_check(stub):
    """Check service health"""
    print("Checking service health")
    
    request = pb2.HealthCheckRequest()
    
    response = stub.HealthCheck(request)
    
    print(f"Status: {response.status}")
    print(f"Service: {response.service}")
    print(f"Version: {response.version}")
    print(f"Uptime: {response.uptime} seconds")
    
    return response


def stream_scan_progress(stub, scan_id):
    """Stream scan progress updates"""
    print(f"Streaming progress for scan ID: {scan_id}")
    
    request = pb2.StreamScanProgressRequest(scan_id=scan_id)
    
    try:
        for update in stub.StreamScanProgress(request):
            print(f"\nUpdate at {update.timestamp}:")
            print(f"  Status: {get_status_name(update.status)}")
            print(f"  Progress: {update.progress_percent}%")
            print(f"  Operation: {update.current_operation}")
            
            if update.partial_results:
                pr = update.partial_results
                print(f"  Emails: {len(pr.emails)}")
                print(f"  URLs: {len(pr.urls)}")
                print(f"  Endpoints: {len(pr.endpoints)}")
                print(f"  Subdomains: {len(pr.subdomains)}")
    except grpc.RpcError as e:
        print(f"Stream error: {e.details()}")


def get_status_name(status_enum):
    """Convert status enum to readable name"""
    status_names = {
        pb2.ScanStatus.SCAN_STATUS_UNKNOWN: "Unknown",
        pb2.ScanStatus.SCAN_STATUS_PENDING: "Pending",
        pb2.ScanStatus.SCAN_STATUS_RUNNING: "Running",
        pb2.ScanStatus.SCAN_STATUS_COMPLETED: "Completed",
        pb2.ScanStatus.SCAN_STATUS_FAILED: "Failed",
        pb2.ScanStatus.SCAN_STATUS_CANCELLED: "Cancelled"
    }
    return status_names.get(status_enum, "Unknown")


def main():
    """Main function"""
    server_addr = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    print(f"Connecting to gRPC server at {server_addr}")
    
    channel = grpc.insecure_channel(server_addr)
    
    stub = pb2_grpc.SiteAnalyzerStub(channel)
    
    try:
        health_check(stub)
        
        get_enumerators(stub)
        
        get_storage_types(stub)
        
        list_scans(stub, limit=5)
        
        target = "https://example.com"
        scan_id = analyze_target(stub, target)
        
        try:
            stream_scan_progress(stub, scan_id)
        except Exception as e:
            print(f"Error streaming progress: {e}")
        
        get_scan_result(stub, scan_id)
        
    except grpc.RpcError as e:
        print(f"RPC error: {e.details()}")
    finally:
        channel.close()


if __name__ == "__main__":
    main()
