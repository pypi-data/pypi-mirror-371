"""
Create database migrations command for ANAL CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

import typer
from rich.console import Console

from anal.db.migrations import create_migration_file, CreateTable, AddField

console = Console()


def make_migrations_command():
    """Create makemigrations command app."""
    app = typer.Typer(help="Create database migrations")
    
    @app.command()
    def create(
        app_name: Optional[str] = typer.Argument(None, help="App name"),
        name: Optional[str] = typer.Option(None, "--name", "-n", help="Migration name"),
        empty: bool = typer.Option(False, "--empty", help="Create empty migration"),
    ):
        """Create new migrations for model changes."""
        if app_name:
            migrations_dir = Path.cwd() / "apps" / app_name / "migrations"
        else:
            migrations_dir = Path.cwd() / "migrations"
        
        # Create migrations directory if it doesn't exist
        migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = migrations_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        
        # Generate migration name if not provided
        if not name:
            if empty:
                name = "empty_migration"
            else:
                name = "auto_migration"
        
        try:
            # For now, create an empty migration
            # In a full implementation, this would analyze model changes
            operations = []
            
            if not empty:
                # This is where you would detect model changes
                # For demonstration, we'll create a simple example
                console.print("[yellow]Auto-detection of model changes not yet implemented[/yellow]")
                console.print("[yellow]Creating empty migration...[/yellow]")
            
            migration_file = create_migration_file(
                name=name,
                operations=operations,
                dependencies=[],
                migrations_dir=migrations_dir
            )
            
            console.print(f"[green]Created migration: {migration_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error creating migration: {e}[/red]")
            raise typer.Exit(1)
    
    @app.command()
    def initial(
        app_name: str = typer.Argument(..., help="App name"),
    ):
        """Create initial migration for an app."""
        migrations_dir = Path.cwd() / "apps" / app_name / "migrations"
        
        # Create migrations directory if it doesn't exist
        migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = migrations_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        
        try:
            # Create initial migration with basic operations
            operations = [
                # Example table creation - this would be generated from models
            ]
            
            migration_file = create_migration_file(
                name="initial",
                operations=operations,
                dependencies=[],
                migrations_dir=migrations_dir
            )
            
            console.print(f"[green]Created initial migration: {migration_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error creating initial migration: {e}[/red]")
            raise typer.Exit(1)
    
    @app.command()
    def auth(
        migrations_dir: Optional[str] = typer.Option(None, "--dir", help="Migrations directory"),
    ):
        """Create migration for auth models."""
        if migrations_dir:
            migrations_path = Path(migrations_dir)
        else:
            migrations_path = Path.cwd() / "migrations"
        
        migrations_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = migrations_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        
        try:
            # Generate timestamp prefix
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_create_auth_tables.py"
            file_path = migrations_path / filename
            
            # Create auth migration content
            content = '''"""
Migration: Create auth tables
Created: {}
"""

from anal.db.migrations import Migration, CreateTable


class CreateAuthTablesMigration(Migration):
    """Migration: Create auth tables"""
    
    dependencies = []
    
    operations = [
        CreateTable('auth_users', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'username': {{'type': 'VARCHAR(150)', 'null': False, 'unique': True}},
            'email': {{'type': 'VARCHAR(254)', 'null': False, 'unique': True}},
            'password_hash': {{'type': 'VARCHAR(255)', 'null': False}},
            'first_name': {{'type': 'VARCHAR(30)', 'default': ''}},
            'last_name': {{'type': 'VARCHAR(30)', 'default': ''}},
            'is_active': {{'type': 'BOOLEAN', 'default': True}},
            'is_staff': {{'type': 'BOOLEAN', 'default': False}},
            'is_superuser': {{'type': 'BOOLEAN', 'default': False}},
            'date_joined': {{'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}},
            'last_login': {{'type': 'TIMESTAMP', 'null': True}},
        }}),
        
        CreateTable('auth_groups', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'name': {{'type': 'VARCHAR(150)', 'null': False, 'unique': True}},
            'description': {{'type': 'TEXT', 'default': ''}},
            'created_at': {{'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}},
        }}),
        
        CreateTable('auth_permissions', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'name': {{'type': 'VARCHAR(255)', 'null': False}},
            'content_type': {{'type': 'VARCHAR(100)', 'null': False}},
            'codename': {{'type': 'VARCHAR(100)', 'null': False}},
        }}),
        
        CreateTable('auth_user_groups', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'user_id': {{'type': 'INTEGER', 'null': False}},
            'group_id': {{'type': 'INTEGER', 'null': False}},
        }}),
        
        CreateTable('auth_user_permissions', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'user_id': {{'type': 'INTEGER', 'null': False}},
            'permission_id': {{'type': 'INTEGER', 'null': False}},
        }}),
        
        CreateTable('auth_group_permissions', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'group_id': {{'type': 'INTEGER', 'null': False}},
            'permission_id': {{'type': 'INTEGER', 'null': False}},
        }}),
        
        CreateTable('auth_sessions', {{
            'session_key': {{'type': 'VARCHAR(40)', 'primary_key': True}},
            'session_data': {{'type': 'TEXT', 'null': False}},
            'expire_date': {{'type': 'TIMESTAMP', 'null': False}},
        }}),
        
        CreateTable('auth_tokens', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'key': {{'type': 'VARCHAR(40)', 'null': False, 'unique': True}},
            'user_id': {{'type': 'INTEGER', 'null': False}},
            'name': {{'type': 'VARCHAR(100)', 'default': ''}},
            'created': {{'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}},
            'last_used': {{'type': 'TIMESTAMP', 'null': True}},
            'is_active': {{'type': 'BOOLEAN', 'default': True}},
        }}),
        
        CreateTable('auth_password_reset_tokens', {{
            'id': {{'type': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'primary_key': True}},
            'user_id': {{'type': 'INTEGER', 'null': False}},
            'token': {{'type': 'VARCHAR(100)', 'null': False, 'unique': True}},
            'created_at': {{'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}},
            'used_at': {{'type': 'TIMESTAMP', 'null': True}},
            'expires_at': {{'type': 'TIMESTAMP', 'null': False}},
        }}),
    ]
'''.format(datetime.now().isoformat())
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            console.print(f"[green]Created auth migration: {file_path}[/green]")
            console.print("[yellow]Run 'anal-admin migrate' to apply the migration[/yellow]")
            
        except Exception as e:
            console.print(f"[red]Error creating auth migration: {e}[/red]")
            raise typer.Exit(1)
    
    return app
