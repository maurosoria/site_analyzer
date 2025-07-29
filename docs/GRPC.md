# Site Analyzer gRPC Service Documentation

This document provides comprehensive documentation for the Site Analyzer gRPC service.

## Overview

The Site Analyzer gRPC service provides high-performance, binary communication for website analysis, scan management, and configuration. gRPC uses Protocol Buffers for efficient serialization and supports bidirectional streaming.

## Proto Definition

The service is defined in the `proto/site_analyzer.proto` file. This file contains the service definition, message types, and enumerations used by the gRPC service.

## Service Address

```
localhost:50051
```

## Service Methods

### Analyze

Analyzes a target website and returns initial results.

```protobuf
rpc Analyze (AnalyzeRequest) returns (AnalyzeResponse) {}
```

**Request:**

```protobuf
message AnalyzeRequest {
  string target = 1;
  repeated string enumerators = 2;
  map<string, string> options = 3;
}
```

**Response:**

```protobuf
message AnalyzeResponse {
  string scan_id = 1;
  string target = 2;
  ScanStatus status = 3;
  string start_time = 4;
  string estimated_completion = 5;
  ScanResult initial_results = 6;
}
```

### GetScanResult

Retrieves detailed results of a previously completed scan.

```protobuf
rpc GetScanResult (GetScanResultRequest) returns (ScanResult) {}
```

**Request:**

```protobuf
message GetScanResultRequest {
  string scan_id = 1;
}
```

**Response:**

See the `ScanResult` message definition below.

### ListScans

Returns a paginated list of recent scan summaries.

```protobuf
rpc ListScans (ListScansRequest) returns (ListScansResponse) {}
```

**Request:**

```protobuf
message ListScansRequest {
  int32 limit = 1;
  int32 offset = 2;
  string target_filter = 3;
  ScanStatus status_filter = 4;
}
```

**Response:**

```protobuf
message ListScansResponse {
  repeated ScanSummary scans = 1;
  int32 total_count = 2;
  bool has_more = 3;
}
```

### DeleteScan

Removes a scan result from storage.

```protobuf
rpc DeleteScan (DeleteScanRequest) returns (DeleteScanResponse) {}
```

**Request:**

```protobuf
message DeleteScanRequest {
  string scan_id = 1;
}
```

**Response:**

```protobuf
message DeleteScanResponse {
  bool success = 1;
  string error_message = 2;
}
```

### GetEnumerators

Returns list of available enumeration strategies.

```protobuf
rpc GetEnumerators (GetEnumeratorsRequest) returns (GetEnumeratorsResponse) {}
```

**Request:**

```protobuf
message GetEnumeratorsRequest {
  // No parameters needed
}
```

**Response:**

```protobuf
message GetEnumeratorsResponse {
  repeated EnumeratorInfo enumerators = 1;
}
```

### GetStorageTypes

Returns list of available storage backends.

```protobuf
rpc GetStorageTypes (GetStorageTypesRequest) returns (GetStorageTypesResponse) {}
```

**Request:**

```protobuf
message GetStorageTypesRequest {
  // No parameters needed
}
```

**Response:**

```protobuf
message GetStorageTypesResponse {
  repeated StorageTypeInfo storage_types = 1;
}
```

### HealthCheck

Returns service health status.

```protobuf
rpc HealthCheck (HealthCheckRequest) returns (HealthCheckResponse) {}
```

**Request:**

```protobuf
message HealthCheckRequest {
  // No parameters needed
}
```

**Response:**

```protobuf
message HealthCheckResponse {
  string status = 1;
  string service = 2;
  string version = 3;
  int64 uptime = 4;
}
```

### StreamScanProgress

Provides real-time updates on scan progress.

```protobuf
rpc StreamScanProgress (StreamScanProgressRequest) returns (stream ScanProgressUpdate) {}
```

**Request:**

```protobuf
message StreamScanProgressRequest {
  string scan_id = 1;
}
```

**Response Stream:**

```protobuf
message ScanProgressUpdate {
  string scan_id = 1;
  ScanStatus status = 2;
  int32 progress_percent = 3;
  string current_operation = 4;
  ScanResult partial_results = 5;
  string timestamp = 6;
}
```

## Message Types

### ScanResult

Complete scan result with all discovered information.

```protobuf
message ScanResult {
  string scan_id = 1;
  string target = 2;
  ScanStatus status = 3;
  string start_time = 4;
  string end_time = 5;
  repeated string emails = 6;
  repeated string urls = 7;
  repeated string endpoints = 8;
  repeated string keywords = 9;
  repeated string subdomains = 10;
  repeated string ip_addresses = 11;
  repeated string virtual_hosts = 12;
  repeated string js_paths = 13;
  repeated string sourcemap_matches = 14;
  map<string, string> dns_records = 15;
  map<string, string> historical_dns = 16;
  map<string, string> whois_data = 17;
  map<string, string> domain_info = 18;
  map<string, string> detected_services = 19;
  repeated EnumerationResult enumeration_results = 20;
  repeated FrameworkInfo frameworks = 21;
  SecurityAnalysis security_analysis = 22;
}
```

