"""
Command to create a new ANAL project.

This module provides functionality to scaffold a new ANAL project
with the standard directory structure and configuration files.
"""

import os
from pathlib import Path
from typing import Optional


def create_project(name: str, project_path: Path, template: Optional[str] = None) -> None:
    """
    Create a new ANAL project with standard structure.
    
    Args:
        name: Project name
        project_path: Path where to create the project
        template: Optional template name
    """
    # Create project directory
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create project structure
    create_project_structure(project_path, name)
    
    # Create configuration files
    create_config_files(project_path, name)
    
    # Create main application files
    create_main_app_files(project_path, name)
    
    # Create sample app
    create_sample_app(project_path)


def create_project_structure(project_path: Path, name: str) -> None:
    """Create the basic project directory structure."""
    
    # Main directories
    directories = [
        "",  # project root
        name,  # main project package
        f"{name}/apps",  # apps directory
        "static",  # static files
        "static/css",
        "static/js", 
        "static/images",
        "templates",  # template files
        "templates/base",
        "media",  # uploaded files
        "docs",  # documentation
        "tests",  # project-level tests
        "scripts",  # utility scripts
        "config",  # configuration files
        "requirements",  # requirements files
    ]
    
    for directory in directories:
        if directory:
            (project_path / directory).mkdir(parents=True, exist_ok=True)


def create_config_files(project_path: Path, name: str) -> None:
    """Create configuration files."""
    
    # Create .env file
    env_content = f"""# Environment variables for {name}
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=sqlite:///./db.sqlite3

# Cache
CACHE_URL=redis://localhost:6379/0

# Email (optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-password
# EMAIL_USE_TLS=True

# Security
CORS_ENABLED=True
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# API
API_PREFIX=/api
OPENAPI_TITLE={name.title()} API
OPENAPI_DESCRIPTION=API for {name} application
"""
    
    (project_path / ".env").write_text(env_content, encoding="utf-8")
    
    # Create settings.py
    settings_content = f'''"""
Settings for {name} project.

This file contains the main configuration for your ANAL application.
For more information see: https://docs.analframework.org/configuration/
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Application definition
INSTALLED_APPS = [
    # ANAL built-in apps
    "anal.auth",
    "anal.admin", 
    "anal.api",
    "anal.files",
    "anal.cache",
    "anal.tasks",
    
    # Your apps
    "{name}.apps.core",
    # Add your apps here
]

# Middleware
MIDDLEWARE = [
    "anal.security.middleware.SecurityMiddleware",
    "anal.http.middleware.RequestLoggingMiddleware",
    "anal.auth.middleware.AuthenticationMiddleware",
    "anal.http.middleware.ErrorHandlerMiddleware",
]

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")

# Cache
CACHE_URL = os.getenv("CACHE_URL")

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Templates
TEMPLATE_DIRS = [
    BASE_DIR / "templates",
]

# Security
CORS_ENABLED = True
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# API Configuration
API_PREFIX = "/api"
OPENAPI_TITLE = "{name.title()} API"
OPENAPI_DESCRIPTION = "API for {name} application"
OPENAPI_VERSION = "1.0.0"

# Logging
LOGGING = {{
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {{
        "console": {{
            "class": "logging.StreamHandler",
        }},
    }},
    "root": {{
        "handlers": ["console"],
    }},
}}
'''
    
    (project_path / "settings.py").write_text(settings_content, encoding="utf-8")
    
    # Create requirements files
    base_requirements = """# Base requirements for ANAL project
ANAL>=0.1.0
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
"""
    
    dev_requirements = """# Development requirements
-r base.txt
pytest>=7.4.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
black>=23.12.0
isort>=5.13.0
flake8>=6.1.0
mypy>=1.8.0
"""
    
    prod_requirements = """# Production requirements  
-r base.txt
gunicorn>=21.2.0
psycopg2-binary>=2.9.0
redis>=5.0.0
"""
    
    requirements_dir = project_path / "requirements"
    (requirements_dir / "base.txt").write_text(base_requirements, encoding="utf-8")
    (requirements_dir / "dev.txt").write_text(dev_requirements, encoding="utf-8")
    (requirements_dir / "prod.txt").write_text(prod_requirements, encoding="utf-8")
    
    # Create requirements.txt for backwards compatibility
    (project_path / "requirements.txt").write_text("-r requirements/dev.txt\\n", encoding="utf-8")


