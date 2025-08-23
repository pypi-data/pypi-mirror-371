"""
Custom exceptions for the ANAL framework.

This module defines the exception hierarchy for the ANAL framework,
providing clear error types for different failure scenarios.
"""

from typing import Any, Dict, Optional


class ANALException(Exception):
    """
    Base exception class for all ANAL framework errors.
    
    This is the root exception that all other ANAL exceptions inherit from.
    It provides additional context and debugging information.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Additional error details
            status_code: HTTP status code if applicable
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.status_code = status_code
    
    def __str__(self) -> str:
        return self.message
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"


class ConfigurationError(ANALException):
    """Raised when there's a configuration error."""
    
    def __init__(self, message: str, setting_name: Optional[str] = None):
        super().__init__(message)
        self.setting_name = setting_name


class DependencyInjectionError(ANALException):
    """Raised when dependency injection fails."""
    pass


class RouterError(ANALException):
    """Raised when there's a routing error."""
    pass


class MiddlewareError(ANALException):
    """Raised when middleware processing fails."""
    pass


class DatabaseError(ANALException):
    """Raised when database operations fail."""
    pass


class AuthenticationError(ANALException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(ANALException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class ValidationError(ANALException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, status_code=400, **kwargs)
        self.field = field


class NotFoundError(ANALException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class MethodNotAllowedError(ANALException):
    """Raised when HTTP method is not allowed."""
    
    def __init__(self, message: str = "Method not allowed", allowed_methods: Optional[list] = None, **kwargs):
        super().__init__(message, status_code=405, **kwargs)
        self.allowed_methods = allowed_methods or []


class RateLimitError(ANALException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class FileUploadError(ANALException):
    """Raised when file upload fails."""
    pass


class TemplateError(ANALException):
    """Raised when template processing fails."""
    pass


class CacheError(ANALException):
    """Raised when cache operations fail."""
    pass


class TaskError(ANALException):
    """Raised when background task processing fails."""
    pass


class WebSocketError(ANALException):
    """Raised when WebSocket operations fail."""
    pass


class APIError(ANALException):
    """Raised when API operations fail."""
    pass


class SerializationError(ANALException):
    """Raised when data serialization/deserialization fails."""
    pass


class ImportError(ANALException):
    """Raised when module/app imports fail."""
    pass


class AppRegistryError(ANALException):
    """Raised when app registry operations fail."""
    pass


class PluginError(ANALException):
    """Raised when plugin operations fail."""
    pass


class MigrationError(ANALException):
    """Raised when database migration fails."""
    pass


class TestError(ANALException):
    """Raised when test operations fail."""
    pass


class DeploymentError(ANALException):
    """Raised when deployment operations fail."""
    pass


class SecurityError(ANALException):
    """Raised when security violations occur."""
    
    def __init__(self, message: str = "Security violation", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class HTTPError(ANALException):
    """Base class for HTTP-related errors."""
    
    def __init__(self, message: str, status_code: int, headers: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(message, status_code=status_code, **kwargs)
        self.headers = headers or {}


class BadRequestError(HTTPError):
    """HTTP 400 Bad Request error."""
    
    def __init__(self, message: str = "Bad request", **kwargs):
        super().__init__(message, 400, **kwargs)


class UnauthorizedError(HTTPError):
    """HTTP 401 Unauthorized error."""
    
    def __init__(self, message: str = "Unauthorized", **kwargs):
        super().__init__(message, 401, **kwargs)


class ForbiddenError(HTTPError):
    """HTTP 403 Forbidden error."""
    
    def __init__(self, message: str = "Forbidden", **kwargs):
        super().__init__(message, 403, **kwargs)


class NotFoundHTTPError(HTTPError):
    """HTTP 404 Not Found error."""
    
    def __init__(self, message: str = "Not found", **kwargs):
        super().__init__(message, 404, **kwargs)


class ConflictError(HTTPError):
    """HTTP 409 Conflict error."""
    
    def __init__(self, message: str = "Conflict", **kwargs):
        super().__init__(message, 409, **kwargs)


class UnprocessableEntityError(HTTPError):
    """HTTP 422 Unprocessable Entity error."""
    
    def __init__(self, message: str = "Unprocessable entity", **kwargs):
        super().__init__(message, 422, **kwargs)


class TooManyRequestsError(HTTPError):
    """HTTP 429 Too Many Requests error."""
    
    def __init__(self, message: str = "Too many requests", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, 429, **kwargs)
        self.retry_after = retry_after


class InternalServerError(HTTPError):
    """HTTP 500 Internal Server Error."""
    
    def __init__(self, message: str = "Internal server error", **kwargs):
        super().__init__(message, 500, **kwargs)


class BadGatewayError(HTTPError):
    """HTTP 502 Bad Gateway error."""
    
    def __init__(self, message: str = "Bad gateway", **kwargs):
        super().__init__(message, 502, **kwargs)


class ServiceUnavailableError(HTTPError):
    """HTTP 503 Service Unavailable error."""
    
    def __init__(self, message: str = "Service unavailable", **kwargs):
        super().__init__(message, 503, **kwargs)


class GatewayTimeoutError(HTTPError):
    """HTTP 504 Gateway Timeout error."""
    
    def __init__(self, message: str = "Gateway timeout", **kwargs):
        super().__init__(message, 504, **kwargs)


# Exception mapping for HTTP status codes
HTTP_EXCEPTION_MAP = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundHTTPError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: TooManyRequestsError,
    500: InternalServerError,
    502: BadGatewayError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def create_http_exception(status_code: int, message: str = None, **kwargs) -> HTTPError:
    """
    Create an HTTP exception for the given status code.
    
    Args:
        status_code: HTTP status code
        message: Optional error message
        **kwargs: Additional exception parameters
        
    Returns:
        HTTP exception instance
    """
    exception_class = HTTP_EXCEPTION_MAP.get(status_code, HTTPError)
    
    if message:
        return exception_class(message, **kwargs)
    else:
        return exception_class(**kwargs)


def handle_exception(exc: Exception) -> Dict[str, Any]:
    """
    Convert an exception to a standardized error response.
    
    Args:
        exc: Exception to handle
        
    Returns:
        Error response dictionary
    """
    if isinstance(exc, ANALException):
        return {
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "status_code": exc.status_code or 500
        }
    else:
        return {
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"original_error": str(exc)},
            "status_code": 500
        }
