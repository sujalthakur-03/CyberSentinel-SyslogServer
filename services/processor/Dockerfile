# Multi-stage build for Log Processor Service
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 processor && \
    chown -R processor:processor /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/processor/.local

# Copy application code
COPY --chown=processor:processor src/ ./src/

# Set environment variables
ENV PATH=/home/processor/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER processor

# Expose metrics port
EXPOSE 9101/tcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(5); s.connect(('localhost', 9101)); s.close()" || exit 1

# Run the service
WORKDIR /app/src
CMD ["python", "-u", "main.py"]
