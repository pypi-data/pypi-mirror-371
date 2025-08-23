"""
HTTP routing system for ANAL framework.

This module provides a sophisticated routing system with support for
path parameters, query parameters, middleware, and automatic API generation.
"""

import inspect
import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Type, Union

from anal.core.exceptions import ANALException, RouterError


class Route:
    """
    Represents a single route in the routing system.
    """
    
    def __init__(
        self,
        path: str,
        endpoint: Callable,
        methods: List[str],
        name: Optional[str] = None,
        middleware: Optional[List[Callable]] = None,
        **kwargs
    ):
        """
        Initialize a route.
        
        Args:
            path: URL path pattern
            endpoint: Handler function
            methods: Allowed HTTP methods
            name: Route name for URL generation
            middleware: Route-specific middleware
            **kwargs: Additional route options
        """
        self.path = path
        self.endpoint = endpoint
        self.methods = [method.upper() for method in methods]
        self.name = name or self._generate_name()
        self.middleware = middleware or []
        self.options = kwargs
        
        # Compile path pattern
        self.path_regex, self.path_params = self._compile_path(path)
    
    def _generate_name(self) -> str:
        """Generate a default name for the route."""
        if hasattr(self.endpoint, '__name__'):
            return self.endpoint.__name__
        elif hasattr(self.endpoint, '__class__'):
            return f"{self.endpoint.__class__.__name__}.{getattr(self.endpoint, '__func__', 'call').__name__}"
        else:
            return "anonymous"
    
    def _compile_path(self, path: str) -> tuple[Pattern, List[str]]:
        """
        Compile path pattern to regex.
        
        Supports:
        - Static paths: /users
        - Parameters: /users/{id}
        - Typed parameters: /users/{id:int}
        - Wildcard: /files/{path:path}
        
        Returns:
            Compiled regex pattern and parameter names
        """
        if not path.startswith('/'):
            path = '/' + path
        
        # Extract parameters
        param_pattern = r'\{([^}]+)\}'
        params = []
        
        def replace_param(match):
            param_spec = match.group(1)
            
            if ':' in param_spec:
                param_name, param_type = param_spec.split(':', 1)
            else:
                param_name = param_spec
                param_type = 'str'
            
            params.append(param_name)
            
            # Type-specific patterns
            if param_type == 'int':
                return r'([0-9]+)'
            elif param_type == 'float':
                return r'([0-9]+\.?[0-9]*)'
            elif param_type == 'uuid':
                return r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
            elif param_type == 'path':
                return r'(.+)'
            else:  # str or any other type
                return r'([^/]+)'
        
        # Replace parameters with regex groups
        pattern_str = re.sub(param_pattern, replace_param, path)
        pattern_str = f'^{pattern_str}$'
        
        return re.compile(pattern_str), params
    
    def match(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """
        Check if the route matches the given path and method.
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            Path parameters if match, None otherwise
        """
        if method.upper() not in self.methods:
            return None
        
        match = self.path_regex.match(path)
        if not match:
            return None
        
        # Extract path parameters
        params = {}
        for i, param_name in enumerate(self.path_params):
            params[param_name] = match.group(i + 1)
        
        return params
    
    def __repr__(self) -> str:
        return f"<Route({self.path}, methods={self.methods}, name='{self.name}')>"


class WebSocketRoute:
    """Represents a WebSocket route."""
    
    def __init__(
        self,
        path: str,
        endpoint: Callable,
        name: Optional[str] = None,
        **kwargs
    ):
        self.path = path
        self.websocket_endpoint = endpoint
        self.name = name or endpoint.__name__
        self.options = kwargs
        
        # Compile path pattern (same as HTTP routes)
        self.path_regex, self.path_params = Route._compile_path(self, path)
    
    def match(self, path: str) -> Optional[Dict[str, Any]]:
        """Check if the WebSocket route matches the path."""
        match = self.path_regex.match(path)
        if not match:
            return None
        
        params = {}
        for i, param_name in enumerate(self.path_params):
            params[param_name] = match.group(i + 1)
        
        return params


class Mount:
    """Represents a mounted sub-application."""
    
    def __init__(self, path: str, app: Any, name: Optional[str] = None):
        self.path = path.rstrip('/')
        self.app = app
        self.name = name


class Router:
    """
    Main routing class for the ANAL framework.
    
    Provides a flexible routing system with support for:
    - HTTP methods (GET, POST, PUT, DELETE, etc.)
    - Path parameters with type conversion
    - Route middleware
    - Sub-routers and mounting
    - WebSocket routes
    - Route generation and URL building
    
    Example:
        ```python
        from anal.http.routing import Router
        
        router = Router()
        
        @router.get('/users')
        async def list_users(request):
            return {'users': []}
        
        @router.post('/users')
        async def create_user(request):
            return {'created': True}
        
        @router.get('/users/{id:int}')
        async def get_user(request):
            user_id = request.path_params['id']
            return {'user_id': user_id}
        ```
    """
    
    def __init__(self, prefix: str = ""):
        """
        Initialize the router.
        
        Args:
            prefix: URL prefix for all routes in this router
        """
        self.prefix = prefix.rstrip('/')
        self.routes: List[Union[Route, WebSocketRoute, Mount]] = []
        self._route_map: Dict[str, Route] = {}  # For name-based lookups
    
    def add_route(
        self,
        path: str,
        endpoint: Callable,
        methods: List[str],
        name: Optional[str] = None,
        middleware: Optional[List[Callable]] = None,
        **kwargs
    ) -> Route:
        """
        Add a route to the router.
        
        Args:
            path: URL path pattern
            endpoint: Handler function
            methods: Allowed HTTP methods
            name: Route name
            middleware: Route-specific middleware
            **kwargs: Additional route options
            
        Returns:
            Created route instance
        """
        # Add prefix if present
        if self.prefix:
            path = self.prefix + path
        
        route = Route(path, endpoint, methods, name, middleware, **kwargs)
        self.routes.append(route)
        
        # Add to name map
        if route.name:
            if route.name in self._route_map:
                raise RouterError(f"Route name '{route.name}' already exists")
            self._route_map[route.name] = route
        
        return route
    
    def add_websocket_route(
        self,
        path: str,
        endpoint: Callable,
        name: Optional[str] = None,
        **kwargs
    ) -> WebSocketRoute:
        """Add a WebSocket route."""
        if self.prefix:
            path = self.prefix + path
        
        route = WebSocketRoute(path, endpoint, name, **kwargs)
        self.routes.append(route)
        return route
    
    def mount(self, path: str, app: Any, name: Optional[str] = None) -> Mount:
        """Mount a sub-application."""
        if self.prefix:
            path = self.prefix + path
        
        mount = Mount(path, app, name)
        self.routes.append(mount)
        return mount
    
    def include_router(self, router: "Router", prefix: str = "") -> None:
        """Include another router with optional prefix."""
        full_prefix = self.prefix + prefix
        
        for route in router.routes:
            if isinstance(route, Route):
                # Adjust path with prefix
                new_path = route.path
                if router.prefix and route.path.startswith(router.prefix):
                    new_path = route.path[len(router.prefix):]
                if full_prefix:
                    new_path = full_prefix + new_path
                
                self.add_route(
                    new_path,
                    route.endpoint,
                    route.methods,
                    route.name,
                    route.middleware,
                    **route.options
                )
            elif isinstance(route, WebSocketRoute):
                new_path = route.path
                if router.prefix and route.path.startswith(router.prefix):
                    new_path = route.path[len(router.prefix):]
                if full_prefix:
                    new_path = full_prefix + new_path
                
                self.add_websocket_route(new_path, route.websocket_endpoint, route.name)
            elif isinstance(route, Mount):
                new_path = route.path
                if router.prefix and route.path.startswith(router.prefix):
                    new_path = route.path[len(router.prefix):]
                if full_prefix:
                    new_path = full_prefix + new_path
                
                self.mount(new_path, route.app, route.name)
    
    # HTTP method decorators
    def route(
        self,
        path: str,
        methods: List[str],
        name: Optional[str] = None,
        middleware: Optional[List[Callable]] = None,
        **kwargs
    ) -> Callable:
        """Generic route decorator."""
        def decorator(func: Callable) -> Callable:
            self.add_route(path, func, methods, name, middleware, **kwargs)
            return func
        return decorator
    
    def get(self, path: str, **kwargs) -> Callable:
        """GET route decorator."""
        return self.route(path, ["GET"], **kwargs)
    
    def post(self, path: str, **kwargs) -> Callable:
        """POST route decorator."""
        return self.route(path, ["POST"], **kwargs)
    
    def put(self, path: str, **kwargs) -> Callable:
        """PUT route decorator."""
        return self.route(path, ["PUT"], **kwargs)
    
    def patch(self, path: str, **kwargs) -> Callable:
        """PATCH route decorator."""
        return self.route(path, ["PATCH"], **kwargs)
    
    def delete(self, path: str, **kwargs) -> Callable:
        """DELETE route decorator."""
        return self.route(path, ["DELETE"], **kwargs)
    
    def head(self, path: str, **kwargs) -> Callable:
        """HEAD route decorator."""
        return self.route(path, ["HEAD"], **kwargs)
    
    def options(self, path: str, **kwargs) -> Callable:
        """OPTIONS route decorator."""
        return self.route(path, ["OPTIONS"], **kwargs)
    
    def websocket(self, path: str, **kwargs) -> Callable:
        """WebSocket route decorator."""
        def decorator(func: Callable) -> Callable:
            self.add_websocket_route(path, func, **kwargs)
            return func
        return decorator
    
    def find_route(self, path: str, method: str) -> Optional[tuple[Route, Dict[str, Any]]]:
        """
        Find a matching route for the given path and method.
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            Tuple of (route, path_params) or None
        """
        for route_item in self.routes:
            if isinstance(route_item, Route):
                params = route_item.match(path, method)
                if params is not None:
                    return route_item, params
        
        return None
    
    def find_websocket_route(self, path: str) -> Optional[tuple[WebSocketRoute, Dict[str, Any]]]:
        """Find a matching WebSocket route."""
        for route_item in self.routes:
            if isinstance(route_item, WebSocketRoute):
                params = route_item.match(path)
                if params is not None:
                    return route_item, params
        
        return None
    
    def get_route_by_name(self, name: str) -> Optional[Route]:
        """Get a route by its name."""
        return self._route_map.get(name)
    
    def url_for(self, name: str, **params) -> str:
        """
        Generate URL for a named route.
        
        Args:
            name: Route name
            **params: Path parameters
            
        Returns:
            Generated URL
        """
        route = self.get_route_by_name(name)
        if not route:
            raise RouterError(f"No route found with name '{name}'")
        
        url = route.path
        
        # Replace parameters
        for param_name, param_value in params.items():
            pattern = f'{{{param_name}}}'
            if pattern in url:
                url = url.replace(pattern, str(param_value))
            else:
                # Try with type specification
                for param_type in ['int', 'float', 'uuid', 'path', 'str']:
                    typed_pattern = f'{{{param_name}:{param_type}}}'
                    if typed_pattern in url:
                        url = url.replace(typed_pattern, str(param_value))
                        break
        
        return url
    
    def get_routes(self) -> List[Route]:
        """Get all HTTP routes."""
        return [r for r in self.routes if isinstance(r, Route)]
    
    def get_websocket_routes(self) -> List[WebSocketRoute]:
        """Get all WebSocket routes."""
        return [r for r in self.routes if isinstance(r, WebSocketRoute)]
    
    def get_mounts(self) -> List[Mount]:
        """Get all mounts."""
        return [r for r in self.routes if isinstance(r, Mount)]
    
    def clear(self) -> None:
        """Clear all routes."""
        self.routes.clear()
        self._route_map.clear()
    
    def __len__(self) -> int:
        """Get number of routes."""
        return len(self.routes)
    
    def __repr__(self) -> str:
        return f"<Router(routes={len(self.routes)}, prefix='{self.prefix}')>"


# Convenience route decorator for standalone use
route = Router()


# Function-based routing helpers
def add_route(path: str, endpoint: Callable, methods: List[str], **kwargs) -> Route:
    """Add a route to the default router."""
    return route.add_route(path, endpoint, methods, **kwargs)


def get(path: str, **kwargs) -> Callable:
    """GET route decorator for default router."""
    return route.get(path, **kwargs)


def post(path: str, **kwargs) -> Callable:
    """POST route decorator for default router."""
    return route.post(path, **kwargs)


def put(path: str, **kwargs) -> Callable:
    """PUT route decorator for default router."""
    return route.put(path, **kwargs)


def patch(path: str, **kwargs) -> Callable:
    """PATCH route decorator for default router."""
    return route.patch(path, **kwargs)


def delete(path: str, **kwargs) -> Callable:
    """DELETE route decorator for default router."""
    return route.delete(path, **kwargs)


def websocket(path: str, **kwargs) -> Callable:
    """WebSocket decorator for default router."""
    return route.websocket(path, **kwargs)
