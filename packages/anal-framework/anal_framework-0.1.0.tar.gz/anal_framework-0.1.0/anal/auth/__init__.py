"""
Authentication module for ANAL framework.

This module provides complete authentication and authorization functionality
including models, backends, middleware, and decorators.
"""

from .models import (
    User,
    Group,
    Permission,
    UserGroup,
    UserPermission,
    GroupPermission,
    Session,
    Token,
    PasswordResetToken,
)

from .backends import (
    BaseBackend,
    UsernamePasswordBackend,
    TokenBackend,
    SessionBackend,
    AuthenticationManager,
    PermissionChecker,
    get_auth_manager,
    authenticate,
    login,
    logout,
)

from .middleware import (
    AuthenticationMiddleware,
    RequireAuthenticationMiddleware,
    PermissionRequiredMiddleware,
    CORSMiddleware,
    RateLimitMiddleware,
)

from .decorators import (
    login_required,
    permission_required,
    permissions_required,
    staff_required,
    superuser_required,
    active_required,
    anonymous_required,
    throttle,
    api_auth_required,
    admin_required,
    secure_api,
)


# Convenience functions for common auth operations
async def create_user(username: str, email: str, password: str, **extra_fields) -> User:
    """Create a new user."""
    user = User(
        username=username,
        email=email,
        **extra_fields
    )
    user.set_password(password)
    await user.asave()
    return user


async def create_superuser(username: str, email: str, password: str, **extra_fields) -> User:
    """Create a new superuser."""
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    
    if extra_fields.get('is_staff') is not True:
        raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
        raise ValueError('Superuser must have is_superuser=True.')
    
    return await create_user(username, email, password, **extra_fields)


async def get_user_by_username(username: str) -> User:
    """Get user by username."""
    return await User.objects.get(username=username)


async def get_user_by_email(email: str) -> User:
    """Get user by email."""
    return await User.objects.get(email=email)


async def change_password(user: User, new_password: str):
    """Change user password."""
    user.set_password(new_password)
    await user.asave()


async def create_password_reset_token(user: User) -> PasswordResetToken:
    """Create password reset token for user."""
    # Deactivate existing tokens
    existing_tokens = await PasswordResetToken.objects.filter(
        user=user, 
        used_at__isnull=True
    ).all()
    
    for token in existing_tokens:
        token.mark_used()
    
    # Create new token
    reset_token = PasswordResetToken(user=user)
    await reset_token.asave()
    return reset_token


async def reset_password_with_token(token: str, new_password: str) -> bool:
    """Reset password using reset token."""
    try:
        reset_token = await PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            return False
        
        # Change password
        user = await reset_token.user
        user.set_password(new_password)
        await user.asave()
        
        # Mark token as used
        reset_token.mark_used()
        
        return True
    except:
        return False


# Export everything
__all__ = [
    # Models
    'User',
    'Group',
    'Permission',
    'UserGroup',
    'UserPermission',
    'GroupPermission',
    'Session',
    'Token',
    'PasswordResetToken',
    
    # Backends
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
    
    # Middleware
    'AuthenticationMiddleware',
    'RequireAuthenticationMiddleware',
    'PermissionRequiredMiddleware',
    'CORSMiddleware',
    'RateLimitMiddleware',
    
    # Decorators
    'login_required',
    'permission_required',
    'permissions_required',
    'staff_required',
    'superuser_required',
    'active_required',
    'anonymous_required',
    'throttle',
    'api_auth_required',
    'admin_required',
    'secure_api',
    
    # Convenience functions
    'create_user',
    'create_superuser',
    'get_user_by_username',
    'get_user_by_email',
    'change_password',
    'create_password_reset_token',
    'reset_password_with_token',
]
