.PHONY: help generate-key start stop restart logs build dev clean shell

help:
	@echo "Moby MCP Server - Available Commands:"
	@echo ""
	@echo "  make generate-key  - Generate a new random API key"
	@echo "  make start         - Start the Docker containers"
	@echo "  make stop          - Stop the Docker containers"
	@echo "  make restart       - Restart the Docker containers"
	@echo "  make logs          - View server logs"
	@echo "  make shell         - Open a shell inside the container"
	@echo "  make build         - Rebuild Docker images"
	@echo "  make dev           - Run in local development mode"
	@echo "  make clean         - Remove containers and volumes"
	@echo ""

generate-key:
	@echo "Generating new API key..."
	@python3 -c "import secrets; print(secrets.token_hex(32))"
	@echo ""
	@echo "Add this to your .env file as:"
	@echo "API_KEY=<generated_key_above>"

start:
	@echo "Starting MCP server..."
	docker compose up -d
	@echo "Server started!"
	@echo "Check logs with: make logs"

stop:
	@echo "Stopping MCP server..."
	docker compose down
	@echo "Server stopped!"

restart:
	@echo "Restarting MCP server..."
	docker compose restart
	@echo "Server restarted!"

logs:
	docker compose logs -f mcp-server

shell:
	@echo "Opening shell in mcp-server container..."
	docker compose exec mcp-server /bin/bash

build:
	@echo "Building MCP server..."
	docker compose up --build -d
	@echo "Build complete!"

dev:
	@echo "Starting local development server..."
	./dev.sh

clean:
	@echo "Cleaning up containers and volumes..."
	docker compose down -v
	@echo "Cleanup complete!"

