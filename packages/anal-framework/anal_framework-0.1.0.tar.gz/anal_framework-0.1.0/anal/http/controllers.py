"""
HTTP controllers for ANAL framework.

This module provides base controller classes that implement common patterns
for handling HTTP requests with clean architecture principles.
"""

import inspect
from typing import Any, Dict, List, Optional, Type, Union

from anal.core.container import inject
from anal.core.exceptions import ValidationError, NotFoundError
from anal.http.responses import JsonResponse, TemplateResponse, ErrorResponse


class Controller:
    """
    Base controller class for handling HTTP requests.
    
    Provides common functionality for request handling, validation,
    and response generation following clean architecture principles.
    
    Features:
    - Automatic dependency injection
    - Request validation
    - Response formatting
    - Error handling
    - Method-based routing
    
    Example:
        ```python
        from anal.http.controllers import Controller
        from anal.http.responses import JsonResponse
        
        class UserController(Controller):
            def __init__(self, user_service: UserService):
                self.user_service = user_service
            
            async def list(self, request):
                users = await self.user_service.get_all()
                return JsonResponse({'users': users})
            
            async def create(self, request):
                data = await self.validate_json(request, UserCreateSchema)
                user = await self.user_service.create(data)
                return JsonResponse({'user': user}, status_code=201)
        ```
    """
    
    def __init__(self):
        """Initialize the controller."""
        pass
    
    async def validate_json(self, request, schema: Type = None) -> Dict[str, Any]:
        """
        Validate JSON request body.
        
        Args:
            request: HTTP request object
            schema: Pydantic schema for validation
            
        Returns:
            Validated data dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            data = await request.json()
        except Exception as e:
            raise ValidationError("Invalid JSON data") from e
        
        if schema:
            try:
                # Use Pydantic for validation if schema provided
                validated = schema(**data)
                return validated.dict()
            except Exception as e:
                raise ValidationError(f"Validation failed: {str(e)}") from e
        
        return data
    
    async def validate_form(self, request, schema: Type = None) -> Dict[str, Any]:
        """
        Validate form data.
        
        Args:
            request: HTTP request object
            schema: Pydantic schema for validation
            
        Returns:
            Validated data dictionary
        """
        try:
            form = await request.form()
            data = dict(form)
        except Exception as e:
            raise ValidationError("Invalid form data") from e
        
        if schema:
            try:
                validated = schema(**data)
                return validated.dict()
            except Exception as e:
                raise ValidationError(f"Validation failed: {str(e)}") from e
        
        return data
    
    def get_query_params(self, request) -> Dict[str, Any]:
        """Get query parameters from request."""
        return dict(request.query_params)
    
    def get_path_params(self, request) -> Dict[str, Any]:
        """Get path parameters from request."""
        return getattr(request, 'path_params', {})
    
    def get_user(self, request):
        """Get authenticated user from request."""
        return getattr(request.state, 'user', None)
    
    def require_auth(self, request):
        """Require authentication for the request."""
        user = self.get_user(request)
        if not user:
            raise ValidationError("Authentication required", status_code=401)
        return user
    
    def paginate(self, request, default_page_size: int = 20) -> tuple[int, int, int]:
        """
        Get pagination parameters from request.
        
        Args:
            request: HTTP request object
            default_page_size: Default page size
            
        Returns:
            Tuple of (page, page_size, offset)
        """
        query_params = self.get_query_params(request)
        
        try:
            page = int(query_params.get('page', 1))
            page_size = int(query_params.get('page_size', default_page_size))
        except ValueError:
            raise ValidationError("Invalid pagination parameters")
        
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = default_page_size
        
        offset = (page - 1) * page_size
        return page, page_size, offset
    
    def get_ordering(self, request, allowed_fields: List[str] = None) -> List[str]:
        """
        Get ordering parameters from request.
        
        Args:
            request: HTTP request object
            allowed_fields: List of allowed ordering fields
            
        Returns:
            List of ordering fields
        """
        query_params = self.get_query_params(request)
        ordering = query_params.get('ordering', '').split(',')
        ordering = [field.strip() for field in ordering if field.strip()]
        
        if allowed_fields:
            # Filter to only allowed fields
            valid_ordering = []
            for field in ordering:
                # Handle descending order (-)
                if field.startswith('-'):
                    base_field = field[1:]
                else:
                    base_field = field
                
                if base_field in allowed_fields:
                    valid_ordering.append(field)
            
            ordering = valid_ordering
        
        return ordering
    
    def get_filters(self, request, allowed_fields: List[str] = None) -> Dict[str, Any]:
        """
        Get filter parameters from request.
        
        Args:
            request: HTTP request object
            allowed_fields: List of allowed filter fields
            
        Returns:
            Dictionary of filters
        """
        query_params = self.get_query_params(request)
        filters = {}
        
        for key, value in query_params.items():
            # Skip pagination and ordering params
            if key in ['page', 'page_size', 'ordering']:
                continue
            
            if allowed_fields and key not in allowed_fields:
                continue
            
            filters[key] = value
        
        return filters


class APIController(Controller):
    """
    Base controller for API endpoints.
    
    Extends Controller with API-specific functionality like
    automatic serialization and standardized responses.
    
    Example:
        ```python
        class UserAPIController(APIController):
            async def list(self, request):
                users = await self.user_service.get_all()
                return self.success_response(users)
            
            async def detail(self, request):
                user_id = self.get_path_params(request)['id']
                user = await self.user_service.get_by_id(user_id)
                if not user:
                    return self.not_found_response("User not found")
                return self.success_response(user)
        ```
    """
    
    def success_response(
        self,
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        **kwargs
    ) -> JsonResponse:
        """Create a standardized success response."""
        content = {
            "success": True,
            "message": message,
            "status_code": status_code
        }
        
        if data is not None:
            content["data"] = data
        
        return JsonResponse(content, status_code=status_code, **kwargs)
    
    def error_response(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> JsonResponse:
        """Create a standardized error response."""
        return ErrorResponse(message, status_code, error_code, details, **kwargs)
    
    def not_found_response(self, message: str = "Resource not found") -> JsonResponse:
        """Create a 404 Not Found response."""
        return self.error_response(message, status_code=404)
    
    def validation_error_response(self, message: str, details: Optional[Dict] = None) -> JsonResponse:
        """Create a 400 Bad Request response for validation errors."""
        return self.error_response(message, status_code=400, error_code="VALIDATION_ERROR", details=details)
    
    def unauthorized_response(self, message: str = "Authentication required") -> JsonResponse:
        """Create a 401 Unauthorized response."""
        return self.error_response(message, status_code=401, error_code="UNAUTHORIZED")
    
    def forbidden_response(self, message: str = "Access denied") -> JsonResponse:
        """Create a 403 Forbidden response."""
        return self.error_response(message, status_code=403, error_code="FORBIDDEN")
    
    def paginated_response(
        self,
        data: List[Any],
        page: int,
        page_size: int,
        total_count: int,
        **kwargs
    ) -> JsonResponse:
        """
        Create a paginated response.
        
        Args:
            data: List of items for current page
            page: Current page number
            page_size: Items per page
            total_count: Total number of items
            **kwargs: Additional response data
            
        Returns:
            Paginated JSON response
        """
        total_pages = (total_count + page_size - 1) // page_size
        
        content = {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
        
        content.update(kwargs)
        return JsonResponse(content)


class ViewController(Controller):
    """
    Base controller for rendering HTML views.
    
    Extends Controller with template rendering and view-specific functionality.
    
    Example:
        ```python
        class UserViewController(ViewController):
            async def list(self, request):
                users = await self.user_service.get_all()
                return self.render('users/list.html', {
                    'users': users,
                    'title': 'Users'
                })
            
            async def detail(self, request):
                user_id = self.get_path_params(request)['id']
                user = await self.user_service.get_by_id(user_id)
                if not user:
                    return self.render_error('User not found', status_code=404)
                return self.render('users/detail.html', {'user': user})
        ```
    """
    
    def render(
        self,
        template: str,
        context: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        **kwargs
    ) -> TemplateResponse:
        """
        Render a template with context.
        
        Args:
            template: Template file name
            context: Template context variables
            status_code: HTTP status code
            **kwargs: Additional template context
            
        Returns:
            Template response
        """
        if context is None:
            context = {}
        
        # Add additional kwargs to context
        context.update(kwargs)
        
        return TemplateResponse(template, context, status_code=status_code)
    
    def render_error(
        self,
        message: str,
        status_code: int = 400,
        template: str = "error.html"
    ) -> TemplateResponse:
        """Render an error page."""
        context = {
            "error_message": message,
            "status_code": status_code
        }
        return self.render(template, context, status_code=status_code)
    
    def redirect(self, url: str, status_code: int = 302):
        """Create a redirect response."""
        from anal.http.responses import RedirectResponse
        return RedirectResponse(url, status_code=status_code)


class ResourceController(APIController):
    """
    RESTful resource controller with CRUD operations.
    
    Provides standard CRUD methods following REST conventions:
    - GET /resource -> list()
    - POST /resource -> create()
    - GET /resource/{id} -> retrieve()
    - PUT /resource/{id} -> update()
    - PATCH /resource/{id} -> partial_update()
    - DELETE /resource/{id} -> destroy()
    
    Example:
        ```python
        class UserResourceController(ResourceController):
            def __init__(self, user_service: UserService):
                super().__init__()
                self.user_service = user_service
            
            async def list(self, request):
                page, page_size, offset = self.paginate(request)
                users, total = await self.user_service.get_paginated(offset, page_size)
                return self.paginated_response(users, page, page_size, total)
            
            async def create(self, request):
                data = await self.validate_json(request, UserCreateSchema)
                user = await self.user_service.create(data)
                return self.success_response(user, status_code=201)
        ```
    """
    
    async def list(self, request):
        """List all resources."""
        raise NotImplementedError("Subclasses must implement list()")
    
    async def create(self, request):
        """Create a new resource."""
        raise NotImplementedError("Subclasses must implement create()")
    
    async def retrieve(self, request):
        """Retrieve a specific resource."""
        raise NotImplementedError("Subclasses must implement retrieve()")
    
    async def update(self, request):
        """Update a specific resource (full update)."""
        raise NotImplementedError("Subclasses must implement update()")
    
    async def partial_update(self, request):
        """Partially update a specific resource."""
        raise NotImplementedError("Subclasses must implement partial_update()")
    
    async def destroy(self, request):
        """Delete a specific resource."""
        raise NotImplementedError("Subclasses must implement destroy()")


# Decorator for automatic dependency injection in controllers
def controller_method(func):
    """
    Decorator for controller methods to enable automatic dependency injection.
    
    Example:
        ```python
        class UserController(Controller):
            @controller_method
            async def create_user(self, request, user_service: UserService):
                # user_service is automatically injected
                pass
        ```
    """
    return inject(func)
