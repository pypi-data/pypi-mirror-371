"""
Dependency Injection Container for ANAL framework

This module implements a sophisticated dependency injection container
that supports singleton patterns, factory methods, and automatic
dependency resolution.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from anal.core.exceptions import ANALException


T = TypeVar('T')


class Container:
    """
    Dependency injection container for managing service instances
    and their lifecycles.
    
    The container supports:
    - Singleton registration
    - Factory registration 
    - Constructor injection
    - Interface binding
    - Circular dependency detection
    
    Example:
        ```python
        from anal.core.container import Container
        
        container = Container()
        
        # Register a singleton
        container.register("config", Config(), singleton=True)
        
        # Register a factory
        container.register("db", DatabaseConnection, singleton=False)
        
        # Resolve dependencies
        db = container.resolve("db")
        ```
    """
    
    def __init__(self):
        """Initialize the container."""
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._bindings: Dict[Type, str] = {}
        self._resolving: List[str] = []  # For circular dependency detection
    
    def register(
        self,
        name: str,
        service: Union[Any, Callable, Type],
        singleton: bool = True,
        interface: Optional[Type] = None
    ) -> None:
        """
        Register a service in the container.
        
        Args:
            name: Service name/identifier
            service: Service instance, factory function, or class
            singleton: Whether to treat as singleton
            interface: Optional interface type to bind to
        """
        if singleton:
            if inspect.isclass(service):
                # Register class as singleton factory
                self._factories[name] = service
                self._singletons[name] = None  # Will be lazily instantiated
            else:
                # Register instance as singleton
                self._singletons[name] = service
        else:
            if inspect.isclass(service) or callable(service):
                # Register as factory
                self._factories[name] = service
            else:
                raise ANALException(
                    f"Non-singleton service '{name}' must be a class or callable"
                )
        
        # Store service reference
        self._services[name] = service
        
        # Bind interface if provided
        if interface:
            self._bindings[interface] = name
    
    def register_singleton(self, name: str, service: Union[Any, Type]) -> None:
        """Register a singleton service."""
        self.register(name, service, singleton=True)
    
    def register_factory(self, name: str, factory: Union[Callable, Type]) -> None:
        """Register a factory service."""
        self.register(name, factory, singleton=False)
    
    def register_instance(self, name: str, instance: Any) -> None:
        """Register a service instance."""
        self._singletons[name] = instance
        self._services[name] = instance
    
    def bind(self, interface: Type, implementation: str) -> None:
        """Bind an interface to a service implementation."""
        self._bindings[interface] = implementation
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a service by name.
        
        Args:
            name: Service name to resolve
            
        Returns:
            Service instance
            
        Raises:
            ANALException: If service not found or circular dependency detected
        """
        # Check for circular dependencies
        if name in self._resolving:
            cycle = " -> ".join(self._resolving + [name])
            raise ANALException(f"Circular dependency detected: {cycle}")
        
        # Check if singleton already instantiated
        if name in self._singletons and self._singletons[name] is not None:
            return self._singletons[name]
        
        # Check if service is registered
        if name not in self._services:
            raise ANALException(f"Service '{name}' not registered")
        
        # Mark as resolving
        self._resolving.append(name)
        
        try:
            service = self._services[name]
            
            # If it's a factory, instantiate it
            if name in self._factories:
                instance = self._create_instance(self._factories[name])
                
                # Store as singleton if needed
                if name in self._singletons:
                    self._singletons[name] = instance
                
                return instance
            
            # Return the service as-is
            return service
            
        finally:
            # Remove from resolving list
            self._resolving.pop()
    
    def resolve_by_type(self, service_type: Type[T]) -> T:
        """
        Resolve a service by its type.
        
        Args:
            service_type: Type to resolve
            
        Returns:
            Service instance of the specified type
        """
        # Check if type is bound to a service
        if service_type in self._bindings:
            service_name = self._bindings[service_type]
            return self.resolve(service_name)
        
        # Look for service registered with type name
        type_name = service_type.__name__
        if type_name in self._services:
            return self.resolve(type_name)
        
        # Try to find service by checking instance types
        for name, service in self._services.items():
            if isinstance(service, service_type):
                return service
            
            # Check singleton instances
            if name in self._singletons and self._singletons[name] is not None:
                if isinstance(self._singletons[name], service_type):
                    return self._singletons[name]
        
        raise ANALException(f"No service registered for type '{service_type.__name__}'")
    
    def _create_instance(self, factory: Union[Callable, Type]) -> Any:
        """
        Create an instance using a factory, injecting dependencies.
        
        Args:
            factory: Factory function or class constructor
            
        Returns:
            Created instance
        """
        if inspect.isclass(factory):
            # Get constructor signature
            signature = inspect.signature(factory.__init__)
            parameters = list(signature.parameters.values())[1:]  # Skip 'self'
        else:
            # Get function signature
            signature = inspect.signature(factory)
            parameters = list(signature.parameters.values())
        
        # Resolve dependencies
        kwargs = {}
        for param in parameters:
            param_name = param.name
            param_type = param.annotation
            
            # Try to resolve by type first
            if param_type != inspect.Parameter.empty and param_type != Any:
                try:
                    kwargs[param_name] = self.resolve_by_type(param_type)
                    continue
                except ANALException:
                    pass
            
            # Try to resolve by name
            try:
                kwargs[param_name] = self.resolve(param_name)
            except ANALException:
                # Check if parameter has default value
                if param.default == inspect.Parameter.empty:
                    raise ANALException(
                        f"Cannot resolve dependency '{param_name}' for '{factory.__name__}'"
                    )
        
        # Create instance
        return factory(**kwargs)
    
    def has(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services
    
    def has_type(self, service_type: Type) -> bool:
        """Check if a service type is available."""
        try:
            self.resolve_by_type(service_type)
            return True
        except ANALException:
            return False
    
    def remove(self, name: str) -> None:
        """Remove a service from the container."""
        self._services.pop(name, None)
        self._singletons.pop(name, None)
        self._factories.pop(name, None)
        
        # Remove type bindings
        to_remove = []
        for interface, service_name in self._bindings.items():
            if service_name == name:
                to_remove.append(interface)
        
        for interface in to_remove:
            del self._bindings[interface]
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()
        self._bindings.clear()
        self._resolving.clear()
    
    def get_services(self) -> Dict[str, Any]:
        """Get all registered service names."""
        return self._services.copy()
    
    def get_singletons(self) -> Dict[str, Any]:
        """Get all instantiated singletons."""
        return {k: v for k, v in self._singletons.items() if v is not None}
    
    def __contains__(self, name: str) -> bool:
        """Check if service is registered using 'in' operator."""
        return self.has(name)
    
    def __getitem__(self, name: str) -> Any:
        """Get service using subscription operator."""
        return self.resolve(name)
    
    def __setitem__(self, name: str, service: Any) -> None:
        """Register service using subscription operator."""
        self.register_instance(name, service)
    
    def __repr__(self) -> str:
        return f"<Container(services={len(self._services)}, singletons={len(self._singletons)})>"


# Global container instance
_container = Container()


def get_container() -> Container:
    """Get the global container instance."""
    return _container


def register(name: str, service: Union[Any, Callable, Type], singleton: bool = True) -> None:
    """Register a service in the global container."""
    _container.register(name, service, singleton)


def resolve(name: str) -> Any:
    """Resolve a service from the global container."""
    return _container.resolve(name)


def resolve_by_type(service_type: Type[T]) -> T:
    """Resolve a service by type from the global container."""
    return _container.resolve_by_type(service_type)


def bind(interface: Type, implementation: str) -> None:
    """Bind an interface to implementation in the global container."""
    _container.bind(interface, implementation)


def inject(func: Callable) -> Callable:
    """
    Decorator for automatic dependency injection.
    
    Example:
        ```python
        @inject
        def my_handler(request, db: DatabaseManager, config: Settings):
            # Dependencies are automatically injected
            pass
        ```
    """
    signature = inspect.signature(func)
    
    def wrapper(*args, **kwargs):
        # Get function parameters
        bound_args = signature.bind_partial(*args, **kwargs)
        
        # Inject missing dependencies
        for param_name, param in signature.parameters.items():
            if param_name not in bound_args.arguments:
                param_type = param.annotation
                
                # Try to resolve by type
                if param_type != inspect.Parameter.empty and param_type != Any:
                    try:
                        bound_args.arguments[param_name] = resolve_by_type(param_type)
                        continue
                    except ANALException:
                        pass
                
                # Try to resolve by name
                try:
                    bound_args.arguments[param_name] = resolve(param_name)
                except ANALException:
                    # Skip if parameter has default value
                    if param.default == inspect.Parameter.empty:
                        raise ANALException(
                            f"Cannot inject dependency '{param_name}' in function '{func.__name__}'"
                        )
        
        return func(**bound_args.arguments)
    
    return wrapper
