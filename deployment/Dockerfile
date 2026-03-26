FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY config/production_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r production_requirements.txt

# Copy application source code
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/

# Copy main entry points
COPY main.py .
COPY quick_test.py .

# Create necessary directories
RUN mkdir -p uploads logs

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "src.backend.app.production_app:app"]
