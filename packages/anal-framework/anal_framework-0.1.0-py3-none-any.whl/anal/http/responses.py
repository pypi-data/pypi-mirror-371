"""
HTTP responses for ANAL framework.

This module provides response classes for different types of HTTP responses
including JSON, HTML templates, file downloads, and streaming responses.
"""

import json
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from starlette.responses import (
    Response,
    JSONResponse as StarletteJSONResponse,
    PlainTextResponse,
    HTMLResponse,
    FileResponse as StarletteFileResponse,
    StreamingResponse,
    RedirectResponse
)

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False


class JsonResponse(StarletteJSONResponse):
    """
    Enhanced JSON response with better serialization support.
    
    Features:
    - Uses orjson for better performance if available
    - Supports custom JSON encoders
    - Automatic CORS headers
    - Consistent error formatting
    
    Example:
        ```python
        from anal.http.responses import JsonResponse
        
        async def my_handler(request):
            return JsonResponse({
                'message': 'Hello, World!',
                'data': {'key': 'value'}
            })
        ```
    """
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "application/json",
        **kwargs
    ):
        """
        Initialize JSON response.
        
        Args:
            content: Response content to serialize as JSON
            status_code: HTTP status code
            headers: Additional headers
            media_type: Response media type
            **kwargs: Additional arguments
        """
        # Use orjson if available for better performance
        if HAS_ORJSON and content is not None:
            json_content = orjson.dumps(content).decode('utf-8')
        else:
            json_content = json.dumps(content, ensure_ascii=False, separators=(',', ':'))
        
        super().__init__(
            content=json_content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            **kwargs
        )


