"""
Authentication Pydantic Schemas

This module defines Pydantic models for request/response validation.
Reference: /backend/auth/README.md
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from models import UserRole, UserStatus


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    department: Optional[str] = Field(None, max_length=100, description="Department")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Username can only contain alphanumeric characters, dots, hyphens, and underscores')
        return v.lower()

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format"""
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v.replace('-', '').replace(' ', '')):
            raise ValueError('Invalid phone number format')
        return v


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special)"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength
        Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    """Schema for user profile update"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone_number: Optional[str]
    department: Optional[str]
    role: UserRole
    status: UserStatus
    is_active: bool
    is_email_verified: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., min_length=3, description="Username or email")
    password: str = Field(..., min_length=1, description="User password")


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: UserResponse


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str = Field(..., description="Refresh token")


class TokenRefreshResponse(BaseModel):
    """Schema for token refresh response"""
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token (optional)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class LogoutRequest(BaseModel):
    """Schema for logout request"""
    refresh_token: Optional[str] = Field(None, description="Refresh token to revoke")


# ============================================================================
# Password Management Schemas
# ============================================================================

class PasswordChangeRequest(BaseModel):
    """Schema for password change"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Schema for password reset"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


# ============================================================================
# Email Verification Schemas
# ============================================================================

class VerifyEmailRequest(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., description="Email verification token")


# ============================================================================
# Session Management Schemas
# ============================================================================

class SessionResponse(BaseModel):
    """Schema for user session response"""
    id: UUID
    user_id: UUID
    session_token: str
    device_type: Optional[str] = None
    device_name: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    is_active: bool
    ended_at: Optional[datetime] = None
    end_reason: Optional[str] = None
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionListResponse(BaseModel):
    """Schema for session list response"""
    sessions: list[SessionResponse]
    total: int


# ============================================================================
# MFA Schemas
# ============================================================================

class MFASetupResponse(BaseModel):
    """Schema for MFA setup response"""
    secret: str = Field(..., description="MFA secret key")
    qr_code_uri: str = Field(..., description="QR code provisioning URI")
    backup_codes: list[str] = Field(..., description="Backup recovery codes")


class MFAVerifyRequest(BaseModel):
    """Schema for MFA code verification"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit MFA code")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate MFA code format"""
        if not v.isdigit():
            raise ValueError('MFA code must be 6 digits')
        return v


class MFADisableRequest(BaseModel):
    """Schema for disabling MFA"""
    password: str = Field(..., description="User password for verification")
    code: Optional[str] = Field(None, description="Current MFA code")


# ============================================================================
# Admin User Management Schemas
# ============================================================================

class AdminUserCreate(UserCreate):
    """Schema for admin user creation"""
    role: UserRole = Field(default=UserRole.END_USER, description="User role")
    is_active: bool = Field(default=True, description="Account active status")


class AdminUserUpdate(UserUpdate):
    """Schema for admin user update"""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: UUID
    user_id: Optional[UUID]
    action_type: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    old_values: Optional[dict]
    new_values: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    severity: Optional[str]
    status: Optional[str]
    session_id: Optional[UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list"""
    logs: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Generic Response Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Error code")


# ============================================================================
# Request Context Schemas
# ============================================================================

class DeviceInfo(BaseModel):
    """Device information schema"""
    user_agent: str
    ip_address: str
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None


# ============================================================================
# Token Payload Schemas
# ============================================================================

class TokenPayload(BaseModel):
    """JWT token payload schema"""
    sub: str = Field(..., description="Subject (user ID)")
    username: str
    email: str
    role: str
    type: str = Field(..., description="Token type (access/refresh)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    jti: str = Field(..., description="JWT ID (unique token identifier)")
