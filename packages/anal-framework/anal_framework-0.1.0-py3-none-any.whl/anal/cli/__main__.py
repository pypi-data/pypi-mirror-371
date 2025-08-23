#!/usr/bin/env python3
"""
Minimal CLI entry point for ANAL framework.

This module provides a lightweight entry point that avoids importing
the full framework until needed.
"""

def main():
    """Main CLI entry point."""
    try:
        # Only import what we need to avoid circular dependencies
        import sys
        import os
        from pathlib import Path
        
        # Import typer and rich separately to avoid framework imports
        import typer
        from rich.console import Console
        
        console = Console()
        
        # Create a minimal app
        app = typer.Typer(
            name="anal-admin",
            help="ANAL Framework - Command Line Interface",
            rich_markup_mode="rich"
        )
        
        @app.command()
        def startproject(
            name: str = typer.Argument(..., help="Project name"),
            directory: str = typer.Option(None, "--dir", "-d", help="Project directory"),
        ):
            """Create a new ANAL project."""
            try:
                from anal.cli.commands.startproject import create_project
                
                if directory is None:
                    directory = name
                
                project_path = Path(directory)
                
                if project_path.exists():
                    console.print(f"[red]Directory '{directory}' already exists[/red]")
                    raise typer.Exit(1)
                
                create_project(name, project_path, None)
                console.print(f"[green]Successfully created project '{name}' in '{directory}'[/green]")
                console.print(f"\nNext steps:")
                console.print(f"  cd {directory}")
                console.print(f"  anal-admin makemigrations auth")
                console.print(f"  anal-admin migrate")
                console.print(f"  anal-admin createsuperuser")
                console.print(f"  anal-admin runserver")
                
            except Exception as e:
                console.print(f"[red]Error creating project: {e}[/red]")
                raise typer.Exit(1)
        
        @app.command()
        def makemigrations(app_name: str = typer.Argument(None, help="App name for migrations")):
            """Create database migrations."""
            try:
                from anal.cli.commands.migration import make_migrations
                make_migrations(app_name)
            except ImportError as e:
                console.print(f"[yellow]Migration system not available: {e}[/yellow]")
                # Create basic migration structure
                migration_dir = Path("migrations")
                migration_dir.mkdir(exist_ok=True)
                (migration_dir / "__init__.py").touch()
                console.print(f"[green]Created migrations directory: {migration_dir}[/green]")
        
        @app.command()
        def migrate():
            """Apply database migrations."""
            try:
                from anal.cli.commands.migration import apply_migrations
                apply_migrations()
            except ImportError as e:
                console.print(f"[yellow]Migration system not available: {e}[/yellow]")
                console.print("Migration command not available in simplified mode")
        
        @app.command()
        def runserver(
            host: str = typer.Option("127.0.0.1", help="Server host"),
            port: int = typer.Option(8000, help="Server port"),
            reload: bool = typer.Option(False, help="Enable auto-reload"),
        ):
            """Start the development server."""
            try:
                from anal.cli.commands.runserver import run_server
                run_server(host=host, port=port, reload=reload)
            except ImportError as e:
                console.print(f"[yellow]Runserver command not available: {e}[/yellow]")
                # Fallback to basic uvicorn
                try:
                    import uvicorn
                    # Look for main.py or asgi.py
                    app_module = None
                    for possible_app in ["main:app", "asgi:application", f"{Path.cwd().name}.main:app", f"{Path.cwd().name}.asgi:application"]:
                        try:
                            # Test if module exists
                            module_name = possible_app.split(':')[0]
                            __import__(module_name)
                            app_module = possible_app
                            break
                        except ImportError:
                            continue
                    
                    if app_module:
                        console.print(f"[green]Starting server with {app_module}[/green]")
                        uvicorn.run(app_module, host=host, port=port, reload=reload)
                    else:
                        console.print("[red]No ASGI application found[/red]")
                except ImportError:
                    console.print("[red]Uvicorn not available[/red]")
        
        @app.command()
        def createsuperuser():
            """Create a superuser account."""
            try:
                from anal.cli.commands.user import create_superuser
                create_superuser()
            except ImportError as e:
                console.print(f"[yellow]User management not available: {e}[/yellow]")
                console.print("Superuser creation not available in simplified mode")
        
        @app.command()
        def shell():
            """Start an interactive shell."""
            try:
                from anal.cli.commands.shell import start_shell
                start_shell()
            except ImportError as e:
                console.print(f"[yellow]Shell command not available: {e}[/yellow]")
                # Fallback to basic Python shell
                import code
                code.interact(local=globals())
        
        @app.command()
        def version():
            """Show ANAL framework version."""
            console.print("ANAL Framework v0.1.0")
            console.print("A modern Python backend framework")
        
        @app.command()
        def info():
            """Show framework information."""
            console.print("[bold blue]ANAL Framework[/bold blue]")
            console.print("Version: 0.1.0")
            console.print("Description: Advanced Network Application Layer")
            console.print("Documentation: https://docs.analframework.org")
            console.print("Repository: https://github.com/analframework/anal")
        
        # Run the app
        app()
        
    except ImportError as e:
        print(f"Error importing CLI: {e}")
        print("Make sure ANAL framework is properly installed.")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
