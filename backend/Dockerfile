# Backend Dockerfile for Downloadix
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install ffmpeg, curl (for healthcheck) and other dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p /app/downloads

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV DOWNLOAD_FOLDER=/app/downloads

# Expose port
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application with gunicorn for production
# --workers 1 is required because we use in-memory state for download tracking
# --threads 8 provides concurrency within the single process
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--timeout", "300", "app:app"]
