"""
Command Line Interface for ANAL framework.

This module provides the main CLI entry point and command management
for the ANAL framework, similar to Django's manage.py and Laravel's artisan.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import typer
from rich.console import Console
from rich.table import Table

from anal.core.config import Settings, get_settings


# Initialize console for rich output
console = Console()
app = typer.Typer(
    name="anal-admin",
    help="ANAL Framework command line interface",
    add_completion=False
)


def get_project_settings() -> Optional[Settings]:
    """Get settings from the current project if available."""
    try:
        # Look for settings.py in current directory
        if Path("settings.py").exists():
            sys.path.insert(0, str(Path.cwd()))
            import settings
            return Settings(**{
                k: v for k, v in vars(settings).items()
                if k.isupper() and not k.startswith('_')
            })
        
        # Look for .env file
        if Path(".env").exists():
            return Settings(_env_file=".env")
        
        # Return default settings
        return Settings()
    except Exception as e:
        console.print(f"[red]Error loading settings: {e}[/red]")
        return None


@app.command()
def startproject(
    name: str = typer.Argument(..., help="Project name"),
    directory: Optional[str] = typer.Option(None, "--dir", "-d", help="Project directory"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Project template"),
):
    """
    Create a new ANAL project.
    
    This command creates a new ANAL project with the standard directory
    structure and configuration files.
    """
    from anal.cli.commands.startproject import create_project
    
    if directory is None:
        directory = name
    
    project_path = Path(directory)
    
    if project_path.exists():
        console.print(f"[red]Directory '{directory}' already exists[/red]")
        raise typer.Exit(1)
    
    try:
        create_project(name, project_path, template)
        console.print(f"[green]Successfully created project '{name}' in '{directory}'[/green]")
        console.print("\nNext steps:")
        console.print(f"  cd {directory}")
        console.print("  anal-admin runserver")
    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def startapp(
    name: str = typer.Argument(..., help="App name"),
    directory: Optional[str] = typer.Option(None, "--dir", "-d", help="App directory"),
):
    """
    Create a new app within the current project.
    """
    from anal.cli.commands.startapp import create_app
    
    if directory is None:
        directory = name
    
    app_path = Path(directory)
    
    if app_path.exists():
        console.print(f"[red]Directory '{directory}' already exists[/red]")
        raise typer.Exit(1)
    
    try:
        create_app(name, app_path)
        console.print(f"[green]Successfully created app '{name}' in '{directory}'[/green]")
        console.print(f"\nDon't forget to add '{name}' to INSTALLED_APPS in your settings!")
    except Exception as e:
        console.print(f"[red]Error creating app: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def runserver(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host address"),
    port: int = typer.Option(8000, "--port", "-p", help="Port number"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of worker processes"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """
    Run the development server.
    """
    from anal.cli.commands.runserver import run_development_server
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    # Override settings with command line options
    if debug:
        settings.DEBUG = True
    
    try:
        run_development_server(
            host=host,
            port=port,
            reload=reload or settings.DEBUG,
            workers=workers,
            settings=settings
        )
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def shell():
    """
    Start an interactive Python shell with project context.
    """
    from anal.cli.commands.shell import start_shell
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        start_shell(settings)
    except Exception as e:
        console.print(f"[red]Error starting shell: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def makemigrations(
    app_name: Optional[str] = typer.Argument(None, help="App name (optional)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Migration name"),
    empty: bool = typer.Option(False, "--empty", help="Create empty migration"),
):
    """
    Create database migrations.
    """
    from anal.cli.commands.migrations import make_migrations
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        make_migrations(settings, app_name, name, empty)
        console.print("[green]Migrations created successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error creating migrations: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def migrate(
    app_name: Optional[str] = typer.Argument(None, help="App name (optional)"),
    migration: Optional[str] = typer.Argument(None, help="Migration name (optional)"),
    fake: bool = typer.Option(False, "--fake", help="Mark migration as run without executing"),
):
    """
    Apply database migrations.
    """
    from anal.cli.commands.migrations import apply_migrations
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        apply_migrations(settings, app_name, migration, fake)
        console.print("[green]Migrations applied successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error applying migrations: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def test(
    app_name: Optional[str] = typer.Argument(None, help="App name to test (optional)"),
    pattern: str = typer.Option("test_*.py", "--pattern", "-p", help="Test file pattern"),
    verbosity: int = typer.Option(1, "--verbosity", "-v", help="Verbosity level"),
    coverage: bool = typer.Option(False, "--coverage", help="Run with coverage"),
):
    """
    Run tests.
    """
    from anal.cli.commands.test import run_tests
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        success = run_tests(settings, app_name, pattern, verbosity, coverage)
        if success:
            console.print("[green]All tests passed[/green]")
        else:
            console.print("[red]Some tests failed[/red]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error running tests: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def collectstatic(
    no_input: bool = typer.Option(False, "--noinput", help="Do not prompt for input"),
    clear: bool = typer.Option(False, "--clear", help="Clear existing static files"),
):
    """
    Collect static files for deployment.
    """
    from anal.cli.commands.collectstatic import collect_static_files
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        collect_static_files(settings, no_input, clear)
        console.print("[green]Static files collected successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error collecting static files: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def createsuperuser():
    """
    Create a superuser account.
    """
    from anal.cli.commands.createsuperuser import create_superuser
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        create_superuser(settings)
        console.print("[green]Superuser created successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error creating superuser: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def showurls():
    """
    Display all registered URL patterns.
    """
    from anal.cli.commands.showurls import show_urls
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        show_urls(settings)
    except Exception as e:
        console.print(f"[red]Error showing URLs: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def generate(
    generator: str = typer.Argument(..., help="Generator type (model, controller, api, etc.)"),
    name: str = typer.Argument(..., help="Name of the component to generate"),
    app: Optional[str] = typer.Option(None, "--app", "-a", help="App name"),
):
    """
    Generate code components (models, controllers, APIs, etc.).
    """
    from anal.cli.commands.generate import generate_component
    
    settings = get_project_settings()
    if settings is None:
        console.print("[red]Could not load project settings[/red]")
        raise typer.Exit(1)
    
    try:
        generate_component(generator, name, app, settings)
        console.print(f"[green]Successfully generated {generator} '{name}'[/green]")
    except Exception as e:
        console.print(f"[red]Error generating component: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """
    Show ANAL framework version information.
    """
    from anal import __version__, framework_info
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")
    
    table.add_row("ANAL Framework", __version__)
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Add dependency versions
    try:
        import uvicorn
        table.add_row("Uvicorn", uvicorn.__version__)
    except ImportError:
        pass
    
    try:
        import starlette
        table.add_row("Starlette", starlette.__version__)
    except ImportError:
        pass
    
    console.print(table)
    
    # Show features
    console.print("\n[bold]Features:[/bold]")
    for feature in framework_info["features"]:
        console.print(f"  ✓ {feature}")


def main():
    """Main CLI entry point."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
