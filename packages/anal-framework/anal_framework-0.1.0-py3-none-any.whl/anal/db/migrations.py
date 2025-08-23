"""
Database migrations for ANAL framework.

This module provides database migration functionality similar to Django's
migration system for managing database schema changes.
"""

import os
import json
import hashlib
import importlib.util
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from pathlib import Path

from .connection import get_database
from .models import Model


class Migration:
    """Base migration class."""
    
    dependencies: List[str] = []
    operations: List['Operation'] = []
    
    def __init__(self):
        """Initialize migration."""
        self.name = self.__class__.__name__
    
    async def apply(self):
        """Apply the migration."""
        db = get_database()
        
        for operation in self.operations:
            await operation.apply(db)
    
    async def unapply(self):
        """Reverse the migration."""
        db = get_database()
        
        # Apply operations in reverse order
        for operation in reversed(self.operations):
            await operation.unapply(db)


class Operation:
    """Base operation class."""
    
    async def apply(self, db):
        """Apply the operation."""
        raise NotImplementedError
    
    async def unapply(self, db):
        """Reverse the operation."""
        raise NotImplementedError


class CreateTable(Operation):
    """Operation to create a table."""
    
    def __init__(self, name: str, fields: Dict[str, Any], options: Dict[str, Any] = None):
        """Initialize CreateTable operation."""
        self.name = name
        self.fields = fields
        self.options = options or {}
    
    async def apply(self, db):
        """Create the table."""
        # Build CREATE TABLE SQL
        field_definitions = []
        
        for field_name, field_info in self.fields.items():
            field_def = self._build_field_definition(field_name, field_info)
            field_definitions.append(field_def)
        
        sql = f"CREATE TABLE {self.name} ({', '.join(field_definitions)})"
        await db.execute(sql)
    
    async def unapply(self, db):
        """Drop the table."""
        sql = f"DROP TABLE {self.name}"
        await db.execute(sql)
    
    def _build_field_definition(self, name: str, field_info: Dict[str, Any]) -> str:
        """Build field definition SQL."""
        field_type = field_info.get('type', 'VARCHAR(255)')
        constraints = []
        
        if field_info.get('primary_key'):
            constraints.append('PRIMARY KEY')
        if field_info.get('unique'):
            constraints.append('UNIQUE')
        if not field_info.get('null', True):
            constraints.append('NOT NULL')
        if 'default' in field_info:
            default_value = field_info['default']
            if isinstance(default_value, str):
                constraints.append(f"DEFAULT '{default_value}'")
            else:
                constraints.append(f"DEFAULT {default_value}")
        
        constraint_str = ' ' + ' '.join(constraints) if constraints else ''
        return f"{name} {field_type}{constraint_str}"


class DropTable(Operation):
    """Operation to drop a table."""
    
    def __init__(self, name: str):
        """Initialize DropTable operation."""
        self.name = name
        # Store table info for rollback
        self.table_info = None
    
    async def apply(self, db):
        """Drop the table."""
        # TODO: Store table schema for rollback
        sql = f"DROP TABLE {self.name}"
        await db.execute(sql)
    
    async def unapply(self, db):
        """Recreate the table."""
        # TODO: Recreate table from stored schema
        pass


class AddField(Operation):
    """Operation to add a field to a table."""
    
    def __init__(self, table: str, name: str, field: Dict[str, Any]):
        """Initialize AddField operation."""
        self.table = table
        self.name = name
        self.field = field
    
    async def apply(self, db):
        """Add the field."""
        field_def = self._build_field_definition(self.name, self.field)
        sql = f"ALTER TABLE {self.table} ADD COLUMN {field_def}"
        await db.execute(sql)
    
    async def unapply(self, db):
        """Remove the field."""
        sql = f"ALTER TABLE {self.table} DROP COLUMN {self.name}"
        await db.execute(sql)
    
    def _build_field_definition(self, name: str, field_info: Dict[str, Any]) -> str:
        """Build field definition SQL."""
        field_type = field_info.get('type', 'VARCHAR(255)')
        constraints = []
        
        if not field_info.get('null', True):
            constraints.append('NOT NULL')
        if 'default' in field_info:
            default_value = field_info['default']
            if isinstance(default_value, str):
                constraints.append(f"DEFAULT '{default_value}'")
            else:
                constraints.append(f"DEFAULT {default_value}")
        
        constraint_str = ' ' + ' '.join(constraints) if constraints else ''
        return f"{name} {field_type}{constraint_str}"


