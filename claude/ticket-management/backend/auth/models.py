"""
Authentication Database Models

This module defines SQLAlchemy models for authentication and user management.
Models are aligned with database schema from /backend/db_migrations/
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    TypeDecorator,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()

# Timezone-aware datetime helper
def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)

# Custom UUID type that works with both PostgreSQL and SQLite
class UUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses
    String(36) for databases like SQLite.
    """
    impl = String
    cache_ok = True

    def __init__(self, as_uuid=True):
        """Initialize UUID type. The as_uuid parameter is accepted for compatibility."""
        self.as_uuid = as_uuid
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=self.as_uuid))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not self.as_uuid:
            return str(value) if value else None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)

# Custom JSONB type that works with both PostgreSQL and SQLite
class JSONB(TypeDecorator):
    """Platform-independent JSONB type.

    Uses PostgreSQL's JSONB type when available, otherwise uses
    JSON for databases like SQLite.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(JSON())

# Password hashing - using bcrypt directly to avoid passlib truncation issues
import bcrypt as _bcrypt_module

def _hash_password(password: str) -> str:
    """Hash password using bcrypt, handling 72-byte limit"""
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    salt = _bcrypt_module.gensalt(rounds=12)
    hashed = _bcrypt_module.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def _verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash, handling 72-byte limit"""
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    hashed_bytes = hashed.encode('utf-8')
    return _bcrypt_module.checkpw(password_bytes, hashed_bytes)


class UserRole(str, PyEnum):
    """
    User roles with hierarchical levels
    Reference: /backend/auth/README.md - User Roles
    """
    ADMIN = "ADMIN"  # Level 5
    MANAGER = "MANAGER"  # Level 4
    TEAM_LEAD = "TEAM_LEAD"  # Level 3
    SENIOR_ENGINEER = "SENIOR_ENGINEER"  # Level 2
    DEVOPS_ENGINEER = "DEVOPS_ENGINEER"  # Level 1
    END_USER = "END_USER"  # Level 0

    @property
    def level(self) -> int:
        """Get numeric level for role comparison"""
        levels = {
            "END_USER": 0,
            "DEVOPS_ENGINEER": 1,
            "SENIOR_ENGINEER": 2,
            "TEAM_LEAD": 3,
            "MANAGER": 4,
            "ADMIN": 5,
        }
        return levels.get(self.value, 0)


