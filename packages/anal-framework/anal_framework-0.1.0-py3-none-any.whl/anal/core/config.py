"""
Configuration management for ANAL framework

This module provides a comprehensive configuration system supporting
environment variables, settings files, and runtime configuration.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Main settings class for ANAL applications.
    
    This class automatically loads configuration from:
    1. Environment variables
    2. .env files
    3. settings.py files
    4. Default values
    
    Example:
        ```python
        from anal.core.config import Settings
        
        settings = Settings(
            DEBUG=True,
            DATABASE_URL="postgresql://user:pass@localhost/db"
        )
        ```
    """
    
    # Application settings
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    TESTING: bool = Field(default=False, description="Enable testing mode")
    SECRET_KEY: str = Field(default="", description="Secret key for cryptographic signing")
    
    # Server settings
    HOST: str = Field(default="127.0.0.1", description="Server host address")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    RELOAD: bool = Field(default=False, description="Enable auto-reload")
    
    # Application info
    APP_NAME: str = Field(default="ANAL Application", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_DESCRIPTION: str = Field(default="Built with ANAL Framework", description="Application description")
    
    # Database settings
    DATABASE_URL: str = Field(default="sqlite:///./app.db", description="Primary database URL")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")
    DATABASE_POOL_PRE_PING: bool = Field(default=True, description="Enable pool pre-ping")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, description="Pool recycle time in seconds")
    
    # Multiple database support
    DATABASES: Dict[str, str] = Field(default_factory=dict, description="Named database connections")
    
    # Cache settings
    CACHE_URL: Optional[str] = Field(default=None, description="Cache backend URL (Redis)")
    CACHE_DEFAULT_TIMEOUT: int = Field(default=300, description="Default cache timeout in seconds")
    CACHE_KEY_PREFIX: str = Field(default="anal:", description="Cache key prefix")
    
    # Security settings
    CORS_ENABLED: bool = Field(default=True, description="Enable CORS middleware")
    CORS_ORIGINS: List[str] = Field(default=["*"], description="Allowed CORS origins")
    CORS_METHODS: List[str] = Field(default=["*"], description="Allowed CORS methods")
    CORS_HEADERS: List[str] = Field(default=["*"], description="Allowed CORS headers")
    
    # JWT settings
    JWT_SECRET_KEY: Optional[str] = Field(default=None, description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="JWT access token expiry")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="JWT refresh token expiry")
    
    # Session settings
    SESSION_COOKIE_NAME: str = Field(default="anal_session", description="Session cookie name")
    SESSION_COOKIE_MAX_AGE: int = Field(default=1209600, description="Session cookie max age (2 weeks)")
    SESSION_COOKIE_SECURE: bool = Field(default=False, description="Secure session cookies")
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True, description="HTTP-only session cookies")
    SESSION_COOKIE_SAMESITE: str = Field(default="lax", description="SameSite policy for session cookies")
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Max upload size in bytes (10MB)")
    UPLOAD_PATH: str = Field(default="uploads", description="Upload directory path")
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".doc", ".docx"],
        description="Allowed file extensions for uploads"
    )
    
    # Static files settings
    STATIC_URL: str = Field(default="/static/", description="Static files URL prefix")
    STATIC_ROOT: Optional[str] = Field(default=None, description="Static files directory")
    MEDIA_URL: str = Field(default="/media/", description="Media files URL prefix")
    MEDIA_ROOT: Optional[str] = Field(default=None, description="Media files directory")
    
    # Template settings
    TEMPLATE_DIRS: List[str] = Field(default_factory=list, description="Template directories")
    TEMPLATE_AUTO_RELOAD: bool = Field(default=False, description="Auto-reload templates")
    
    # Internationalization
    LANGUAGE_CODE: str = Field(default="en-us", description="Default language code")
    TIME_ZONE: str = Field(default="UTC", description="Default timezone")
    USE_I18N: bool = Field(default=True, description="Enable internationalization")
    USE_TZ: bool = Field(default=True, description="Enable timezone support")
    LOCALE_PATHS: List[str] = Field(default_factory=list, description="Locale directories")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    LOG_MAX_SIZE: int = Field(default=10 * 1024 * 1024, description="Max log file size (10MB)")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Number of log backup files")
    
    # Email settings
    EMAIL_BACKEND: str = Field(default="smtp", description="Email backend")
    EMAIL_HOST: Optional[str] = Field(default=None, description="SMTP host")
    EMAIL_PORT: int = Field(default=587, description="SMTP port")
    EMAIL_USE_TLS: bool = Field(default=True, description="Use TLS for email")
    EMAIL_USE_SSL: bool = Field(default=False, description="Use SSL for email")
    EMAIL_HOST_USER: Optional[str] = Field(default=None, description="SMTP username")
    EMAIL_HOST_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    DEFAULT_FROM_EMAIL: str = Field(default="noreply@example.com", description="Default from email")
    
    # Task queue settings
    CELERY_BROKER_URL: Optional[str] = Field(default=None, description="Celery broker URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None, description="Celery result backend")
    CELERY_TASK_SERIALIZER: str = Field(default="json", description="Celery task serializer")
    CELERY_RESULT_SERIALIZER: str = Field(default="json", description="Celery result serializer")
    CELERY_ACCEPT_CONTENT: List[str] = Field(default=["json"], description="Celery accepted content types")
    CELERY_TIMEZONE: str = Field(default="UTC", description="Celery timezone")
    
    # API settings
    API_VERSION: str = Field(default="v1", description="Default API version")
    API_PREFIX: str = Field(default="/api", description="API URL prefix")
    OPENAPI_TITLE: Optional[str] = Field(default=None, description="OpenAPI documentation title")
    OPENAPI_DESCRIPTION: Optional[str] = Field(default=None, description="OpenAPI documentation description")
    OPENAPI_VERSION: str = Field(default="1.0.0", description="OpenAPI version")
    OPENAPI_URL: str = Field(default="/openapi.json", description="OpenAPI JSON endpoint")
    DOCS_URL: str = Field(default="/docs", description="Swagger UI documentation URL")
    REDOC_URL: str = Field(default="/redoc", description="ReDoc documentation URL")
    
    # Installed apps
    INSTALLED_APPS: List[str] = Field(
        default=[
            "anal.auth",
            "anal.admin", 
            "anal.api",
            "anal.files",
            "anal.cache",
            "anal.tasks"
        ],
        description="List of installed ANAL apps"
    )
    
    # Middleware classes
    MIDDLEWARE: List[str] = Field(
        default=[
            "anal.security.middleware.SecurityMiddleware",
            "anal.http.middleware.RequestLoggingMiddleware",
            "anal.auth.middleware.AuthenticationMiddleware",
            "anal.http.middleware.ErrorHandlerMiddleware"
        ],
        description="List of middleware classes"
    )
    
    # Custom settings
    CUSTOM_SETTINGS: Dict[str, Any] = Field(default_factory=dict, description="Custom application settings")
    
    @field_validator('CORS_ORIGINS', 'CORS_METHODS', 'CORS_HEADERS', mode='before')
    @classmethod
    def parse_cors_list(cls, v):
        """Parse CORS lists from string or keep as list."""
        if isinstance(v, str):
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated values
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    @field_validator('INSTALLED_APPS', 'MIDDLEWARE', mode='before')
    @classmethod
    def parse_app_list(cls, v):
        """Parse app/middleware lists from string or keep as list."""
        if isinstance(v, str):
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated values
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow additional fields
        
        # Environment variable prefixes
        env_prefix = "ANAL_"
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )
    
    def __init__(self, **kwargs):
        """Initialize settings with optional overrides."""
        super().__init__(**kwargs)
        
        # Auto-generate secret key if not provided
        if not self.SECRET_KEY:
            self.SECRET_KEY = self._generate_secret_key()
        
        # Set JWT secret key to main secret key if not provided
        if not self.JWT_SECRET_KEY:
            self.JWT_SECRET_KEY = self.SECRET_KEY
        
        # Setup default paths
        self._setup_default_paths()
    
    def _generate_secret_key(self) -> str:
        """Generate a random secret key."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _setup_default_paths(self) -> None:
        """Setup default file paths."""
        if not self.STATIC_ROOT:
            self.STATIC_ROOT = str(Path.cwd() / "static")
        
        if not self.MEDIA_ROOT:
            self.MEDIA_ROOT = str(Path.cwd() / "media")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value with optional default."""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        setattr(self, key, value)
    
    def update(self, **kwargs) -> None:
        """Update multiple settings."""
        for key, value in kwargs.items():
            self.set(key, value)
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.DEBUG
    
    def is_testing(self) -> bool:
        """Check if testing mode is enabled."""
        return self.TESTING
    
    def get_database_url(self, name: str = "default") -> Optional[str]:
        """Get database URL by name."""
        if name == "default":
            return self.DATABASE_URL
        return self.DATABASES.get(name)
    
    def add_database(self, name: str, url: str) -> None:
        """Add a named database connection."""
        self.DATABASES[name] = url
    
    def get_installed_apps(self) -> List[str]:
        """Get list of installed apps."""
        return self.INSTALLED_APPS.copy()
    
    def add_installed_app(self, app_name: str) -> None:
        """Add an app to installed apps."""
        if app_name not in self.INSTALLED_APPS:
            self.INSTALLED_APPS.append(app_name)
    
    def remove_installed_app(self, app_name: str) -> None:
        """Remove an app from installed apps."""
        if app_name in self.INSTALLED_APPS:
            self.INSTALLED_APPS.remove(app_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.dict()
    
    def __repr__(self) -> str:
        return f"<Settings(debug={self.DEBUG}, apps={len(self.INSTALLED_APPS)})>"


# Global settings instance (lazy initialization)
_settings = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def configure(settings_module: Optional[str] = None, **kwargs) -> Settings:
    """
    Configure the global settings.
    
    Args:
        settings_module: Python path to settings module
        **kwargs: Setting overrides
    
    Returns:
        Configured settings instance
    """
    global _settings
    
    if settings_module:
        # Import and apply settings from module
        import importlib
        module = importlib.import_module(settings_module)
        
        # Extract settings from module
        module_settings = {}
        for attr in dir(module):
            if attr.isupper() and not attr.startswith('_'):
                module_settings[attr] = getattr(module, attr)
        
        # Update with module settings
        kwargs.update(module_settings)
    
    # Create new settings instance with overrides
    _settings = Settings(**kwargs)
    return _settings


# Module-level settings access for backward compatibility
def __getattr__(name):
    if name == 'settings':
        return get_settings()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
