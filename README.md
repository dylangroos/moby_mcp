# MCP File System Server

A Docker-containerized MCP (Model Context Protocol) server that exposes file system operations over HTTPS via ngrok with API key authentication.

## Features

- Full file system access (read, write, list, delete, mkdir)
- API key authentication
- Public HTTPS access via ngrok
- Docker containerized
- Fast dependency management with uv

## Quick Start

1. **Copy and configure environment file:**
   ```bash
   # The start.sh script will create .env if it doesn't exist
   ./start.sh
   ```

2. **Edit `.env` file:**
   ```bash
   # Generate API key
   openssl rand -hex 32
   
   # Get ngrok token from: https://dashboard.ngrok.com/get-started/your-authtoken
   # Add both to .env file
   ```

3. **Start the server:**
   ```bash
   ./start.sh
   ```

4. **Test it:**
   ```bash
   ./test_server.sh
   ```

## Architecture

```
Web Client --HTTPS--> ngrok --HTTP--> MCP Server ---> /data volume
                                (with auth)
```

## Available Operations

- `read_file(path)` - Read file contents
- `write_file(path, content)` - Create/update files
- `list_directory(path)` - List directory contents
- `delete_file(path)` - Delete files
- `create_directory(path)` - Create directories

All operations are relative to the `./data` directory.

## Configuration

Required environment variables in `.env`:

```
API_KEY=your-secret-api-key-here
NGROK_AUTHTOKEN=your-ngrok-authtoken-here
DATA_DIRECTORY=./data
```

## Usage from MCP Client

Configure your MCP client with:

```json
{
  "name": "filesystem-server",
  "transport": {
    "type": "sse",
    "url": "https://your-ngrok-url.ngrok.io/sse"
  },
  "headers": {
    "Authorization": "Bearer your-api-key"
  }
}
```

## Development

Run locally without Docker:

```bash
./dev.sh
```

This will:
- Install uv if needed
- Set up virtual environment
- Install dependencies
- Run server on http://localhost:8080

## Technology Stack

- **Python 3.11+** - Modern async Python
- **uv** - Fast Python package manager (10-100x faster than pip)
- **MCP SDK** - Official Model Context Protocol implementation
- **aiohttp** - Async HTTP server for SSE transport
- **Docker** - Containerization
- **ngrok** - Secure public tunneling

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop server
docker-compose down

# Restart server
docker-compose restart

# View ngrok dashboard
open http://localhost:4040

# Rebuild after changes
docker-compose up --build
```

## Security Notes

- Keep your API key secret
- Only mount directories you want to expose
- Path traversal protection is implemented
- ngrok free tier provides random URLs that change on restart

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
