"""
Authentication middleware for MCP server.
Validates API key from Authorization header.
"""
import os
from aiohttp import web
from typing import Callable, Awaitable


class APIKeyAuthMiddleware:
    """Middleware to validate API key from Authorization header."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @web.middleware
    async def middleware(
        self, 
        request: web.Request, 
        handler: Callable[[web.Request], Awaitable[web.Response]]
    ) -> web.Response:
        """
        Validate API key from Authorization header.
        Expected format: Authorization: Bearer <API_KEY>
        """
        # Allow OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await handler(request)
        
        # Get Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        # Check if it's a Bearer token
        if not auth_header.startswith("Bearer "):
            return web.json_response(
                {"error": "Missing or invalid Authorization header. Expected: Authorization: Bearer <API_KEY>"},
                status=401
            )
        
        # Extract and validate the token
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        if token != self.api_key:
            return web.json_response(
                {"error": "Invalid API key"},
                status=401
            )
        
        # Token is valid, proceed with the request
        return await handler(request)

