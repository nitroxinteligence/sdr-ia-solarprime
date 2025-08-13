# Build stage
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    tesseract-ocr \
    tesseract-ocr-por \
    ffmpeg \
    poppler-utils \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Setup NLTK data (download punkt tokenizer for sentence splitting)
# SIMPLES: Pre-download para evitar download em runtime - apenas punkt padrão
RUN python -c "import nltk; nltk.download('punkt', quiet=True)" || true

# Clean Python cache to force fresh imports
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete 2>/dev/null || true && \
    find . -type f -name "*.pyo" -delete 2>/dev/null || true && \
    rm -rf /root/.cache/pip/* 2>/dev/null || true && \
    python -c "import py_compile; import compileall; compileall.compile_dir('/app', force=True)" || true

# Copy .env file if exists (can be overridden by docker-compose volume)
# Using shell to handle if file doesn't exist
RUN if [ -f .env ]; then cp .env /app/.env; fi

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/temp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]