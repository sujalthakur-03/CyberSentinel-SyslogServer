# Multi-stage build for Alerting Service
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
RUN useradd -m -u 1000 alerting && \
    chown -R alerting:alerting /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/alerting/.local

# Copy application code
COPY --chown=alerting:alerting src/ ./src/

# Set environment variables
ENV PATH=/home/alerting/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER alerting

# Expose metrics port
EXPOSE 9103/tcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(5); s.connect(('localhost', 9103)); s.close()" || exit 1

# Run the service
WORKDIR /app/src
CMD ["python", "-u", "main.py"]
