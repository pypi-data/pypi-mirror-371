"""
Development server commands for ANAL framework.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def run_server(
    host: str = "127.0.0.1", 
    port: int = 8000, 
    reload: bool = False, 
    workers: int = 1
):
    """
    Start the ANAL development server.
    
    Args:
        host: Server host address
        port: Server port
        reload: Enable auto-reload
        workers: Number of worker processes
    """
    try:
        # Try to import the full framework
        from anal.core.config import get_settings
        
        settings = get_settings()
        
        # Look for application instance
        app_instance = _find_application()
        
        if app_instance:
            console.print(f"[green]🚀 Starting ANAL server on http://{host}:{port}[/green]")
            console.print(f"[blue]Application: {app_instance}[/blue]")
            
            import uvicorn
            uvicorn.run(
                app_instance,
                host=host,
                port=port,
                reload=reload,
                workers=workers if not reload else 1,
                access_log=True
            )
        else:
            console.print("[red]No ANAL application found[/red]")
            _fallback_server(host, port, reload)
            
    except ImportError as e:
        console.print(f"[yellow]Full framework not available: {e}[/yellow]")
        _fallback_server(host, port, reload)


def _find_application():
    """Find the ANAL application instance."""
    
    # Common application module patterns
    app_patterns = [
        "main:app",
        "app:app", 
        "asgi:app",
        "asgi:application",
    ]
    
    # Try each pattern
    for pattern in app_patterns:
        try:
            module_name, app_name = pattern.split(':')
            import importlib
            module = importlib.import_module(module_name)
            if hasattr(module, app_name):
                return pattern
        except (ImportError, ValueError):
            continue
    
    return None


def _fallback_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Fallback server using basic uvicorn."""
    
    console.print("[yellow]Starting fallback server...[/yellow]")
    
    # Try to find any ASGI application
    app_module = _find_asgi_app()
    
    if app_module:
        console.print(f"[blue]Found ASGI app: {app_module}[/blue]")
        console.print(f"[green]🚀 Starting server on http://{host}:{port}[/green]")
        
        try:
            import uvicorn
            uvicorn.run(
                app_module,
                host=host,
                port=port,
                reload=reload,
                access_log=True
            )
        except ImportError:
            console.print("[red]Uvicorn not available[/red]")
    else:
        console.print("[red]No ASGI application found[/red]")
        _create_demo_server(host, port)


def _find_asgi_app():
    """Find any ASGI application."""
    
    # Try common patterns
    patterns = [
        "main:app",
        "app:app",
        "asgi:app", 
        "asgi:application",
        "app.main:app",
        "app.asgi:application",
    ]
    
    for pattern in patterns:
        try:
            module_name, app_name = pattern.split(':')
            import importlib
            module = importlib.import_module(module_name)
            if hasattr(module, app_name):
                return pattern
        except (ImportError, ValueError):
            continue
    
    return None


def _create_demo_server(host: str = "127.0.0.1", port: int = 8000):
    """Create a simple demo server."""
    
    console.print("[blue]Creating demo ASGI application...[/blue]")
    
    # Create a simple demo app
    demo_content = '''"""
Demo ASGI application for ANAL framework.
"""

async def app(scope, receive, send):
    """Simple ASGI demo application."""
    assert scope['type'] == 'http'

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'text/html'],
        ],
    })
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ANAL Framework</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
            h1 { color: #333; text-align: center; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ANAL Framework</h1>
            <div class="status">
                <strong>Server is running successfully!</strong><br>
                Your ANAL framework installation is working correctly.
            </div>
        </div>
    </body>
    </html>
    """.encode('utf-8')
    
    await send({
        'type': 'http.response.body',
        'body': html_content,
    })
'''
    
    # Write demo app
    demo_file = Path("demo_app.py")
    demo_file.write_text(demo_content, encoding='utf-8')
    
    console.print(f"[green]✓ Created demo application: {demo_file}[/green]")
    console.print(f"[green]🚀 Starting demo server on http://{host}:{port}[/green]")
    
    try:
        import uvicorn
        import sys
        
        # Ensure current directory is in Python path
        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Test import before running uvicorn
        try:
            import demo_app
            console.print("[blue]Demo app imported successfully[/blue]")
        except ImportError as e:
            console.print(f"[red]Could not import demo_app: {e}[/red]")
            return
        
        uvicorn.run("demo_app:app", host=host, port=port, access_log=True)
    except ImportError:
        console.print("[red]Uvicorn not available. Please install with: pip install uvicorn[/red]")
