# Ticket Service Dockerfile
# Multi-stage build for optimal image size
# Reference: /backend/ticket/README.md

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.11-slim

# Create non-root user first
RUN useradd -m -u 1000 ticketuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/ticketuser/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder to ticketuser's home
COPY --from=builder --chown=ticketuser:ticketuser /root/.local /home/ticketuser/.local

# Copy application code
COPY --chown=ticketuser:ticketuser . .

# Create upload directories with proper permissions
RUN mkdir -p /app/uploads && \
    chown -R ticketuser:ticketuser /app/uploads && \
    chmod 755 /app/uploads

# Switch to non-root user
USER ticketuser

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
