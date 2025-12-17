"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
import re


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    bio: Optional[str] = Field(None, max_length=1000, description="User biography")


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Includes password with validation rules.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 chars, 1 uppercase, 1 number)"
    )

    @validator("password")
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.

        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

    @validator("username")
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.

        Requirements:
        - Only alphanumeric characters, underscores, and hyphens
        - Must start with a letter
        """
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError(
                "Username must start with a letter and contain only "
                "alphanumeric characters, underscores, and hyphens"
            )
        return v


class UserUpdate(BaseModel):
    """
    Schema for updating a user.

    All fields are optional.
    """
    email: Optional[EmailStr] = Field(None, description="User's email address")
    username: Optional[str] = Field(None, min_length=3, max_length=100, description="Username")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name")
    bio: Optional[str] = Field(None, max_length=1000, description="User biography")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="New password"
    )
    is_active: Optional[bool] = Field(None, description="Active status")

    @validator("password")
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password if provided."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

    @validator("username")
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format if provided."""
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError(
                "Username must start with a letter and contain only "
                "alphanumeric characters, underscores, and hyphens"
            )
        return v


class UserResponse(UserBase):
    """
    Schema for user response.

    Includes all fields except password.
    """
    id: UUID = Field(..., description="User ID")
    is_active: bool = Field(..., description="Active status")
    is_superuser: bool = Field(..., description="Superuser status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of skipped items")
    limit: int = Field(..., description="Number of items per page")


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")


class RegisterRequest(UserCreate):
    """Schema for registration request (same as UserCreate)."""
    pass


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")


class MessageResponse(BaseModel):
    """Schema for generic message response."""
    message: str = Field(..., description="Response message")
    detail: Optional[str] = Field(None, description="Additional details")


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")
