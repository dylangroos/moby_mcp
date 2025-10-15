#!/bin/bash

# Development script for running server locally with uv

set -e

echo "MCP File Server - Development Mode"
echo "====================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "WARNING: uv is not installed. Installing now..."
    echo ""
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
    echo "SUCCESS: uv installed! Please restart your shell or run:"
    echo "   source $HOME/.cargo/env"
    echo ""
    echo "Then run this script again."
    exit 0
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "WARNING: No .env file found. Creating from template..."
    
    # Create .env from inline template
    cat > .env << 'EOF'
# API key for authenticating requests to the MCP server
# Generate with: openssl rand -hex 32
API_KEY=your-secret-api-key-here

# ngrok authentication token (not needed for local dev)
NGROK_AUTHTOKEN=your-ngrok-authtoken-here

# Directory to expose via the file system server
DATA_DIRECTORY=./data
EOF
    
    echo "SUCCESS: Created .env file"
    echo ""
    echo "Please edit .env and set:"
    echo "   - API_KEY (generate with: openssl rand -hex 32)"
    echo ""
    echo "Note: ngrok is not needed for local development."
    echo "      The server will run on http://localhost:8000"
    echo ""
fi

# Load .env
export $(cat .env | grep -v '^#' | grep -v 'NGROK' | xargs)

# Check if API_KEY is set
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-secret-api-key-here" ]; then
    echo "ERROR: API_KEY not set in .env file"
    echo "   Generate one with: openssl rand -hex 32"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv
    echo "SUCCESS: Virtual environment created"
    echo ""
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies with uv (this is fast!)..."
uv pip install -r requirements.txt
echo "SUCCESS: Dependencies installed"
echo ""

# Override BASE_DIR for local development
export PORT=8000

echo "Starting server..."
echo "   URL: http://localhost:8000"
echo "   API Key: $API_KEY"
echo "   Data directory: $(pwd)/data"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the server (modify BASE_DIR in the Python script)
# For local dev, we'll use the local data directory
python -c "
import os
import sys
from pathlib import Path

# Override BASE_DIR for local development
import server
server.BASE_DIR = Path('data').resolve()

# Run main
import asyncio
asyncio.run(server.main())
"

