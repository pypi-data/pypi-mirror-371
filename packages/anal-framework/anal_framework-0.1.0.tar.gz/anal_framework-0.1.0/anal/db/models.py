"""
Database models for ANAL framework.

This module provides the base Model class and field types for defining
database models with support for multiple database backends.
"""

from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime
import inspect


class ModelMeta(type):
    """Metaclass for Model classes."""
    
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__
        
        # Ensure initialization is only performed for subclasses of Model
        parents = [b for b in bases if isinstance(b, ModelMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        
        # Create the class
        new_class = super_new(cls, name, bases, attrs, **kwargs)
        
        # Process fields
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                fields[key] = value
                value.name = key
                value.model = new_class
        
        new_class._fields = fields
        
        # Process Meta options
        meta = attrs.get('Meta', None)
        if meta:
            new_class._meta = meta
        else:
            new_class._meta = type('Meta', (), {})
        
        # Set default table name if not specified
        if not hasattr(new_class._meta, 'table_name'):
            new_class._meta.table_name = name.lower() + 's'
        
        return new_class


class Model(metaclass=ModelMeta):
    """
    Base model class for all database models.
    
    Example:
        ```python
        from anal.db import Model, fields
        
        class User(Model):
            name = fields.CharField(max_length=100)
            email = fields.EmailField(unique=True)
            created_at = fields.DateTimeField(auto_now_add=True)
            
            class Meta:
                table_name = "users"
                ordering = ["-created_at"]
        ```
    """
    
    objects = None  # Will be set to a manager instance
    
    def __init__(self, **kwargs):
        """Initialize model instance."""
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name, field.get_default())
            setattr(self, field_name, value)
        
        # Set additional attributes
        for key, value in kwargs.items():
            if key not in self._fields:
                setattr(self, key, value)
    
    def save(self):
        """Save the model instance."""
        # This would be implemented with actual database operations
        pass
    
    async def asave(self):
        """Async save the model instance."""
        # This would be implemented with actual database operations
        pass
    
    def delete(self):
        """Delete the model instance."""
        # This would be implemented with actual database operations
        pass
    
    async def adelete(self):
        """Async delete the model instance."""
        # This would be implemented with actual database operations
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {}
        for field_name in self._fields:
            value = getattr(self, field_name, None)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[field_name] = value
        return result
    
    def __str__(self):
        """String representation of the model."""
        if hasattr(self, 'name'):
            return str(self.name)
        elif hasattr(self, 'title'):
            return str(self.title)
        elif hasattr(self, 'id'):
            return f"{self.__class__.__name__} {self.id}"
        else:
            return f"{self.__class__.__name__} object"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self}>"


class Field:
    """Base field class for model fields."""
    
    def __init__(
        self,
        default=None,
        null=False,
        blank=False,
        unique=False,
        db_index=False,
        help_text="",
        **kwargs
    ):
        self.default = default
        self.null = null
        self.blank = blank
        self.unique = unique
        self.db_index = db_index
        self.help_text = help_text
        self.name = None
        self.model = None
        
        # Store additional options
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def get_default(self):
        """Get the default value for this field."""
        if callable(self.default):
            return self.default()
        return self.default
    
    def validate(self, value):
        """Validate field value."""
        if value is None and not self.null:
            raise ValueError(f"Field '{self.name}' cannot be null")
        return value
    
    def to_python(self, value):
        """Convert value to Python type."""
        return value
    
    def to_db(self, value):
        """Convert value to database type."""
        return value


class CharField(Field):
    """Character field for storing strings."""
    
    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
    
    def validate(self, value):
        value = super().validate(value)
        if value and len(str(value)) > self.max_length:
            raise ValueError(f"Value too long for field '{self.name}' (max {self.max_length})")
        return value


class TextField(Field):
    """Text field for storing long strings."""
    pass


class IntegerField(Field):
    """Integer field."""
    
    def to_python(self, value):
        if value is None:
            return value
        return int(value)


class FloatField(Field):
    """Float field."""
    
    def to_python(self, value):
        if value is None:
            return value
        return float(value)


class BooleanField(Field):
    """Boolean field."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('default', False)
        super().__init__(**kwargs)
    
    def to_python(self, value):
        if value is None:
            return value
        return bool(value)


class DateTimeField(Field):
    """DateTime field."""
    
    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        
        if auto_now_add:
            kwargs['default'] = self._get_current_time
        
        super().__init__(**kwargs)
    
    def _get_current_time(self):
        return datetime.now()
    
    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, datetime):
            return value
        # Handle string parsing here
        return value


class DateField(Field):
    """Date field."""
    pass


class TimeField(Field):
    """Time field."""
    pass


class EmailField(CharField):
    """Email field with validation."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 254)
        super().__init__(**kwargs)
    
    def validate(self, value):
        value = super().validate(value)
        if value:
            # Basic email validation
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                raise ValueError(f"Invalid email format: {value}")
        return value


class URLField(CharField):
    """URL field with validation."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 2048)
        super().__init__(**kwargs)


class SlugField(CharField):
    """Slug field for URL-friendly strings."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 50)
        super().__init__(**kwargs)


class UUIDField(Field):
    """UUID field."""
    
    def __init__(self, **kwargs):
        import uuid
        kwargs.setdefault('default', uuid.uuid4)
        super().__init__(**kwargs)


class JSONField(Field):
    """JSON field for storing JSON data."""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('default', dict)
        super().__init__(**kwargs)


class ForeignKey(Field):
    """Foreign key field for model relationships."""
    
    def __init__(self, to, on_delete='CASCADE', related_name=None, **kwargs):
        super().__init__(**kwargs)
        self.to = to
        self.on_delete = on_delete
        self.related_name = related_name


class AutoField(IntegerField):
    """Auto-incrementing integer field (typically used for primary keys)."""
    
    def __init__(self, **kwargs):
        kwargs['unique'] = True
        kwargs['null'] = False
        super().__init__(**kwargs)


# Export field types for convenience
__all__ = [
    'Model',
    'Field',
    'CharField',
    'TextField', 
    'IntegerField',
    'FloatField',
    'BooleanField',
    'DateTimeField',
    'DateField',
    'TimeField',
    'EmailField',
    'URLField',
    'SlugField',
    'UUIDField',
    'JSONField',
    'ForeignKey',
    'AutoField',
]
