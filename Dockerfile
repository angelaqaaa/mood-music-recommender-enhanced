# Multi-stage build for smaller production image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir --user -r requirements-prod.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY *.md ./
COPY pyproject.toml ./

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Make sure Python packages are in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port (will be set by platform)
EXPOSE 8040

# Command to run the application
CMD ["python", "src/musicrec/main.py", "--port", "8040", "--sample"]