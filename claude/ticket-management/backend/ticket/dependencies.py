"""
Ticket Service Dependencies

FastAPI dependency injection functions for ticket service operations.
Reference: /backend/ticket/README.md - Dependencies
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Ticket, Comment, Attachment
from config import get_settings


settings = get_settings()
security = HTTPBearer()


# ============================================================================
# Database Dependency
# ============================================================================

# Database engine and session factory
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Database session dependency
    Provides database session for each request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Authentication Dependencies (from auth service)
# ============================================================================

# Import auth dependencies from auth service
# In a real microservice setup, these would validate JWT tokens
# For now, we'll create simplified versions

from jose import JWTError, jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT access token

    Args:
        token: JWT token string

    Returns:
        Token payload dictionary

    Raises:
        HTTPException: If token is invalid
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
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object (simplified - returns dict with user info from token)

    Raises:
        HTTPException: If user not found or inactive
    """
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        username = payload.get("username")
        email = payload.get("email")
        role = payload.get("role")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Return user info from token
        # In production, you might want to fetch full user from auth service
        return {
            "id": UUID(user_id),
            "username": username,
            "email": email,
            "role": role,
            "is_active": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def require_role(required_role: str):
    """
    Dependency factory to check if user has required role or higher

    Args:
        required_role: Minimum required role

    Returns:
        Dependency function that checks user role
    """
    role_hierarchy = {
        "END_USER": 0,
        "DEVOPS_ENGINEER": 1,
        "TEAM_LEAD": 2,
        "MANAGER": 3,
        "ADMIN": 4
    }

    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "END_USER")
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role or higher. Your role: {user_role}"
            )
        return current_user

    return role_checker


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin role

    Args:
        current_user: Current authenticated user

    Returns:
        User dict if admin

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )
    return current_user


def require_engineer(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require DevOps engineer role or higher

    Args:
        current_user: Current authenticated user

    Returns:
        User dict if engineer or higher

    Raises:
        HTTPException: If user is not engineer or higher
    """
    role_hierarchy = ["END_USER", "DEVOPS_ENGINEER", "TEAM_LEAD", "MANAGER", "ADMIN"]
    user_role = current_user.get("role", "END_USER")

    if user_role not in role_hierarchy[1:]:  # Must be engineer or higher
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DevOps Engineer access required"
        )
    return current_user


# ============================================================================
# Ticket-Specific Dependencies
# ============================================================================

async def get_ticket_or_404(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Ticket:
    """
    Get ticket by ID or raise 404

    Args:
        ticket_id: Ticket UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Ticket object

    Raises:
        HTTPException: If ticket not found or deleted
    """
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.deleted_at == None
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


async def get_comment_or_404(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Comment:
    """
    Get comment by ID or raise 404

    Args:
        comment_id: Comment UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Comment object

    Raises:
        HTTPException: If comment not found or deleted
    """
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.deleted_at == None
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return comment


async def get_attachment_or_404(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Attachment:
    """
    Get attachment by ID or raise 404

    Args:
        attachment_id: Attachment UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Attachment object

    Raises:
        HTTPException: If attachment not found or deleted
    """
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id,
        Attachment.deleted_at == None
    ).first()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    return attachment


# ============================================================================
# Permission Check Dependencies
# ============================================================================

async def check_ticket_access(
    ticket: Ticket,
    current_user: dict,
    require_owner: bool = False
) -> bool:
    """
    Check if user has access to view ticket

    Args:
        ticket: Ticket object
        current_user: Current authenticated user
        require_owner: If True, only ticket owner/assignee can access

    Returns:
        True if user has access

    Raises:
        HTTPException: If user doesn't have access
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Admins can access everything
    if user_role == "ADMIN":
        return True

    # Engineers can access all tickets
    if user_role in ["DEVOPS_ENGINEER", "TEAM_LEAD", "MANAGER"]:
        return True

    # End users can only access their own tickets
    if require_owner:
        if str(ticket.requestor_id) != str(user_id) and str(ticket.assigned_to) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this ticket"
            )
    else:
        if str(ticket.requestor_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this ticket"
            )

    return True


def can_view_ticket(
    ticket: Ticket = Depends(get_ticket_or_404),
    current_user: dict = Depends(get_current_user)
) -> Ticket:
    """
    Dependency to check if user can view ticket

    Args:
        ticket: Ticket object
        current_user: Current authenticated user

    Returns:
        Ticket object if user has access

    Raises:
        HTTPException: If user doesn't have access
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Check access
    if user_role in ["ADMIN", "MANAGER", "TEAM_LEAD", "DEVOPS_ENGINEER"]:
        return ticket

    # End users can view their own tickets
    if str(ticket.requestor_id) == str(user_id):
        return ticket

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to view this ticket"
    )


def can_edit_ticket(
    ticket: Ticket = Depends(get_ticket_or_404),
    current_user: dict = Depends(get_current_user)
) -> Ticket:
    """
    Dependency to check if user can edit ticket

    Args:
        ticket: Ticket object
        current_user: Current authenticated user

    Returns:
        Ticket object if user can edit

    Raises:
        HTTPException: If user doesn't have permission
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Check if ticket is closed
    if ticket.is_closed() and user_role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit closed ticket"
        )

    # Admins and managers can edit any ticket
    if user_role in ["ADMIN", "MANAGER"]:
        return ticket

    # Team leads and engineers can edit assigned tickets
    if user_role in ["TEAM_LEAD", "DEVOPS_ENGINEER"]:
        if str(ticket.assigned_to) == str(user_id):
            return ticket
        if user_role == "TEAM_LEAD":  # Team leads can edit team tickets
            return ticket

    # End users can edit their own unassigned tickets
    if user_role == "END_USER" and str(ticket.requestor_id) == str(user_id):
        if ticket.assigned_to is None:
            return ticket

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to edit this ticket"
    )


def can_assign_ticket(
    ticket: Ticket = Depends(get_ticket_or_404),
    current_user: dict = Depends(require_engineer)
) -> Ticket:
    """
    Dependency to check if user can assign tickets

    Args:
        ticket: Ticket object
        current_user: Current authenticated user

    Returns:
        Ticket object if user can assign

    Raises:
        HTTPException: If user doesn't have permission
    """
    if ticket.is_closed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign closed ticket"
        )

    return ticket


def can_delete_ticket(
    ticket: Ticket = Depends(get_ticket_or_404),
    current_user: dict = Depends(require_admin)
) -> Ticket:
    """
    Dependency to check if user can delete tickets (admin only)

    Args:
        ticket: Ticket object
        current_user: Current authenticated user

    Returns:
        Ticket object if user can delete
    """
    return ticket


async def can_edit_comment(
    comment: Comment,
    current_user: dict
) -> bool:
    """
    Check if user can edit comment

    Args:
        comment: Comment object
        current_user: Current authenticated user

    Returns:
        True if user can edit

    Raises:
        HTTPException: If user doesn't have permission
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Admins can edit any comment
    if user_role == "ADMIN":
        return True

    # Authors can edit their own comments
    if str(comment.author_id) == str(user_id):
        if comment.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit deleted comment"
            )
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to edit this comment"
    )


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
