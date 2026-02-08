# Multi-stage Dockerfile for optimized production deployment
# Validates Requirements: 10.1, 10.2, 10.3, 10.4, 10.5

# Stage 1: Builder
# Use Python slim image for smaller base
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
# Use minimal Alpine Linux image for smallest final size
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install runtime dependencies and healthcheck tool
RUN apk add --no-cache \
    libpq \
    libstdc++ \
    curl \
    && rm -rf /var/cache/apk/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Create non-root user for security and create log file
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app && \
    touch app.log && chown appuser:appuser app.log

USER appuser

# Health check using curl (installed above) since requests module might not be present or we want to avoid python startup overhead
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
