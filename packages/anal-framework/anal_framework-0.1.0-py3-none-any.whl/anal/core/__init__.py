"""Core module initialization."""

from anal.core.application import ANAL
from anal.core.config import Settings, get_settings, configure
from anal.core.container import Container, get_container, inject
from anal.core.events import EventBus, get_event_bus, on, once, emit
from anal.core.exceptions import *
from anal.core.registry import AppConfig, AppRegistry, apps, get_app_config

__all__ = [
    # Application
    "ANAL",
    
    # Configuration
    "Settings",
    "get_settings", 
    "configure",
    
    # Container
    "Container",
    "get_container",
    "inject",
    
    # Events
    "EventBus",
    "get_event_bus",
    "on",
    "once", 
    "emit",
    
    # Registry
    "AppConfig",
    "AppRegistry",
    "apps",
    "get_app_config",
]
