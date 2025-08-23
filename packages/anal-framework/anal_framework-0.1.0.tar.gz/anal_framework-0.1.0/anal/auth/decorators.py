"""
Authentication decorators for ANAL framework.

This module provides decorators for protecting views and functions
with authentication and authorization.
"""

import functools
from typing import Callable, List, Optional, Union

from ..http.responses import JsonResponse
from .backends import get_auth_manager, PermissionChecker


def login_required(func: Callable) -> Callable:
    """Decorator that requires user to be authenticated."""
    
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        """Check if user is authenticated."""
        if not getattr(request.state, 'is_authenticated', False):
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def permission_required(permission: str):
    """Decorator that requires specific permission."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            """Check if user has permission."""
            # Check authentication first
            if not getattr(request.state, 'is_authenticated', False):
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )
            
            # Check permission
            permission_checker = getattr(request.state, 'permission_checker', None)
            if not permission_checker:
                return JsonResponse(
                    {'error': 'Permission denied'},
                    status=403
                )
            
            has_permission = await permission_checker.has_permission(permission)
            if not has_permission:
                return JsonResponse(
                    {'error': 'Permission denied'},
                    status=403
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def permissions_required(permissions: List[str], require_all: bool = True):
    """Decorator that requires multiple permissions."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            """Check if user has required permissions."""
            # Check authentication first
            if not getattr(request.state, 'is_authenticated', False):
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )
            
            # Check permissions
            permission_checker = getattr(request.state, 'permission_checker', None)
            if not permission_checker:
                return JsonResponse(
                    {'error': 'Permission denied'},
                    status=403
                )
            
            if require_all:
                has_permissions = await permission_checker.has_permissions(permissions)
            else:
                has_permissions = await permission_checker.has_any_permission(permissions)
            
            if not has_permissions:
                return JsonResponse(
                    {'error': 'Permission denied'},
                    status=403
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def staff_required(func: Callable) -> Callable:
    """Decorator that requires user to be staff."""
    
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        """Check if user is staff."""
        if not getattr(request.state, 'is_authenticated', False):
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        user = getattr(request.state, 'user', None)
        if not user or not user.is_staff:
            return JsonResponse(
                {'error': 'Staff access required'},
                status=403
            )
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def superuser_required(func: Callable) -> Callable:
    """Decorator that requires user to be superuser."""
    
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        """Check if user is superuser."""
        if not getattr(request.state, 'is_authenticated', False):
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        user = getattr(request.state, 'user', None)
        if not user or not user.is_superuser:
            return JsonResponse(
                {'error': 'Superuser access required'},
                status=403
            )
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def active_required(func: Callable) -> Callable:
    """Decorator that requires user to be active."""
    
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        """Check if user is active."""
        if not getattr(request.state, 'is_authenticated', False):
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        user = getattr(request.state, 'user', None)
        if not user or not user.is_active:
            return JsonResponse(
                {'error': 'Account is inactive'},
                status=403
            )
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def anonymous_required(func: Callable) -> Callable:
    """Decorator that requires user to NOT be authenticated (for login/register views)."""
    
    @functools.wraps(func)
    async def wrapper(request, *args, **kwargs):
        """Check if user is anonymous."""
        if getattr(request.state, 'is_authenticated', False):
            return JsonResponse(
                {'error': 'Already authenticated'},
                status=400
            )
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def throttle(requests_per_minute: int = 60):
    """Decorator for rate limiting."""
    
    def decorator(func: Callable) -> Callable:
        request_counts = {}  # In practice, use Redis or similar
        
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            """Apply rate limiting."""
            from datetime import datetime
            
            client_ip = request.client.host
            current_minute = datetime.now().minute
            
            # Simple in-memory rate limiting (not suitable for production)
            key = f"{client_ip}:{current_minute}"
            
            if key not in request_counts:
                request_counts[key] = 0
            
            request_counts[key] += 1
            
            if request_counts[key] > requests_per_minute:
                return JsonResponse(
                    {'error': 'Rate limit exceeded'},
                    status=429
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


# Combine decorators for common patterns
def api_auth_required(func: Callable) -> Callable:
    """Decorator that combines login_required and active_required."""
    return active_required(login_required(func))


def admin_required(func: Callable) -> Callable:
    """Decorator that requires staff access."""
    return staff_required(api_auth_required(func))


def secure_api(permissions: Optional[Union[str, List[str]]] = None, throttle_rate: int = 60):
    """Decorator that combines authentication, permissions, and rate limiting."""
    
    def decorator(func: Callable) -> Callable:
        # Apply rate limiting
        decorated_func = throttle(throttle_rate)(func)
        
        # Apply authentication
        decorated_func = api_auth_required(decorated_func)
        
        # Apply permission check if specified
        if permissions:
            if isinstance(permissions, str):
                decorated_func = permission_required(permissions)(decorated_func)
            elif isinstance(permissions, list):
                decorated_func = permissions_required(permissions)(decorated_func)
        
        return decorated_func
    
    return decorator


# Export all decorators
__all__ = [
    'login_required',
    'permission_required',
    'permissions_required',
    'staff_required',
    'superuser_required',
    'active_required',
    'anonymous_required',
    'throttle',
    'api_auth_required',
    'admin_required',
    'secure_api',
]
