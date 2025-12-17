"""
Authentication Module

Comprehensive authentication and authorization system for Ticket Management.
Reference: /backend/auth/README.md
"""

from .models import User, UserRole, UserStatus, RefreshToken, UserSession, PasswordReset, AuditLog
from .schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from .jwt import create_access_token, create_refresh_token, decode_jwt_token
from .dependencies import get_current_user, require_role, require_admin
from .permissions import Permission, check_permission
from .config import get_settings

__all__ = [
    # Models
    "User",
    "UserRole",
    "UserStatus",
    "RefreshToken",
    "UserSession",
    "PasswordReset",
    "AuditLog",
    # Schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenRefreshRequest",
    "TokenRefreshResponse",
    # JWT
    "create_access_token",
    "create_refresh_token",
    "decode_jwt_token",
    # Dependencies
    "get_current_user",
    "require_role",
    "require_admin",
    # Permissions
    "Permission",
    "check_permission",
    # Config
    "get_settings",
]
