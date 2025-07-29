# Multi-stage build for optimized site_analyzer Docker image
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements_refactored.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_refactored.txt

# Development stage
FROM python:3.12-slim AS development

# Install development dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    git \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install development tools
RUN pip install --no-cache-dir debugpy pytest pytest-cov

# Create necessary directories
RUN mkdir -p /app/data/scans /app/data/screenshots /app/logs

# Install Playwright browsers (Chromium only)
RUN playwright install chromium --with-deps

# Set default environment variables
ENV PYTHONPATH=/app
ENV STORAGE_TYPE=file
ENV HEADLESS=true
ENV LOG_LEVEL=DEBUG
ENV DEBUG=true

# Expose ports (including debugger port)
EXPOSE 5000 50051 5678 5679

# Production stage
FROM python:3.12-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app user for security
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/scans /app/data/screenshots /app/logs && \
    chown -R appuser:appgroup /app/data /app/logs

# Install Playwright browsers (Chromium only)
RUN playwright install chromium --with-deps

# Switch to non-root user
USER appuser

# Set default environment variables
ENV PYTHONPATH=/app
ENV STORAGE_TYPE=file
ENV HEADLESS=true
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "main_refactored.py", "rest"]

# Expose ports
EXPOSE 5000 50051
