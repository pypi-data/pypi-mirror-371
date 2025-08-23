"""
Event system for the ANAL framework.

This module provides a sophisticated event bus system for decoupled
communication between different parts of the application.
"""

import asyncio
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Union

from anal.core.exceptions import ANALException


logger = logging.getLogger(__name__)


class Event:
    """
    Represents an event with data and metadata.
    """
    
    def __init__(
        self,
        name: str,
        data: Any = None,
        source: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        """
        Initialize an event.
        
        Args:
            name: Event name
            data: Event data
            source: Event source identifier
            timestamp: Event timestamp (defaults to current time)
        """
        self.name = name
        self.data = data
        self.source = source
        self.timestamp = timestamp or asyncio.get_event_loop().time()
    
    def __repr__(self) -> str:
        return f"<Event('{self.name}', source='{self.source}')>"


class EventHandler:
    """
    Wrapper for event handler functions with metadata.
    """
    
    def __init__(
        self,
        handler: Callable,
        priority: int = 0,
        once: bool = False,
        condition: Optional[Callable[[Event], bool]] = None
    ):
        """
        Initialize an event handler.
        
        Args:
            handler: Handler function
            priority: Handler priority (higher runs first)
            once: Whether to run only once
            condition: Optional condition function
        """
        self.handler = handler
        self.priority = priority
        self.once = once
        self.condition = condition
        self.call_count = 0
        self.is_async = asyncio.iscoroutinefunction(handler)
    
    async def __call__(self, event: Event) -> Any:
        """Execute the handler."""
        # Check condition if provided
        if self.condition and not self.condition(event):
            return None
        
        self.call_count += 1
        
        try:
            if self.is_async:
                return await self.handler(event)
            else:
                return self.handler(event)
        except Exception as e:
            logger.error(f"Error in event handler {self.handler.__name__}: {e}")
            raise
    
    def __repr__(self) -> str:
        return f"<EventHandler({self.handler.__name__}, priority={self.priority})>"


class EventBus:
    """
    Event bus for managing event subscriptions and dispatching.
    
    Supports:
    - Synchronous and asynchronous handlers
    - Handler priorities
    - One-time handlers
    - Conditional handlers
    - Event propagation control
    - Middleware for event processing
    
    Example:
        ```python
        from anal.core.events import EventBus
        
        bus = EventBus()
        
        @bus.on('user.created')
        async def send_welcome_email(event):
            user = event.data
            await send_email(user.email, "Welcome!")
        
        # Emit event
        await bus.emit('user.created', user_data)
        ```
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._middleware: List[Callable] = []
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._running = False
    
    def on(
        self,
        event_name: str,
        handler: Optional[Callable] = None,
        priority: int = 0,
        once: bool = False,
        condition: Optional[Callable[[Event], bool]] = None
    ) -> Union[Callable, None]:
        """
        Register an event handler.
        
        Can be used as a decorator or direct method call.
        
        Args:
            event_name: Name of the event to listen for
            handler: Handler function (if not used as decorator)
            priority: Handler priority (higher runs first)
            once: Whether to run only once
            condition: Optional condition function
            
        Returns:
            Handler function or decorator
        """
        def decorator(func: Callable) -> Callable:
            self._add_handler(event_name, func, priority, once, condition)
            return func
        
        if handler is not None:
            # Direct method call
            self._add_handler(event_name, handler, priority, once, condition)
            return None
        else:
            # Used as decorator
            return decorator
    
    def once(
        self,
        event_name: str,
        handler: Optional[Callable] = None,
        priority: int = 0,
        condition: Optional[Callable[[Event], bool]] = None
    ) -> Union[Callable, None]:
        """Register a one-time event handler."""
        return self.on(event_name, handler, priority, once=True, condition=condition)
    
    def off(self, event_name: str, handler: Optional[Callable] = None) -> None:
        """
        Remove event handler(s).
        
        Args:
            event_name: Event name
            handler: Specific handler to remove (removes all if None)
        """
        if event_name not in self._handlers:
            return
        
        if handler is None:
            # Remove all handlers for event
            del self._handlers[event_name]
        else:
            # Remove specific handler
            self._handlers[event_name] = [
                h for h in self._handlers[event_name]
                if h.handler != handler
            ]
            
            # Clean up empty handler list
            if not self._handlers[event_name]:
                del self._handlers[event_name]
    
    def _add_handler(
        self,
        event_name: str,
        handler: Callable,
        priority: int,
        once: bool,
        condition: Optional[Callable[[Event], bool]]
    ) -> None:
        """Add a handler to the event bus."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        
        event_handler = EventHandler(handler, priority, once, condition)
        self._handlers[event_name].append(event_handler)
        
        # Sort by priority (highest first)
        self._handlers[event_name].sort(key=lambda h: h.priority, reverse=True)
    
    async def emit(
        self,
        event_name: str,
        data: Any = None,
        source: Optional[str] = None,
        wait: bool = True
    ) -> List[Any]:
        """
        Emit an event.
        
        Args:
            event_name: Name of the event
            data: Event data
            source: Event source identifier
            wait: Whether to wait for all handlers to complete
            
        Returns:
            List of handler results
        """
        event = Event(event_name, data, source)
        
        # Add to history
        self._add_to_history(event)
        
        # Apply middleware
        for middleware in self._middleware:
            if asyncio.iscoroutinefunction(middleware):
                event = await middleware(event)
            else:
                event = middleware(event)
            
            if event is None:
                # Middleware stopped propagation
                return []
        
        # Get handlers for this event
        handlers = self._handlers.get(event_name, [])
        
        if not handlers:
            logger.debug(f"No handlers registered for event '{event_name}'")
            return []
        
        logger.debug(f"Emitting event '{event_name}' to {len(handlers)} handlers")
        
        # Execute handlers
        results = []
        to_remove = []
        
        for handler in handlers:
            try:
                if wait:
                    result = await handler(event)
                    results.append(result)
                else:
                    # Fire and forget
                    asyncio.create_task(handler(event))
                
                # Mark one-time handlers for removal
                if handler.once:
                    to_remove.append(handler)
                    
            except Exception as e:
                logger.error(f"Error executing handler {handler.handler.__name__}: {e}")
                if wait:
                    raise
        
        # Remove one-time handlers
        for handler in to_remove:
            if event_name in self._handlers:
                try:
                    self._handlers[event_name].remove(handler)
                except ValueError:
                    pass
        
        return results
    
    def emit_sync(self, event_name: str, data: Any = None, source: Optional[str] = None) -> List[Any]:
        """
        Emit an event synchronously (for non-async contexts).
        
        Args:
            event_name: Name of the event
            data: Event data
            source: Event source identifier
            
        Returns:
            List of handler results
        """
        if asyncio.get_event_loop().is_running():
            # Create a task if event loop is running
            task = asyncio.create_task(self.emit(event_name, data, source))
            return []  # Can't wait for results in sync context
        else:
            # Run in new event loop
            return asyncio.run(self.emit(event_name, data, source))
    
    def add_middleware(self, middleware: Callable[[Event], Union[Event, None]]) -> None:
        """
        Add middleware for event processing.
        
        Middleware can modify events or stop propagation by returning None.
        
        Args:
            middleware: Middleware function
        """
        self._middleware.append(middleware)
    
    def remove_middleware(self, middleware: Callable) -> None:
        """Remove middleware."""
        if middleware in self._middleware:
            self._middleware.remove(middleware)
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to history."""
        self._event_history.append(event)
        
        # Limit history size
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_history(self, event_name: Optional[str] = None, limit: Optional[int] = None) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_name: Filter by event name
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = self._event_history
        
        if event_name:
            events = [e for e in events if e.name == event_name]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def get_handlers(self, event_name: Optional[str] = None) -> Dict[str, List[EventHandler]]:
        """
        Get registered handlers.
        
        Args:
            event_name: Filter by event name
            
        Returns:
            Dictionary of handlers
        """
        if event_name:
            return {event_name: self._handlers.get(event_name, [])}
        else:
            return self._handlers.copy()
    
    def clear_handlers(self, event_name: Optional[str] = None) -> None:
        """
        Clear handlers.
        
        Args:
            event_name: Specific event name (clears all if None)
        """
        if event_name:
            self._handlers.pop(event_name, None)
        else:
            self._handlers.clear()
    
    def has_handlers(self, event_name: str) -> bool:
        """Check if event has handlers."""
        return event_name in self._handlers and len(self._handlers[event_name]) > 0
    
    def handler_count(self, event_name: str) -> int:
        """Get number of handlers for an event."""
        return len(self._handlers.get(event_name, []))
    
    def event_names(self) -> Set[str]:
        """Get all registered event names."""
        return set(self._handlers.keys())
    
    def __repr__(self) -> str:
        total_handlers = sum(len(handlers) for handlers in self._handlers.values())
        return f"<EventBus(events={len(self._handlers)}, handlers={total_handlers})>"


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus


def on(event_name: str, **kwargs) -> Callable:
    """Register handler on global event bus."""
    return _event_bus.on(event_name, **kwargs)


def once(event_name: str, **kwargs) -> Callable:
    """Register one-time handler on global event bus."""
    return _event_bus.once(event_name, **kwargs)


def off(event_name: str, handler: Optional[Callable] = None) -> None:
    """Remove handler from global event bus."""
    _event_bus.off(event_name, handler)


async def emit(event_name: str, data: Any = None, source: Optional[str] = None) -> List[Any]:
    """Emit event on global event bus."""
    return await _event_bus.emit(event_name, data, source)


def emit_sync(event_name: str, data: Any = None, source: Optional[str] = None) -> List[Any]:
    """Emit event synchronously on global event bus."""
    return _event_bus.emit_sync(event_name, data, source)
