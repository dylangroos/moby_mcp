# Moby MCP Server

A Docker-containerized MCP (Model Context Protocol) server that exposes file system operations over HTTPS via ngrok with API key authentication. Named after Docker's Moby project, it provides a simple filesystem interface for MCP clients. Built with FastMCP.

## Features

- File system access (read, write, list, delete) for .txt and .md files only
- Simple API key authentication
- Public HTTPS access via ngrok
- Docker containerized
- Fast dependency management with uv
- Streamable HTTP transport

## Quick Start

```bash
# 1. Generate an API key
make generate-key

# 2. Create .env file and add your API_KEY and NGROK_AUTHTOKEN
# (See Configuration section below)

# 3. Start the server
make start

# 4. View logs and get your public URL
make logs

# 5. Your server is live! Check http://localhost:4040 for the ngrok URL
```

## Architecture

```
MCP Client --HTTPS--> ngrok --HTTP--> FastMCP Server ---> /data volume
                                (API key auth)
```

## Available Operations

- `read_file(path)` - Read file contents (.txt and .md only)
- `write_file(path, content)` - Create/update files (.txt and .md only)
- `list_directory(path)` - List directory contents (shows only .txt and .md files)
- `delete_file(path)` - Delete files (.txt and .md only)

All operations are relative to the `./data` directory. Only `.txt` and `.md` file types are allowed for security.

## Configuration

Required environment variables in `.env`:

```bash
# Generate with: make generate-key
API_KEY=your-secret-api-key-here

# Get from: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTHTOKEN=your-ngrok-authtoken-here

# Local directory to expose (mounted to /data in container)
DATA_DIRECTORY=./data

# Server port (default: 8080)
PORT=8080
```

**Quick setup:**
```bash
# Generate a secure API key
make generate-key

# Edit .env and add your API_KEY and NGROK_AUTHTOKEN
# Then start the server
make start
```

## Usage from MCP Client

Configure your MCP client with:

```json
{
  "name": "moby",
  "transport": {
    "type": "http",
    "url": "https://your-ngrok-url.ngrok-free.app/mcp"
  },
  "headers": {
    "Authorization": "Bearer your-api-key-here"
  }
}
```

**Important:** The Authorization header must be exactly `Bearer <your-api-key>` with no extra quotes or colons.

## Development

Run locally without Docker:

```bash
make dev
# or
./dev.sh
```

This will:
- Install uv if needed
- Set up virtual environment
- Install dependencies
- Run server on http://localhost:8080

## Technology Stack

- **Python 3.11+** - Modern async Python
- **FastMCP** - Pythonic MCP server framework
- **uv** - Fast Python package manager (10-100x faster than pip)
- **MCP SDK** - Official Model Context Protocol implementation
- **Docker** - Containerization
- **ngrok** - Secure public tunneling

## Makefile Commands

All server operations are managed through simple Makefile targets:

```bash
make help          # Show all available commands
make generate-key  # Generate a new random API key
make start         # Start the Docker containers
make stop          # Stop the Docker containers
make restart       # Restart the Docker containers
make logs          # View server logs (follow mode)
make shell         # Open a shell inside the container
make build         # Rebuild Docker images
make dev           # Run in local development mode (no Docker)
make clean         # Remove containers and volumes
```

**Useful links:**
```bash
# View ngrok dashboard (shows your public URL)
open http://localhost:4040
```

## Security Notes

- **Keep your API key secret** - Never commit `.env` to git
- **File type restrictions** - Only `.txt` and `.md` files can be accessed
- **Path traversal protection** - Prevents access outside the data directory
- **Generate strong keys** - Use `make generate-key` for cryptographically secure API keys
- **ngrok URLs** - Free tier provides random URLs that change on restart
- **Directory access** - Only mount directories you want to expose

## Troubleshooting

**Authentication errors:**
- Verify API key is correct in .env
- Ensure header format: `Authorization: Bearer <API_KEY>`

**ngrok connection failed:**
- Verify NGROK_AUTHTOKEN is correct
- Check ngrok dashboard for account status

**File access errors:**
- Verify DATA_DIRECTORY exists and has proper permissions
- Check Docker has access to the directory

## License

MIT License
