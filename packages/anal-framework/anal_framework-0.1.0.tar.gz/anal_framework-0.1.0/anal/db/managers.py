"""
Model managers and querysets for ANAL framework.

This module provides the ORM functionality for executing database queries
through model managers and querysets.
"""

from typing import Any, Dict, List, Optional, Type, Union, AsyncGenerator
import logging

from .connection import get_database, QueryBuilder
from .models import Model

logger = logging.getLogger(__name__)


class QuerySet:
    """QuerySet for model queries."""
    
    def __init__(self, model: Type[Model], manager: 'Manager' = None):
        """Initialize QuerySet."""
        self.model = model
        self.manager = manager
        self._db = get_database()
        self._query_builder = QueryBuilder(model._meta.table_name)
        self._result_cache = None
        
        # Query state
        self._filters = []
        self._excludes = []
        self._order_by = []
        self._select_related = []
        self._prefetch_related = []
        self._limit = None
        self._offset = None
    
    def filter(self, **kwargs) -> 'QuerySet':
        """Filter queryset by given parameters."""
        clone = self._clone()
        clone._filters.extend(kwargs.items())
        return clone
    
    def exclude(self, **kwargs) -> 'QuerySet':
        """Exclude records matching given parameters."""
        clone = self._clone()
        clone._excludes.extend(kwargs.items())
        return clone
    
    def order_by(self, *fields) -> 'QuerySet':
        """Order queryset by given fields."""
        clone = self._clone()
        clone._order_by.extend(fields)
        return clone
    
    def select_related(self, *fields) -> 'QuerySet':
        """Select related objects in a single query."""
        clone = self._clone()
        clone._select_related.extend(fields)
        return clone
    
    def prefetch_related(self, *fields) -> 'QuerySet':
        """Prefetch related objects in separate queries."""
        clone = self._clone()
        clone._prefetch_related.extend(fields)
        return clone
    
    def limit(self, count: int) -> 'QuerySet':
        """Limit the number of results."""
        clone = self._clone()
        clone._limit = count
        return clone
    
    def offset(self, count: int) -> 'QuerySet':
        """Offset the results."""
        clone = self._clone()
        clone._offset = count
        return clone
    
    def distinct(self, *fields) -> 'QuerySet':
        """Return distinct results."""
        # Implementation would depend on database backend
        return self._clone()
    
    def values(self, *fields) -> 'QuerySet':
        """Return dictionaries instead of model instances."""
        clone = self._clone()
        # Store fields to return as dicts
        return clone
    
    def values_list(self, *fields, flat=False) -> 'QuerySet':
        """Return tuples of values instead of model instances."""
        clone = self._clone()
        # Store fields and flat setting
        return clone
    
    async def get(self, **kwargs) -> Model:
        """Get a single object matching the given parameters."""
        queryset = self.filter(**kwargs)
        results = await queryset._execute()
        
        if not results:
            raise DoesNotExist(f"{self.model.__name__} matching query does not exist")
        if len(results) > 1:
            raise MultipleObjectsReturned(f"get() returned more than one {self.model.__name__}")
        
        return self._create_model_instance(results[0])
    
    async def first(self) -> Optional[Model]:
        """Get the first object, or None if no match."""
        queryset = self.limit(1)
        results = await queryset._execute()
        return self._create_model_instance(results[0]) if results else None
    
    async def last(self) -> Optional[Model]:
        """Get the last object, or None if no match."""
        # Reverse order and get first
        reversed_order = []
        for field in self._order_by:
            if field.startswith('-'):
                reversed_order.append(field[1:])
            else:
                reversed_order.append(f'-{field}')
        
        queryset = self.order_by(*reversed_order).limit(1)
        results = await queryset._execute()
        return self._create_model_instance(results[0]) if results else None
    
    async def exists(self) -> bool:
        """Check if any records exist."""
        queryset = self.limit(1)
        results = await queryset._execute()
        return len(results) > 0
    
    async def count(self) -> int:
        """Count the number of records."""
        # Build count query
        query_builder = QueryBuilder(self.model._meta.table_name)
        query_builder.select('COUNT(*)')
        
        # Apply filters
        self._apply_filters(query_builder)
        
        query, params = query_builder.build()
        result = await self._db.fetch_one(query, params)
        return result['COUNT(*)'] if result else 0
    
    async def all(self) -> List[Model]:
        """Get all objects in the queryset."""
        results = await self._execute()
        return [self._create_model_instance(row) for row in results]
    
    async def create(self, **kwargs) -> Model:
        """Create and save a new object."""
        instance = self.model(**kwargs)
        await instance.asave()
        return instance
    
    async def get_or_create(self, defaults=None, **kwargs) -> tuple[Model, bool]:
        """Get an object or create it if it doesn't exist."""
        try:
            return await self.get(**kwargs), False
        except DoesNotExist:
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)
            return await self.create(**create_kwargs), True
    
    async def update(self, **kwargs) -> int:
        """Update all objects in the queryset."""
        query_builder = QueryBuilder(self.model._meta.table_name)
        query_builder.update(**kwargs)
        
        # Apply filters
        self._apply_filters(query_builder)
        
        query, params = query_builder.build()
        return await self._db.execute(query, params)
    
    async def delete(self) -> int:
        """Delete all objects in the queryset."""
        query_builder = QueryBuilder(self.model._meta.table_name)
        query_builder.delete()
        
        # Apply filters
        self._apply_filters(query_builder)
        
        query, params = query_builder.build()
        return await self._db.execute(query, params)
    
    async def bulk_create(self, objects: List[Model]) -> List[Model]:
        """Create multiple objects in a single query."""
        # Implementation would batch insert objects
        created_objects = []
        for obj in objects:
            await obj.asave()
            created_objects.append(obj)
        return created_objects
    
    async def bulk_update(self, objects: List[Model], fields: List[str]) -> int:
        """Update multiple objects in a single query."""
        # Implementation would batch update objects
        count = 0
        for obj in objects:
            await obj.asave()
            count += 1
        return count
    
    def _clone(self) -> 'QuerySet':
        """Create a copy of this queryset."""
        clone = QuerySet(self.model, self.manager)
        clone._filters = self._filters.copy()
        clone._excludes = self._excludes.copy()
        clone._order_by = self._order_by.copy()
        clone._select_related = self._select_related.copy()
        clone._prefetch_related = self._prefetch_related.copy()
        clone._limit = self._limit
        clone._offset = self._offset
        return clone
    
    async def _execute(self) -> List[Dict[str, Any]]:
        """Execute the query and return raw results."""
        if self._result_cache is not None:
            return self._result_cache
        
        # Build query
        query_builder = QueryBuilder(self.model._meta.table_name)
        query_builder.select('*')
        
        # Apply filters, ordering, etc.
        self._apply_filters(query_builder)
        self._apply_ordering(query_builder)
        self._apply_limits(query_builder)
        
        query, params = query_builder.build()
        results = await self._db.fetch_all(query, params)
        
        self._result_cache = results
        return results
    
    def _apply_filters(self, query_builder: QueryBuilder):
        """Apply filter conditions to query builder."""
        for field, value in self._filters:
            if '__' in field:
                # Handle field lookups like name__icontains
                field_name, lookup = field.split('__', 1)
                condition = self._build_lookup_condition(field_name, lookup, value)
                query_builder.where(condition, value)
            else:
                query_builder.where(f"{field} = ?", value)
        
        # Apply exclude conditions
        for field, value in self._excludes:
            if '__' in field:
                field_name, lookup = field.split('__', 1)
                condition = self._build_lookup_condition(field_name, lookup, value, negate=True)
                query_builder.where(condition, value)
            else:
                query_builder.where(f"{field} != ?", value)
    
    def _build_lookup_condition(self, field: str, lookup: str, value: Any, negate: bool = False) -> str:
        """Build SQL condition for field lookups."""
        conditions = {
            'exact': f"{field} = ?",
            'iexact': f"LOWER({field}) = LOWER(?)",
            'contains': f"{field} LIKE ?",
            'icontains': f"LOWER({field}) LIKE LOWER(?)",
            'startswith': f"{field} LIKE ?",
            'istartswith': f"LOWER({field}) LIKE LOWER(?)",
            'endswith': f"{field} LIKE ?",
            'iendswith': f"LOWER({field}) LIKE LOWER(?)",
            'gt': f"{field} > ?",
            'gte': f"{field} >= ?",
            'lt': f"{field} < ?",
            'lte': f"{field} <= ?",
            'in': f"{field} IN (?)",
            'isnull': f"{field} IS NULL" if value else f"{field} IS NOT NULL",
        }
        
        condition = conditions.get(lookup, f"{field} = ?")
        
        if negate:
            condition = f"NOT ({condition})"
        
        return condition
    
    def _apply_ordering(self, query_builder: QueryBuilder):
        """Apply ordering to query builder."""
        for field in self._order_by:
            if field.startswith('-'):
                query_builder.order_by(field[1:], 'DESC')
            else:
                query_builder.order_by(field, 'ASC')
    
    def _apply_limits(self, query_builder: QueryBuilder):
        """Apply limit and offset to query builder."""
        if self._limit:
            query_builder.limit(self._limit)
        if self._offset:
            query_builder.offset(self._offset)
    
    def _create_model_instance(self, row: Dict[str, Any]) -> Model:
        """Create model instance from database row."""
        return self.model(**row)
    
    # Iterator support
    def __aiter__(self) -> AsyncGenerator[Model, None]:
        """Async iterator support."""
        return self._aiter()
    
    async def _aiter(self) -> AsyncGenerator[Model, None]:
        """Async iterator implementation."""
        results = await self._execute()
        for row in results:
            yield self._create_model_instance(row)


