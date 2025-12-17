"""
Authentication Dependencies

FastAPI dependency injection functions for authentication and authorization.
Reference: /backend/auth/README.md - Authorization & Permissions
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from models import User, UserRole, UserStatus
from jwt import decode_access_token, extract_user_id_from_token
from config import get_settings


settings = get_settings()
security = HTTPBearer()


# ============================================================================
# Database Dependency
# ============================================================================

def get_db():
    """
    Database session dependency
    This should be imported from a central database module
    For now, this is a placeholder
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Authentication Dependencies
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If user not found or inactive

    Reference: /backend/auth/README.md - Get Current User
    """
    token = credentials.credentials

    # Decode and validate JWT token
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Fetch user from database
    user = db.query(User).filter(User.id == UUID(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    # Check if account is locked
    if user.is_account_locked():
        lockout_time = user.account_locked_until.isoformat() if user.account_locked_until else "unknown"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked until {lockout_time}"
        )

    # Check account status
    if user.status not in [UserStatus.ACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account status is {user.status.value}"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional check for is_active flag)

    Args:
        current_user: Current authenticated user

    Returns:
        Active user object

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user with verified email

    Args:
        current_user: Current authenticated user

    Returns:
        User object with verified email

    Raises:
        HTTPException: If email is not verified
    """
    if not current_user.is_email_verified and settings.EMAIL_VERIFICATION_REQUIRED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that work differently for authenticated vs anonymous users

    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session

    Returns:
        User object or None
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            return None

        user = db.query(User).filter(User.id == UUID(user_id)).first()
        return user if user and user.is_active else None
    except:
        return None


# ============================================================================
# Role-Based Authorization Dependencies
# ============================================================================

def require_role(required_role: UserRole):
    """
    Dependency factory to check if user has required role or higher

    Args:
        required_role: Minimum required role

    Returns:
        Dependency function that checks user role

    Reference: /backend/auth/README.md - Require Specific Role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher. Your role: {current_user.role.value}"
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin role

    Args:
        current_user: Current authenticated user

    Returns:
        User object if admin

    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.has_role(UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )
    return current_user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require manager role or higher

    Args:
        current_user: Current authenticated user

    Returns:
        User object if manager or higher

    Raises:
        HTTPException: If user is not manager or higher
    """
    if not current_user.has_role(UserRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user


def require_team_lead(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require team lead role or higher

    Args:
        current_user: Current authenticated user

    Returns:
        User object if team lead or higher

    Raises:
        HTTPException: If user is not team lead or higher
    """
    if not current_user.has_role(UserRole.TEAM_LEAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team Lead access required"
        )
    return current_user


# ============================================================================
# Request Context Dependencies
# ============================================================================

async def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request

    Args:
        request: FastAPI request object

    Returns:
        Client IP address string
    """
    # Check for X-Forwarded-For header (reverse proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"


async def get_user_agent(request: Request) -> str:
    """
    Get user agent from request

    Args:
        request: FastAPI request object

    Returns:
        User agent string
    """
    return request.headers.get("User-Agent", "unknown")


async def get_device_info(request: Request) -> dict:
    """
    Get device information from request

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with device information
    """
    user_agent = await get_user_agent(request)
    ip_address = await get_client_ip(request)

    return {
        "user_agent": user_agent,
        "ip_address": ip_address,
        "headers": dict(request.headers)
    }


# ============================================================================
# MFA Dependencies
# ============================================================================

async def require_mfa(current_user: User = Depends(get_current_user)) -> User:
    """
    Require user to have MFA enabled

    Args:
        current_user: Current authenticated user

    Returns:
        User object if MFA is enabled

    Raises:
        HTTPException: If MFA is not enabled
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Multi-factor authentication required"
        )
    return current_user


async def require_mfa_verified(current_user: User = Depends(get_current_user)) -> User:
    """
    Require user to have completed MFA verification in current session
    This would typically check a session flag or token claim

    Args:
        current_user: Current authenticated user

    Returns:
        User object if MFA is verified

    Raises:
        HTTPException: If MFA verification is pending
    """
    # TODO: Implement MFA verification check
    # This should verify that the user has completed MFA challenge
    # in the current session (check token claims or session data)
    return current_user


# ============================================================================
# Utility Dependencies
# ============================================================================

async def verify_token_validity(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify token and return decoded payload without fetching user

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload


async def get_pagination_params(
    page: int = 1,
    page_size: int = 50,
    max_page_size: int = 100
) -> dict:
    """
    Get pagination parameters with validation

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size

    Returns:
        Dictionary with validated pagination parameters

    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be >= 1"
        )

    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be >= 1"
        )

    if page_size > max_page_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page size cannot exceed {max_page_size}"
        )

    offset = (page - 1) * page_size

    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
        "limit": page_size
    }
