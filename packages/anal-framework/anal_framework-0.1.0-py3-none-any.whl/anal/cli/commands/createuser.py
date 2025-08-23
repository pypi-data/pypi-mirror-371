"""
Create user command for ANAL CLI.
"""

import asyncio
import getpass
from typing import Optional

import typer
from rich.console import Console

from anal.auth import create_user, create_superuser

console = Console()


def createuser_command():
    """Create user command app."""
    app = typer.Typer(help="User management commands")
    
    @app.command()
    def create(
        username: str = typer.Argument(..., help="Username"),
        email: str = typer.Argument(..., help="Email address"),
        password: Optional[str] = typer.Option(None, "--password", "-p", help="Password"),
        first_name: Optional[str] = typer.Option(None, "--first-name", help="First name"),
        last_name: Optional[str] = typer.Option(None, "--last-name", help="Last name"),
        staff: bool = typer.Option(False, "--staff", help="Give staff permissions"),
        superuser: bool = typer.Option(False, "--superuser", help="Give superuser permissions"),
    ):
        """Create a new user."""
        
        async def create_user_async():
            # Get password if not provided
            if not password:
                password_input = getpass.getpass("Password: ")
                password_confirm = getpass.getpass("Password (again): ")
                
                if password_input != password_confirm:
                    console.print("[red]Passwords don't match[/red]")
                    raise typer.Exit(1)
                
                password_to_use = password_input
            else:
                password_to_use = password
            
            try:
                # Prepare extra fields
                extra_fields = {}
                if first_name:
                    extra_fields['first_name'] = first_name
                if last_name:
                    extra_fields['last_name'] = last_name
                if staff:
                    extra_fields['is_staff'] = True
                if superuser:
                    extra_fields['is_superuser'] = True
                
                # Create user
                if superuser:
                    user = await create_superuser(username, email, password_to_use, **extra_fields)
                    console.print(f"[green]Superuser '{username}' created successfully[/green]")
                else:
                    user = await create_user(username, email, password_to_use, **extra_fields)
                    console.print(f"[green]User '{username}' created successfully[/green]")
                
            except Exception as e:
                console.print(f"[red]Error creating user: {e}[/red]")
                raise typer.Exit(1)
        
        asyncio.run(create_user_async())
    
    @app.command()
    def createsuperuser(
        username: Optional[str] = typer.Option(None, "--username", help="Username"),
        email: Optional[str] = typer.Option(None, "--email", help="Email address"),
        noinput: bool = typer.Option(False, "--noinput", help="Don't prompt for input"),
    ):
        """Create a superuser."""
        
        async def create_superuser_async():
            # Get username if not provided
            if not username and not noinput:
                username_input = typer.prompt("Username")
            else:
                username_input = username
            
            # Get email if not provided  
            if not email and not noinput:
                email_input = typer.prompt("Email address")
            else:
                email_input = email
            
            # Get password
            if not noinput:
                password_input = getpass.getpass("Password: ")
                password_confirm = getpass.getpass("Password (again): ")
                
                if password_input != password_confirm:
                    console.print("[red]Passwords don't match[/red]")
                    raise typer.Exit(1)
            else:
                console.print("[red]Password required when using --noinput[/red]")
                raise typer.Exit(1)
            
            try:
                user = await create_superuser(username_input, email_input, password_input)
                console.print(f"[green]Superuser '{username_input}' created successfully[/green]")
                
            except Exception as e:
                console.print(f"[red]Error creating superuser: {e}[/red]")
                raise typer.Exit(1)
        
        asyncio.run(create_superuser_async())
    
    @app.command()  
    def changepassword(
        username: str = typer.Argument(..., help="Username"),
        password: Optional[str] = typer.Option(None, "--password", "-p", help="New password"),
    ):
        """Change user password."""
        
        async def change_password_async():
            # Get password if not provided
            if not password:
                password_input = getpass.getpass("New password: ")
                password_confirm = getpass.getpass("New password (again): ")
                
                if password_input != password_confirm:
                    console.print("[red]Passwords don't match[/red]")
                    raise typer.Exit(1)
                
                password_to_use = password_input
            else:
                password_to_use = password
            
            try:
                from anal.auth import get_user_by_username, change_password
                
                user = await get_user_by_username(username)
                await change_password(user, password_to_use)
                
                console.print(f"[green]Password changed for user '{username}'[/green]")
                
            except Exception as e:
                console.print(f"[red]Error changing password: {e}[/red]")
                raise typer.Exit(1)
        
        asyncio.run(change_password_async())
    
    return app
