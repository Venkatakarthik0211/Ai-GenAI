"""
SQLAlchemy database models.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from database import Base


class User(Base):
    """
    User model representing a user account in the system.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique)
        username: User's username (unique)
        full_name: User's full name
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active (soft delete flag)
        is_superuser: Whether the user has admin privileges
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
        last_login: Timestamp of user's last login
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # User credentials
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User status and permissions
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Optional fields
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    def to_dict(self) -> dict:
        """
        Convert user model to dictionary.

        Returns:
            dict: Dictionary representation of the user (without password)
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "bio": self.bio,
        }
