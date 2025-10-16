#!/bin/bash

# MCP File System Server - Quick Start Script

set -e

echo "MCP File System Server Setup"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "WARNING: No .env file found. Creating from template..."
    
    # Create .env from inline template since env.template was deleted
    cat > .env << 'EOF'
# API key for authenticating requests to the MCP server
# Generate with: openssl rand -hex 32
API_KEY=your-secret-api-key-here

# ngrok authentication token
# Get from: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTHTOKEN=your-ngrok-authtoken-here

# Directory to expose via the file system server
# This will be mounted to /data in the container
DATA_DIRECTORY=./data

# Port for the MCP server (default: 8080)
PORT=8080
EOF
    
    echo "SUCCESS: Created .env file"
    echo ""
    echo "Please edit .env and set:"
    echo "   - API_KEY (generate with: openssl rand -hex 32)"
    echo "   - NGROK_AUTHTOKEN (get from: https://dashboard.ngrok.com/get-started/your-authtoken)"
    echo ""
    echo "After updating .env, run this script again."
    exit 1
fi

# Load .env
export $(cat .env | grep -v '^#' | xargs)

# Check if required variables are set
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your-secret-api-key-here" ]; then
    echo "ERROR: API_KEY not set in .env file"
    echo "   Generate one with: openssl rand -hex 32"
    exit 1
fi

if [ -z "$NGROK_AUTHTOKEN" ] || [ "$NGROK_AUTHTOKEN" = "your-ngrok-authtoken-here" ]; then
    echo "ERROR: NGROK_AUTHTOKEN not set in .env file"
    echo "   Get yours from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Ensure data directory exists
mkdir -p data

echo "SUCCESS: Configuration valid"
echo ""
echo "Building and starting Docker containers..."
echo ""

# Build and start
docker-compose up --build -d

echo ""
echo "SUCCESS: Containers started!"
echo ""
echo "Getting your public URL..."
sleep 3

# Try to get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "WARNING: Could not retrieve ngrok URL automatically."
    echo "   Visit http://localhost:4040 to see your public URL"
else
    echo "Your public URL: $NGROK_URL"
    echo ""
    echo "API Key: $API_KEY"
fi

echo ""
echo "View ngrok dashboard: http://localhost:4040"
echo "View logs: docker-compose logs -f"
echo "Stop server: docker-compose down"
echo ""
echo "MCP File System Server is ready!"

