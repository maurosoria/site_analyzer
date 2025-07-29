# Multi-stage build for optimized site_analyzer Docker image
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    build-base

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements_refactored.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_refactored.txt

# Development stage
FROM python:3.12-alpine AS development

# Install development dependencies for Playwright and Chromium
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    nodejs \
    npm \
    bash \
    curl \
    git

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set Playwright to use system Chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install development tools
RUN pip install --no-cache-dir debugpy pytest pytest-cov

# Create necessary directories
RUN mkdir -p /app/data/scans /app/data/screenshots /app/logs

# Install Playwright browsers (Chromium only)
RUN playwright install chromium --with-deps || true

# Set default environment variables
ENV PYTHONPATH=/app
ENV STORAGE_TYPE=file
ENV HEADLESS=true
ENV LOG_LEVEL=DEBUG
ENV DEBUG=true

# Expose ports (including debugger port)
EXPOSE 5000 50051 5678 5679

# Production stage
FROM python:3.12-alpine AS production

# Install runtime dependencies for Playwright and Chromium
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    nodejs \
    npm

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set Playwright to use system Chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Create app user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/scans /app/data/screenshots /app/logs && \
    chown -R appuser:appgroup /app/data /app/logs

# Install Playwright browsers (Chromium only)
RUN playwright install chromium --with-deps || true

# Switch to non-root user
USER appuser

# Set default environment variables
ENV PYTHONPATH=/app
ENV STORAGE_TYPE=file
ENV HEADLESS=true
ENV LOG_LEVEL=INFO

# Health check script
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "main_refactored.py", "rest"]

# Expose ports
EXPOSE 5000 50051