def create_main_app_files(project_path: Path, name: str) -> None:
    """Create main application files."""
    
    main_package = project_path / name
    
    # Create __init__.py
    init_content = f'''"""
{name} - ANAL Framework Project
"""

__version__ = "0.1.0"
'''
    
    (main_package / "__init__.py").write_text(init_content, encoding="utf-8")
    
    # Create main.py (application entry point)
    main_content = f'''"""
Main application module for {name}.

This is the entry point for your ANAL application.
"""

from anal import ANAL
from anal.core.config import Settings

# Import your apps and routes
from {name}.apps.core.routes import router as core_router

# Create the application
def create_app(settings_override=None) -> ANAL:
    """
    Application factory function.
    
    Args:
        settings_override: Optional settings override
        
    Returns:
        Configured ANAL application
    """
    # Load settings
    if settings_override:
        settings = Settings(**settings_override)
    else:
        # Load from settings.py
        import settings as settings_module
        settings_dict = {{
            k: v for k, v in vars(settings_module).items()
            if k.isupper() and not k.startswith('_')
        }}
        settings = Settings(**settings_dict)
    
    # Create application
    app = ANAL(
        title=settings.OPENAPI_TITLE,
        description=settings.OPENAPI_DESCRIPTION,
        debug=settings.DEBUG,
        settings=settings
    )
    
    # Include routers
    app.include_router(core_router, prefix="/api")
    
    # Add static files
    app.add_static_files("/static", "static")
    app.add_static_files("/media", "media")
    
    return app

# Create the main application instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
'''
    
    (main_package / "main.py").write_text(main_content, encoding="utf-8")
    
    # Create ASGI module
    asgi_content = f'''"""
ASGI config for {name} project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

from {name}.main import app

application = app
'''
    
    (main_package / "asgi.py").write_text(asgi_content, encoding="utf-8")
    
    # Create apps __init__.py
    (main_package / "apps" / "__init__.py").write_text("", encoding="utf-8")


