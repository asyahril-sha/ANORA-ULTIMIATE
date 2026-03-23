# AMORIA - Virtual Human dengan Jiwa
# Dockerfile optimized for Railway

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Jakarta \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies (minimal, tanpa Rust)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create required directories
RUN mkdir -p data/logs data/backups data/sessions data/vector_db data/memory

# Create non-root user for security (like MYLOVE)
RUN useradd -m -u 1000 amoria && chown -R amoria:amoria /app
USER amoria

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the bot (using run_deploy.py for Railway deployment)
CMD ["python", "run_deploy.py"]
