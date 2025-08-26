# Multi-stage build for optimized Docker image
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV UV_SYSTEM_PYTHON=1
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache --no-dev

# Development stage
FROM base as development

# Install dev dependencies
RUN uv sync --frozen --no-cache --all-extras --dev

# Copy source code
COPY . .

# Run linting and tests
RUN uv run ruff check .
RUN uv run ruff format --check .
RUN uv run pytest -xvs

# Production stage
FROM base as production

# Copy source code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Create necessary directories
RUN mkdir -p logs audio projects

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port (if needed for webhooks)
EXPOSE 8080

# Run the application
CMD ["uv", "run", "python", "main.py"]