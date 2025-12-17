"""
User management routes.

Handles CRUD operations for users.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from database import get_db
from schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    MessageResponse
)
from auth import get_current_active_user, get_current_superuser
from models import User
import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search query for email, username, or name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a paginated list of users.

    Requires authentication. Users can see the list of all users.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        search: Optional search query
        is_active: Optional filter by active status
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserListResponse: Paginated list of users
    """
    try:
        users, total = await crud.get_users(
            db,
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active
        )

        return UserListResponse(
            users=users,
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a user by ID.

    Requires authentication. Users can view any user's public information.

    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserResponse: User information

    Raises:
        HTTPException: If user not found
    """
    user = await crud.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Create a new user.

    Requires superuser (admin) privileges.

    Args:
        user_data: User creation data
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If email or username already exists
    """
    try:
        user = await crud.create_user(db, user_data)

        logger.info(f"User created by admin {current_user.email}: {user.email}")

        return user

    except ValueError as e:
        logger.warning(f"User creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a user's information.

    Users can update their own profile. Superusers can update any user.

    Args:
        user_id: User ID to update
        user_data: User update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        UserResponse: Updated user information

    Raises:
        HTTPException: If user not found or permission denied
    """
    try:
        # Check if user exists
        user = await crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check permissions: users can only update themselves unless they're superuser
        if not current_user.is_superuser and str(user.id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )

        # Non-superusers cannot modify is_active status
        if not current_user.is_superuser and user_data.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify user active status"
            )

        # Update user
        updated_user = await crud.update_user(db, user_id, user_data, current_user)

        logger.info(f"User updated: {updated_user.email} by {current_user.email}")

        return updated_user

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"User update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    permanent: bool = Query(False, description="Permanently delete user (hard delete)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a user (soft delete by default).

    Requires superuser (admin) privileges.

    By default, users are soft deleted (marked as inactive). Use permanent=true
    to permanently delete the user from the database.

    Args:
        user_id: User ID to delete
        permanent: If true, permanently delete; otherwise soft delete
        db: Database session
        current_user: Current authenticated superuser

    Returns:
        MessageResponse: Success message

    Raises:
        HTTPException: If user not found or deletion fails
    """
    try:
        # Check if user exists
        user = await crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent deleting yourself
        if str(user.id) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        # Delete user
        success = await crud.delete_user(db, user_id, soft_delete=not permanent, current_user=current_user)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

        delete_type = "permanently deleted" if permanent else "deactivated"
        logger.info(f"User {delete_type}: {user.email} by {current_user.email}")

        return MessageResponse(
            message=f"User {delete_type} successfully",
            detail=f"User ID: {user_id}"
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