### ScanSummary

Scan result summary for listing.

```protobuf
message ScanSummary {
  string scan_id = 1;
  string target = 2;
  ScanStatus status = 3;
  string start_time = 4;
  string end_time = 5;
  ScanStats stats = 6;
}
```

### EnumerationResult

Enumeration result from a specific enumerator.

```protobuf
message EnumerationResult {
  string enumerator_name = 1;
  string target = 2;
  string timestamp = 3;
  map<string, string> data = 4;
  repeated string errors = 5;
  int64 execution_time_ms = 6;
}
```

### FrameworkInfo

Information about detected frameworks.

```protobuf
message FrameworkInfo {
  string name = 1;
  string version = 2;
  float confidence = 3;
  repeated string evidence = 4;
  string category = 5;
}
```

### SecurityAnalysis

Security analysis results.

```protobuf
message SecurityAnalysis {
  int32 security_score = 1;
  repeated SecurityVulnerability vulnerabilities = 2;
  repeated string recommendations = 3;
  repeated SensitiveInfo exposed_info = 4;
}
```

### SecurityVulnerability

Security vulnerability information.

```protobuf
message SecurityVulnerability {
  string type = 1;
  VulnerabilitySeverity severity = 2;
  string description = 3;
  string location = 4;
  string remediation = 5;
}
```

### SensitiveInfo

Sensitive information exposure.

```protobuf
message SensitiveInfo {
  string type = 1;
  string value = 2;
  string location = 3;
  RiskLevel risk_level = 4;
}
```

### ScanStats

Statistics about scan results.

```protobuf
message ScanStats {
  int32 email_count = 1;
  int32 url_count = 2;
  int32 endpoint_count = 3;
  int32 subdomain_count = 4;
  int32 ip_count = 5;
  int32 framework_count = 6;
}
```

### EnumeratorInfo

Information about an enumerator.

```protobuf
message EnumeratorInfo {
  string name = 1;
  string description = 2;
  bool enabled = 3;
  repeated string required_config = 4;
  string estimated_time = 5;
}
```

### StorageTypeInfo

Information about a storage type.

```protobuf
message StorageTypeInfo {
  string name = 1;
  string description = 2;
  bool supported = 3;
  repeated string required_config = 4;
}
```

## Enumerations

### ScanStatus

Scan status enumeration.

```protobuf
enum ScanStatus {
  SCAN_STATUS_UNKNOWN = 0;
  SCAN_STATUS_PENDING = 1;
  SCAN_STATUS_RUNNING = 2;
  SCAN_STATUS_COMPLETED = 3;
  SCAN_STATUS_FAILED = 4;
  SCAN_STATUS_CANCELLED = 5;
}
```

### VulnerabilitySeverity

Vulnerability severity levels.

```protobuf
enum VulnerabilitySeverity {
  VULNERABILITY_SEVERITY_UNKNOWN = 0;
  VULNERABILITY_SEVERITY_LOW = 1;
  VULNERABILITY_SEVERITY_MEDIUM = 2;
  VULNERABILITY_SEVERITY_HIGH = 3;
  VULNERABILITY_SEVERITY_CRITICAL = 4;
}
```

### RiskLevel

Risk levels for sensitive information.

```protobuf
enum RiskLevel {
  RISK_LEVEL_UNKNOWN = 0;
  RISK_LEVEL_LOW = 1;
  RISK_LEVEL_MEDIUM = 2;
  RISK_LEVEL_HIGH = 3;
  RISK_LEVEL_CRITICAL = 4;
}
```

## Client Examples

### Python Client Example

A complete Python client example is available in `examples/grpc_client_example.py`. Here's a simplified version:

```python
import grpc
import sys
from proto import site_analyzer_pb2 as pb2
from proto import site_analyzer_pb2_grpc as pb2_grpc

def analyze_target(stub, target):
    """Analyze a target website using the gRPC service"""
    request = pb2.AnalyzeRequest(target=target)
    response = stub.Analyze(request)
    print(f"Scan ID: {response.scan_id}")
    return response.scan_id

def get_scan_result(stub, scan_id):
    """Get scan result by ID"""
    request = pb2.GetScanResultRequest(scan_id=scan_id)
    result = stub.GetScanResult(request)
    print(f"Target: {result.target}")
    print(f"Emails found: {len(result.emails)}")
    return result

def main():
    server_addr = "localhost:50051"
    channel = grpc.insecure_channel(server_addr)
    stub = pb2_grpc.SiteAnalyzerStub(channel)
    
    try:
        # Analyze a target
        target = "https://example.com"
        scan_id = analyze_target(stub, target)
        
        # Get scan result
        get_scan_result(stub, scan_id)
        
    except grpc.RpcError as e:
        print(f"RPC error: {e.details()}")
    finally:
        channel.close()

if __name__ == "__main__":
    main()
```

