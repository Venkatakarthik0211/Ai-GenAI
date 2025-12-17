"""
CRUD operations for database models.

Provides async functions for creating, reading, updating, and deleting users.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from models import User
from schemas import UserCreate, UserUpdate
from auth import get_password_hash

logger = logging.getLogger(__name__)


async def get_user_by_id(db: AsyncSession, user_id: str | UUID) -> Optional[User]:
    """
    Get a user by their ID.

    Args:
        db: Database session
        user_id: User ID (UUID or string)

    Returns:
        User: User object if found, None otherwise
    """
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user
    except Exception as e:
        logger.error(f"Error fetching user by ID {user_id}: {str(e)}")
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by their email address.

    Args:
        db: Database session
        email: User's email address

    Returns:
        User: User object if found, None otherwise
    """
    try:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user
    except Exception as e:
        logger.error(f"Error fetching user by email {email}: {str(e)}")
        return None


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Get a user by their username.

    Args:
        db: Database session
        username: User's username

    Returns:
        User: User object if found, None otherwise
    """
    try:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        return user
    except Exception as e:
        logger.error(f"Error fetching user by username {username}: {str(e)}")
        return None


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    is_active: Optional[bool] = None
) -> tuple[List[User], int]:
    """
    Get a paginated list of users with optional filtering.

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        search: Optional search query (searches email, username, full_name)
        is_active: Optional filter by active status

    Returns:
        tuple: (list of users, total count)
    """
    try:
        # Build base query
        stmt = select(User)

        # Apply filters
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.email.ilike(search_pattern),
                    User.username.ilike(search_pattern),
                    User.full_name.ilike(search_pattern)
                )
            )

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        # Apply pagination and ordering
        stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)

        # Execute query
        result = await db.execute(stmt)
        users = result.scalars().all()

        return list(users), total

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return [], 0


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        User: Created user object

    Raises:
        ValueError: If email or username already exists
    """
    try:
        # Check if email already exists
        existing_email = await get_user_by_email(db, user_data.email)
        if existing_email:
            raise ValueError("Email already registered")

        # Check if username already exists
        existing_username = await get_user_by_username(db, user_data.username)
        if existing_username:
            raise ValueError("Username already taken")

        # Create user instance
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            bio=user_data.bio,
            is_active=True,
            is_superuser=False,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"User created successfully: {user.email}")
        return user

    except ValueError:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise ValueError(f"Failed to create user: {str(e)}")


async def update_user(
    db: AsyncSession,
    user_id: str | UUID,
    user_data: UserUpdate,
    current_user: Optional[User] = None
) -> Optional[User]:
    """
    Update a user's information.

    Args:
        db: Database session
        user_id: ID of the user to update
        user_data: User update data
        current_user: Current authenticated user (for permission checks)

    Returns:
        User: Updated user object if successful, None otherwise

    Raises:
        ValueError: If validation fails or user not found
        PermissionError: If user doesn't have permission to update
    """
    try:
        # Get the user to update
        user = await get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Permission check: users can only update themselves unless they're superuser
        if current_user and not current_user.is_superuser:
            if str(user.id) != str(current_user.id):
                raise PermissionError("Not authorized to update this user")

        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != user.email:
            existing_email = await get_user_by_email(db, user_data.email)
            if existing_email:
                raise ValueError("Email already registered")

        # Check username uniqueness if username is being updated
        if user_data.username and user_data.username != user.username:
            existing_username = await get_user_by_username(db, user_data.username)
            if existing_username:
                raise ValueError("Username already taken")

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)

        # Handle password update separately
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        # Apply updates
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(user)

        logger.info(f"User updated successfully: {user.email}")
        return user

    except (ValueError, PermissionError):
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise ValueError(f"Failed to update user: {str(e)}")


async def delete_user(
    db: AsyncSession,
    user_id: str | UUID,
    soft_delete: bool = True,
    current_user: Optional[User] = None
) -> bool:
    """
    Delete a user (soft delete by default).

    Args:
        db: Database session
        user_id: ID of the user to delete
        soft_delete: If True, mark as inactive; if False, permanently delete
        current_user: Current authenticated user (for permission checks)

    Returns:
        bool: True if successful, False otherwise

    Raises:
        ValueError: If user not found
        PermissionError: If user doesn't have permission to delete
    """
    try:
        # Get the user to delete
        user = await get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Permission check: only superusers can delete users
        if current_user and not current_user.is_superuser:
            raise PermissionError("Not authorized to delete users")

        if soft_delete:
            # Soft delete: mark as inactive
            user.is_active = False
            user.updated_at = datetime.utcnow()
            await db.commit()
            logger.info(f"User soft deleted: {user.email}")
        else:
            # Hard delete: permanently remove from database
            await db.delete(user)
            await db.commit()
            logger.info(f"User permanently deleted: {user.email}")

        return True

    except (ValueError, PermissionError):
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return False


async def update_last_login(db: AsyncSession, user_id: str | UUID) -> bool:
    """
    Update the user's last login timestamp.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            return False

        user.last_login = datetime.utcnow()
        await db.commit()

        return True

    except Exception as e:
        logger.error(f"Error updating last login for user {user_id}: {str(e)}")
        return False


async def get_user_count(db: AsyncSession, is_active: Optional[bool] = None) -> int:
    """
    Get the total count of users.

    Args:
        db: Database session
        is_active: Optional filter by active status

    Returns:
        int: Total user count
    """
    try:
        stmt = select(func.count(User.id))

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)

        result = await db.execute(stmt)
        count = result.scalar_one()

        return count

    except Exception as e:
        logger.error(f"Error getting user count: {str(e)}")
        return 0
