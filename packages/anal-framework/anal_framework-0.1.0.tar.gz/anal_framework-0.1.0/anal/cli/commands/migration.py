"""
Database migration commands for ANAL framework.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def make_migrations(app_name: Optional[str] = None):
    """
    Create database migrations.
    
    Args:
        app_name: Optional app name to create migrations for
    """
    try:
        # Try to import the full framework
        from anal.core.config import get_settings
        from anal.db.migration import MigrationManager
        
        settings = get_settings()
        migration_manager = MigrationManager(settings)
        
        if app_name:
            console.print(f"[blue]Creating migrations for app: {app_name}[/blue]")
            migration_manager.create_migration(app_name)
        else:
            console.print("[blue]Creating migrations for all apps[/blue]")
            migration_manager.create_all_migrations()
            
    except ImportError as e:
        console.print(f"[yellow]Full migration system not available: {e}[/yellow]")
        _create_basic_migration_structure(app_name)


def apply_migrations():
    """Apply database migrations."""
    try:
        # Try to import the full framework
        from anal.core.config import get_settings
        from anal.db.migration import MigrationManager
        
        settings = get_settings()
        migration_manager = MigrationManager(settings)
        
        console.print("[blue]Applying database migrations...[/blue]")
        migration_manager.apply_migrations()
        console.print("[green]✓ Migrations applied successfully[/green]")
        
    except ImportError as e:
        console.print(f"[yellow]Full migration system not available: {e}[/yellow]")
        _create_basic_migration_structure()


def _create_basic_migration_structure(app_name: Optional[str] = None):
    """Create basic migration directory structure."""
    
    # Create migrations directory
    migrations_dir = Path("migrations")
    migrations_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    init_file = migrations_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Database migrations."""\n')
    
    # Create versions directory
    versions_dir = migrations_dir / "versions"
    versions_dir.mkdir(exist_ok=True)
    (versions_dir / "__init__.py").touch()
    
    # Create alembic.ini if it doesn't exist
    alembic_ini = Path("alembic.ini")
    if not alembic_ini.exists():
        alembic_content = f"""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%Y%%m%%d_%%H%%M%%S_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = sqlite:///./app.db

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, executing a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        alembic_ini.write_text(alembic_content)
    
    # Create env.py for alembic
    env_py = migrations_dir / "env.py"
    if not env_py.exists():
        env_content = '''"""
Alembic environment configuration.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
try:
    from anal.db.models import Base
    target_metadata = Base.metadata
except ImportError:
    target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        env_py.write_text(env_content)
    
    # Create script.py.mako template
    script_mako = migrations_dir / "script.py.mako"
    if not script_mako.exists():
        script_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
        script_mako.write_text(script_content)
    
    if app_name:
        console.print(f"[green]✓ Created migration structure for app: {app_name}[/green]")
    else:
        console.print("[green]✓ Created basic migration structure[/green]")
    
    console.print("\n[blue]Migration files created:[/blue]")
    console.print(f"  📁 {migrations_dir}/")
    console.print(f"  📄 alembic.ini")
    console.print(f"  📄 {migrations_dir}/env.py")
    console.print(f"  📄 {migrations_dir}/script.py.mako")
    
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("  1. Configure your database URL in alembic.ini")
    console.print("  2. Run: alembic revision --autogenerate -m 'Initial migration'")
    console.print("  3. Run: alembic upgrade head")


def show_migration_status():
    """Show current migration status."""
    try:
        from anal.core.config import get_settings
        from anal.db.migration import MigrationManager
        
        settings = get_settings()
        migration_manager = MigrationManager(settings)
        
        status = migration_manager.get_migration_status()
        
        table = Table(title="Migration Status")
        table.add_column("Migration", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Applied", style="yellow")
        
        for migration in status:
            table.add_row(
                migration['name'],
                "✓" if migration['applied'] else "✗",
                migration['applied_at'] or "N/A"
            )
        
        console.print(table)
        
    except ImportError:
        console.print("[yellow]Migration status not available in simplified mode[/yellow]")
        console.print("Run: alembic current")
