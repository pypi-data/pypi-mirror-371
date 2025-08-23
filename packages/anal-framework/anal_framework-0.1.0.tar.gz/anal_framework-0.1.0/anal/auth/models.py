"""
Authentication models for ANAL framework.

This module provides user models and authentication-related database models.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List

from ..db import Model, fields


class User(Model):
    """Default user model for authentication."""
    
    id = fields.AutoField()
    username = fields.CharField(max_length=150, unique=True)
    email = fields.EmailField(unique=True)
    password_hash = fields.CharField(max_length=255)
    first_name = fields.CharField(max_length=30, blank=True)
    last_name = fields.CharField(max_length=30, blank=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    date_joined = fields.DateTimeField(auto_now_add=True)
    last_login = fields.DateTimeField(null=True, blank=True)
    
    class Meta:
        table_name = 'auth_users'
        ordering = ['username']
    
    def __str__(self):
        return self.username
    
    def set_password(self, raw_password: str):
        """Set password with hashing."""
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(raw_password, salt)
        self.password_hash = f"{salt}${password_hash}"
    
    def check_password(self, raw_password: str) -> bool:
        """Check if raw password matches stored hash."""
        if '$' not in self.password_hash:
            return False
        
        salt, stored_hash = self.password_hash.split('$', 1)
        password_hash = self._hash_password(raw_password, salt)
        return password_hash == stored_hash
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    
    def get_full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self) -> str:
        """Get user's short name."""
        return self.first_name or self.username
    
    def has_perm(self, permission: str) -> bool:
        """Check if user has permission."""
        if self.is_superuser:
            return True
        
        # Check user permissions
        # This would be implemented with actual permission checking
        return False
    
    def has_perms(self, permissions: List[str]) -> bool:
        """Check if user has all permissions."""
        return all(self.has_perm(perm) for perm in permissions)
    
    def has_module_perms(self, app_label: str) -> bool:
        """Check if user has permissions for an app."""
        if self.is_superuser:
            return True
        
        # This would be implemented with actual module permission checking
        return False


class Group(Model):
    """Group model for permission grouping."""
    
    id = fields.AutoField()
    name = fields.CharField(max_length=150, unique=True)
    description = fields.TextField(blank=True)
    created_at = fields.DateTimeField(auto_now_add=True)
    
    class Meta:
        table_name = 'auth_groups'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Permission(Model):
    """Permission model for access control."""
    
    id = fields.AutoField()
    name = fields.CharField(max_length=255)
    content_type = fields.CharField(max_length=100)  # app.model
    codename = fields.CharField(max_length=100)
    
    class Meta:
        table_name = 'auth_permissions'
        ordering = ['content_type', 'codename']
    
    def __str__(self):
        return f"{self.content_type} | {self.name}"


class UserGroup(Model):
    """Many-to-many relationship between Users and Groups."""
    
    id = fields.AutoField()
    user = fields.ForeignKey(User, on_delete='CASCADE')
    group = fields.ForeignKey(Group, on_delete='CASCADE')
    
    class Meta:
        table_name = 'auth_user_groups'


class UserPermission(Model):
    """Many-to-many relationship between Users and Permissions."""
    
    id = fields.AutoField()
    user = fields.ForeignKey(User, on_delete='CASCADE')
    permission = fields.ForeignKey(Permission, on_delete='CASCADE')
    
    class Meta:
        table_name = 'auth_user_permissions'


class GroupPermission(Model):
    """Many-to-many relationship between Groups and Permissions."""
    
    id = fields.AutoField()
    group = fields.ForeignKey(Group, on_delete='CASCADE')
    permission = fields.ForeignKey(Permission, on_delete='CASCADE')
    
    class Meta:
        table_name = 'auth_group_permissions'


class Session(Model):
    """Session model for session management."""
    
    session_key = fields.CharField(max_length=40, unique=True)
    session_data = fields.TextField()
    expire_date = fields.DateTimeField()
    
    class Meta:
        table_name = 'auth_sessions'
        ordering = ['expire_date']
    
    def __str__(self):
        return self.session_key
    
    @classmethod
    def generate_key(cls) -> str:
        """Generate a new session key."""
        return secrets.token_urlsafe(30)
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now() > self.expire_date
    
    def set_expiry(self, days: int = 14):
        """Set session expiry."""
        self.expire_date = datetime.now() + timedelta(days=days)


class Token(Model):
    """API token model for authentication."""
    
    id = fields.AutoField()
    key = fields.CharField(max_length=40, unique=True)
    user = fields.ForeignKey(User, on_delete='CASCADE')
    name = fields.CharField(max_length=100, blank=True)
    created = fields.DateTimeField(auto_now_add=True)
    last_used = fields.DateTimeField(null=True, blank=True)
    is_active = fields.BooleanField(default=True)
    
    class Meta:
        table_name = 'auth_tokens'
        ordering = ['-created']
    
    def __str__(self):
        return f"Token for {self.user.username}"
    
    @classmethod
    def generate_key(cls) -> str:
        """Generate a new token key."""
        return secrets.token_urlsafe(30)
    
    def save(self):
        """Override save to generate key if not present."""
        if not self.key:
            self.key = self.generate_key()
        super().save()


class PasswordResetToken(Model):
    """Password reset token model."""
    
    id = fields.AutoField()
    user = fields.ForeignKey(User, on_delete='CASCADE')
    token = fields.CharField(max_length=100, unique=True)
    created_at = fields.DateTimeField(auto_now_add=True)
    used_at = fields.DateTimeField(null=True, blank=True)
    expires_at = fields.DateTimeField()
    
    class Meta:
        table_name = 'auth_password_reset_tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password reset for {self.user.username}"
    
    @classmethod
    def generate_token(cls) -> str:
        """Generate a new reset token."""
        return secrets.token_urlsafe(32)
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now() > self.expires_at
    
    def is_used(self) -> bool:
        """Check if token has been used."""
        return self.used_at is not None
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)."""
        return not self.is_expired() and not self.is_used()
    
    def mark_used(self):
        """Mark token as used."""
        self.used_at = datetime.now()
        self.save()
    
    def save(self):
        """Override save to set expiry and generate token."""
        if not self.token:
            self.token = self.generate_token()
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(hours=24)
        super().save()


# Export all models
__all__ = [
    'User',
    'Group', 
    'Permission',
    'UserGroup',
    'UserPermission',
    'GroupPermission',
    'Session',
    'Token',
    'PasswordResetToken',
]
