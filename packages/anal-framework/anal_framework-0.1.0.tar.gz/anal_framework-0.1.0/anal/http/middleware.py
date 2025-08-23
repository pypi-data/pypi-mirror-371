"""
Middleware system for ANAL framework.

This module provides a comprehensive middleware system for handling
cross-cutting concerns like authentication, logging, CORS, etc.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional, Type

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from anal.core.exceptions import ANALException


logger = logging.getLogger(__name__)


class Middleware:
    """
    Base middleware class for ANAL framework.
    
    Provides a simple interface for creating middleware that can
    process requests and responses.
    
    Example:
        ```python
        from anal.http.middleware import Middleware
        
        class CustomMiddleware(Middleware):
            async def process_request(self, request):
                # Process request before handler
                request.state.start_time = time.time()
            
            async def process_response(self, request, response):
                # Process response after handler
                duration = time.time() - request.state.start_time
                response.headers['X-Process-Time'] = str(duration)
                return response
        ```
    """
    
    async def process_request(self, request: Request) -> Optional[Response]:
        """
        Process request before it reaches the handler.
        
        Args:
            request: HTTP request object
            
        Returns:
            Optional response to short-circuit request processing
        """
        pass
    
    async def process_response(self, request: Request, response: Response) -> Response:
        """
        Process response after handler execution.
        
        Args:
            request: HTTP request object
            response: HTTP response object
            
        Returns:
            Modified response object
        """
        return response
    
    async def process_exception(self, request: Request, exc: Exception) -> Optional[Response]:
        """
        Process exceptions that occur during request handling.
        
        Args:
            request: HTTP request object
            exc: Exception that occurred
            
        Returns:
            Optional response to handle the exception
        """
        pass


class MiddlewareAdapter(BaseHTTPMiddleware):
    """
    Adapter to convert ANAL middleware to Starlette middleware.
    """
    
    def __init__(self, app, middleware_class: Type[Middleware], **kwargs):
        super().__init__(app)
        self.middleware = middleware_class(**kwargs)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatch request through middleware."""
        try:
            # Process request
            response = await self.middleware.process_request(request)
            if response:
                return response
            
            # Call next middleware/handler
            response = await call_next(request)
            
            # Process response
            response = await self.middleware.process_response(request, response)
            return response
            
        except Exception as exc:
            # Process exception
            response = await self.middleware.process_exception(request, exc)
            if response:
                return response
            
            # Re-raise if not handled
            raise


