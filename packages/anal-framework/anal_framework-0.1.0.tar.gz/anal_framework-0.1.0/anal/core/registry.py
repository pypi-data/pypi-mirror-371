"""
App registry for managing installed ANAL applications.

This module provides functionality for loading, managing, and configuring
ANAL applications and plugins.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from anal.core.exceptions import ANALException, AppRegistryError


logger = logging.getLogger(__name__)


class AppConfig:
    """
    Configuration class for ANAL applications.
    
    Each ANAL app should define an AppConfig class that inherits from this.
    """
    
    name: str = None
    verbose_name: str = None
    description: str = None
    version: str = "1.0.0"
    author: str = None
    license: str = None
    dependencies: List[str] = []
    default_auto_field: str = "anal.db.fields.AutoField"
    
    def __init__(self, app_name: str, app_module):
        """
        Initialize app config.
        
        Args:
            app_name: Application name
            app_module: Application module
        """
        self.name = app_name
        self.module = app_module
        self.apps = None  # Will be set by registry
        
        if not self.verbose_name:
            self.verbose_name = self.name.replace('_', ' ').title()
    
    def ready(self) -> None:
        """
        Called when the app is ready.
        
        Override this method to perform app initialization tasks.
        """
        pass
    
    def get_models(self) -> List[Type]:
        """Get all models defined in this app."""
        models = []
        
        try:
            models_module = importlib.import_module(f"{self.name}.models")
            
            for name in dir(models_module):
                obj = getattr(models_module, name)
                if (inspect.isclass(obj) and 
                    hasattr(obj, '__module__') and 
                    obj.__module__ == models_module.__name__ and
                    hasattr(obj, '_meta')):  # Duck typing for Model classes
                    models.append(obj)
        except ImportError:
            pass
        
        return models
    
    def get_admin_classes(self) -> List[Type]:
        """Get all admin classes defined in this app."""
        admin_classes = []
        
        try:
            admin_module = importlib.import_module(f"{self.name}.admin")
            
            for name in dir(admin_module):
                obj = getattr(admin_module, name)
                if (inspect.isclass(obj) and 
                    hasattr(obj, '__module__') and 
                    obj.__module__ == admin_module.__name__ and
                    name.endswith('Admin')):
                    admin_classes.append(obj)
        except ImportError:
            pass
        
        return admin_classes
    
    def get_api_classes(self) -> List[Type]:
        """Get all API classes defined in this app."""
        api_classes = []
        
        try:
            api_module = importlib.import_module(f"{self.name}.api")
            
            for name in dir(api_module):
                obj = getattr(api_module, name)
                if (inspect.isclass(obj) and 
                    hasattr(obj, '__module__') and 
                    obj.__module__ == api_module.__name__):
                    api_classes.append(obj)
        except ImportError:
            pass
        
        return api_classes
    
    def __repr__(self) -> str:
        return f"<AppConfig: {self.verbose_name}>"


class AppRegistry:
    """
    Registry for managing ANAL applications.
    
    This class is responsible for:
    - Loading and configuring apps
    - Managing app dependencies
    - Providing access to app metadata and components
    - Handling app lifecycle events
    """
    
    def __init__(self):
        """Initialize the app registry."""
        self.app_configs: Dict[str, AppConfig] = {}
        self.apps_ready = False
        self._loading = False
    
    def populate(self, installed_apps: List[str]) -> None:
        """
        Populate the registry with installed apps.
        
        Args:
            installed_apps: List of app names to load
        """
        if self._loading:
            raise AppRegistryError("Apps are already being loaded")
        
        self._loading = True
        
        try:
            # Load all apps
            for app_name in installed_apps:
                self.load_app(app_name)
            
            # Check dependencies
            self._check_dependencies()
            
            # Initialize apps in dependency order
            self._initialize_apps()
            
            self.apps_ready = True
            logger.info(f"Loaded {len(self.app_configs)} apps successfully")
            
        except Exception as e:
            logger.error(f"Failed to populate apps: {e}")
            raise
        finally:
            self._loading = False
    
    def load_app(self, app_name: str) -> AppConfig:
        """
        Load a single app.
        
        Args:
            app_name: Name of the app to load
            
        Returns:
            App configuration instance
        """
        if app_name in self.app_configs:
            return self.app_configs[app_name]
        
        try:
            # Import the app module
            app_module = importlib.import_module(app_name)
            
            # Look for AppConfig
            app_config = self._find_app_config(app_name, app_module)
            
            # Register the app
            self.app_configs[app_name] = app_config
            app_config.apps = self
            
            logger.debug(f"Loaded app: {app_name}")
            return app_config
            
        except ImportError as e:
            raise AppRegistryError(f"Failed to import app '{app_name}': {e}")
        except Exception as e:
            raise AppRegistryError(f"Failed to load app '{app_name}': {e}")
    
    def _find_app_config(self, app_name: str, app_module) -> AppConfig:
        """Find and instantiate AppConfig for an app."""
        # Look for AppConfig class in the module
        for name in dir(app_module):
            obj = getattr(app_module, name)
            if (inspect.isclass(obj) and 
                issubclass(obj, AppConfig) and 
                obj is not AppConfig):
                return obj(app_name, app_module)
        
        # Look for apps.py module
        try:
            apps_module = importlib.import_module(f"{app_name}.apps")
            for name in dir(apps_module):
                obj = getattr(apps_module, name)
                if (inspect.isclass(obj) and 
                    issubclass(obj, AppConfig) and 
                    obj is not AppConfig):
                    return obj(app_name, app_module)
        except ImportError:
            pass
        
        # Create default AppConfig
        return AppConfig(app_name, app_module)
    
    def _check_dependencies(self) -> None:
        """Check that all app dependencies are satisfied."""
        for app_name, app_config in self.app_configs.items():
            for dependency in app_config.dependencies:
                if dependency not in self.app_configs:
                    raise AppRegistryError(
                        f"App '{app_name}' depends on '{dependency}' which is not installed"
                    )
    
    def _initialize_apps(self) -> None:
        """Initialize apps in dependency order."""
        # Topological sort to handle dependencies
        sorted_apps = self._topological_sort()
        
        for app_name in sorted_apps:
            app_config = self.app_configs[app_name]
            try:
                app_config.ready()
                logger.debug(f"Initialized app: {app_name}")
            except Exception as e:
                logger.error(f"Failed to initialize app '{app_name}': {e}")
                raise AppRegistryError(f"App initialization failed: {e}")
    
    def _topological_sort(self) -> List[str]:
        """Sort apps by dependencies using topological sort."""
        # Build dependency graph
        graph = {}
        in_degree = {}
        
        for app_name, app_config in self.app_configs.items():
            graph[app_name] = app_config.dependencies
            in_degree[app_name] = 0
        
        # Calculate in-degrees
        for app_name, dependencies in graph.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Kahn's algorithm
        queue = [app for app, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            app = queue.pop(0)
            result.append(app)
            
            for neighbor in graph[app]:
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # Check for circular dependencies
        if len(result) != len(self.app_configs):
            raise AppRegistryError("Circular dependency detected in apps")
        
        return result
    
    def get_app_config(self, app_label: str) -> AppConfig:
        """
        Get app config by label.
        
        Args:
            app_label: App label/name
            
        Returns:
            App configuration
        """
        if app_label not in self.app_configs:
            raise AppRegistryError(f"No app with label '{app_label}' found")
        
        return self.app_configs[app_label]
    
    def get_app_configs(self) -> List[AppConfig]:
        """Get all app configurations."""
        return list(self.app_configs.values())
    
    def get_models(self, app_label: Optional[str] = None) -> List[Type]:
        """
        Get all models from apps.
        
        Args:
            app_label: Optional app label to filter by
            
        Returns:
            List of model classes
        """
        models = []
        
        if app_label:
            app_config = self.get_app_config(app_label)
            models.extend(app_config.get_models())
        else:
            for app_config in self.app_configs.values():
                models.extend(app_config.get_models())
        
        return models
    
    def get_model(self, app_label: str, model_name: str) -> Type:
        """
        Get a specific model by app and name.
        
        Args:
            app_label: App label
            model_name: Model name
            
        Returns:
            Model class
        """
        app_config = self.get_app_config(app_label)
        models = app_config.get_models()
        
        for model in models:
            if model.__name__.lower() == model_name.lower():
                return model
        
        raise AppRegistryError(f"Model '{model_name}' not found in app '{app_label}'")
    
    def has_app(self, app_label: str) -> bool:
        """Check if an app is registered."""
        return app_label in self.app_configs
    
    def is_ready(self) -> bool:
        """Check if all apps are loaded and ready."""
        return self.apps_ready
    
    def clear(self) -> None:
        """Clear all registered apps."""
        self.app_configs.clear()
        self.apps_ready = False
    
    def __iter__(self):
        """Iterate over app configs."""
        return iter(self.app_configs.values())
    
    def __len__(self):
        """Get number of registered apps."""
        return len(self.app_configs)
    
    def __contains__(self, app_label: str):
        """Check if app is registered using 'in' operator."""
        return self.has_app(app_label)
    
    def __repr__(self) -> str:
        return f"<AppRegistry(apps={len(self.app_configs)}, ready={self.apps_ready})>"


# Global app registry instance
apps = AppRegistry()


def get_app_registry() -> AppRegistry:
    """Get the global app registry."""
    return apps


def get_app_config(app_label: str) -> AppConfig:
    """Get app config from global registry."""
    return apps.get_app_config(app_label)


def get_models(app_label: Optional[str] = None) -> List[Type]:
    """Get models from global registry."""
    return apps.get_models(app_label)


def get_model(app_label: str, model_name: str) -> Type:
    """Get specific model from global registry."""
    return apps.get_model(app_label, model_name)
