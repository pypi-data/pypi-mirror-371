"""
Interactive shell commands for ANAL framework.
"""

import os
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def start_shell():
    """Start an interactive shell with ANAL framework context."""
    try:
        # Try to import the full framework
        from anal.core.config import get_settings
        from anal.core.application import ANAL
        
        settings = get_settings()
        
        console.print("[blue]Starting ANAL framework shell...[/blue]")
        console.print("[green]Available objects:[/green]")
        console.print("  - settings: Application settings")
        console.print("  - ANAL: Framework application class")
        
        # Create shell context
        shell_context = {
            'settings': settings,
            'ANAL': ANAL,
            'os': os,
            'sys': sys,
            'Path': Path,
        }
        
        # Try to import models if available
        try:
            from anal.auth.models import User
            from anal.db.models import Base
            shell_context.update({
                'User': User,
                'Base': Base,
            })
            console.print("  - User: User model")
            console.print("  - Base: Database base model")
        except ImportError:
            pass
        
        # Start enhanced shell
        _start_enhanced_shell(shell_context)
        
    except ImportError as e:
        console.print(f"[yellow]Full framework not available: {e}[/yellow]")
        console.print("[blue]Starting basic Python shell...[/blue]")
        _start_basic_shell()


def _start_enhanced_shell(context: dict):
    """Start enhanced shell with framework context."""
    
    # Try IPython first
    try:
        from IPython import start_ipython
        console.print("[green]Starting IPython shell...[/green]")
        start_ipython(argv=[], user_ns=context)
        return
    except ImportError:
        pass
    
    # Try ptpython
    try:
        from ptpython.repl import embed
        console.print("[green]Starting ptpython shell...[/green]")
        embed(globals=context, locals=context)
        return
    except ImportError:
        pass
    
    # Fall back to basic shell
    console.print("[green]Starting basic Python shell...[/green]")
    import code
    code.interact(local=context)


def _start_basic_shell():
    """Start basic Python shell."""
    
    console.print("[blue]Python interactive shell[/blue]")
    console.print("Use exit() or Ctrl-Z plus Return to exit")
    
    # Basic context
    basic_context = {
        'os': os,
        'sys': sys,
        'Path': Path,
    }
    
    import code
    code.interact(local=basic_context)


def run_script(script_path: str):
    """Run a Python script with ANAL framework context."""
    
    script_file = Path(script_path)
    if not script_file.exists():
        console.print(f"[red]Script not found: {script_path}[/red]")
        return
    
    try:
        # Try to import the full framework
        from anal.core.config import get_settings
        from anal.core.application import ANAL
        
        settings = get_settings()
        
        console.print(f"[blue]Running script: {script_path}[/blue]")
        
        # Create script context
        script_context = {
            'settings': settings,
            'ANAL': ANAL,
            '__file__': str(script_file.absolute()),
            '__name__': '__main__',
        }
        
        # Execute the script
        with open(script_file, 'r') as f:
            script_content = f.read()
        
        exec(script_content, script_context)
        console.print("[green]✓ Script completed successfully[/green]")
        
    except ImportError as e:
        console.print(f"[yellow]Full framework not available: {e}[/yellow]")
        console.print("[blue]Running script in basic Python context...[/blue]")
        
        # Run with basic Python
        import subprocess
        result = subprocess.run([sys.executable, str(script_file)], capture_output=True, text=True)
        
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]")
        
        if result.returncode == 0:
            console.print("[green]✓ Script completed successfully[/green]")
        else:
            console.print(f"[red]Script failed with exit code: {result.returncode}[/red]")


def shell_plus():
    """Start shell with additional utilities loaded."""
    
    console.print("[blue]Starting ANAL shell plus...[/blue]")
    
    try:
        # Import framework
        from anal.core.config import get_settings
        from anal.core.application import ANAL
        
        settings = get_settings()
        
        # Extended context
        shell_context = {
            'settings': settings,
            'ANAL': ANAL,
            'os': os,
            'sys': sys,
            'Path': Path,
        }
        
        # Add common utilities
        try:
            import json
            import datetime
            import asyncio
            import requests
            
            shell_context.update({
                'json': json,
                'datetime': datetime,
                'asyncio': asyncio,
                'requests': requests,
            })
            
            console.print("[green]Available utilities:[/green]")
            console.print("  - json: JSON utilities")
            console.print("  - datetime: Date/time utilities")  
            console.print("  - asyncio: Async utilities")
            console.print("  - requests: HTTP client")
            
        except ImportError:
            pass
        
        # Try to load all models
        try:
            from anal.auth.models import User
            from anal.db.models import Base
            
            shell_context.update({
                'User': User,
                'Base': Base,
            })
            
            console.print("  - User: User model")
            console.print("  - Base: Database base")
            
        except ImportError:
            pass
        
        _start_enhanced_shell(shell_context)
        
    except ImportError:
        console.print("[yellow]Full framework not available, starting basic shell...[/yellow]")
        _start_basic_shell()
