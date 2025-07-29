# Site Analyzer REST API Documentation

This document provides comprehensive documentation for the Site Analyzer REST API.

## API Overview

The Site Analyzer REST API provides HTTP endpoints for website analysis, scan management, and configuration. The API follows RESTful principles and returns JSON responses.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, the API does not require authentication. For production deployments, it is recommended to implement an authentication mechanism.

## Swagger Documentation

Interactive API documentation is available at:

```
http://localhost:5000/docs/
```

The Swagger UI allows you to:
- Explore available endpoints
- View request/response schemas
- Test API calls directly from the browser

## Endpoints

### Health Check

#### GET /health

Check the health status of the API service.

**Response:**

```json
{
  "status": "healthy",
  "service": "site_analyzer"
}
```

### Analysis

#### POST /analyze

Analyze a target website.

**Request:**

```json
{
  "target": "https://example.com",
  "enumerators": ["web_scanner", "dns_enumeration"]
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `target` | string | Yes | Target URL to analyze |
| `enumerators` | array | No | Specific enumerators to use |

**Response:**

```json
{
  "scan_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "target": "https://example.com",
  "status": "completed",
  "start_time": "2025-07-29T00:00:00.000Z",
  "end_time": "2025-07-29T00:01:30.000Z",
  "emails": ["contact@example.com"],
  "urls": ["https://example.com/about", "https://example.com/contact"],
  "endpoints": ["/api/v1/users", "/api/v1/products"],
  "keywords": ["example", "demo", "test"],
  "subdomains": ["api.example.com", "blog.example.com"],
  "ip_addresses": ["93.184.216.34"],
  "virtual_hosts": ["example.com", "www.example.com"],
  "enumeration_results": [
    {
      "enumerator_name": "web_scanner",
      "target": "https://example.com",
      "timestamp": "2025-07-29T00:00:30.000Z",
      "data_summary": {
        "keys": ["urls", "emails", "endpoints"],
        "total_items": 15
      },
      "errors": []
    }
  ]
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request (e.g., missing target) |
| 500 | Server error |

### Scans

#### GET /scans

List recent scans.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `limit` | integer | No | 100 | Maximum number of scans to return |

**Response:**

```json
{
  "scans": [
    {
      "scan_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "target": "https://example.com",
      "status": "completed",
      "start_time": "2025-07-29T00:00:00.000Z",
      "end_time": "2025-07-29T00:01:30.000Z"
    }
  ]
}
```

#### GET /scans/{scan_id}

Get a specific scan result.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scan_id` | string | Yes | Scan identifier |

**Response:**

Same as the response for POST /analyze.

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Scan not found |
| 500 | Server error |

#### DELETE /scans/{scan_id}

Delete a scan result.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scan_id` | string | Yes | Scan identifier |

**Response:**

```json
{
  "message": "Scan deleted successfully"
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Scan not found |
| 500 | Server error |

### Configuration

#### GET /config/enumerators

List available enumerators.

**Response:**

```json
{
  "enumerators": [
    {
      "name": "web_scanner",
      "description": "Scans websites for emails, URLs, and endpoints",
      "enabled": true
    },
    {
      "name": "dns_enumeration",
      "description": "Enumerates DNS records and subdomains",
      "enabled": true
    },
    {
      "name": "security_trails",
      "description": "Uses SecurityTrails API for domain intelligence",
      "enabled": true
    }
  ]
}
```

#### GET /config/storage-types

List available storage types.

**Response:**

```json
{
  "storage_types": [
    {
      "name": "file",
      "description": "File-based storage",
      "supported": true
    },
    {
      "name": "mongodb",
      "description": "MongoDB storage",
      "supported": true
    },
    {
      "name": "sql",
      "description": "SQL database storage",
      "supported": true
    }
  ]
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages in the response body:

```json
{
  "error": "Error message describing what went wrong"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. The default limits are:

- 60 requests per minute
- 1000 requests per hour

Rate limit headers are included in the response:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1627308000
```

## Pagination

List endpoints support pagination through the `limit` and `offset` query parameters:

```
GET /scans?limit=10&offset=20
```

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for the API. The allowed origins can be configured in the `.env.rest` file:

```
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Versioning

The API uses URL versioning:

```
/api/v1/analyze
```

Future versions will be available at:

```
/api/v2/analyze
```

## Examples

### cURL Examples

#### Analyze a website:

```bash
curl -X POST "http://localhost:5000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"target": "https://example.com"}'
```

#### Get a scan result:

```bash
curl -X GET "http://localhost:5000/api/v1/scans/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### List recent scans:

```bash
curl -X GET "http://localhost:5000/api/v1/scans?limit=5"
```

### Python Example

```python
import requests
import json

# Analyze a website
response = requests.post(
    "http://localhost:5000/api/v1/analyze",
    json={"target": "https://example.com"}
)
result = response.json()
scan_id = result["scan_id"]
print(f"Scan ID: {scan_id}")

# Get scan result
response = requests.get(f"http://localhost:5000/api/v1/scans/{scan_id}")
scan_result = response.json()
print(f"Found {len(scan_result['emails'])} emails")
print(f"Found {len(scan_result['subdomains'])} subdomains")
```

## Troubleshooting

### Common Issues

1. **400 Bad Request**:
   - Check that your request body is valid JSON
   - Ensure required parameters are provided

2. **404 Not Found**:
   - Verify the scan ID exists
   - Check that you're using the correct API version

3. **500 Internal Server Error**:
   - Check the server logs for details
   - Verify that all required services (MongoDB, Redis) are running

### Logging

The API logs errors and requests to the file specified in the `LOG_FILE` environment variable. Check this file for detailed error information.
