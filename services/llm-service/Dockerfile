# LLM Service Dockerfile with GPU support - Multi-stage Optimized
# Stage 1: Builder
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04 AS builder

# Set environment variables for compilation
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    python3-dev \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Create virtual environment to isolate dependencies
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
COPY services/llm-service/requirements.txt .

# Use BuildKit cache mount and pre-compiled wheels for faster installation
# Using abetlen's pre-compiled wheels for llama-cpp-python with CUDA support
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --no-cache-dir --prefix=/install \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121 \
    -r requirements.txt

# Stage 2: Runtime
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install runtime dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY services/llm-service/src ./src

# Create models and logs directory
RUN mkdir -p /app/models /app/logs

# Expose port
EXPOSE 8000

# Environment variables
ENV SERVICE_NAME=llm-service
ENV PORT=8000
ENV MODELS_DIR=/app/models

# Health check using curl
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the service
CMD ["python3.11", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
