# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better caching
COPY pyproject.toml .
COPY requirements.txt .

# Install dependencies using uv (much faster than pip)
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY server.py .
COPY auth_middleware.py .

# Create data directory
RUN mkdir -p /data

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python", "server.py"]