class RequestLoggingMiddleware(Middleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Features:
    - Request/response logging
    - Performance timing
    - Error logging
    - Configurable log levels
    
    Example:
        ```python
        app.add_middleware(RequestLoggingMiddleware, 
                          level=logging.INFO,
                          include_headers=True)
        ```
    """
    
    def __init__(
        self,
        level: int = logging.INFO,
        include_headers: bool = False,
        include_body: bool = False,
        max_body_size: int = 1024
    ):
        self.level = level
        self.include_headers = include_headers
        self.include_body = include_body
        self.max_body_size = max_body_size
    
    async def process_request(self, request: Request) -> None:
        """Log incoming request."""
        request.state.start_time = time.time()
        
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "client": getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        }
        
        if self.include_headers:
            log_data["headers"] = dict(request.headers)
        
        if self.include_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    log_data["body"] = body.decode('utf-8', errors='replace')
                else:
                    log_data["body"] = f"<body too large: {len(body)} bytes>"
            except Exception:
                log_data["body"] = "<unable to read body>"
        
        logger.log(self.level, f"Request started: {request.method} {request.url.path}", extra=log_data)
    
    async def process_response(self, request: Request, response: Response) -> Response:
        """Log response."""
        duration = time.time() - getattr(request.state, 'start_time', time.time())
        
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration": duration
        }
        
        if self.include_headers:
            log_data["response_headers"] = dict(response.headers)
        
        logger.log(
            self.level,
            f"Request completed: {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
            extra=log_data
        )
        
        # Add timing header
        response.headers['X-Process-Time'] = str(duration)
        
        return response
    
    async def process_exception(self, request: Request, exc: Exception) -> None:
        """Log exceptions."""
        duration = time.time() - getattr(request.state, 'start_time', time.time())
        
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "exception": str(exc),
            "exception_type": type(exc).__name__,
            "duration": duration
        }
        
        logger.error(
            f"Request failed: {request.method} {request.url.path} - {type(exc).__name__}: {exc} ({duration:.3f}s)",
            extra=log_data,
            exc_info=True
        )


class ErrorHandlerMiddleware(Middleware):
    """
    Middleware for handling and formatting errors.
    
    Features:
    - Catches and formats exceptions
    - Returns appropriate HTTP responses
    - Logs errors for debugging
    - Supports custom error handlers
    
    Example:
        ```python
        app.add_middleware(ErrorHandlerMiddleware, debug=True)
        ```
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.custom_handlers: Dict[Type[Exception], Callable] = {}
    
    def add_exception_handler(self, exc_type: Type[Exception], handler: Callable):
        """Add custom exception handler."""
        self.custom_handlers[exc_type] = handler
    
    async def process_exception(self, request: Request, exc: Exception) -> Response:
        """Handle exceptions."""
        from anal.http.responses import JsonResponse, ErrorResponse
        
        # Check for custom handlers
        for exc_type, handler in self.custom_handlers.items():
            if isinstance(exc, exc_type):
                return await handler(request, exc)
        
        # Handle ANAL exceptions
        if isinstance(exc, ANALException):
            return ErrorResponse(
                message=exc.message,
                status_code=exc.status_code or 500,
                details=exc.details if self.debug else None
            )
        
        # Handle generic exceptions
        if self.debug:
            import traceback
            return JsonResponse(
                {
                    "error": True,
                    "message": str(exc),
                    "type": type(exc).__name__,
                    "traceback": traceback.format_exc().split('\n')
                },
                status_code=500
            )
        else:
            return ErrorResponse(
                message="Internal server error",
                status_code=500
            )


class CacheMiddleware(Middleware):
    """
    Middleware for HTTP caching.
    
    Features:
    - Response caching
    - ETags generation
    - Cache headers
    - Conditional requests
    
    Example:
        ```python
        app.add_middleware(CacheMiddleware, default_ttl=300)
        ```
    """
    
    def __init__(self, default_ttl: int = 300, cache_private: bool = False):
        self.default_ttl = default_ttl
        self.cache_private = cache_private
    
    async def process_response(self, request: Request, response: Response) -> Response:
        """Add cache headers to response."""
        # Only cache GET requests
        if request.method != "GET":
            return response
        
        # Skip if already has cache headers
        if "Cache-Control" in response.headers:
            return response
        
        # Add cache headers
        cache_control = f"{'private' if self.cache_private else 'public'}, max-age={self.default_ttl}"
        response.headers["Cache-Control"] = cache_control
        
        # Add ETag if not present
        if "ETag" not in response.headers and hasattr(response, 'body'):
            import hashlib
            etag = hashlib.md5(response.body).hexdigest()
            response.headers["ETag"] = f'"{etag}"'
        
        return response


class CompressionMiddleware(Middleware):
    """
    Middleware for response compression.
    
    Features:
    - Gzip compression
    - Content type filtering
    - Size threshold
    - Quality negotiation
    
    Example:
        ```python
        app.add_middleware(CompressionMiddleware, minimum_size=500)
        ```
    """
    
    def __init__(
        self,
        minimum_size: int = 500,
        compressible_types: Optional[List[str]] = None
    ):
        self.minimum_size = minimum_size
        self.compressible_types = compressible_types or [
            "text/html",
            "text/css", 
            "text/javascript",
            "application/json",
            "application/javascript",
            "text/xml",
            "application/xml"
        ]
    
    async def process_response(self, request: Request, response: Response) -> Response:
        """Compress response if appropriate."""
        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return response
        
        # Check content type
        content_type = response.headers.get("Content-Type", "").split(";")[0]
        if content_type not in self.compressible_types:
            return response
        
        # Check size threshold
        if hasattr(response, 'body') and len(response.body) < self.minimum_size:
            return response
        
        # Apply compression (this would need proper implementation)
        # response.headers["Content-Encoding"] = "gzip"
        # response.headers["Vary"] = "Accept-Encoding"
        
        return response


class MiddlewareStack:
    """
    Container for managing middleware stack.
    
    Handles middleware registration, ordering, and conversion
    to Starlette middleware format.
    
    Example:
        ```python
        stack = MiddlewareStack()
        stack.add(RequestLoggingMiddleware, level=logging.INFO)
        stack.add(ErrorHandlerMiddleware, debug=True)
        
        # Convert to Starlette middleware
        middleware = stack.build()
        ```
    """
    
    def __init__(self):
        self.middleware: List[tuple] = []
    
    def add(self, middleware_class: Type[Middleware], **kwargs) -> None:
        """
        Add middleware to the stack.
        
        Args:
            middleware_class: Middleware class
            **kwargs: Middleware initialization arguments
        """
        self.middleware.append((middleware_class, kwargs))
    
    def insert(self, index: int, middleware_class: Type[Middleware], **kwargs) -> None:
        """Insert middleware at specific position."""
        self.middleware.insert(index, (middleware_class, kwargs))
    
    def remove(self, middleware_class: Type[Middleware]) -> None:
        """Remove middleware from stack."""
        self.middleware = [
            (cls, kwargs) for cls, kwargs in self.middleware
            if cls != middleware_class
        ]
    
    def clear(self) -> None:
        """Clear all middleware."""
        self.middleware.clear()
    
    def build(self) -> List:
        """
        Build middleware stack for Starlette.
        
        Returns:
            List of Starlette middleware
        """
        from starlette.middleware import Middleware as StarletteMiddleware
        
        starlette_middleware = []
        
        for middleware_class, kwargs in self.middleware:
            # Convert ANAL middleware to Starlette middleware
            adapter = lambda app, cls=middleware_class, kw=kwargs: MiddlewareAdapter(app, cls, **kw)
            starlette_middleware.append(StarletteMiddleware(adapter))
        
        return starlette_middleware
    
    def __len__(self) -> int:
        return len(self.middleware)
    
    def __repr__(self) -> str:
        return f"<MiddlewareStack(count={len(self.middleware)})>"
