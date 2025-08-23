"""
User management commands for ANAL framework.
"""

import os
import sys
import getpass
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()


def create_superuser():
    """Create a superuser account."""
    try:
        # Try to import the full framework
        from anal.auth.models import User
        from anal.auth.managers import UserManager
        from anal.core.config import get_settings
        
        settings = get_settings()
        user_manager = UserManager(settings)
        
        console.print("[blue]Creating superuser account[/blue]")
        
        # Get user details
        username = Prompt.ask("Username")
        email = Prompt.ask("Email address")
        
        # Get password securely
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Password (again): ")
        
        if password != password_confirm:
            console.print("[red]Error: Passwords don't match[/red]")
            return
        
        # Create the user
        user = user_manager.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        console.print(f"[green]✓ Superuser '{username}' created successfully[/green]")
        
    except ImportError as e:
        console.print(f"[yellow]Full user system not available: {e}[/yellow]")
        _create_basic_superuser()


def _create_basic_superuser():
    """Create basic superuser in simplified mode."""
    
    console.print("[blue]Creating basic superuser configuration[/blue]")
    
    # Get user details
    username = Prompt.ask("Username", default="admin")
    email = Prompt.ask("Email address", default="admin@example.com")
    password = getpass.getpass("Password: ")
    
    # Create superuser config file
    superuser_config = {
        "username": username,
        "email": email,
        "password_hash": _hash_password(password),
        "is_superuser": True,
        "is_active": True
    }
    
    # Create auth directory
    auth_dir = Path("auth")
    auth_dir.mkdir(exist_ok=True)
    
    # Save superuser config
    import json
    superuser_file = auth_dir / "superuser.json"
    with open(superuser_file, 'w') as f:
        json.dump(superuser_config, f, indent=2)
    
    console.print(f"[green]✓ Superuser configuration saved to: {superuser_file}[/green]")
    console.print("[yellow]Note: This is a basic configuration. Full user management requires the complete framework.[/yellow]")


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt if available, otherwise basic hash."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    except ImportError:
        # Fallback to basic hash (not secure for production)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()


def list_users():
    """List all users."""
    try:
        from anal.auth.models import User
        from anal.auth.managers import UserManager
        from anal.core.config import get_settings
        
        settings = get_settings()
        user_manager = UserManager(settings)
        
        users = user_manager.list_users()
        
        if not users:
            console.print("[yellow]No users found[/yellow]")
            return
        
        from rich.table import Table
        
        table = Table(title="Users")
        table.add_column("ID", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Email", style="blue")
        table.add_column("Superuser", style="red")
        table.add_column("Active", style="yellow")
        table.add_column("Created", style="magenta")
        
        for user in users:
            table.add_row(
                str(user.id),
                user.username,
                user.email,
                "✓" if user.is_superuser else "✗",
                "✓" if user.is_active else "✗",
                user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
            )
        
        console.print(table)
        
    except ImportError:
        console.print("[yellow]User listing not available in simplified mode[/yellow]")


def change_password(username: str):
    """Change user password."""
    try:
        from anal.auth.models import User
        from anal.auth.managers import UserManager
        from anal.core.config import get_settings
        
        settings = get_settings()
        user_manager = UserManager(settings)
        
        # Find user
        user = user_manager.get_user_by_username(username)
        if not user:
            console.print(f"[red]User '{username}' not found[/red]")
            return
        
        # Get new password
        password = getpass.getpass("New password: ")
        password_confirm = getpass.getpass("New password (again): ")
        
        if password != password_confirm:
            console.print("[red]Error: Passwords don't match[/red]")
            return
        
        # Update password
        user_manager.set_password(user, password)
        console.print(f"[green]✓ Password changed for user '{username}'[/green]")
        
    except ImportError:
        console.print("[yellow]Password change not available in simplified mode[/yellow]")


def deactivate_user(username: str):
    """Deactivate a user account."""
    try:
        from anal.auth.models import User
        from anal.auth.managers import UserManager
        from anal.core.config import get_settings
        
        settings = get_settings()
        user_manager = UserManager(settings)
        
        # Find user
        user = user_manager.get_user_by_username(username)
        if not user:
            console.print(f"[red]User '{username}' not found[/red]")
            return
        
        # Confirm deactivation
        if not Confirm.ask(f"Are you sure you want to deactivate user '{username}'?"):
            console.print("[yellow]Cancelled[/yellow]")
            return
        
        # Deactivate user
        user_manager.deactivate_user(user)
        console.print(f"[green]✓ User '{username}' deactivated[/green]")
        
    except ImportError:
        console.print("[yellow]User deactivation not available in simplified mode[/yellow]")


def activate_user(username: str):
    """Activate a user account."""
    try:
        from anal.auth.models import User
        from anal.auth.managers import UserManager
        from anal.core.config import get_settings
        
        settings = get_settings()
        user_manager = UserManager(settings)
        
        # Find user
        user = user_manager.get_user_by_username(username)
        if not user:
            console.print(f"[red]User '{username}' not found[/red]")
            return
        
        # Activate user
        user_manager.activate_user(user)
        console.print(f"[green]✓ User '{username}' activated[/green]")
        
    except ImportError:
        console.print("[yellow]User activation not available in simplified mode[/yellow]")
