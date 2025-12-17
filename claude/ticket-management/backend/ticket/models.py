"""
Ticket Management Models

SQLAlchemy ORM models for tickets, comments, attachments, and ticket history.
Reference: /backend/db_migrations/V3__ticket_tables.sql
"""

import enum
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, BigInteger, TIMESTAMP,
    ForeignKey, CheckConstraint, Index, ARRAY, event
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, TSVECTOR
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ============================================================================
# Enums
# ============================================================================

class TicketStatus(str, enum.Enum):
    """Ticket workflow status"""
    NEW = "NEW"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_INFO = "PENDING_INFO"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"
    ESCALATED = "ESCALATED"


class TicketPriority(str, enum.Enum):
    """Ticket priority levels"""
    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low


class TicketCategory(str, enum.Enum):
    """Ticket categories"""
    INCIDENT = "INCIDENT"
    SERVICE_REQUEST = "SERVICE_REQUEST"
    CHANGE_REQUEST = "CHANGE_REQUEST"
    PROBLEM = "PROBLEM"
    MAINTENANCE = "MAINTENANCE"


class Environment(str, enum.Enum):
    """Deployment environment"""
    DEV = "DEV"
    QA = "QA"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    DR = "DR"
    UNKNOWN = "UNKNOWN"


class ImpactLevel(str, enum.Enum):
    """Impact level"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ClosureCode(str, enum.Enum):
    """Ticket closure codes"""
    RESOLVED = "RESOLVED"
    WORKAROUND = "WORKAROUND"
    DUPLICATE = "DUPLICATE"
    CANNOT_REPRODUCE = "CANNOT_REPRODUCE"
    NOT_AN_ISSUE = "NOT_AN_ISSUE"
    CANCELLED = "CANCELLED"
    DEFERRED = "DEFERRED"


class CommentType(str, enum.Enum):
    """Comment types"""
    COMMENT = "COMMENT"
    NOTE = "NOTE"
    SOLUTION = "SOLUTION"
    WORKAROUND = "WORKAROUND"
    STATUS_CHANGE = "STATUS_CHANGE"
    ASSIGNMENT_CHANGE = "ASSIGNMENT_CHANGE"
    ESCALATION = "ESCALATION"


class StorageType(str, enum.Enum):
    """File storage types"""
    LOCAL = "LOCAL"
    S3 = "S3"
    AZURE_BLOB = "AZURE_BLOB"
    GCS = "GCS"


class ScanStatus(str, enum.Enum):
    """File scan status"""
    PENDING = "PENDING"
    CLEAN = "CLEAN"
    INFECTED = "INFECTED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class ChangeType(str, enum.Enum):
    """Ticket history change types"""
    CREATED = "CREATED"
    STATUS_CHANGE = "STATUS_CHANGE"
    PRIORITY_CHANGE = "PRIORITY_CHANGE"
    ASSIGNMENT_CHANGE = "ASSIGNMENT_CHANGE"
    UPDATE = "UPDATE"
    COMMENT_ADDED = "COMMENT_ADDED"
    ATTACHMENT_ADDED = "ATTACHMENT_ADDED"
    ESCALATED = "ESCALATED"
    REOPENED = "REOPENED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    SLA_BREACH = "SLA_BREACH"
    DUE_DATE_CHANGE = "DUE_DATE_CHANGE"


# ============================================================================
# Utility Functions
# ============================================================================

def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


# ============================================================================
# Models
# ============================================================================

class Ticket(Base):
    """
    Core ticket entity with complete workflow state machine

    Reference: /backend/db_migrations/V3__ticket_tables.sql
    """
    __tablename__ = "tickets"

    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Unique Identifier
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)

    # Basic Information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50))

    # Status & Priority
    status = Column(String(30), nullable=False, default=TicketStatus.NEW.value)
    priority = Column(String(10), nullable=False, default=TicketPriority.P3.value)

    # Assignment
    requestor_id = Column(PGUUID(as_uuid=True), nullable=False)  # Foreign key to users
    assigned_to = Column(PGUUID(as_uuid=True))  # Foreign key to users
    assigned_team = Column(String(100))

    # Escalation Tracking
    current_escalation_level = Column(Integer, default=0, nullable=False)  # 0=END_USER, 1=DEVOPS, 2=SENIOR, 3=LEAD, 4=MANAGER, 5=ADMIN
    escalation_count = Column(Integer, default=0, nullable=False)  # Number of times escalated
    last_escalated_at = Column(TIMESTAMP(timezone=True))  # When last escalated
    last_escalated_by = Column(PGUUID(as_uuid=True))  # Who escalated last

    # SLA & Tracking
    sla_policy_id = Column(PGUUID(as_uuid=True))
    due_date = Column(TIMESTAMP(timezone=True))
    response_due_at = Column(TIMESTAMP(timezone=True))
    resolution_due_at = Column(TIMESTAMP(timezone=True))
    first_response_at = Column(TIMESTAMP(timezone=True))
    resolved_at = Column(TIMESTAMP(timezone=True))

    # Closure Information
    resolution_notes = Column(Text)
    closed_by = Column(PGUUID(as_uuid=True))  # Foreign key to users
    closure_code = Column(String(50))

    # Metadata
    tags = Column(ARRAY(Text))
    environment = Column(String(50))
    affected_service = Column(String(100))
    impact_level = Column(String(20))

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    updated_by = Column(PGUUID(as_uuid=True))  # Foreign key to users
    deleted_at = Column(TIMESTAMP(timezone=True))

    # Full-text Search
    search_vector = Column(TSVECTOR)

    # Relationships (will be populated when integrated with auth service)
    # requestor = relationship("User", foreign_keys=[requestor_id])
    # assignee = relationship("User", foreign_keys=[assigned_to])
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            status.in_([s.value for s in TicketStatus]),
            name='chk_tickets_status'
        ),
        CheckConstraint(
            priority.in_([p.value for p in TicketPriority]),
            name='chk_tickets_priority'
        ),
        CheckConstraint(
            category.in_([c.value for c in TicketCategory]),
            name='chk_tickets_category'
        ),
        Index('idx_tickets_status', 'status'),
        Index('idx_tickets_priority', 'priority'),
        Index('idx_tickets_category', 'category'),
        Index('idx_tickets_requestor_id', 'requestor_id'),
        Index('idx_tickets_assigned_to', 'assigned_to'),
        Index('idx_tickets_created_at', 'created_at'),
        Index('idx_tickets_updated_at', 'updated_at'),
    )

    def __repr__(self):
        return f"<Ticket {self.ticket_number}: {self.title}>"

    def is_closed(self) -> bool:
        """Check if ticket is closed"""
        return self.status in [TicketStatus.CLOSED.value]

    def is_resolved(self) -> bool:
        """Check if ticket is resolved"""
        return self.status in [TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]

    def can_reopen(self) -> bool:
        """Check if ticket can be reopened"""
        return self.status == TicketStatus.CLOSED.value

    def can_assign(self) -> bool:
        """Check if ticket can be assigned"""
        return self.status not in [TicketStatus.CLOSED.value]

    def is_overdue(self) -> bool:
        """Check if ticket is overdue"""
        if not self.due_date:
            return False
        return utcnow() > self.due_date and not self.is_resolved()


class Comment(Base):
    """
    Ticket comments with rich text support and internal notes

    Reference: /backend/db_migrations/V3__ticket_tables.sql
    """
    __tablename__ = "comments"

    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    ticket_id = Column(PGUUID(as_uuid=True), ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    author_id = Column(PGUUID(as_uuid=True), nullable=False)  # Foreign key to users

    # Comment Content
    content = Column(Text, nullable=False)
    comment_type = Column(String(30), nullable=False, default=CommentType.COMMENT.value)

    # Visibility & Privacy
    is_internal = Column(Boolean, nullable=False, default=False)
    is_system_generated = Column(Boolean, nullable=False, default=False)

    # Attachments
    has_attachments = Column(Boolean, nullable=False, default=False)

    # Metadata
    edited_at = Column(TIMESTAMP(timezone=True))
    edited_by = Column(PGUUID(as_uuid=True))  # Foreign key to users

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=utcnow)
    deleted_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    attachments = relationship("Attachment", back_populates="comment", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            comment_type.in_([c.value for c in CommentType]),
            name='chk_comments_type'
        ),
        Index('idx_comments_ticket_id', 'ticket_id', 'created_at'),
        Index('idx_comments_author_id', 'author_id'),
    )

    def __repr__(self):
        return f"<Comment {self.id} on Ticket {self.ticket_id}>"

    def is_editable(self, user_id: UUID) -> bool:
        """Check if comment can be edited by user"""
        if self.deleted_at:
            return False
        return str(self.author_id) == str(user_id)


class Attachment(Base):
    """
    File attachments for tickets and comments

    Reference: /backend/db_migrations/V3__ticket_tables.sql
    """
    __tablename__ = "attachments"

    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys (one must be set)
    ticket_id = Column(PGUUID(as_uuid=True), ForeignKey('tickets.id', ondelete='CASCADE'))
    comment_id = Column(PGUUID(as_uuid=True), ForeignKey('comments.id', ondelete='CASCADE'))

    # Uploader
    uploaded_by = Column(PGUUID(as_uuid=True), nullable=False)  # Foreign key to users

    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    file_extension = Column(String(20))

    # Storage Information
    storage_type = Column(String(30), nullable=False, default=StorageType.LOCAL.value)
    storage_location = Column(String(500), nullable=False)
    storage_key = Column(String(255))

    # Security
    is_scanned = Column(Boolean, nullable=False, default=False)
    scan_status = Column(String(30))
    scan_result = Column(Text)

    # Metadata
    content_hash = Column(String(64))  # SHA-256 hash
    thumbnail_path = Column(String(500))

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=utcnow)
    deleted_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    comment = relationship("Comment", back_populates="attachments")

    __table_args__ = (
        CheckConstraint(
            '(ticket_id IS NOT NULL AND comment_id IS NULL) OR (ticket_id IS NULL AND comment_id IS NOT NULL)',
            name='chk_attachments_reference'
        ),
        CheckConstraint(
            'file_size > 0 AND file_size <= 52428800',  # Max 50MB
            name='chk_attachments_file_size'
        ),
        CheckConstraint(
            storage_type.in_([s.value for s in StorageType]),
            name='chk_attachments_storage_type'
        ),
        Index('idx_attachments_ticket_id', 'ticket_id'),
        Index('idx_attachments_comment_id', 'comment_id'),
        Index('idx_attachments_uploaded_by', 'uploaded_by'),
    )

    def __repr__(self):
        return f"<Attachment {self.file_name}>"

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)


class TicketHistory(Base):
    """
    Complete audit trail of all changes made to tickets

    Reference: /backend/db_migrations/V3__ticket_tables.sql
    """
    __tablename__ = "ticket_history"

    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    ticket_id = Column(PGUUID(as_uuid=True), ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    changed_by = Column(PGUUID(as_uuid=True))  # Foreign key to users

    # Change Information
    change_type = Column(String(50), nullable=False)
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)

    # Additional Context
    change_description = Column(Text)
    change_metadata = Column(JSONB)

    # Timestamp
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="history")

    __table_args__ = (
        CheckConstraint(
            change_type.in_([c.value for c in ChangeType]),
            name='chk_ticket_history_change_type'
        ),
        Index('idx_ticket_history_ticket_id', 'ticket_id', 'created_at'),
        Index('idx_ticket_history_changed_by', 'changed_by'),
        Index('idx_ticket_history_change_type', 'change_type'),
    )

    def __repr__(self):
        return f"<TicketHistory {self.change_type} on {self.ticket_id}>"


# ============================================================================
# Event Listeners for Automatic History Tracking
# ============================================================================

@event.listens_for(Ticket, 'after_update')
def log_ticket_changes(mapper, connection, target):
    """
    Automatically log ticket changes to history table
    This will be triggered by SQLAlchemy after any ticket update
    """
    # This is a placeholder - actual implementation would compare
    # old and new values and insert history records
    pass
