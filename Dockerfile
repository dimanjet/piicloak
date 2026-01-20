# PIICloak - Production Docker Image
# Multi-stage build for optimized image size

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies globally (no --user flag needed in Docker)
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Download spaCy model
RUN python -m spacy download en_core_web_lg


# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder (global site-packages)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Copy application code
COPY src/ ./src/
COPY setup.py pyproject.toml README.md gunicorn.conf.py ./

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash piicloak && \
    chown -R piicloak:piicloak /app

USER piicloak

# Expose standard port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Environment variables with standard defaults
ENV PIICLOAK_HOST=0.0.0.0
ENV PIICLOAK_PORT=8000
ENV PIICLOAK_DEBUG=false
ENV PIICLOAK_WORKERS=4

# Run with Gunicorn for production
CMD ["gunicorn", "-c", "gunicorn.conf.py", "piicloak.app:create_application()"]