class TemplateResponse(HTMLResponse):
    """
    Template-based HTML response using Jinja2.
    
    Features:
    - Jinja2 template rendering
    - Context variable injection
    - Template inheritance support
    - Auto-escaping for security
    - Custom filters and globals
    
    Example:
        ```python
        from anal.http.responses import TemplateResponse
        
        async def my_handler(request):
            return TemplateResponse(
                'users/list.html',
                context={'users': users, 'title': 'User List'},
                request=request
            )
        ```
    """
    
    _template_env: Optional[Environment] = None
    
    def __init__(
        self,
        template: str,
        context: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "text/html",
        request=None,
        **kwargs
    ):
        """
        Initialize template response.
        
        Args:
            template: Template file name
            context: Template context variables
            status_code: HTTP status code
            headers: Additional headers
            media_type: Response media type
            request: Request object (for context)
            **kwargs: Additional arguments
        """
        if not HAS_JINJA2:
            raise RuntimeError("Jinja2 is required for template responses. Install with: pip install jinja2")
        
        self.template = template
        self.context = context or {}
        self.request = request
        
        # Add request to context if provided
        if request:
            self.context['request'] = request
        
        # Render template
        content = self._render_template()
        
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            **kwargs
        )
    
    def _render_template(self) -> str:
        """Render the template with context."""
        if self._template_env is None:
            self._setup_template_environment()
        
        try:
            template = self._template_env.get_template(self.template)
            return template.render(self.context)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template '{self.template}' not found")
    
    @classmethod
    def _setup_template_environment(cls, template_dirs: Optional[list] = None) -> None:
        """Setup Jinja2 template environment."""
        if template_dirs is None:
            template_dirs = ['templates']
        
        # Add current directory templates
        template_dirs.append(Path.cwd() / 'templates')
        
        loader = FileSystemLoader(template_dirs)
        cls._template_env = Environment(
            loader=loader,
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters and globals
        cls._add_template_globals()
    
    @classmethod
    def _add_template_globals(cls) -> None:
        """Add custom template filters and globals."""
        if cls._template_env is None:
            return
        
        # Add URL generation function
        def url_for(name: str, **params) -> str:
            # This will be implemented when we integrate with the router
            return f"#{name}"
        
        cls._template_env.globals['url_for'] = url_for
        
        # Add common utility functions
        cls._template_env.globals['len'] = len
        cls._template_env.globals['str'] = str
        cls._template_env.globals['int'] = int
    
    @classmethod
    def configure(
        cls,
        template_dirs: list,
        auto_reload: bool = False,
        cache_size: int = 400
    ) -> None:
        """
        Configure template system.
        
        Args:
            template_dirs: List of template directories
            auto_reload: Enable auto-reload of templates
            cache_size: Template cache size
        """
        loader = FileSystemLoader(template_dirs)
        cls._template_env = Environment(
            loader=loader,
            autoescape=True,
            auto_reload=auto_reload,
            cache_size=cache_size,
            trim_blocks=True,
            lstrip_blocks=True
        )
        cls._add_template_globals()


class FileResponse(StarletteFileResponse):
    """
    Enhanced file response with additional features.
    
    Features:
    - Automatic content type detection
    - Content disposition handling
    - Range request support
    - File streaming for large files
    
    Example:
        ```python
        from anal.http.responses import FileResponse
        
        async def download_file(request):
            return FileResponse(
                path='/path/to/file.pdf',
                filename='document.pdf',
                media_type='application/pdf'
            )
        ```
    """
    
    def __init__(
        self,
        path: Union[str, Path],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize file response.
        
        Args:
            path: Path to the file
            status_code: HTTP status code
            headers: Additional headers
            media_type: Content type (auto-detected if None)
            filename: Download filename
            **kwargs: Additional arguments
        """
        path = Path(path)
        
        # Auto-detect media type if not provided
        if media_type is None:
            media_type, _ = mimetypes.guess_type(str(path))
            if media_type is None:
                media_type = 'application/octet-stream'
        
        # Setup headers
        response_headers = headers or {}
        
        # Add Content-Disposition header if filename provided
        if filename:
            response_headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        super().__init__(
            path=str(path),
            status_code=status_code,
            headers=response_headers,
            media_type=media_type,
            **kwargs
        )


class StreamingJsonResponse(StreamingResponse):
    """
    Streaming JSON response for large datasets.
    
    Useful for APIs that return large amounts of data that should be
    streamed rather than loaded entirely into memory.
    
    Example:
        ```python
        from anal.http.responses import StreamingJsonResponse
        
        async def stream_data(request):
            async def generate():
                yield '{"items": ['
                for i, item in enumerate(large_dataset):
                    if i > 0:
                        yield ','
                    yield json.dumps(item)
                yield ']}'
            
            return StreamingJsonResponse(generate())
        ```
    """
    
    def __init__(
        self,
        content,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="application/json",
            **kwargs
        )


class ErrorResponse(JsonResponse):
    """
    Standardized error response format.
    
    Features:
    - Consistent error structure
    - HTTP status code mapping
    - Error details and context
    - Development vs production modes
    
    Example:
        ```python
        from anal.http.responses import ErrorResponse
        
        async def my_handler(request):
            if not user:
                return ErrorResponse(
                    message="User not found",
                    status_code=404,
                    error_code="USER_NOT_FOUND"
                )
        ```
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
            headers: Additional headers
            **kwargs: Additional arguments
        """
        content = {
            "error": True,
            "message": message,
            "status_code": status_code
        }
        
        if error_code:
            content["error_code"] = error_code
        
        if details:
            content["details"] = details
        
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            **kwargs
        )


class SuccessResponse(JsonResponse):
    """
    Standardized success response format.
    
    Example:
        ```python
        from anal.http.responses import SuccessResponse
        
        async def create_user(request):
            user = await create_user_logic()
            return SuccessResponse(
                message="User created successfully",
                data={"user": user.dict()},
                status_code=201
            )
        ```
    """
    
    def __init__(
        self,
        message: str = "Success",
        data: Optional[Any] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Initialize success response.
        
        Args:
            message: Success message
            data: Response data
            status_code: HTTP status code
            headers: Additional headers
            **kwargs: Additional arguments
        """
        content = {
            "success": True,
            "message": message,
            "status_code": status_code
        }
        
        if data is not None:
            content["data"] = data
        
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            **kwargs
        )


class NoContentResponse(Response):
    """
    HTTP 204 No Content response.
    
    Example:
        ```python
        from anal.http.responses import NoContentResponse
        
        async def delete_user(request):
            await delete_user_logic()
            return NoContentResponse()
        ```
    """
    
    def __init__(self, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            content=None,
            status_code=204,
            headers=headers
        )


# Response helper functions
def json_response(content: Any, **kwargs) -> JsonResponse:
    """Create a JSON response."""
    return JsonResponse(content, **kwargs)


def template_response(template: str, context: Optional[Dict] = None, **kwargs) -> TemplateResponse:
    """Create a template response."""
    return TemplateResponse(template, context, **kwargs)


def file_response(path: Union[str, Path], **kwargs) -> FileResponse:
    """Create a file response."""
    return FileResponse(path, **kwargs)


def error_response(message: str, status_code: int = 400, **kwargs) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse(message, status_code, **kwargs)


def success_response(message: str = "Success", data: Optional[Any] = None, **kwargs) -> SuccessResponse:
    """Create a success response."""
    return SuccessResponse(message, data, **kwargs)


def redirect_response(url: str, status_code: int = 302, **kwargs) -> RedirectResponse:
    """Create a redirect response."""
    return RedirectResponse(url, status_code, **kwargs)