def create_sample_app(project_path: Path) -> None:
    """Create a sample core app."""
    
    # Get project name from path
    project_name = project_path.name
    app_path = project_path / project_name / "apps" / "core"
    app_path.mkdir(parents=True, exist_ok=True)
    
    # Create app files
    files_to_create = {
        "__init__.py": "",
        
        "apps.py": f'''"""
Core app configuration.
"""

from anal.core.registry import AppConfig


class CoreConfig(AppConfig):
    name = "{project_name}.apps.core"
    verbose_name = "Core"
    description = "Core functionality for {project_name}"

default_app_config = "core.apps.CoreConfig"
''',
        
        "models.py": '''"""
Core models for the application.
"""

from anal.db import Model, fields


class BaseModel(Model):
    """Base model with common fields."""
    
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Example model
class Example(BaseModel):
    """Example model to demonstrate ANAL ORM."""
    
    title = fields.CharField(max_length=255)
    description = fields.TextField(blank=True)
    is_active = fields.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        table_name = "examples"
        ordering = ["-created_at"]
''',
        
        "routes.py": '''"""
Core routes for the application.
"""

from anal.http import Router, JsonResponse
from anal.http.controllers import APIController

router = Router()


class HomeController(APIController):
    """Home page controller."""
    
    async def index(self, request):
        """Home page endpoint."""
        return self.success_response({
            "message": "Welcome to ANAL Framework!",
            "version": "0.1.0",
            "docs": "/docs"
        })
    
    async def health(self, request):
        """Health check endpoint."""
        return self.success_response({
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z"
        })


# Register routes
home_controller = HomeController()

@router.get("/")
async def home(request):
    return await home_controller.index(request)

@router.get("/health")
async def health(request):
    return await home_controller.health(request)

@router.get("/hello/{name}")
async def hello(request):
    name = request.path_params.get("name", "World")
    return JsonResponse({"message": f"Hello, {name}!"})
''',
        
        "serializers.py": '''"""
Serializers for the core app.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExampleSerializer(BaseModel):
    """Serializer for Example model."""
    
    id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExampleCreateSerializer(BaseModel):
    """Serializer for creating Example instances."""
    
    title: str
    description: Optional[str] = ""
    is_active: bool = True
''',
        
        "admin.py": '''"""
Admin configuration for core models.
"""

from anal.admin import admin, ModelAdmin
from .models import Example


@admin.register(Example)
class ExampleAdmin(ModelAdmin):
    """Admin interface for Example model."""
    
    list_display = ["id", "title", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "description"]
    ordering = ["-created_at"]
''',
        
        "tests.py": '''"""
Tests for the core app.
"""

import pytest
from anal.test import TestCase
from .models import Example


class ExampleModelTests(TestCase):
    """Tests for Example model."""
    
    async def test_create_example(self):
        """Test creating an example."""
        example = await Example.objects.create(
            title="Test Example",
            description="This is a test"
        )
        
        assert example.id is not None
        assert example.title == "Test Example"
        assert example.is_active is True
    
    async def test_example_str(self):
        """Test Example string representation."""
        example = Example(title="Test Example")
        assert str(example) == "Test Example"


class HomeControllerTests(TestCase):
    """Tests for home controller."""
    
    async def test_home_endpoint(self):
        """Test home endpoint."""
        response = await self.client.get("/api/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data["data"]
    
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        response = await self.client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["status"] == "healthy"
    
    async def test_hello_endpoint(self):
        """Test hello endpoint."""
        response = await self.client.get("/api/hello/ANAL")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Hello, ANAL!"
'''
    }
    
    for filename, content in files_to_create.items():
        (app_path / filename).write_text(content, encoding="utf-8")


def create_additional_files(project_path: Path, name: str) -> None:
    """Create additional project files."""
    
    # Create .gitignore
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# ANAL specific
db.sqlite3
media/
staticfiles/
.DS_Store
"""
    
    (project_path / ".gitignore").write_text(gitignore_content, encoding="utf-8")
    
    # Create README.md
    readme_content = f"""# {name.title()}

A modern web application built with the ANAL Framework.

## Getting Started

### Prerequisites

- Python 3.12+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd {name}
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   anal-admin migrate
   ```

6. Create a superuser:
   ```bash
   anal-admin createsuperuser
   ```

7. Start the development server:
   ```bash
   anal-admin runserver
   ```

Visit http://127.0.0.1:8000 to see your application!

## Project Structure

```
{name}/
├── {name}/                 # Main project package
│   ├── apps/              # Application modules
│   │   └── core/          # Core app
│   ├── main.py           # Application entry point
│   └── asgi.py           # ASGI configuration
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
├── media/               # User-uploaded files
├── tests/               # Project-level tests
├── requirements/        # Dependency files
├── settings.py          # Project settings
└── .env                # Environment variables
```

## Development

### Running Tests

```bash
anal-admin test
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in your environment
2. Configure a production database
3. Set up static file serving
4. Configure your web server (nginx + gunicorn recommended)

### Docker

```bash
docker build -t {name} .
docker run -p 8000:8000 {name}
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
"""
    
    (project_path / "README.md").write_text(readme_content, encoding="utf-8")
    
    # Create Dockerfile
    dockerfile_content = f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy project
COPY . .

# Collect static files
RUN anal-admin collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "{name}.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
"""
    
    (project_path / "Dockerfile").write_text(dockerfile_content, encoding="utf-8")
    
    # Create docker-compose.yml
    compose_content = f"""version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - media_volume:/app/media
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://postgres:password@db:5432/{name}
      - CACHE_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB={name}
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
  media_volume:
"""
    
    (project_path / "docker-compose.yml").write_text(compose_content, encoding="utf-8")
