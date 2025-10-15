"""
MCP File System Server
Exposes file system operations via MCP protocol over SSE/HTTP.
"""
import os
import asyncio
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from aiohttp import web

from auth_middleware import APIKeyAuthMiddleware

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path("/data")  # Base directory for file operations (Docker volume)
API_KEY = os.getenv("API_KEY", "")
PORT = int(os.getenv("PORT", "8000"))

# Validate configuration
if not API_KEY:
    raise ValueError("API_KEY environment variable must be set")

# Create MCP server
mcp_server = Server("filesystem-server")


def validate_path(path: str) -> Path:
    """
    Validate and normalize a path to prevent directory traversal attacks.
    Returns absolute path within BASE_DIR.
    """
    # Remove leading slash if present
    path = path.lstrip("/")
    
    # Resolve the full path
    full_path = (BASE_DIR / path).resolve()
    
    # Ensure the path is within BASE_DIR
    if not str(full_path).startswith(str(BASE_DIR.resolve())):
        raise ValueError(f"Path '{path}' is outside the allowed directory")
    
    return full_path


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available file system tools."""
    return [
        Tool(
            name="read_file",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read (relative to base directory)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a file (creates or overwrites)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write (relative to base directory)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list (relative to base directory, empty string for root)",
                        "default": ""
                    }
                }
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to delete (relative to base directory)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="create_directory",
            description="Create a directory (including parent directories)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to create (relative to base directory)"
                    }
                },
                "required": ["path"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "read_file":
            path = validate_path(arguments["path"])
            
            if not path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: File '{arguments['path']}' does not exist"
                )]
            
            if not path.is_file():
                return [TextContent(
                    type="text",
                    text=f"Error: '{arguments['path']}' is not a file"
                )]
            
            content = path.read_text()
            return [TextContent(
                type="text",
                text=content
            )]
        
        elif name == "write_file":
            path = validate_path(arguments["path"])
            content = arguments["content"]
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            path.write_text(content)
            
            return [TextContent(
                type="text",
                text=f"Successfully wrote {len(content)} characters to '{arguments['path']}'"
            )]
        
        elif name == "list_directory":
            path = validate_path(arguments.get("path", ""))
            
            if not path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: Directory '{arguments.get('path', '')}' does not exist"
                )]
            
            if not path.is_dir():
                return [TextContent(
                    type="text",
                    text=f"Error: '{arguments.get('path', '')}' is not a directory"
                )]
            
            # List directory contents
            items = []
            for item in sorted(path.iterdir()):
                item_type = "dir" if item.is_dir() else "file"
                rel_path = item.relative_to(BASE_DIR)
                items.append(f"[{item_type}] {rel_path}")
            
            if not items:
                result = f"Directory '{arguments.get('path', '/')}' is empty"
            else:
                result = f"Contents of '{arguments.get('path', '/')}':\n" + "\n".join(items)
            
            return [TextContent(
                type="text",
                text=result
            )]
        
        elif name == "delete_file":
            path = validate_path(arguments["path"])
            
            if not path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: File '{arguments['path']}' does not exist"
                )]
            
            if not path.is_file():
                return [TextContent(
                    type="text",
                    text=f"Error: '{arguments['path']}' is not a file"
                )]
            
            path.unlink()
            
            return [TextContent(
                type="text",
                text=f"Successfully deleted '{arguments['path']}'"
            )]
        
        elif name == "create_directory":
            path = validate_path(arguments["path"])
            
            path.mkdir(parents=True, exist_ok=True)
            
            return [TextContent(
                type="text",
                text=f"Successfully created directory '{arguments['path']}'"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
    
    except ValueError as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def handle_sse(request: web.Request) -> web.Response:
    """Handle SSE connections for MCP."""
    async with SseServerTransport("/messages") as transport:
        await mcp_server.run(
            transport.read_stream,
            transport.write_stream,
            mcp_server.create_initialization_options()
        )
    return web.Response()


async def handle_messages(request: web.Request) -> web.Response:
    """Handle MCP messages via POST."""
    try:
        data = await request.json()
        # Process MCP message
        # This is handled by the SSE transport
        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


def create_app() -> web.Application:
    """Create and configure the aiohttp application."""
    # Create auth middleware
    auth = APIKeyAuthMiddleware(API_KEY)
    
    # Create app with middleware
    app = web.Application(middlewares=[auth.middleware])
    
    # Add CORS middleware for web clients
    @web.middleware
    async def cors_middleware(request: web.Request, handler):
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    
    # Insert CORS middleware before auth middleware
    app.middlewares.insert(0, cors_middleware)
    
    # Add routes
    app.router.add_get("/sse", handle_sse)
    app.router.add_post("/messages", handle_messages)
    app.router.add_get("/health", lambda _: web.json_response({"status": "healthy"}))
    
    return app


async def main():
    """Main entry point."""
    # Ensure BASE_DIR exists
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting MCP File System Server on port {PORT}")
    print(f"Base directory: {BASE_DIR}")
    print(f"Authentication: API Key required")
    
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    print(f"Server running at http://0.0.0.0:{PORT}")
    print("Waiting for connections...")
    
    # Keep the server running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

