"""
Authentication middleware for ANAL framework.

This module provides middleware for handling authentication and authorization.
"""

from datetime import datetime
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from .backends import get_auth_manager, PermissionChecker
from .models import User


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add user authentication."""
        # Initialize user as None
        request.state.user = None
        request.state.is_authenticated = False
        
        # Try to authenticate user
        user = await self._authenticate_request(request)
        if user:
            request.state.user = user
            request.state.is_authenticated = True
            request.state.permission_checker = PermissionChecker(user)
        
        response = await call_next(request)
        return response
    
    async def _authenticate_request(self, request: Request) -> Optional[User]:
        """Authenticate request using various methods."""
        auth_manager = get_auth_manager()
        
        # Try session authentication
        session_key = request.cookies.get('sessionid')
        if session_key:
            user = await auth_manager.authenticate(session_key=session_key)
            if user:
                return user
        
        # Try token authentication
        authorization = request.headers.get('Authorization')
        if authorization and authorization.startswith('Bearer '):
            token = authorization.split(' ')[1]
            user = await auth_manager.authenticate(token=token)
            if user:
                return user
        
        # Try API key authentication
        api_key = request.headers.get('X-API-Key')
        if api_key:
            user = await auth_manager.authenticate(token=api_key)
            if user:
                return user
        
        return None


class RequireAuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware that requires authentication for all requests."""
    
    def __init__(self, app, exclude_paths: list = None):
        """Initialize middleware with optional exclude paths."""
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check authentication before processing request."""
        # Skip authentication for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Check if user is authenticated
        if not getattr(request.state, 'is_authenticated', False):
            return JSONResponse(
                {'error': 'Authentication required'},
                status_code=401
            )
        
        return await call_next(request)


class PermissionRequiredMiddleware(BaseHTTPMiddleware):
    """Middleware that checks permissions for requests."""
    
    def __init__(self, app, permission_map: dict = None):
        """
        Initialize middleware with permission mapping.
        
        Args:
            permission_map: Dict mapping URL patterns to required permissions
        """
        super().__init__(app)
        self.permission_map = permission_map or {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check permissions before processing request."""
        # Get required permission for this path
        required_permission = self._get_required_permission(request.url.path)
        
        if required_permission:
            # Check if user is authenticated
            if not getattr(request.state, 'is_authenticated', False):
                return JSONResponse(
                    {'error': 'Authentication required'},
                    status_code=401
                )
            
            # Check permission
            permission_checker = getattr(request.state, 'permission_checker', None)
            if not permission_checker:
                return JSONResponse(
                    {'error': 'Permission denied'},
                    status_code=403
                )
            
            has_permission = await permission_checker.has_permission(required_permission)
            if not has_permission:
                return JSONResponse(
                    {'error': 'Permission denied'},
                    status_code=403
                )
        
        return await call_next(request)
    
    def _get_required_permission(self, path: str) -> Optional[str]:
        """Get required permission for path."""
        # Simple exact match - in practice you'd want pattern matching
        return self.permission_map.get(path)


class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware for handling CORS headers."""
    
    def __init__(
        self,
        app,
        allow_origins: list = None,
        allow_methods: list = None,
        allow_headers: list = None,
        allow_credentials: bool = False
    ):
        """Initialize CORS middleware."""
        super().__init__(app)
        self.allow_origins = allow_origins or ['*']
        self.allow_methods = allow_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allow_headers = allow_headers or ['*']
        self.allow_credentials = allow_credentials
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add CORS headers to response."""
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = Response()
        else:
            response = await call_next(request)
        
        # Add CORS headers
        origin = request.headers.get('Origin')
        if origin and (origin in self.allow_origins or '*' in self.allow_origins):
            response.headers['Access-Control-Allow-Origin'] = origin
        elif '*' in self.allow_origins:
            response.headers['Access-Control-Allow-Origin'] = '*'
        
        response.headers['Access-Control-Allow-Methods'] = ', '.join(self.allow_methods)
        response.headers['Access-Control-Allow-Headers'] = ', '.join(self.allow_headers)
        
        if self.allow_credentials:
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        """Initialize rate limiting middleware."""
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # In practice, use Redis or similar
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limits before processing request."""
        client_ip = request.client.host
        current_minute = datetime.now().minute
        
        # Simple in-memory rate limiting (not suitable for production)
        key = f"{client_ip}:{current_minute}"
        
        if key not in self.request_counts:
            self.request_counts[key] = 0
        
        self.request_counts[key] += 1
        
        if self.request_counts[key] > self.requests_per_minute:
            return JSONResponse(
                {'error': 'Rate limit exceeded'},
                status_code=429
            )
        
        return await call_next(request)


# Export all middleware
__all__ = [
    'AuthenticationMiddleware',
    'RequireAuthenticationMiddleware',
    'PermissionRequiredMiddleware',
    'CORSMiddleware',
    'RateLimitMiddleware',
]
