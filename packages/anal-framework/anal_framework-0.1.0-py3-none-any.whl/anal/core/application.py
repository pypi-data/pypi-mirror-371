"""
Core Application class - The heart of the ANAL framework

This module implements the main ANAL application class that orchestrates
all framework components following Clean Architecture principles.
"""

import asyncio
import inspect
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route, WebSocketRoute
from starlette.staticfiles import StaticFiles

from anal.core.config import Settings
from anal.core.container import Container
from anal.core.events import EventBus
from anal.core.exceptions import ANALException
from anal.core.registry import AppRegistry
from anal.http.middleware import MiddlewareStack
from anal.http.routing import Router
from anal.db.connection import get_database, connect_database, disconnect_database


logger = logging.getLogger(__name__)


class ANAL:
    """
    Main ANAL framework application class.
    
    This class serves as the central orchestrator for the entire framework,
    implementing dependency injection, plugin loading, and lifecycle management.
    
    Example:
        ```python
        from anal import ANAL, route
        
        app = ANAL(debug=True)
        
        @app.route('/')
        async def hello(request):
            return {'message': 'Hello, World!'}
            
        if __name__ == '__main__':
            app.run()
        ```
    """
    
    def __init__(
        self,
        debug: bool = False,
        settings: Optional[Settings] = None,
        title: str = "ANAL Application",
        description: str = "Built with ANAL Framework",
        version: str = "1.0.0",
        **kwargs
    ):
        """
        Initialize the ANAL application.
        
        Args:
            debug: Enable debug mode
            settings: Custom settings instance
            title: Application title
            description: Application description  
            version: Application version
            **kwargs: Additional configuration options
        """
        self.debug = debug
        self.title = title
        self.description = description
        self.version = version
        self.settings = settings or Settings()
        
        # Core components
        self.container = Container()
        self.event_bus = EventBus()
        self.router = Router()
        self.middleware_stack = MiddlewareStack()
        self.app_registry = AppRegistry()
        
        # Framework managers
        self.db = None
        
        # Internal state
        self._started = False
        self._starlette_app: Optional[Starlette] = None
        self._startup_tasks: List[Callable] = []
        self._shutdown_tasks: List[Callable] = []
        
        # Initialize core services
        self._initialize_core_services()
        
        # Setup default middleware
        self._setup_default_middleware()
        
        # Load installed apps
        self._load_installed_apps()
    
    def _initialize_core_services(self) -> None:
        """Initialize core framework services in the container."""
        # Register self as the main application
        self.container.register("app", self, singleton=True)
        self.container.register("settings", self.settings, singleton=True)
        self.container.register("event_bus", self.event_bus, singleton=True)
        self.container.register("router", self.router, singleton=True)
        
        # Initialize database if configured
        if self.settings.DATABASE_URL:
            self.db = get_database()
            self.container.register("db", self.db, singleton=True)
    
    def _setup_default_middleware(self) -> None:
        """Setup default middleware stack."""
        # CORS middleware
        if self.settings.CORS_ENABLED:
            self.middleware_stack.add(
                CORSMiddleware,
                allow_origins=self.settings.CORS_ORIGINS,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )
        
        # Session middleware
        if self.settings.SECRET_KEY:
            self.middleware_stack.add(
                SessionMiddleware,
                secret_key=self.settings.SECRET_KEY
            )
    
    def _load_installed_apps(self) -> None:
        """Load all installed apps from settings."""
        for app_name in self.settings.INSTALLED_APPS:
            try:
                self.app_registry.load_app(app_name)
                logger.info(f"Loaded app: {app_name}")
            except Exception as e:
                logger.error(f"Failed to load app {app_name}: {e}")
                if self.debug:
                    raise
    
    # Routing decorators and methods
    def route(
        self, 
        path: str, 
        methods: Optional[List[str]] = None,
        **kwargs
    ) -> Callable:
        """
        Decorator for registering routes.
        
        Args:
            path: URL path pattern
            methods: HTTP methods (default: ["GET"])
            **kwargs: Additional route options
        """
        return self.router.route(path, methods or ["GET"], **kwargs)
    
    def get(self, path: str, **kwargs) -> Callable:
        """Register a GET route."""
        return self.route(path, ["GET"], **kwargs)
    
    def post(self, path: str, **kwargs) -> Callable:
        """Register a POST route."""
        return self.route(path, ["POST"], **kwargs)
    
    def put(self, path: str, **kwargs) -> Callable:
        """Register a PUT route.""" 
        return self.route(path, ["PUT"], **kwargs)
    
    def delete(self, path: str, **kwargs) -> Callable:
        """Register a DELETE route."""
        return self.route(path, ["DELETE"], **kwargs)
    
    def patch(self, path: str, **kwargs) -> Callable:
        """Register a PATCH route."""
        return self.route(path, ["PATCH"], **kwargs)
    
    def websocket(self, path: str, **kwargs) -> Callable:
        """Register a WebSocket route."""
        return self.router.websocket(path, **kwargs)
    
    def include_router(self, router: "Router", prefix: str = "") -> None:
        """Include another router with optional prefix."""
        self.router.include_router(router, prefix=prefix)
    
    def add_middleware(self, middleware_class: Type, **kwargs) -> None:
        """Add middleware to the stack."""
        self.middleware_stack.add(middleware_class, **kwargs)
    
    def mount(self, path: str, app: Any, name: str = None) -> None:
        """Mount a sub-application."""
        self.router.mount(path, app, name=name)
    
    def add_static_files(
        self, 
        path: str, 
        directory: Union[str, Path],
        name: str = "static"
    ) -> None:
        """Add static file serving."""
        self.mount(path, StaticFiles(directory=str(directory)), name=name)
    
    # App lifecycle management
    def on_startup(self, func: Callable) -> Callable:
        """Register startup event handler."""
        self._startup_tasks.append(func)
        return func
    
    def on_shutdown(self, func: Callable) -> Callable:
        """Register shutdown event handler."""
        self._shutdown_tasks.append(func)
        return func
    
    async def startup(self) -> None:
        """Execute startup sequence."""
        if self._started:
            return
            
        logger.info("Starting ANAL application...")
        
        try:
            # Initialize database connections
            if self.db_manager:
                await self.db_manager.connect()
            
            # Execute custom startup tasks
            for task in self._startup_tasks:
                if asyncio.iscoroutinefunction(task):
                    await task()
                else:
                    task()
            
            # Emit startup event
            await self.event_bus.emit("app.startup", {"app": self})
            
            self._started = True
            logger.info("ANAL application started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise ANALException(f"Startup failed: {e}") from e
    
    async def shutdown(self) -> None:
        """Execute shutdown sequence."""
        if not self._started:
            return
            
        logger.info("Shutting down ANAL application...")
        
        try:
            # Emit shutdown event
            await self.event_bus.emit("app.shutdown", {"app": self})
            
            # Execute custom shutdown tasks
            for task in self._shutdown_tasks:
                if asyncio.iscoroutinefunction(task):
                    await task()
                else:
                    task()
            
            # Close database connections
            if self.db_manager:
                await self.db_manager.disconnect()
            
            self._started = False
            logger.info("ANAL application shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise ANALException(f"Shutdown failed: {e}") from e
    
    def create_asgi_app(self) -> Starlette:
        """Create the underlying Starlette ASGI application."""
        if self._starlette_app is not None:
            return self._starlette_app
        
        # Convert ANAL routes to Starlette routes
        routes = []
        for route in self.router.routes:
            if hasattr(route, 'endpoint'):
                routes.append(Route(
                    route.path,
                    endpoint=route.endpoint,
                    methods=route.methods,
                    name=getattr(route, 'name', None)
                ))
            elif hasattr(route, 'websocket_endpoint'):
                routes.append(WebSocketRoute(
                    route.path,
                    endpoint=route.websocket_endpoint,
                    name=getattr(route, 'name', None)
                ))
        
        # Create Starlette app with middleware
        self._starlette_app = Starlette(
            debug=self.debug,
            routes=routes,
            middleware=self.middleware_stack.build(),
            on_startup=[self.startup],
            on_shutdown=[self.shutdown]
        )
        
        return self._starlette_app
    
    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = None,
        workers: int = 1,
        **kwargs
    ) -> None:
        """
        Run the application using Uvicorn.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
            reload: Enable auto-reload (defaults to debug mode)
            workers: Number of worker processes
            **kwargs: Additional Uvicorn options
        """
        if reload is None:
            reload = self.debug
        
        app = self.create_asgi_app()
        
        logger.info(f"Starting server at http://{host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            **kwargs
        )
    
    def __call__(self, scope, receive, send):
        """ASGI interface."""
        app = self.create_asgi_app()
        return app(scope, receive, send)
    
    def __repr__(self) -> str:
        return f"<ANAL('{self.title}', debug={self.debug})>"
