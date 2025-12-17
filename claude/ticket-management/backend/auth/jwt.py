"""
JWT Token Management

This module handles JWT token creation, validation, and decoding.
Reference: /backend/auth/README.md - JWT Token Management
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status

from models import User
from config import get_settings


settings = get_settings()


# Timezone-aware datetime helper
def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        user: User object
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT access token string

    Reference: /backend/auth/README.md - Token Generation
    """
    if expires_delta:
        expire = utcnow() + expires_delta
    else:
        expire = utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "type": "access",
        "exp": expire,
        "iat": utcnow(),
        "jti": secrets.token_urlsafe(16)
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token

    Args:
        user: User object
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string

    Reference: /backend/auth/README.md - Token Generation
    """
    if expires_delta:
        expire = utcnow() + expires_delta
    else:
        expire = utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "exp": expire,
        "iat": utcnow(),
        "jti": secrets.token_urlsafe(16)
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict:
    """
    Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload dictionary

    Raises:
        HTTPException: If token is invalid or expired

    Reference: /backend/auth/README.md - Token Validation
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def decode_access_token(token: str) -> dict:
    """
    Decode and validate access token

    Args:
        token: JWT access token string

    Returns:
        Decoded token payload dictionary

    Raises:
        HTTPException: If token is invalid, expired, or not an access token
    """
    payload = decode_jwt_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def decode_refresh_token(token: str) -> dict:
    """
    Decode and validate refresh token

    Args:
        token: JWT refresh token string

    Returns:
        Decoded token payload dictionary

    Raises:
        HTTPException: If token is invalid, expired, or not a refresh token
    """
    payload = decode_jwt_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token",
        )

    return payload


def verify_token_not_expired(payload: dict) -> bool:
    """
    Verify that token is not expired

    Args:
        payload: Decoded token payload

    Returns:
        True if token is valid, False if expired
    """
    exp = payload.get("exp")
    if exp is None:
        return False

    return datetime.fromtimestamp(exp) > utcnow()


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token

    Args:
        token: JWT token string

    Returns:
        User ID string

    Raises:
        HTTPException: If token is invalid or user ID not found
    """
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user ID not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def get_token_expiration(payload: dict) -> Optional[datetime]:
    """
    Get token expiration datetime from payload

    Args:
        payload: Decoded token payload

    Returns:
        Expiration datetime or None if not found
    """
    exp = payload.get("exp")
    if exp:
        return datetime.fromtimestamp(exp)
    return None


def get_token_issued_at(payload: dict) -> Optional[datetime]:
    """
    Get token issued at datetime from payload

    Args:
        payload: Decoded token payload

    Returns:
        Issued at datetime or None if not found
    """
    iat = payload.get("iat")
    if iat:
        return datetime.fromtimestamp(iat)
    return None


def get_token_jti(payload: dict) -> Optional[str]:
    """
    Get token JWT ID (jti) from payload

    Args:
        payload: Decoded token payload

    Returns:
        JWT ID string or None if not found
    """
    return payload.get("jti")


def create_token_pair(user: User) -> tuple[str, str]:
    """
    Create both access and refresh tokens for a user

    Args:
        user: User object

    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return access_token, refresh_token


def get_access_token_expires_in() -> int:
    """
    Get access token expiration time in seconds

    Returns:
        Expiration time in seconds
    """
    return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def get_refresh_token_expires_in() -> int:
    """
    Get refresh token expiration time in seconds

    Returns:
        Expiration time in seconds
    """
    return settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def validate_token_format(token: str) -> bool:
    """
    Validate JWT token format (basic check)

    Args:
        token: JWT token string

    Returns:
        True if format is valid, False otherwise
    """
    parts = token.split('.')
    return len(parts) == 3


def generate_unique_jti() -> str:
    """
    Generate unique JWT ID for token tracking

    Returns:
        Unique token identifier string
    """
    return secrets.token_urlsafe(16)
