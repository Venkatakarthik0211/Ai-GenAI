"""
Ticket Service Utility Functions

Helper functions for ticket management, SLA calculations, and history tracking.
Reference: /backend/ticket/README.md - Utilities
"""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from models import (
    Ticket, TicketHistory, ChangeType, TicketStatus,
    TicketPriority
)
from config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


# ============================================================================
# Timezone Helper
# ============================================================================

def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


# ============================================================================
# Ticket Number Generation
# ============================================================================

def generate_ticket_number(db: Session) -> str:
    """
    Generate unique ticket number in format TKT-YYYY-NNNNN

    Args:
        db: Database session

    Returns:
        Unique ticket number string

    Example:
        TKT-2025-00001
        TKT-2025-00002
    """
    current_year = utcnow().year
    prefix = f"{settings.TICKET_NUMBER_PREFIX}-{current_year}-"

    # Get the latest ticket number for current year
    latest_ticket = db.query(Ticket).filter(
        Ticket.ticket_number.like(f"{prefix}%")
    ).order_by(Ticket.ticket_number.desc()).first()

    if latest_ticket:
        # Extract sequence number and increment
        last_number = int(latest_ticket.ticket_number.split('-')[-1])
        new_number = last_number + 1
    else:
        # First ticket of the year
        new_number = 1

    # Format with leading zeros
    ticket_number = f"{prefix}{new_number:05d}"

    # Verify uniqueness
    existing = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
    if existing:
        # Recursively generate new number if collision occurs
        logger.warning(f"Ticket number collision detected: {ticket_number}")
        return generate_ticket_number(db)

    return ticket_number


# ============================================================================
# Status Transition Validation
# ============================================================================

# Valid status transitions
# Note: CLOSED status should primarily be reached through the /close endpoint
# The generic /status endpoint enforces proper workflow (must be RESOLVED first)
STATUS_TRANSITIONS = {
    TicketStatus.NEW: [
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS
    ],
    TicketStatus.OPEN: [
        TicketStatus.IN_PROGRESS,
        TicketStatus.PENDING_INFO,
        TicketStatus.RESOLVED
    ],
    TicketStatus.IN_PROGRESS: [
        TicketStatus.PENDING_INFO,
        TicketStatus.RESOLVED,
        TicketStatus.ESCALATED,
        TicketStatus.OPEN
    ],
    TicketStatus.PENDING_INFO: [
        TicketStatus.IN_PROGRESS,
        TicketStatus.OPEN
    ],
    TicketStatus.RESOLVED: [
        TicketStatus.CLOSED,
        TicketStatus.REOPENED
    ],
    TicketStatus.CLOSED: [
        TicketStatus.REOPENED
    ],
    TicketStatus.REOPENED: [
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS,
        TicketStatus.RESOLVED
    ],
    TicketStatus.ESCALATED: [
        TicketStatus.IN_PROGRESS,
        TicketStatus.RESOLVED
    ]
}