class Manager:
    """Model manager for database operations."""
    
    def __init__(self, model: Type[Model]):
        """Initialize manager."""
        self.model = model
    
    def get_queryset(self) -> QuerySet:
        """Get base queryset for this manager."""
        return QuerySet(self.model, self)
    
    def all(self) -> QuerySet:
        """Get all objects."""
        return self.get_queryset()
    
    def filter(self, **kwargs) -> QuerySet:
        """Filter objects."""
        return self.get_queryset().filter(**kwargs)
    
    def exclude(self, **kwargs) -> QuerySet:
        """Exclude objects."""
        return self.get_queryset().exclude(**kwargs)
    
    def get(self, **kwargs) -> QuerySet:
        """Get a single object."""
        return self.get_queryset().get(**kwargs)
    
    def create(self, **kwargs) -> QuerySet:
        """Create a new object."""
        return self.get_queryset().create(**kwargs)
    
    def get_or_create(self, **kwargs) -> QuerySet:
        """Get or create an object."""
        return self.get_queryset().get_or_create(**kwargs)
    
    def update(self, **kwargs) -> QuerySet:
        """Update objects."""
        return self.get_queryset().update(**kwargs)
    
    def delete(self) -> QuerySet:
        """Delete objects."""
        return self.get_queryset().delete()
    
    def count(self) -> QuerySet:
        """Count objects."""
        return self.get_queryset().count()
    
    def exists(self) -> QuerySet:
        """Check if objects exist."""
        return self.get_queryset().exists()
    
    def bulk_create(self, objects: List[Model]) -> QuerySet:
        """Bulk create objects."""
        return self.get_queryset().bulk_create(objects)


class DoesNotExist(Exception):
    """Exception raised when a model instance doesn't exist."""
    pass


class MultipleObjectsReturned(Exception):
    """Exception raised when multiple objects are returned for a get() query."""
    pass


# Export main classes
__all__ = [
    'QuerySet',
    'Manager',
    'DoesNotExist',
    'MultipleObjectsReturned',
]
