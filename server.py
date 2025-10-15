"""
MCP File System Server
Exposes file system operations via MCP protocol over HTTP.
"""
import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path("/data")  # Base directory for file operations (Docker volume)
PORT = int(os.getenv("PORT", "8000"))

# Allowed file extensions
ALLOWED_EXTENSIONS = {".txt", ".json"}

# Initialize FastMCP server
# Note: Authentication can be added via reverse proxy (nginx, Caddy, etc.)
mcp = FastMCP(name="filesystem-server")


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


def validate_file_type(path: Path) -> None:
    """
    Validate that the file has an allowed extension.
    Raises ValueError if the file type is not allowed.
    """
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        raise ValueError(f"File type '{path.suffix}' not allowed. Only {allowed} files are permitted")


@mcp.tool(
    name="read_file",
    description="Read the contents of a file (only .txt and .json files allowed)",
)
def read_file(path: str) -> Dict[str, Any]:
    """Read a file and return its contents"""
    try:
        file_path = validate_path(path)
        validate_file_type(file_path)
        
        if not file_path.exists():
            return {"error": f"File '{path}' does not exist"}
        
        if not file_path.is_file():
            return {"error": f"'{path}' is not a file"}
        
        content = file_path.read_text()
        return {
            "success": True,
            "path": path,
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="write_file",
    description="Write content to a file (creates or overwrites, only .txt and .json files allowed)",
)
def write_file(path: str, content: str) -> Dict[str, Any]:
    """Write content to a file"""
    try:
        file_path = validate_path(path)
        validate_file_type(file_path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        file_path.write_text(content)
        
        return {
            "success": True,
            "path": path,
            "size": len(content),
            "message": f"Successfully wrote {len(content)} characters to '{path}'"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="list_directory",
    description="List contents of a directory (only shows .txt and .json files)",
)
def list_directory(path: str = "") -> Dict[str, Any]:
    """List directory contents"""
    try:
        dir_path = validate_path(path)
        
        if not dir_path.exists():
            return {"error": f"Directory '{path}' does not exist"}
        
        if not dir_path.is_dir():
            return {"error": f"'{path}' is not a directory"}
        
        # List directory contents (only show allowed file types)
        items = []
        for item in sorted(dir_path.iterdir()):
            if item.is_dir():
                rel_path = str(item.relative_to(BASE_DIR))
                items.append({"type": "dir", "path": rel_path})
            elif item.suffix.lower() in ALLOWED_EXTENSIONS:
                rel_path = str(item.relative_to(BASE_DIR))
                items.append({"type": "file", "path": rel_path})
        
        return {
            "success": True,
            "path": path if path else "/",
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="delete_file",
    description="Delete a file (only .txt and .json files allowed)",
)
def delete_file(path: str) -> Dict[str, Any]:
    """Delete a file"""
    try:
        file_path = validate_path(path)
        validate_file_type(file_path)
        
        if not file_path.exists():
            return {"error": f"File '{path}' does not exist"}
        
        if not file_path.is_file():
            return {"error": f"'{path}' is not a file"}
        
        file_path.unlink()
        
        return {
            "success": True,
            "path": path,
            "message": f"Successfully deleted '{path}'"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="create_directory",
    description="Create a directory (including parent directories)",
)
def create_directory(path: str) -> Dict[str, Any]:
    """Create a directory"""
    try:
        dir_path = validate_path(path)
        
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": path,
            "message": f"Successfully created directory '{path}'"
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Ensure BASE_DIR exists
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting MCP File System Server")
    print(f"Port: {PORT}")
    print(f"Base directory: {BASE_DIR}")
    print(f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"Note: Add authentication via reverse proxy for production use")
    
    # Run with HTTP transport
    mcp.run(transport="http", host="0.0.0.0", port=PORT, path="/mcp")
