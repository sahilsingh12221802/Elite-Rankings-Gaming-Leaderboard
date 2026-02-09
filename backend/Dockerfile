# Backend Dockerfile - Production-grade Python application
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/opt/python -r requirements.txt

# Final runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /opt/python /opt/python
ENV PATH=/opt/python/bin:$PATH
ENV PYTHONPATH=/opt/python/lib/python3.11/site-packages:$PYTHONPATH

# Copy application code
COPY backend/app ./app
COPY backend/migrations ./migrations

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /opt/python
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

EXPOSE 8000