def validate_status_transition(
    old_status: str,
    new_status: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate if status transition is allowed

    Args:
        old_status: Current ticket status
        new_status: Proposed new status

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_status_transition("NEW", "IN_PROGRESS")
        (True, None)
        >>> validate_status_transition("CLOSED", "IN_PROGRESS")
        (False, "Invalid status transition from CLOSED to IN_PROGRESS")
    """
    # Same status is always valid
    if old_status == new_status:
        return True, None

    try:
        old_status_enum = TicketStatus(old_status)
        new_status_enum = TicketStatus(new_status)

        # Check if transition is allowed
        allowed_transitions = STATUS_TRANSITIONS.get(old_status_enum, [])

        if new_status_enum in allowed_transitions:
            return True, None

        return False, f"Invalid status transition from {old_status} to {new_status}"

    except ValueError as e:
        return False, f"Invalid status value: {str(e)}"


# ============================================================================
# Ticket History Management
# ============================================================================

def create_ticket_history_entry(
    db: Session,
    ticket_id: UUID,
    change_type: ChangeType,
    changed_by: Optional[UUID] = None,
    field_name: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    change_description: Optional[str] = None,
    change_metadata: Optional[Dict] = None
) -> TicketHistory:
    """
    Create a ticket history entry

    Args:
        db: Database session
        ticket_id: Ticket UUID
        change_type: Type of change
        changed_by: User ID who made the change
        field_name: Name of field changed
        old_value: Previous value
        new_value: New value
        change_description: Human-readable description
        change_metadata: Additional metadata as JSON

    Returns:
        Created TicketHistory object
    """
    history = TicketHistory(
        ticket_id=ticket_id,
        changed_by=changed_by,
        change_type=change_type.value,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        change_description=change_description,
        change_metadata=change_metadata,
        created_at=utcnow()
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    logger.info(f"Created history entry for ticket {ticket_id}: {change_type.value}")

    return history


def log_ticket_creation(
    db: Session,
    ticket: Ticket,
    created_by: UUID
) -> TicketHistory:
    """
    Log ticket creation to history

    Args:
        db: Database session
        ticket: Ticket object
        created_by: User ID who created ticket

    Returns:
        TicketHistory entry
    """
    return create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.CREATED,
        changed_by=created_by,
        change_description=f"Ticket {ticket.ticket_number} created",
        change_metadata={
            "title": ticket.title,
            "priority": ticket.priority,
            "category": ticket.category,
            "status": ticket.status
        }
    )


def log_status_change(
    db: Session,
    ticket: Ticket,
    old_status: str,
    new_status: str,
    changed_by: UUID,
    notes: Optional[str] = None
) -> TicketHistory:
    """
    Log status change to history

    Args:
        db: Database session
        ticket: Ticket object
        old_status: Previous status
        new_status: New status
        changed_by: User ID who changed status
        notes: Optional notes about the change

    Returns:
        TicketHistory entry
    """
    return create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.STATUS_CHANGE,
        changed_by=changed_by,
        field_name="status",
        old_value=old_status,
        new_value=new_status,
        change_description=f"Status changed from {old_status} to {new_status}",
        change_metadata={"notes": notes} if notes else None
    )


def log_assignment_change(
    db: Session,
    ticket: Ticket,
    old_assignee: Optional[UUID],
    new_assignee: Optional[UUID],
    changed_by: UUID,
    notes: Optional[str] = None
) -> TicketHistory:
    """
    Log assignment change to history

    Args:
        db: Database session
        ticket: Ticket object
        old_assignee: Previous assignee ID
        new_assignee: New assignee ID
        changed_by: User ID who changed assignment
        notes: Optional notes about the change

    Returns:
        TicketHistory entry
    """
    return create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.ASSIGNMENT_CHANGE,
        changed_by=changed_by,
        field_name="assigned_to",
        old_value=str(old_assignee) if old_assignee else None,
        new_value=str(new_assignee) if new_assignee else None,
        change_description="Ticket reassigned",
        change_metadata={"notes": notes} if notes else None
    )


def log_priority_change(
    db: Session,
    ticket: Ticket,
    old_priority: str,
    new_priority: str,
    changed_by: UUID
) -> TicketHistory:
    """
    Log priority change to history

    Args:
        db: Database session
        ticket: Ticket object
        old_priority: Previous priority
        new_priority: New priority
        changed_by: User ID who changed priority

    Returns:
        TicketHistory entry
    """
    return create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.PRIORITY_CHANGE,
        changed_by=changed_by,
        field_name="priority",
        old_value=old_priority,
        new_value=new_priority,
        change_description=f"Priority changed from {old_priority} to {new_priority}"
    )


# ============================================================================
# SLA Calculation
# ============================================================================

def calculate_sla_due_dates(
    priority: str,
    created_at: Optional[datetime] = None
) -> Dict[str, datetime]:
    """
    Calculate SLA due dates based on priority

    Args:
        priority: Ticket priority (P1, P2, P3, P4)
        created_at: Ticket creation time (defaults to now)

    Returns:
        Dictionary with response_due_at and resolution_due_at

    Example:
        >>> calculate_sla_due_dates("P1")
        {
            'response_due_at': datetime(2025, 11, 21, 15, 0, 0),
            'resolution_due_at': datetime(2025, 11, 21, 18, 0, 0)
        }
    """
    if created_at is None:
        created_at = utcnow()

    # Ensure timezone-aware datetime
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    # Get SLA hours from settings
    response_hours = settings.get_sla_response_hours(priority)
    resolution_hours = settings.get_sla_resolution_hours(priority)

    # Calculate due dates
    response_due_at = created_at + timedelta(hours=response_hours)
    resolution_due_at = created_at + timedelta(hours=resolution_hours)

    return {
        "response_due_at": response_due_at,
        "resolution_due_at": resolution_due_at
    }


def is_sla_breached(
    due_date: Optional[datetime],
    current_status: str
) -> bool:
    """
    Check if SLA is breached

    Args:
        due_date: SLA due date
        current_status: Current ticket status

    Returns:
        True if SLA is breached
    """
    if not due_date:
        return False

    # If ticket is resolved or closed, SLA is not breached
    if current_status in [TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]:
        return False

    # Ensure timezone-aware comparison
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)

    return utcnow() > due_date


def calculate_resolution_time(
    created_at: datetime,
    resolved_at: Optional[datetime]
) -> Optional[int]:
    """
    Calculate ticket resolution time in minutes

    Args:
        created_at: Ticket creation time
        resolved_at: Ticket resolution time

    Returns:
        Resolution time in minutes, or None if not resolved
    """
    if not resolved_at:
        return None

    # Ensure timezone-aware datetimes
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if resolved_at.tzinfo is None:
        resolved_at = resolved_at.replace(tzinfo=timezone.utc)

    delta = resolved_at - created_at
    return int(delta.total_seconds() / 60)


# ============================================================================
# File Utilities
# ============================================================================

def calculate_file_hash(file_content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content

    Args:
        file_content: File content as bytes

    Returns:
        SHA-256 hash as hex string
    """
    return hashlib.sha256(file_content).hexdigest()


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename

    Args:
        filename: File name

    Returns:
        File extension (lowercase, without dot)

    Example:
        >>> get_file_extension("document.pdf")
        "pdf"
    """
    if '.' not in filename:
        return ""
    return filename.rsplit('.', 1)[1].lower()


def is_allowed_file_extension(filename: str) -> bool:
    """
    Check if file extension is allowed

    Args:
        filename: File name

    Returns:
        True if extension is allowed
    """
    extension = get_file_extension(filename)
    return extension in settings.UPLOAD_ALLOWED_EXTENSIONS


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size string

    Example:
        >>> format_file_size(1024)
        "1.00 KB"
        >>> format_file_size(1048576)
        "1.00 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


# ============================================================================
# Notification Helpers
# ============================================================================

def send_ticket_notification(
    ticket: Ticket,
    notification_type: str,
    recipient_id: UUID,
    additional_data: Optional[Dict] = None
):
    """
    Send ticket notification (placeholder for notification service integration)

    Args:
        ticket: Ticket object
        notification_type: Type of notification
        recipient_id: User ID to notify
        additional_data: Additional notification data

    TODO: Integrate with notification service
    """
    logger.info(
        f"Notification: {notification_type} for ticket {ticket.ticket_number} "
        f"to user {recipient_id}"
    )
    # TODO: Implement actual notification sending
    pass


def notify_ticket_assigned(ticket: Ticket, assignee_id: UUID):
    """Notify assignee about new ticket assignment"""
    if settings.NOTIFICATIONS_ENABLED:
        send_ticket_notification(
            ticket=ticket,
            notification_type="ticket_assigned",
            recipient_id=assignee_id
        )


def notify_ticket_status_changed(ticket: Ticket, old_status: str, new_status: str):
    """Notify requestor about status change"""
    if settings.NOTIFICATIONS_ENABLED:
        send_ticket_notification(
            ticket=ticket,
            notification_type="status_changed",
            recipient_id=ticket.requestor_id,
            additional_data={
                "old_status": old_status,
                "new_status": new_status
            }
        )


def notify_comment_added(ticket: Ticket, comment_author_id: UUID):
    """Notify relevant parties about new comment"""
    if settings.NOTIFICATIONS_ENABLED:
        # Notify requestor if comment is from someone else
        if str(ticket.requestor_id) != str(comment_author_id):
            send_ticket_notification(
                ticket=ticket,
                notification_type="comment_added",
                recipient_id=ticket.requestor_id
            )


# ============================================================================
# Data Sanitization
# ============================================================================

def sanitize_search_query(query: str) -> str:
    """
    Sanitize search query to prevent SQL injection

    Args:
        query: Search query string

    Returns:
        Sanitized query string
    """
    # Remove special characters that could be used for SQL injection
    dangerous_chars = ['--', ';', '/*', '*/', 'xp_', 'sp_']
    sanitized = query

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    return sanitized.strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
