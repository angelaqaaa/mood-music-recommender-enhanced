# Single-stage build for simplicity and reliability
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and application code
COPY requirements.txt requirements-prod.txt ./
COPY src/ ./src/
COPY *.md ./
COPY pyproject.toml ./

# Create data directory and copy real data files for production use
COPY data/ ./data/

# Install Python dependencies globally
RUN pip install --no-cache-dir -r requirements-prod.txt

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PORT=8040

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port (will be set by platform)
EXPOSE 8040

# Command to run the application as a module (try real data first, fallback to sample)
CMD ["python", "-m", "src.musicrec.main", "--port", "8040"]