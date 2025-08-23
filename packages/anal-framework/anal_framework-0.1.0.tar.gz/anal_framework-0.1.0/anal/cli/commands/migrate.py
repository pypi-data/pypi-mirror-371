"""
Database migration commands for ANAL CLI.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from anal.db.migrations import MigrationRunner

console = Console()


async def run_migrate(app_name: Optional[str] = None, migration: Optional[str] = None, fake: bool = False):
    """Run database migrations."""
    # Find migrations directory
    if app_name:
        migrations_dir = Path.cwd() / "apps" / app_name / "migrations"
    else:
        migrations_dir = Path.cwd() / "migrations"
    
    if not migrations_dir.exists():
        console.print(f"[yellow]No migrations directory found at {migrations_dir}[/yellow]")
        return
    
    runner = MigrationRunner(migrations_dir)
    
    try:
        # Ensure migration table exists
        await runner.create_migration_table()
        
        if migration:
            # Migrate to specific migration
            await runner.migrate(target=migration)
            console.print(f"[green]Applied migrations up to: {migration}[/green]")
        else:
            # Apply all pending migrations
            await runner.migrate()
            console.print("[green]Applied all pending migrations[/green]")
    
    except Exception as e:
        console.print(f"[red]Migration failed: {e}[/red]")
        raise typer.Exit(1)


async def show_migrations(app_name: Optional[str] = None):
    """Show migration status."""
    # Find migrations directory
    if app_name:
        migrations_dir = Path.cwd() / "apps" / app_name / "migrations"
    else:
        migrations_dir = Path.cwd() / "migrations"
    
    if not migrations_dir.exists():
        console.print(f"[yellow]No migrations directory found at {migrations_dir}[/yellow]")
        return
    
    runner = MigrationRunner(migrations_dir)
    migrations = runner.discover_migrations()
    
    table = Table(title="Migration Status")
    table.add_column("Migration")
    table.add_column("Status")
    
    for migration in migrations:
        status = "[green]Applied[/green]" if runner.state.is_applied(migration) else "[red]Pending[/red]"
        table.add_row(migration, status)
    
    console.print(table)


def migrate_command():
    """Create migrate command app."""
    app = typer.Typer(help="Database migration commands")
    
    @app.command()
    def apply(
        app_name: Optional[str] = typer.Argument(None, help="App name (optional)"),
        migration: Optional[str] = typer.Argument(None, help="Migration name (optional)"),
        fake: bool = typer.Option(False, "--fake", help="Mark migration as run without executing"),
    ):
        """Apply database migrations."""
        asyncio.run(run_migrate(app_name, migration, fake))
    
    @app.command()
    def rollback(
        app_name: Optional[str] = typer.Argument(None, help="App name"),
        target: str = typer.Argument(..., help="Target migration"),
    ):
        """Rollback migrations to target."""
        async def run_rollback():
            if app_name:
                migrations_dir = Path.cwd() / "apps" / app_name / "migrations"
            else:
                migrations_dir = Path.cwd() / "migrations"
            
            if not migrations_dir.exists():
                console.print(f"[yellow]No migrations directory found at {migrations_dir}[/yellow]")
                return
            
            runner = MigrationRunner(migrations_dir)
            
            try:
                await runner.rollback(target)
                console.print(f"[green]Rolled back to: {target}[/green]")
            except Exception as e:
                console.print(f"[red]Rollback failed: {e}[/red]")
                raise typer.Exit(1)
        
        asyncio.run(run_rollback())
    
    @app.command()
    def status(
        app_name: Optional[str] = typer.Argument(None, help="App name (optional)"),
    ):
        """Show migration status."""
        asyncio.run(show_migrations(app_name))
    
    return app
