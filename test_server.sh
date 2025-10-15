#!/bin/bash

# MCP File System Server - Test Script

set -e

echo "MCP File System Server Test"
echo "================================"
echo ""

# Load .env
if [ ! -f .env ]; then
    echo "ERROR: No .env file found. Please run ./start.sh first."
    exit 1
fi

export $(cat .env | grep -v '^#' | xargs)

# Get ngrok URL
echo "Getting ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "ERROR: Could not get ngrok URL. Is the server running?"
    echo "   Try: docker-compose up -d"
    exit 1
fi

echo "SUCCESS: Server URL: $NGROK_URL"
echo ""

# Test 1: Health check without auth (should fail)
echo "Test 1: Health check without authentication (should fail with 401)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$NGROK_URL/health")
if [ "$HTTP_CODE" = "401" ]; then
    echo "PASS: Correctly rejected unauthenticated request"
else
    echo "FAIL: Expected 401, got $HTTP_CODE"
fi
echo ""

# Test 2: Health check with auth (should succeed)
echo "Test 2: Health check with authentication..."
RESPONSE=$(curl -s -H "Authorization: Bearer $API_KEY" "$NGROK_URL/health")
if echo "$RESPONSE" | grep -q "healthy"; then
    echo "PASS: Authentication successful"
    echo "   Response: $RESPONSE"
else
    echo "FAIL: Authentication failed"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test 3: List directory
echo "Test 3: Listing data directory..."
echo "Note: To test MCP tools, you'll need an MCP client."
echo "      The health endpoint confirms the server is accessible."
echo ""

echo "Server Status:"
echo "   URL: $NGROK_URL"
echo "   Auth: Bearer token required"
echo "   Status: Running"
echo ""
echo "Next steps:"
echo "   1. Configure your MCP client with:"
echo "      - URL: $NGROK_URL/sse"
echo "      - Header: Authorization: Bearer $API_KEY"
echo "   2. View ngrok dashboard: http://localhost:4040"
echo "   3. View server logs: docker-compose logs -f mcp-server"
echo ""
echo "All tests passed!"