class RemoveField(Operation):
    """Operation to remove a field from a table."""
    
    def __init__(self, table: str, name: str):
        """Initialize RemoveField operation."""
        self.table = table
        self.name = name
        # Store field info for rollback
        self.field_info = None
    
    async def apply(self, db):
        """Remove the field."""
        # TODO: Store field schema for rollback
        sql = f"ALTER TABLE {self.table} DROP COLUMN {self.name}"
        await db.execute(sql)
    
    async def unapply(self, db):
        """Add the field back."""
        # TODO: Recreate field from stored schema
        pass


class AlterField(Operation):
    """Operation to alter a field in a table."""
    
    def __init__(self, table: str, name: str, field: Dict[str, Any]):
        """Initialize AlterField operation."""
        self.table = table
        self.name = name
        self.field = field
        # Store old field info for rollback
        self.old_field = None
    
    async def apply(self, db):
        """Alter the field."""
        # TODO: Implementation depends on database backend
        pass
    
    async def unapply(self, db):
        """Revert field changes."""
        # TODO: Revert to old field definition
        pass


class CreateIndex(Operation):
    """Operation to create an index."""
    
    def __init__(self, table: str, fields: List[str], name: str = None, unique: bool = False):
        """Initialize CreateIndex operation."""
        self.table = table
        self.fields = fields
        self.name = name or f"idx_{table}_{'_'.join(fields)}"
        self.unique = unique
    
    async def apply(self, db):
        """Create the index."""
        index_type = "UNIQUE INDEX" if self.unique else "INDEX"
        fields_str = ', '.join(self.fields)
        sql = f"CREATE {index_type} {self.name} ON {self.table} ({fields_str})"
        await db.execute(sql)
    
    async def unapply(self, db):
        """Drop the index."""
        sql = f"DROP INDEX {self.name}"
        await db.execute(sql)


class DropIndex(Operation):
    """Operation to drop an index."""
    
    def __init__(self, name: str):
        """Initialize DropIndex operation."""
        self.name = name
        # Store index info for rollback
        self.index_info = None
    
    async def apply(self, db):
        """Drop the index."""
        sql = f"DROP INDEX {self.name}"
        await db.execute(sql)
    
    async def unapply(self, db):
        """Recreate the index."""
        # TODO: Recreate index from stored info
        pass


class RunSQL(Operation):
    """Operation to run raw SQL."""
    
    def __init__(self, sql: str, reverse_sql: str = None):
        """Initialize RunSQL operation."""
        self.sql = sql
        self.reverse_sql = reverse_sql
    
    async def apply(self, db):
        """Execute the SQL."""
        await db.execute(self.sql)
    
    async def unapply(self, db):
        """Execute reverse SQL."""
        if self.reverse_sql:
            await db.execute(self.reverse_sql)


