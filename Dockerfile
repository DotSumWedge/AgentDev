# Phase 1: Basic Development Container
FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV DEV_MODE=true
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/src /app/logs /app/data && \
    chown -R appuser:appuser /app

# Copy health check script
COPY health_check.py .

# Switch to non-root user
USER appuser

# Expose port for development server
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python health_check.py

# Default command
CMD ["python", "-m", "http.server", "8000", "--directory", "/app"]