"""
Authentication backends for ANAL framework.

This module provides authentication backends for different authentication methods.
"""

import secrets
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from .models import User, Token, Session
from ..core.config import get_settings


class BaseBackend(ABC):
    """Base authentication backend."""
    
    @abstractmethod
    async def authenticate(self, **credentials) -> Optional[User]:
        """Authenticate user with given credentials."""
        pass
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return await User.objects.get(id=user_id, is_active=True)
        except:
            return None


class UsernamePasswordBackend(BaseBackend):
    """Username/password authentication backend."""
    
    async def authenticate(self, username: str = None, password: str = None, **kwargs) -> Optional[User]:
        """Authenticate user with username and password."""
        if not username or not password:
            return None
        
        try:
            # Try to get user by username or email
            user = None
            try:
                user = await User.objects.get(username=username, is_active=True)
            except:
                try:
                    user = await User.objects.get(email=username, is_active=True)
                except:
                    return None
            
            if user and user.check_password(password):
                # Update last login
                user.last_login = datetime.now()
                await user.asave()
                return user
            
        except Exception:
            pass
        
        return None


class TokenBackend(BaseBackend):
    """Token-based authentication backend."""
    
    async def authenticate(self, token: str = None, **kwargs) -> Optional[User]:
        """Authenticate user with API token."""
        if not token:
            return None
        
        try:
            token_obj = await Token.objects.get(key=token, is_active=True)
            
            # Update last used
            token_obj.last_used = datetime.now()
            await token_obj.asave()
            
            return await token_obj.user
        except:
            return None


class SessionBackend(BaseBackend):
    """Session-based authentication backend."""
    
    async def authenticate(self, session_key: str = None, **kwargs) -> Optional[User]:
        """Authenticate user with session."""
        if not session_key:
            return None
        
        try:
            session = await Session.objects.get(session_key=session_key)
            
            if session.is_expired():
                await session.adelete()
                return None
            
            # Decode session data to get user ID
            # This is simplified - in practice you'd use proper session serialization
            session_data = eval(session.session_data)  # Don't use eval in production!
            user_id = session_data.get('user_id')
            
            if user_id:
                return await self.get_user(user_id)
            
        except Exception:
            pass
        
        return None


class AuthenticationManager:
    """Manages authentication across multiple backends."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.backends = [
            UsernamePasswordBackend(),
            TokenBackend(),
            SessionBackend(),
        ]
    
    async def authenticate(self, **credentials) -> Optional[User]:
        """Authenticate user using available backends."""
        for backend in self.backends:
            user = await backend.authenticate(**credentials)
            if user:
                return user
        return None
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        for backend in self.backends:
            user = await backend.get_user(user_id)
            if user:
                return user
        return None
    
    async def login(self, user: User, request=None) -> Dict[str, Any]:
        """Log in user and create session."""
        # Create session
        session_key = Session.generate_key()
        session_data = {'user_id': user.id}
        
        session = Session(
            session_key=session_key,
            session_data=str(session_data),  # In practice, use proper serialization
        )
        session.set_expiry()
        await session.asave()
        
        # Update last login
        user.last_login = datetime.now()
        await user.asave()
        
        return {
            'session_key': session_key,
            'expires_at': session.expire_date,
            'user': user
        }
    
    async def logout(self, session_key: str):
        """Log out user by deleting session."""
        try:
            session = await Session.objects.get(session_key=session_key)
            await session.adelete()
        except:
            pass
    
    async def create_token(self, user: User, name: str = None) -> Token:
        """Create API token for user."""
        token = Token(
            user=user,
            name=name or f"Token for {user.username}"
        )
        await token.asave()
        return token
    
    async def revoke_token(self, token_key: str):
        """Revoke API token."""
        try:
            token = await Token.objects.get(key=token_key)
            token.is_active = False
            await token.asave()
        except:
            pass


class PermissionChecker:
    """Handles permission checking."""
    
    def __init__(self, user: User):
        """Initialize permission checker for user."""
        self.user = user
        self._permission_cache = None
    
    async def has_permission(self, permission: str) -> bool:
        """Check if user has permission."""
        if self.user.is_superuser:
            return True
        
        if not self.user.is_active:
            return False
        
        # Load permissions if not cached
        if self._permission_cache is None:
            await self._load_permissions()
        
        return permission in self._permission_cache
    
    async def has_permissions(self, permissions: list) -> bool:
        """Check if user has all permissions."""
        return all(await self.has_permission(perm) for perm in permissions)
    
    async def has_any_permission(self, permissions: list) -> bool:
        """Check if user has any of the permissions."""
        return any(await self.has_permission(perm) for perm in permissions)
    
    async def _load_permissions(self):
        """Load user permissions from database."""
        permissions = set()
        
        # Get direct user permissions
        user_permissions = await self.user.userpermission_set.all()
        for up in user_permissions:
            permission = await up.permission
            permissions.add(f"{permission.content_type}.{permission.codename}")
        
        # Get group permissions
        user_groups = await self.user.usergroup_set.all()
        for ug in user_groups:
            group = await ug.group
            group_permissions = await group.grouppermission_set.all()
            for gp in group_permissions:
                permission = await gp.permission
                permissions.add(f"{permission.content_type}.{permission.codename}")
        
        self._permission_cache = permissions


# Global authentication manager
_auth_manager = None


def get_auth_manager() -> AuthenticationManager:
    """Get global authentication manager."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager


async def authenticate(**credentials) -> Optional[User]:
    """Authenticate user with credentials."""
    auth_manager = get_auth_manager()
    return await auth_manager.authenticate(**credentials)


async def login(user: User, request=None) -> Dict[str, Any]:
    """Log in user."""
    auth_manager = get_auth_manager()
    return await auth_manager.login(user, request)


async def logout(session_key: str):
    """Log out user."""
    auth_manager = get_auth_manager()
    await auth_manager.logout(session_key)


# Export main classes and functions
__all__ = [
    'BaseBackend',
    'UsernamePasswordBackend',
    'TokenBackend',
    'SessionBackend',
    'AuthenticationManager',
    'PermissionChecker',
    'get_auth_manager',
    'authenticate',
    'login',
    'logout',
]