class MigrationState:
    """Tracks applied migrations."""
    
    def __init__(self, migrations_dir: Path):
        """Initialize migration state."""
        self.migrations_dir = migrations_dir
        self.state_file = migrations_dir / '.migration_state.json'
        self.applied_migrations = self._load_state()
    
    def _load_state(self) -> List[str]:
        """Load migration state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return data.get('applied_migrations', [])
        return []
    
    def _save_state(self):
        """Save migration state to file."""
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        data = {
            'applied_migrations': self.applied_migrations,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_applied(self, migration_name: str) -> bool:
        """Check if migration is applied."""
        return migration_name in self.applied_migrations
    
    def mark_applied(self, migration_name: str):
        """Mark migration as applied."""
        if migration_name not in self.applied_migrations:
            self.applied_migrations.append(migration_name)
            self._save_state()
    
    def mark_unapplied(self, migration_name: str):
        """Mark migration as unapplied."""
        if migration_name in self.applied_migrations:
            self.applied_migrations.remove(migration_name)
            self._save_state()


class MigrationRunner:
    """Runs database migrations."""
    
    def __init__(self, migrations_dir: Path):
        """Initialize migration runner."""
        self.migrations_dir = Path(migrations_dir)
        self.state = MigrationState(self.migrations_dir)
    
    def discover_migrations(self) -> List[str]:
        """Discover migration files."""
        if not self.migrations_dir.exists():
            return []
        
        migration_files = []
        for file_path in self.migrations_dir.glob('*.py'):
            if file_path.name != '__init__.py':
                migration_files.append(file_path.stem)
        
        return sorted(migration_files)
    
    def load_migration(self, migration_name: str) -> Migration:
        """Load a migration class from file."""
        migration_file = self.migrations_dir / f"{migration_name}.py"
        
        spec = importlib.util.spec_from_file_location(migration_name, migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Migration class in module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Migration) and 
                attr != Migration):
                return attr()
        
        raise ValueError(f"No Migration class found in {migration_file}")
    
    async def migrate(self, target: str = None):
        """Apply migrations up to target."""
        migrations = self.discover_migrations()
        
        if target:
            # Apply migrations up to target
            try:
                target_index = migrations.index(target)
                migrations = migrations[:target_index + 1]
            except ValueError:
                raise ValueError(f"Migration '{target}' not found")
        
        for migration_name in migrations:
            if not self.state.is_applied(migration_name):
                print(f"Applying migration: {migration_name}")
                migration = self.load_migration(migration_name)
                await migration.apply()
                self.state.mark_applied(migration_name)
                print(f"Applied migration: {migration_name}")
    
    async def rollback(self, target: str):
        """Rollback migrations to target."""
        migrations = self.discover_migrations()
        
        try:
            target_index = migrations.index(target)
        except ValueError:
            raise ValueError(f"Migration '{target}' not found")
        
        # Get migrations to rollback (in reverse order)
        rollback_migrations = []
        for migration_name in reversed(migrations[target_index + 1:]):
            if self.state.is_applied(migration_name):
                rollback_migrations.append(migration_name)
        
        for migration_name in rollback_migrations:
            print(f"Rolling back migration: {migration_name}")
            migration = self.load_migration(migration_name)
            await migration.unapply()
            self.state.mark_unapplied(migration_name)
            print(f"Rolled back migration: {migration_name}")
    
    async def create_migration_table(self):
        """Create migration tracking table."""
        db = get_database()
        
        sql = """
        CREATE TABLE IF NOT EXISTS anal_migrations (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        await db.execute(sql)


def create_migration_file(
    name: str, 
    operations: List[Operation], 
    dependencies: List[str] = None,
    migrations_dir: Path = None
) -> Path:
    """Create a new migration file."""
    if migrations_dir is None:
        migrations_dir = Path.cwd() / 'migrations'
    
    migrations_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp prefix
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{name}.py"
    file_path = migrations_dir / filename
    
    # Generate migration content
    content = f'''"""
Migration: {name}
Created: {datetime.now().isoformat()}
"""

from anal.db.migrations import Migration, CreateTable, AddField, RemoveField, CreateIndex


class {name.title().replace('_', '')}Migration(Migration):
    """Migration: {name}"""
    
    dependencies = {dependencies or []}
    
    operations = [
        # Add your operations here
        # CreateTable('my_table', {{
        #     'id': {{'type': 'INTEGER PRIMARY KEY'}},
        #     'name': {{'type': 'VARCHAR(100)', 'null': False}},
        # }}),
    ]
'''
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return file_path


# Export main classes
__all__ = [
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
