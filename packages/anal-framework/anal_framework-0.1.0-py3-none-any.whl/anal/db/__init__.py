"""
Database module for ANAL framework.

This module provides the complete ORM functionality including models,
connections, managers, and migrations.
"""

from .models import (
    Model,
    Field,
    CharField,
    TextField,
    IntegerField,
    FloatField,
    BooleanField,
    DateTimeField,
    DateField,
    TimeField,
    EmailField,
    URLField,
    SlugField,
    UUIDField,
    JSONField,
    ForeignKey,
    AutoField,
)

from .connection import (
    Database,
    QueryBuilder,
    DatabaseError,
    ConnectionError,
    QueryError,
    get_database,
    connect_database,
    disconnect_database,
)

from .managers import (
    QuerySet,
    Manager,
    DoesNotExist,
    MultipleObjectsReturned,
)

from .migrations import (
    Migration,
    Operation,
    CreateTable,
    DropTable,
    AddField,
    RemoveField,
    AlterField,
    CreateIndex,
    DropIndex,
    RunSQL,
    MigrationState,
    MigrationRunner,
    create_migration_file,
)


# Patch Model to include default manager
def _setup_model_manager():
    """Setup default manager for Model class."""
    # Add default objects manager to Model
    Model.objects = Manager(Model)
    
    # Patch ModelMeta to automatically add managers
    original_new = Model.__class__.__new__
    
    def patched_new(cls, name, bases, attrs, **kwargs):
        new_class = original_new(cls, name, bases, attrs, **kwargs)
        
        # Add default manager if not present
        if not hasattr(new_class, 'objects'):
            new_class.objects = Manager(new_class)
        
        return new_class
    
    Model.__class__.__new__ = staticmethod(patched_new)


# Setup model manager when module is imported
_setup_model_manager()


# Export convenience fields module
class fields:
    """Field types for model definitions."""
    CharField = CharField
    TextField = TextField
    IntegerField = IntegerField
    FloatField = FloatField
    BooleanField = BooleanField
    DateTimeField = DateTimeField
    DateField = DateField
    TimeField = TimeField
    EmailField = EmailField
    URLField = URLField
    SlugField = SlugField
    UUIDField = UUIDField
    JSONField = JSONField
    ForeignKey = ForeignKey
    AutoField = AutoField


# Export all components
__all__ = [
    # Models
    'Model',
    'Field',
    'fields',
    
    # Field types
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
    
    # Database
    'Database',
    'QueryBuilder',
    'DatabaseError',
    'ConnectionError',
    'QueryError',
    'get_database',
    'connect_database',
    'disconnect_database',
    
    # Managers
    'QuerySet',
    'Manager',
    'DoesNotExist',
    'MultipleObjectsReturned',
    
    # Migrations
    'Migration',
    'Operation',
    'CreateTable',
    'DropTable',
    'AddField',
    'RemoveField',
    'AlterField',
    'CreateIndex',
    'DropIndex',
    'RunSQL',
    'MigrationState',
    'MigrationRunner',
    'create_migration_file',
]
