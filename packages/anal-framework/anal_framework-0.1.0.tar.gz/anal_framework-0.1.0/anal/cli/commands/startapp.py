"""
Command to create a new ANAL app within a project.
"""

from pathlib import Path


def create_app(name: str, app_path: Path) -> None:
    """
    Create a new ANAL app with standard structure.
    
    Args:
        name: App name
        app_path: Path where to create the app
    """
    # Create app directory
    app_path.mkdir(parents=True, exist_ok=True)
    
    # Create app files
    create_app_files(app_path, name)


def create_app_files(app_path: Path, name: str) -> None:
    """Create the standard app files."""
    
    files_to_create = {
        "__init__.py": "",
        
        "apps.py": f'''"""
{name.title()} app configuration.
"""

from anal.core.registry import AppConfig


class {name.title()}Config(AppConfig):
    name = "{name}"
    verbose_name = "{name.title()}"
    description = "{name.title()} application"

default_app_config = "{name}.apps.{name.title()}Config"
''',
        
        "models.py": f'''"""
Models for the {name} app.
"""

from anal.db import Model, fields


class BaseModel(Model):
    """Base model with common fields."""
    
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Add your models here
''',
        
        "views.py": f'''"""
Views for the {name} app.
"""

from anal.http import JsonResponse
from anal.http.controllers import APIController, ViewController


class {name.title()}APIController(APIController):
    """API controller for {name}."""
    
    async def index(self, request):
        """List endpoint."""
        return self.success_response({{
            "message": "Welcome to {name} API"
        }})


class {name.title()}ViewController(ViewController):
    """View controller for {name}."""
    
    async def index(self, request):
        """Index page."""
        return self.render("{name}/index.html", {{
            "title": "{name.title()}"
        }})
''',
        
        "routes.py": f'''"""
Routes for the {name} app.
"""

from anal.http import Router
from .views import {name.title()}APIController, {name.title()}ViewController

router = Router()

# API routes
api_controller = {name.title()}APIController()
router.get("/api/{name}", api_controller.index, name="{name}_api_index")

# View routes
view_controller = {name.title()}ViewController()
router.get("/{name}", view_controller.index, name="{name}_index")
''',
        
        "serializers.py": f'''"""
Serializers for the {name} app.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Base{name.title()}Serializer(BaseModel):
    """Base serializer for {name} models."""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Add your serializers here
''',
        
        "admin.py": f'''"""
Admin configuration for {name} models.
"""

from anal.admin import admin, ModelAdmin

# Register your models here
# Example:
# from .models import YourModel
# 
# @admin.register(YourModel)
# class YourModelAdmin(ModelAdmin):
#     list_display = ["id", "name", "created_at"]
#     list_filter = ["created_at"]
#     search_fields = ["name"]
''',
        
        "tests.py": f'''"""
Tests for the {name} app.
"""

import pytest
from anal.test import TestCase


class {name.title()}Tests(TestCase):
    """Tests for {name} app."""
    
    async def test_api_index(self):
        """Test API index endpoint."""
        response = await self.client.get("/api/{name}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data["data"]
    
    async def test_view_index(self):
        """Test view index endpoint."""
        response = await self.client.get("/{name}")
        assert response.status_code == 200
''',
        
        "urls.py": f'''"""
URL patterns for the {name} app.

This file is for compatibility with Django-style URL patterns.
The preferred way in ANAL is to use routes.py.
"""

from .routes import router

urlpatterns = router.routes
''',
        
        "forms.py": f'''"""
Forms for the {name} app.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Base{name.title()}Form(BaseModel):
    """Base form for {name}."""
    pass


# Add your forms here
''',
        
        "services.py": f'''"""
Business logic services for the {name} app.
"""

from typing import Any, Dict, List, Optional


class {name.title()}Service:
    """Service class for {name} business logic."""
    
    def __init__(self):
        pass
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all items."""
        return []
    
    async def get_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get item by ID."""
        return None
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new item."""
        return data
    
    async def update(self, item_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing item."""
        return None
    
    async def delete(self, item_id: int) -> bool:
        """Delete item."""
        return False
''',
    }
    
    for filename, content in files_to_create.items():
        (app_path / filename).write_text(content, encoding="utf-8")
    
    # Create templates directory
    templates_dir = app_path / "templates" / name
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Create index template
    index_template = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{{{ title }}}} - ANAL Framework</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .info {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>{{{{ title }}}}</h1>
    
    <div class="info">
        <p>Welcome to the <strong>{name}</strong> app!</p>
        <p>This page was generated by the ANAL framework.</p>
    </div>
    
    <h2>Getting Started</h2>
    <ul>
        <li>Edit <code>{name}/views.py</code> to add your views</li>
        <li>Edit <code>{name}/models.py</code> to add your models</li>
        <li>Edit <code>{name}/routes.py</code> to add your routes</li>
        <li>Edit this template at <code>{name}/templates/{name}/index.html</code></li>
    </ul>
    
    <h2>API Endpoints</h2>
    <ul>
        <li><a href="/api/{name}">API Index</a></li>
    </ul>
    
    <h2>Documentation</h2>
    <ul>
        <li><a href="/docs">API Documentation (Swagger UI)</a></li>
        <li><a href="/redoc">API Documentation (ReDoc)</a></li>
    </ul>
</body>
</html>
'''
    
    (templates_dir / "index.html").write_text(index_template, encoding="utf-8")
    
    # Create static files directory
    static_dir = app_path / "static" / name
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Create CSS directory and basic stylesheet
    css_dir = static_dir / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    
    css_content = f'''/* Styles for {name} app */

.{name}-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

.{name}-header {{
    background: #3498db;
    color: white;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 20px;
}}

.{name}-card {{
    background: white;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
'''
    
    (css_dir / f"{name}.css").write_text(css_content, encoding="utf-8")
    
    # Create JS directory
    js_dir = static_dir / "js"
    js_dir.mkdir(parents=True, exist_ok=True)
    
    js_content = f'''// JavaScript for {name} app

document.addEventListener('DOMContentLoaded', function() {{
    console.log('{name.title()} app loaded');
    
    // Add your JavaScript code here
}});
'''
    
    (js_dir / f"{name}.js").write_text(js_content, encoding="utf-8")