### Go Client Example

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "google.golang.org/grpc"
    pb "path/to/proto"
)

func main() {
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("Failed to connect: %v", err)
    }
    defer conn.Close()

    client := pb.NewSiteAnalyzerClient(conn)
    ctx, cancel := context.WithTimeout(context.Background(), time.Second*30)
    defer cancel()

    // Analyze a target
    analyzeResp, err := client.Analyze(ctx, &pb.AnalyzeRequest{
        Target: "https://example.com",
    })
    if err != nil {
        log.Fatalf("Analyze failed: %v", err)
    }
    fmt.Printf("Scan ID: %s\n", analyzeResp.ScanId)

    // Get scan result
    scanResult, err := client.GetScanResult(ctx, &pb.GetScanResultRequest{
        ScanId: analyzeResp.ScanId,
    })
    if err != nil {
        log.Fatalf("GetScanResult failed: %v", err)
    }
    fmt.Printf("Found %d emails\n", len(scanResult.Emails))
}
```

### Node.js Client Example

```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const PROTO_PATH = './proto/site_analyzer.proto';

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
const siteAnalyzer = protoDescriptor.site_analyzer;

function main() {
  const client = new siteAnalyzer.SiteAnalyzer(
    'localhost:50051',
    grpc.credentials.createInsecure()
  );

  // Analyze a target
  client.Analyze({ target: 'https://example.com' }, (err, response) => {
    if (err) {
      console.error('Error:', err);
      return;
    }
    
    console.log(`Scan ID: ${response.scan_id}`);
    const scanId = response.scan_id;
    
    // Get scan result
    client.GetScanResult({ scan_id: scanId }, (err, result) => {
      if (err) {
        console.error('Error:', err);
        return;
      }
      
      console.log(`Target: ${result.target}`);
      console.log(`Emails found: ${result.emails.length}`);
    });
  });
}

main();
```

## Streaming Example

### Python Streaming Example

```python
def stream_scan_progress(stub, scan_id):
    """Stream scan progress updates"""
    request = pb2.StreamScanProgressRequest(scan_id=scan_id)
    
    try:
        for update in stub.StreamScanProgress(request):
            print(f"\nUpdate at {update.timestamp}:")
            print(f"  Status: {get_status_name(update.status)}")
            print(f"  Progress: {update.progress_percent}%")
            print(f"  Operation: {update.current_operation}")
            
            # Print partial results summary
            if update.partial_results:
                pr = update.partial_results
                print(f"  Emails: {len(pr.emails)}")
                print(f"  URLs: {len(pr.urls)}")
    except grpc.RpcError as e:
        print(f"Stream error: {e.details()}")
```

## Error Handling

gRPC uses status codes to indicate errors. The service returns appropriate status codes and error details:

| Code | Description |
|------|-------------|
| OK | Success |
| INVALID_ARGUMENT | Bad request (e.g., missing target) |
| NOT_FOUND | Resource not found (e.g., scan ID) |
| INTERNAL | Server error |
| UNAVAILABLE | Service unavailable |

Example error handling in Python:

```python
try:
    result = stub.GetScanResult(request)
except grpc.RpcError as e:
    status_code = e.code()
    if status_code == grpc.StatusCode.NOT_FOUND:
        print("Scan not found")
    elif status_code == grpc.StatusCode.INTERNAL:
        print(f"Server error: {e.details()}")
    else:
        print(f"Error: {e.details()}")
```

## Reflection and Health Services

The gRPC server includes reflection and health services:

- **Reflection**: Allows clients to discover service methods at runtime
- **Health**: Provides health status for the service

### Using Reflection with grpcurl

[grpcurl](https://github.com/fullstorydev/grpcurl) is a command-line tool that lets you interact with gRPC servers:

```bash
# List services
grpcurl -plaintext localhost:50051 list

# List methods
grpcurl -plaintext localhost:50051 list site_analyzer.SiteAnalyzer

# Describe a method
grpcurl -plaintext localhost:50051 describe site_analyzer.SiteAnalyzer.Analyze

# Call a method
grpcurl -plaintext -d '{"target": "https://example.com"}' \
  localhost:50051 site_analyzer.SiteAnalyzer.Analyze
```

### Checking Health Status

```bash
grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check
```

## Performance Considerations

- Use streaming for long-running operations
- Implement proper error handling and retries
- Consider using connection pooling for multiple clients
- Use TLS for secure communication in production

## Troubleshooting

### Common Issues

1. **Connection refused**:
   - Verify the server is running
   - Check the port is correct and not blocked by firewall

2. **Deadline exceeded**:
   - Increase timeout for long-running operations
   - Check server performance and resource usage

3. **Protocol buffer errors**:
   - Ensure client and server are using compatible proto definitions
   - Regenerate client code if needed

### Debugging Tools

- Use `grpcurl` for testing and debugging
- Enable gRPC logging for detailed information
- Check server logs for error details