class UserStatus(str, PyEnum):
    """User account status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"


class User(Base):
    """
    User Model
    Reference: /backend/db_migrations/V1__create_users_table.sql
    Reference: /backend/db_migrations/README.md - users table
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication Fields
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Profile Fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    department = Column(String(100))

    # Role & Status
    role = Column(Enum(UserRole), default=UserRole.END_USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Email Verification
    is_email_verified = Column(Boolean, default=False, nullable=False)

    # Security Fields
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255))

    # Account Security
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password: str) -> None:
        """
        Hash and set user password

        Uses bcrypt directly with automatic truncation to 72 bytes.
        """
        self.password_hash = _hash_password(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash

        Uses bcrypt directly with automatic truncation to 72 bytes.
        """
        return _verify_password(password, self.password_hash)

    def has_role(self, required_role: UserRole) -> bool:
        """Check if user has specific role or higher"""
        return self.role.level >= required_role.level

    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.status == UserStatus.LOCKED:
            if self.account_locked_until and utcnow() < self.account_locked_until:
                return True
            else:
                # Auto-unlock if duration expired
                self.status = UserStatus.ACTIVE
                self.failed_login_attempts = 0
                self.account_locked_until = None
                return False
        return False

    def record_login_success(self) -> None:
        """Record successful login"""
        self.last_login = utcnow()
        self.failed_login_attempts = 0
        self.account_locked_until = None

    def record_login_failure(self, max_attempts: int = 5, lockout_minutes: int = 30) -> None:
        """Record failed login attempt and lock account if threshold exceeded"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.status = UserStatus.LOCKED
            self.account_locked_until = utcnow() + timedelta(minutes=lockout_minutes)

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary (excluding sensitive data by default)"""
        data = {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "department": self.department,
            "role": self.role.value,
            "status": self.status.value,
            "is_active": self.is_active,
            "is_email_verified": self.is_email_verified,
            "mfa_enabled": self.mfa_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive:
            data["failed_login_attempts"] = self.failed_login_attempts
            data["account_locked_until"] = (
                self.account_locked_until.isoformat() if self.account_locked_until else None
            )

        return data


class RefreshToken(Base):
    """
    Refresh Token Model
    Reference: /backend/db_migrations/V2__create_refresh_tokens_table.sql
    Reference: /backend/db_migrations/README.md - refresh_tokens table
    """
    __tablename__ = "refresh_tokens"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Token Fields
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    token_family = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)

    # Device & Location Information
    device_type = Column(String(50))
    device_name = Column(String(100))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    location = Column(String(255))

    # Status & Expiry
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True))
    revoked_reason = Column(String(255))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"

    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)"""
        return not self.is_revoked and utcnow() < self.expires_at

    def revoke(self) -> None:
        """Revoke the token"""
        self.is_revoked = True

    def update_last_used(self) -> None:
        """Update last used timestamp"""
        self.last_used_at = utcnow()


class UserSession(Base):
    """
    User Session Model
    Reference: /backend/db_migrations/V3__create_user_sessions_table.sql
    Reference: /backend/db_migrations/README.md - user_sessions table
    """
    __tablename__ = "user_sessions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Session Fields
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token_id = Column(UUID(as_uuid=True), ForeignKey("refresh_tokens.id", ondelete="SET NULL"))

    # Device & Location
    device_type = Column(String(50))
    device_name = Column(String(100))
    user_agent = Column(Text)
    ip_address = Column(String(45), nullable=False)
    location = Column(String(255))

    # Session Status
    is_active = Column(Boolean, default=True, nullable=False)
    ended_at = Column(DateTime(timezone=True))
    end_reason = Column(String(100))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"

    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)"""
        return self.is_active and utcnow() < self.expires_at

    def terminate(self, reason: str = "logout") -> None:
        """Terminate the session"""
        self.is_active = False
        self.ended_at = utcnow()
        self.end_reason = reason

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity_at = utcnow()

    def extend_expiration(self, days: int = 7) -> None:
        """Extend session expiration"""
        self.expires_at = utcnow() + timedelta(days=days)


class PasswordReset(Base):
    """
    Password Reset Model
    Reference: /backend/db_migrations/V4__create_password_resets_table.sql
    Reference: /backend/db_migrations/README.md - password_resets table
    """
    __tablename__ = "password_resets"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Token Fields
    token_hash = Column(String(255), nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)

    # Request Information
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="password_resets")

    def __repr__(self):
        return f"<PasswordReset(id={self.id}, user_id={self.user_id}, is_used={self.is_used})>"

    def is_valid(self) -> bool:
        """Check if reset token is valid (not used and not expired)"""
        return not self.is_used and utcnow() < self.expires_at

    def mark_as_used(self) -> None:
        """Mark token as used"""
        self.is_used = True
        self.used_at = utcnow()


class AuditLog(Base):
    """
    Audit Log Model
    Reference: /backend/db_migrations/V5__create_audit_logs_table.sql
    Reference: /backend/db_migrations/README.md - audit_logs table
    """
    __tablename__ = "audit_logs"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key (nullable to preserve logs even if user is deleted)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    # Event Fields
    action_type = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID(as_uuid=True))
    action_description = Column(Text)  # Made nullable in V7

    # Request Information
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_method = Column(String(10))  # GET, POST, PUT, DELETE
    request_path = Column(String(255))

    # Change Tracking
    old_values = Column(JSONB)
    new_values = Column(JSONB)

    # Status & Error
    status = Column(String(20), nullable=False)  # SUCCESS, FAILED, ERROR
    error_message = Column(Text)

    # Additional Information (added in V7)
    severity = Column(String(20))  # INFO, WARNING, ERROR, CRITICAL
    session_id = Column(UUID(as_uuid=True))
    details = Column(JSONB)  # Additional structured details

    # Timestamp (immutable)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    @property
    def timestamp(self):
        """Alias for created_at for API compatibility"""
        return self.created_at

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action_type}', user_id={self.user_id})>"

    def to_dict(self) -> dict:
        """Convert audit log to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "action_type": self.action_type,
            "resource_type": self.resource_type,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "severity": self.severity,
            "status": self.status,
            "session_id": str(self.session_id) if self.session_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Audit event types
class AuditEventType(str, PyEnum):
    """Standard audit event types"""
    # Authentication Events
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    TOKEN_REFRESH = "TOKEN_REFRESH"

    # Password Events
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET_REQUEST = "PASSWORD_RESET_REQUEST"
    PASSWORD_RESET_COMPLETE = "PASSWORD_RESET_COMPLETE"

    # Account Events
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED"
    ACCOUNT_DELETED = "ACCOUNT_DELETED"
    ACCOUNT_ENABLED = "ACCOUNT_ENABLED"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"

    # Email Events
    EMAIL_VERIFICATION_SENT = "EMAIL_VERIFICATION_SENT"
    EMAIL_VERIFIED = "EMAIL_VERIFIED"

    # Profile Events
    PROFILE_UPDATED = "PROFILE_UPDATED"
    USER_UPDATED = "USER_UPDATED"
    ROLE_CHANGED = "ROLE_CHANGED"

    # Token Events
    TOKEN_REVOKED = "TOKEN_REVOKED"
    TOKENS_REVOKED = "TOKENS_REVOKED"

    # MFA Events
    MFA_ENABLED = "MFA_ENABLED"
    MFA_DISABLED = "MFA_DISABLED"
    MFA_CODE_VERIFIED = "MFA_CODE_VERIFIED"

    # Session Events
    SESSION_CREATED = "SESSION_CREATED"
    SESSION_TERMINATED = "SESSION_TERMINATED"
