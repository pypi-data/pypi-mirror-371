"""
Database connection and query management for ANAL framework.

This module provides database connectivity and query execution
with support for multiple database backends.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type, Union
from urllib.parse import urlparse
import json

# Database backends
try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

try:
    import aiomysql
    HAS_AIOMYSQL = True
except ImportError:
    HAS_AIOMYSQL = False

try:
    import aiosqlite
    HAS_AIOSQLITE = True
except ImportError:
    HAS_AIOSQLITE = False

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base database error."""
    pass


class ConnectionError(DatabaseError):
    """Database connection error."""
    pass


class QueryError(DatabaseError):
    """Database query error."""
    pass


class Database:
    """Database connection manager."""
    
    def __init__(self, url: str = None):
        """Initialize database connection."""
        self.url = url or get_settings().DATABASE_URL
        self.pool = None
        self.backend = None
        self._parse_url()
    
    def _parse_url(self):
        """Parse database URL to determine backend."""
        parsed = urlparse(self.url)
        self.backend = parsed.scheme
        
        if self.backend.startswith('postgresql'):
            if not HAS_ASYNCPG:
                raise ConnectionError("asyncpg not installed. Install with: pip install asyncpg")
        elif self.backend.startswith('mysql'):
            if not HAS_AIOMYSQL:
                raise ConnectionError("aiomysql not installed. Install with: pip install aiomysql")
        elif self.backend.startswith('sqlite'):
            if not HAS_AIOSQLITE:
                raise ConnectionError("aiosqlite not installed. Install with: pip install aiosqlite")
        else:
            raise ConnectionError(f"Unsupported database backend: {self.backend}")
    
    async def connect(self):
        """Establish database connection."""
        try:
            if self.backend.startswith('postgresql'):
                self.pool = await asyncpg.create_pool(self.url)
            elif self.backend.startswith('mysql'):
                parsed = urlparse(self.url)
                self.pool = await aiomysql.create_pool(
                    host=parsed.hostname,
                    port=parsed.port or 3306,
                    user=parsed.username,
                    password=parsed.password,
                    db=parsed.path.lstrip('/'),
                )
            elif self.backend.startswith('sqlite'):
                # For SQLite, we'll use a simple connection
                import aiosqlite
                self.pool = self.url.replace('sqlite:///', '')
            
            logger.info(f"Connected to {self.backend} database")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
    
    async def disconnect(self):
        """Close database connection."""
        if self.pool:
            if hasattr(self.pool, 'close'):
                await self.pool.close()
            self.pool = None
            logger.info("Disconnected from database")
    
    async def execute(self, query: str, params: List[Any] = None) -> int:
        """Execute a query and return affected rows."""
        if not self.pool:
            await self.connect()
        
        try:
            if self.backend.startswith('postgresql'):
                async with self.pool.acquire() as conn:
                    result = await conn.execute(query, *(params or []))
                    return len(result) if result else 0
            
            elif self.backend.startswith('mysql'):
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(query, params or [])
                        return cursor.rowcount
            
            elif self.backend.startswith('sqlite'):
                import aiosqlite
                async with aiosqlite.connect(self.pool) as db:
                    cursor = await db.execute(query, params or [])
                    await db.commit()
                    return cursor.rowcount
        
        except Exception as e:
            raise QueryError(f"Failed to execute query: {e}")
    
    async def fetch_one(self, query: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        """Fetch one row from the database."""
        if not self.pool:
            await self.connect()
        
        try:
            if self.backend.startswith('postgresql'):
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(query, *(params or []))
                    return dict(row) if row else None
            
            elif self.backend.startswith('mysql'):
                async with self.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        await cursor.execute(query, params or [])
                        return await cursor.fetchone()
            
            elif self.backend.startswith('sqlite'):
                import aiosqlite
                async with aiosqlite.connect(self.pool) as db:
                    db.row_factory = aiosqlite.Row
                    cursor = await db.execute(query, params or [])
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        
        except Exception as e:
            raise QueryError(f"Failed to fetch row: {e}")
    
    async def fetch_all(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from the database."""
        if not self.pool:
            await self.connect()
        
        try:
            if self.backend.startswith('postgresql'):
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(query, *(params or []))
                    return [dict(row) for row in rows]
            
            elif self.backend.startswith('mysql'):
                async with self.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        await cursor.execute(query, params or [])
                        return await cursor.fetchall()
            
            elif self.backend.startswith('sqlite'):
                import aiosqlite
                async with aiosqlite.connect(self.pool) as db:
                    db.row_factory = aiosqlite.Row
                    cursor = await db.execute(query, params or [])
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        
        except Exception as e:
            raise QueryError(f"Failed to fetch rows: {e}")
    
    async def begin_transaction(self):
        """Begin a database transaction."""
        # Implementation would depend on backend
        pass
    
    async def commit(self):
        """Commit current transaction."""
        # Implementation would depend on backend
        pass
    
    async def rollback(self):
        """Rollback current transaction."""
        # Implementation would depend on backend
        pass


class QueryBuilder:
    """SQL query builder."""
    
    def __init__(self, table: str = None):
        """Initialize query builder."""
        self.table = table
        self.query_type = None
        self.select_fields = []
        self.where_conditions = []
        self.join_clauses = []
        self.order_by_clauses = []
        self.group_by_clauses = []
        self.having_conditions = []
        self.limit_value = None
        self.offset_value = None
        self.update_values = {}
        self.insert_values = {}
    
    def select(self, *fields):
        """Add SELECT fields."""
        self.query_type = 'SELECT'
        if fields:
            self.select_fields.extend(fields)
        else:
            self.select_fields = ['*']
        return self
    
    def from_table(self, table: str):
        """Set table name."""
        self.table = table
        return self
    
    def where(self, condition: str, *params):
        """Add WHERE condition."""
        self.where_conditions.append((condition, params))
        return self
    
    def join(self, table: str, condition: str, join_type: str = 'INNER'):
        """Add JOIN clause."""
        self.join_clauses.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def order_by(self, field: str, direction: str = 'ASC'):
        """Add ORDER BY clause."""
        self.order_by_clauses.append(f"{field} {direction}")
        return self
    
    def group_by(self, *fields):
        """Add GROUP BY clause."""
        self.group_by_clauses.extend(fields)
        return self
    
    def having(self, condition: str, *params):
        """Add HAVING condition."""
        self.having_conditions.append((condition, params))
        return self
    
    def limit(self, count: int):
        """Add LIMIT clause."""
        self.limit_value = count
        return self
    
    def offset(self, count: int):
        """Add OFFSET clause."""
        self.offset_value = count
        return self
    
    def insert(self, **values):
        """Set INSERT values."""
        self.query_type = 'INSERT'
        self.insert_values.update(values)
        return self
    
    def update(self, **values):
        """Set UPDATE values."""
        self.query_type = 'UPDATE'
        self.update_values.update(values)
        return self
    
    def delete(self):
        """Set query type to DELETE."""
        self.query_type = 'DELETE'
        return self
    
    def build(self) -> tuple[str, List[Any]]:
        """Build the SQL query."""
        if self.query_type == 'SELECT':
            return self._build_select()
        elif self.query_type == 'INSERT':
            return self._build_insert()
        elif self.query_type == 'UPDATE':
            return self._build_update()
        elif self.query_type == 'DELETE':
            return self._build_delete()
        else:
            raise ValueError("No query type specified")
    
    def _build_select(self) -> tuple[str, List[Any]]:
        """Build SELECT query."""
        query_parts = ['SELECT']
        params = []
        
        # SELECT fields
        query_parts.append(', '.join(self.select_fields))
        
        # FROM table
        query_parts.extend(['FROM', self.table])
        
        # JOIN clauses
        for join_clause in self.join_clauses:
            query_parts.append(join_clause)
        
        # WHERE conditions
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query_parts.extend(['WHERE', ' AND '.join(where_parts)])
        
        # GROUP BY
        if self.group_by_clauses:
            query_parts.extend(['GROUP BY', ', '.join(self.group_by_clauses)])
        
        # HAVING
        if self.having_conditions:
            having_parts = []
            for condition, condition_params in self.having_conditions:
                having_parts.append(condition)
                params.extend(condition_params)
            query_parts.extend(['HAVING', ' AND '.join(having_parts)])
        
        # ORDER BY
        if self.order_by_clauses:
            query_parts.extend(['ORDER BY', ', '.join(self.order_by_clauses)])
        
        # LIMIT
        if self.limit_value:
            query_parts.extend(['LIMIT', str(self.limit_value)])
        
        # OFFSET
        if self.offset_value:
            query_parts.extend(['OFFSET', str(self.offset_value)])
        
        return ' '.join(query_parts), params
    
    def _build_insert(self) -> tuple[str, List[Any]]:
        """Build INSERT query."""
        if not self.insert_values:
            raise ValueError("No values to insert")
        
        fields = list(self.insert_values.keys())
        values = list(self.insert_values.values())
        placeholders = ', '.join(['?' for _ in values])
        
        query = f"INSERT INTO {self.table} ({', '.join(fields)}) VALUES ({placeholders})"
        return query, values
    
    def _build_update(self) -> tuple[str, List[Any]]:
        """Build UPDATE query."""
        if not self.update_values:
            raise ValueError("No values to update")
        
        set_clauses = []
        params = []
        
        for field, value in self.update_values.items():
            set_clauses.append(f"{field} = ?")
            params.append(value)
        
        query_parts = ['UPDATE', self.table, 'SET', ', '.join(set_clauses)]
        
        # WHERE conditions
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query_parts.extend(['WHERE', ' AND '.join(where_parts)])
        
        return ' '.join(query_parts), params
    
    def _build_delete(self) -> tuple[str, List[Any]]:
        """Build DELETE query."""
        query_parts = ['DELETE FROM', self.table]
        params = []
        
        # WHERE conditions
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query_parts.extend(['WHERE', ' AND '.join(where_parts)])
        
        return ' '.join(query_parts), params


# Global database instance
_database = None


def get_database() -> Database:
    """Get global database instance."""
    global _database
    if _database is None:
        _database = Database()
    return _database


async def connect_database():
    """Connect to the database."""
    db = get_database()
    await db.connect()


async def disconnect_database():
    """Disconnect from the database."""
    db = get_database()
    await db.disconnect()


# Export main classes
__all__ = [
    'Database',
    'QueryBuilder',
    'DatabaseError',
    'ConnectionError',
    'QueryError',
    'get_database',
    'connect_database',
    'disconnect_database',
]
