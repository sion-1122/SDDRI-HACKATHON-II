# Multi-stage Dockerfile for FastAPI Backend
# Stage 1: Builder stage - Install dependencies with UV
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies and UV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

# Copy pyproject.toml, uv.lock, and src directory for package build
COPY pyproject.toml ./
COPY uv.lock ./
COPY src/ src/

# Install dependencies to a temporary location (use --no-editable to avoid symlinks)
RUN uv sync --no-dev --no-editable

# Stage 2: Production stage - Copy dependencies and run application
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Create non-root user
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser -s /sbin/nologin -d /app -m appuser

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
