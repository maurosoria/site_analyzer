# Docker Setup for Site Analyzer

This document provides instructions for setting up and running the Site Analyzer using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10.0 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0.0 or higher)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/maurosoria/site_analyzer.git
   cd site_analyzer
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env.rest
   cp .env.example .env.grpc
   cp .env.example .env.cli
   ```

3. Edit the environment files to add your API keys:
   ```bash
   # Add your API keys to each .env file
   GEMINI_API_KEY=your-gemini-api-key
   SECURITY_TRAILS_API_KEY=your-security-trails-api-key
   CAPSOLVER_API_KEY=your-capsolver-api-key
   ```

4. Start the services:
   ```bash
   docker-compose up -d
   ```

5. Access the services:
   - REST API: http://localhost:5000/docs/ (Swagger UI)
   - gRPC: localhost:50051 (Use a gRPC client)

## Available Services

The Docker Compose setup includes the following services:

### 1. REST API Service (`site-analyzer-rest`)

A Flask-based REST API with Swagger documentation.

- **Port**: 5000
- **Documentation**: http://localhost:5000/docs/
- **Environment**: `.env.rest`

### 2. gRPC Service (`site-analyzer-grpc`)

A gRPC server for efficient binary communication.

- **Port**: 50051
- **Environment**: `.env.grpc`
- **Client Example**: See `examples/grpc_client_example.py`

### 3. CLI Service (`site-analyzer-cli`)

A command-line interface for batch operations.

- **Environment**: `.env.cli`
- **Usage**: `docker-compose exec site-analyzer-cli python main_refactored.py --target example.com`

### 4. MongoDB (Storage Backend)

- **Port**: 27017 (internal)
- **Credentials**: admin/password123 (default, change in production)
- **Data Volume**: `./data/mongodb`

### 5. Redis (Optional Caching)

- **Port**: 6379 (internal)
- **Data Volume**: `./data/redis`

## Environment Variables

Each service uses its own environment file:

- `.env.rest` - Configuration for the REST API service
- `.env.grpc` - Configuration for the gRPC service
- `.env.cli` - Configuration for the CLI service

See the [Environment Variables Reference](#environment-variables-reference) section for details on available options.

## Volume Mounts

The Docker Compose setup uses the following volumes:

- `./data/scans`: Shared storage for scan results
- `./data/screenshots`: Storage for screenshots
- `./data/mongodb`: MongoDB data persistence
- `./data/redis`: Redis data persistence
- `./logs`: Application logs

## Environment Variables Reference

### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REST_PORT` | Port for REST API | 5000 | No |
| `GRPC_PORT` | Port for gRPC server | 50051 | No |
| `STORAGE_TYPE` | Storage backend (file, mongodb, sql) | file | No |
| `STORAGE_DIRECTORY` | Directory for file storage | ./data/scans | No |
| `MONGODB_URL` | MongoDB connection URL | mongodb://admin:password123@mongodb:27017/site_analyzer | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `LOG_FILE` | Log file path | ./logs/site_analyzer.log | No |

### Browser Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HEADLESS` | Run browser in headless mode | true | No |
| `TIMEOUT` | Browser timeout in milliseconds | 30000 | No |

### API Keys

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | Yes |
| `SECURITY_TRAILS_API_KEY` | SecurityTrails API key | - | Yes |
| `CAPSOLVER_API_KEY` | CapSolver API key | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - | No |
| `AWS_BEDROCK_URL` | AWS Bedrock URL (optional) | - | No |

### LLM Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | LLM provider (gemini, openai, bedrock) | gemini | No |
| `LLM_MODEL` | Model name | gemini-2.0-flash-exp | No |

### Performance Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MAX_CONCURRENT_SCANS` | Maximum concurrent scans | 5 | No |
| `SCAN_TIMEOUT` | Scan timeout in seconds | 300 | No |

## Custom Docker Compose Configurations

### Development Setup

For development, you can use the `docker-compose.dev.yml` file:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This configuration:
- Mounts the source code as a volume for live reloading
- Enables debug mode for the services
- Exposes additional ports for debugging

### Production Setup

For production, use the `docker-compose.prod.yml` file:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

This configuration:
- Uses optimized build settings
- Configures proper resource limits
- Sets up health checks and restart policies

## Troubleshooting

### Common Issues

1. **Services fail to start**:
   - Check the logs: `docker-compose logs <service-name>`
   - Verify API keys in environment files
   - Ensure ports are not already in use

2. **MongoDB connection issues**:
   - Check MongoDB logs: `docker-compose logs mongodb`
   - Verify MongoDB URL in environment files
   - Check if MongoDB data directory has proper permissions

3. **Browser automation issues**:
   - Ensure Playwright is properly installed in the container
   - Check if the browser can run in headless mode
   - Increase browser timeout if needed

### Viewing Logs

```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs site-analyzer-rest

# Follow logs in real-time
docker-compose logs -f site-analyzer-grpc
```

## Advanced Configuration

### Custom Network Configuration

To use a custom network:

```yaml
# docker-compose.custom.yml
networks:
  site-analyzer-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Using External Services

To use external MongoDB or Redis instances:

```yaml
# docker-compose.external.yml
services:
  site-analyzer-rest:
    environment:
      - MONGODB_URL=mongodb://user:pass@external-mongodb:27017/site_analyzer
      - REDIS_URL=redis://external-redis:6379/0
```

## Security Considerations

For production deployments:

1. **Change default credentials**:
   - Update MongoDB and Redis passwords
   - Use environment variables for sensitive information

2. **Secure network access**:
   - Use a reverse proxy (e.g., Nginx) with HTTPS
   - Implement proper firewall rules
   - Consider using Docker Swarm or Kubernetes for advanced security features

3. **Limit resource usage**:
   - Set memory and CPU limits for containers
   - Monitor resource usage to prevent DoS attacks
