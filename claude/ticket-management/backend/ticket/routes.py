"""
Ticket Service API Routes

FastAPI routes for ticket management endpoints.
Reference: /backend/ticket/README.md - API Endpoints
"""

import os
import logging
import httpx
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from fastapi import (
    APIRouter, Depends, HTTPException, status, Request,
    UploadFile, File, Form, Query
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from models import (
    Ticket, Comment, Attachment, TicketHistory,
    TicketStatus, ChangeType, CommentType, StorageType
)
from schemas import (
    TicketCreate, TicketUpdate, TicketPatch, TicketResponse,
    TicketDetailResponse, TicketListResponse,
    AssignTicketRequest, UpdateStatusRequest,
    ResolveTicketRequest, CloseTicketRequest, ReopenTicketRequest,
    CommentCreate, CommentUpdate, CommentResponse, CommentListResponse,
    AttachmentResponse, AttachmentListResponse,
    TicketHistoryResponse, TicketHistoryListResponse,
    MessageResponse
)
from dependencies import (
    get_db, get_current_user, require_admin, require_engineer,
    get_ticket_or_404, get_comment_or_404, get_attachment_or_404,
    can_view_ticket, can_edit_ticket, can_assign_ticket,
    can_delete_ticket, can_edit_comment,
    get_client_ip, get_user_agent
)
from utils import (
    generate_ticket_number, validate_status_transition,
    create_ticket_history_entry, log_ticket_creation,
    log_status_change, log_assignment_change, log_priority_change,
    calculate_sla_due_dates, calculate_file_hash,
    get_file_extension, is_allowed_file_extension,
    notify_ticket_assigned, notify_ticket_status_changed,
    notify_comment_added, sanitize_search_query
)
from config import get_settings


settings = get_settings()
router = APIRouter(prefix="/tickets", tags=["Tickets"])
logger = logging.getLogger(__name__)


# Timezone-aware datetime helper
def utcnow():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


# ============================================================================
# Ticket CRUD Endpoints
# ============================================================================

@router.get("", response_model=TicketListResponse)
async def list_tickets(
    status: Optional[List[TicketStatus]] = Query(None),
    priority: Optional[List[str]] = Query(None),
    category: Optional[List[str]] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    requestor_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|priority|status|due_date)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List tickets with filtering and pagination

    - Supports filtering by status, priority, category, assignee, requestor
    - Full-text search on title and description
    - Sorting and pagination
    - End users see only their tickets, engineers see all
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Build query
    query = db.query(Ticket).filter(Ticket.deleted_at == None)

    # Role-based filtering
    if user_role == "END_USER":
        # End users only see their own tickets
        query = query.filter(Ticket.requestor_id == user_id)
    # Engineers and above see all tickets (no additional filter)

    # Apply filters
    if status:
        status_values = [s.value for s in status]
        query = query.filter(Ticket.status.in_(status_values))

    if priority:
        query = query.filter(Ticket.priority.in_(priority))

    if category:
        query = query.filter(Ticket.category.in_(category))

    if assigned_to:
        query = query.filter(Ticket.assigned_to == assigned_to)

    if requestor_id:
        # Only admins/managers can filter by other users
        if user_role in ["ADMIN", "MANAGER"] or str(requestor_id) == str(user_id):
            query = query.filter(Ticket.requestor_id == requestor_id)

    # Full-text search
    if search:
        search_term = sanitize_search_query(search)
        search_filter = or_(
            Ticket.title.ilike(f"%{search_term}%"),
            Ticket.description.ilike(f"%{search_term}%"),
            Ticket.ticket_number.ilike(f"%{search_term}%")
        )
        query = query.filter(search_filter)

    # Get total count before pagination
    total = query.count()

    # Sorting
    sort_column = getattr(Ticket, sort_by)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (page - 1) * page_size
    tickets = query.offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    return TicketListResponse(
        tickets=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new ticket

    - Generates unique ticket number
    - Sets requestor to current user
    - Calculates SLA due dates
    - Auto-assigns to DEVOPS_ENGINEER if creator is END_USER
    - Creates history entry
    """
    from config import get_settings
    settings = get_settings()

    # Log incoming data for debugging
    logger.info(f"Create ticket request data: {ticket_data.model_dump()}")

    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Generate ticket number
    ticket_number = generate_ticket_number(db)

    # Calculate SLA due dates
    sla_dates = calculate_sla_due_dates(ticket_data.priority.value)

    # Auto-assignment logic for END_USER tickets
    assigned_user_id = ticket_data.assigned_to
    initial_escalation_level = 0

    if not assigned_user_id and user_role == "END_USER":
        # Auto-assign to DEVOPS_ENGINEER (Level 1)
        try:
            auth_header = request.headers.get("Authorization", "")
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": auth_header}
                response = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/admin/users",
                    headers=headers,
                    params={"is_active": True, "role": "DEVOPS_ENGINEER"}
                )

                if response.status_code == 200:
                    devops_users = response.json()
                    if devops_users:
                        # Auto-assign to first DEVOPS_ENGINEER (can be enhanced with load balancing)
                        assigned_user_id = UUID(devops_users[0]["id"])
                        initial_escalation_level = 1  # Set to DEVOPS level
                        logger.info(f"Auto-assigned ticket to {devops_users[0]['username']} (DEVOPS_ENGINEER)")
                else:
                    logger.warning("Failed to fetch DEVOPS_ENGINEER for auto-assignment")
        except Exception as e:
            logger.warning(f"Auto-assignment failed: {str(e)}. Ticket will be unassigned.")

    # Create ticket
    ticket = Ticket(
        ticket_number=ticket_number,
        title=ticket_data.title,
        description=ticket_data.description,
        category=ticket_data.category.value,
        subcategory=ticket_data.subcategory,
        priority=ticket_data.priority.value,
        status=TicketStatus.NEW.value if not assigned_user_id else TicketStatus.OPEN.value,
        requestor_id=user_id,
        assigned_to=assigned_user_id,
        assigned_team=ticket_data.assigned_team,
        environment=ticket_data.environment.value if ticket_data.environment else None,
        affected_service=ticket_data.affected_service,
        impact_level=ticket_data.impact_level.value if ticket_data.impact_level else None,
        tags=ticket_data.tags,
        current_escalation_level=initial_escalation_level,
        escalation_count=0,
        response_due_at=sla_dates["response_due_at"],
        resolution_due_at=sla_dates["resolution_due_at"],
        created_at=utcnow(),
        updated_at=utcnow(),
        updated_by=user_id
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Log creation
    log_ticket_creation(db, ticket, user_id)

    # Notify assignee if assigned
    if ticket.assigned_to:
        notify_ticket_assigned(ticket, ticket.assigned_to)

    logger.info(f"Ticket {ticket.ticket_number} created by user {user_id}")

    return TicketResponse.model_validate(ticket)


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket: Ticket = Depends(can_view_ticket),
    db: Session = Depends(get_db)
):
    """
    Get ticket details by ID

    - Returns detailed ticket information
    - Includes comment and attachment counts
    - Checks if ticket is overdue
    """
    # Count comments and attachments
    comment_count = db.query(func.count(Comment.id)).filter(
        Comment.ticket_id == ticket.id,
        Comment.deleted_at == None
    ).scalar()

    attachment_count = db.query(func.count(Attachment.id)).filter(
        Attachment.ticket_id == ticket.id,
        Attachment.deleted_at == None
    ).scalar()

    # Convert to response
    response_data = TicketResponse.model_validate(ticket)
    detail_response = TicketDetailResponse(
        **response_data.model_dump(),
        comment_count=comment_count or 0,
        attachment_count=attachment_count or 0,
        is_overdue=ticket.is_overdue()
    )

    return detail_response


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_data: TicketUpdate,
    ticket: Ticket = Depends(can_edit_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update ticket (full update)

    - Updates all provided fields
    - Logs changes to history
    - Validates status transitions
    """
    user_id = current_user["id"]
    changes_made = []

    # Track status change
    old_status = ticket.status
    if ticket_data.status and ticket_data.status.value != old_status:
        is_valid, error_msg = validate_status_transition(old_status, ticket_data.status.value)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        ticket.status = ticket_data.status.value
        log_status_change(db, ticket, old_status, ticket.status, user_id)
        changes_made.append("status")

    # Track priority change
    old_priority = ticket.priority
    if ticket_data.priority and ticket_data.priority.value != old_priority:
        ticket.priority = ticket_data.priority.value
        log_priority_change(db, ticket, old_priority, ticket.priority, user_id)
        changes_made.append("priority")

    # Track assignment change
    old_assignee = ticket.assigned_to
    if ticket_data.assigned_to and ticket_data.assigned_to != old_assignee:
        ticket.assigned_to = ticket_data.assigned_to
        log_assignment_change(db, ticket, old_assignee, ticket.assigned_to, user_id)
        notify_ticket_assigned(ticket, ticket.assigned_to)
        changes_made.append("assigned_to")

    # Update basic fields
    ticket.title = ticket_data.title
    ticket.description = ticket_data.description
    ticket.category = ticket_data.category.value
    ticket.subcategory = ticket_data.subcategory
    ticket.assigned_team = ticket_data.assigned_team
    ticket.environment = ticket_data.environment.value if ticket_data.environment else None
    ticket.affected_service = ticket_data.affected_service
    ticket.impact_level = ticket_data.impact_level.value if ticket_data.impact_level else None
    ticket.tags = ticket_data.tags
    ticket.resolution_notes = ticket_data.resolution_notes
    ticket.due_date = ticket_data.due_date

    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    # Log general update if no specific changes tracked
    if not changes_made:
        create_ticket_history_entry(
            db=db,
            ticket_id=ticket.id,
            change_type=ChangeType.UPDATE,
            changed_by=user_id,
            change_description="Ticket updated"
        )

    logger.info(f"Ticket {ticket.ticket_number} updated by user {user_id}")

    return TicketResponse.model_validate(ticket)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def patch_ticket(
    ticket_data: TicketPatch,
    ticket: Ticket = Depends(can_edit_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Partially update ticket

    - Updates only provided fields
    - Logs changes to history
    - Validates status transitions
    """
    user_id = current_user["id"]
    update_data = ticket_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Handle status change with validation
    if "status" in update_data and update_data["status"]:
        new_status = update_data["status"].value
        old_status = ticket.status
        if new_status != old_status:
            is_valid, error_msg = validate_status_transition(old_status, new_status)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            ticket.status = new_status
            log_status_change(db, ticket, old_status, new_status, user_id)

    # Handle priority change
    if "priority" in update_data and update_data["priority"]:
        new_priority = update_data["priority"].value
        old_priority = ticket.priority
        if new_priority != old_priority:
            ticket.priority = new_priority
            log_priority_change(db, ticket, old_priority, new_priority, user_id)

    # Handle assignment change
    if "assigned_to" in update_data:
        new_assignee = update_data["assigned_to"]
        old_assignee = ticket.assigned_to
        if new_assignee != old_assignee:
            ticket.assigned_to = new_assignee
            log_assignment_change(db, ticket, old_assignee, new_assignee, user_id)
            if new_assignee:
                notify_ticket_assigned(ticket, new_assignee)

    # Update other fields
    for field, value in update_data.items():
        if field in ["status", "priority", "assigned_to"]:
            continue  # Already handled
        if hasattr(ticket, field):
            # Handle enum values
            if hasattr(value, "value"):
                setattr(ticket, field, value.value)
            else:
                setattr(ticket, field, value)

    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    logger.info(f"Ticket {ticket.ticket_number} patched by user {user_id}")

    return TicketResponse.model_validate(ticket)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket: Ticket = Depends(can_delete_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete ticket (admin only)

    - Marks ticket as deleted
    - Does not remove from database
    """
    user_id = current_user["id"]

    ticket.deleted_at = utcnow()
    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()

    logger.info(f"Ticket {ticket.ticket_number} deleted by admin {user_id}")

    return None


# ============================================================================
# Ticket Actions
# ============================================================================

@router.put("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    assignment: AssignTicketRequest,
    ticket: Ticket = Depends(can_assign_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign ticket to engineer

    - Updates assigned_to field
    - Changes status to OPEN if NEW
    - Logs assignment change
    - Notifies assignee
    """
    user_id = current_user["id"]
    old_assignee = ticket.assigned_to

    ticket.assigned_to = assignment.assignee_id

    # Change status to OPEN if NEW
    if ticket.status == TicketStatus.NEW.value:
        old_status = ticket.status
        ticket.status = TicketStatus.OPEN.value
        log_status_change(db, ticket, old_status, ticket.status, user_id)

    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    # Log assignment
    log_assignment_change(db, ticket, old_assignee, assignment.assignee_id, user_id, assignment.notes)

    # Notify assignee
    notify_ticket_assigned(ticket, assignment.assignee_id)

    logger.info(f"Ticket {ticket.ticket_number} assigned to {assignment.assignee_id}")

    return TicketResponse.model_validate(ticket)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    status_update: UpdateStatusRequest,
    ticket: Ticket = Depends(can_edit_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update ticket status

    - Validates status transition
    - Logs status change
    - Notifies requestor
    """
    user_id = current_user["id"]
    old_status = ticket.status
    new_status = status_update.status.value

    # Validate transition
    is_valid, error_msg = validate_status_transition(old_status, new_status)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    ticket.status = new_status
    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    # Log change
    log_status_change(db, ticket, old_status, new_status, user_id, status_update.notes)

    # Notify
    notify_ticket_status_changed(ticket, old_status, new_status)

    logger.info(f"Ticket {ticket.ticket_number} status changed to {new_status}")

    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_ticket(
    resolution: ResolveTicketRequest,
    ticket: Ticket = Depends(can_edit_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark ticket as resolved

    - Sets status to RESOLVED
    - Records resolution notes
    - Sets resolved_at timestamp
    - Records first response if not set
    """
    user_id = current_user["id"]
    old_status = ticket.status

    ticket.status = TicketStatus.RESOLVED.value
    ticket.resolution_notes = resolution.resolution_notes
    ticket.resolved_at = utcnow()

    # Set first response time if not already set
    if not ticket.first_response_at:
        ticket.first_response_at = utcnow()

    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    # Log resolution
    create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.RESOLVED,
        changed_by=user_id,
        change_description="Ticket resolved",
        change_metadata={"resolution_notes": resolution.resolution_notes}
    )

    log_status_change(db, ticket, old_status, ticket.status, user_id)

    notify_ticket_status_changed(ticket, old_status, ticket.status)

    logger.info(f"Ticket {ticket.ticket_number} resolved by user {user_id}")

    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/close", response_model=TicketResponse)
async def close_ticket(
    closure: CloseTicketRequest,
    ticket: Ticket = Depends(can_edit_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Close ticket

    - Sets status to CLOSED
    - Records closure code and notes
    - Sets closed_by user
    """
    user_id = current_user["id"]
    old_status = ticket.status

    ticket.status = TicketStatus.CLOSED.value
    ticket.closure_code = closure.closure_code.value
    ticket.resolution_notes = closure.closure_notes or ticket.resolution_notes
    ticket.closed_by = user_id
    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    # Log closure
    create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.CLOSED,
        changed_by=user_id,
        change_description=f"Ticket closed with code: {closure.closure_code.value}",
        change_metadata={"closure_code": closure.closure_code.value}
    )

    log_status_change(db, ticket, old_status, ticket.status, user_id)

    notify_ticket_status_changed(ticket, old_status, ticket.status)

    logger.info(f"Ticket {ticket.ticket_number} closed by user {user_id}")

    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/reopen", response_model=TicketResponse)
async def reopen_ticket(
    reopen_request: ReopenTicketRequest,
    ticket: Ticket = Depends(get_ticket_or_404),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reopen closed ticket

    - Changes status to REOPENED
    - Validates reopen window
    - Logs reopen reason
    """
    user_id = current_user["id"]

    # Check if ticket can be reopened
    if not ticket.can_reopen():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket cannot be reopened (not closed)"
        )

    # Check reopen window (optional, based on settings)
    if ticket.updated_at:
        days_since_closure = (utcnow() - ticket.updated_at).days
        if days_since_closure > settings.TICKET_REOPEN_WINDOW_DAYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ticket cannot be reopened after {settings.TICKET_REOPEN_WINDOW_DAYS} days"
            )

    old_status = ticket.status
    ticket.status = TicketStatus.REOPENED.value
    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    # Log reopen
    create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.REOPENED,
        changed_by=user_id,
        change_description=f"Ticket reopened: {reopen_request.reason}",
        change_metadata={"reason": reopen_request.reason}
    )

    log_status_change(db, ticket, old_status, ticket.status, user_id, reopen_request.reason)

    logger.info(f"Ticket {ticket.ticket_number} reopened by user {user_id}")

    return TicketResponse.model_validate(ticket)


# ============================================================================
# Ticket History
# ============================================================================

@router.get("/{ticket_id}/history", response_model=TicketHistoryListResponse)
async def get_ticket_history(
    ticket: Ticket = Depends(can_view_ticket),
    db: Session = Depends(get_db)
):
    """
    Get complete ticket history

    - Returns all changes made to ticket
    - Ordered by timestamp (newest first)
    """
    history_entries = db.query(TicketHistory).filter(
        TicketHistory.ticket_id == ticket.id
    ).order_by(TicketHistory.created_at.desc()).all()

    return TicketHistoryListResponse(
        history=[TicketHistoryResponse.model_validate(h) for h in history_entries],
        total=len(history_entries)
    )


# ============================================================================
# Comments
# ============================================================================

@router.get("/{ticket_id}/comments", response_model=CommentListResponse)
async def list_comments(
    ticket: Ticket = Depends(can_view_ticket),
    include_internal: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all comments for a ticket

    - End users see only public comments
    - Engineers see all comments including internal
    """
    user_role = current_user.get("role", "END_USER")

    query = db.query(Comment).filter(
        Comment.ticket_id == ticket.id,
        Comment.deleted_at == None
    )

    # Filter internal comments for end users
    if user_role == "END_USER":
        query = query.filter(Comment.is_internal == False)
    elif include_internal or user_role in ["DEVOPS_ENGINEER", "TEAM_LEAD", "MANAGER", "ADMIN"]:
        # Include all comments
        pass
    else:
        query = query.filter(Comment.is_internal == False)

    comments = query.order_by(Comment.created_at.asc()).all()

    return CommentListResponse(
        comments=[CommentResponse.model_validate(c) for c in comments],
        total=len(comments)
    )


@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    comment_data: CommentCreate,
    ticket: Ticket = Depends(can_view_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add comment to ticket

    - Creates new comment
    - Logs comment addition
    - Notifies relevant parties
    - Only engineers can create internal comments
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Only engineers can create internal comments
    if comment_data.is_internal and user_role == "END_USER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only engineers can create internal comments"
        )

    comment = Comment(
        ticket_id=ticket.id,
        author_id=user_id,
        content=comment_data.content,
        comment_type=comment_data.comment_type.value,
        is_internal=comment_data.is_internal,
        created_at=utcnow()
    )

    db.add(comment)

    # Update ticket's first response time if this is first comment from engineer
    if not ticket.first_response_at and user_role in ["DEVOPS_ENGINEER", "TEAM_LEAD", "MANAGER", "ADMIN"]:
        ticket.first_response_at = utcnow()

    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(comment)

    # Log comment addition
    create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.COMMENT_ADDED,
        changed_by=user_id,
        change_description="Comment added"
    )

    # Notify
    notify_comment_added(ticket, user_id)

    logger.info(f"Comment added to ticket {ticket.ticket_number} by user {user_id}")

    return CommentResponse.model_validate(comment)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_data: CommentUpdate,
    comment: Comment = Depends(get_comment_or_404),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update comment

    - Only comment author can edit
    - Marks comment as edited
    """
    user_id = current_user["id"]

    # Check permission
    await can_edit_comment(comment, current_user)

    comment.content = comment_data.content
    comment.edited_at = utcnow()
    comment.edited_by = user_id

    db.commit()
    db.refresh(comment)

    logger.info(f"Comment {comment.id} updated by user {user_id}")

    return CommentResponse.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment: Comment = Depends(get_comment_or_404),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete comment (soft delete)

    - Only comment author or admin can delete
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Check permission
    if str(comment.author_id) != str(user_id) and user_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this comment"
        )

    comment.deleted_at = utcnow()

    db.commit()

    logger.info(f"Comment {comment.id} deleted by user {user_id}")

    return None


# ============================================================================
# Attachments
# ============================================================================

@router.get("/{ticket_id}/attachments", response_model=AttachmentListResponse)
async def list_attachments(
    ticket: Ticket = Depends(can_view_ticket),
    db: Session = Depends(get_db)
):
    """
    List all attachments for a ticket
    """
    attachments = db.query(Attachment).filter(
        Attachment.ticket_id == ticket.id,
        Attachment.deleted_at == None
    ).order_by(Attachment.created_at.desc()).all()

    return AttachmentListResponse(
        attachments=[AttachmentResponse.model_validate(a) for a in attachments],
        total=len(attachments)
    )


@router.post("/{ticket_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: UUID,
    file: UploadFile = File(...),
    ticket: Ticket = Depends(can_view_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload attachment to ticket

    - Validates file type and size
    - Calculates file hash
    - Stores file locally or in cloud storage
    """
    user_id = current_user["id"]

    # Validate file extension
    if not is_allowed_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.UPLOAD_ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file size
    if file_size > settings.UPLOAD_MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.UPLOAD_MAX_FILE_SIZE / 1048576:.2f} MB"
        )

    # Calculate file hash
    content_hash = calculate_file_hash(file_content)

    # Generate storage path
    file_extension = get_file_extension(file.filename)
    storage_filename = f"{ticket.ticket_number}_{content_hash[:8]}.{file_extension}"
    storage_path = os.path.join(settings.UPLOAD_STORAGE_PATH, storage_filename)

    # Save file
    os.makedirs(settings.UPLOAD_STORAGE_PATH, exist_ok=True)
    with open(storage_path, "wb") as f:
        f.write(file_content)

    # Create attachment record
    attachment = Attachment(
        ticket_id=ticket.id,
        uploaded_by=user_id,
        file_name=file.filename,
        file_path=storage_path,
        file_size=file_size,
        file_type=file.content_type or "application/octet-stream",
        file_extension=file_extension,
        storage_type=StorageType.LOCAL.value,
        storage_location=storage_path,
        content_hash=content_hash,
        created_at=utcnow()
    )

    db.add(attachment)

    # Update ticket
    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(attachment)

    # Log attachment
    create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.ATTACHMENT_ADDED,
        changed_by=user_id,
        change_description=f"Attachment added: {file.filename}"
    )

    logger.info(f"Attachment uploaded to ticket {ticket.ticket_number}")

    return AttachmentResponse.model_validate(attachment)


@router.get("/attachments/{attachment_id}")
async def download_attachment(
    attachment: Attachment = Depends(get_attachment_or_404),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download attachment file

    - Validates access to ticket
    - Returns file for download
    """
    # Verify user has access to the ticket
    ticket = db.query(Ticket).filter(Ticket.id == attachment.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Check if file exists
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage"
        )

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.file_name,
        media_type=attachment.file_type
    )


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment: Attachment = Depends(get_attachment_or_404),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete attachment

    - Soft delete in database
    - Optionally remove file from storage
    """
    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Check permission
    if str(attachment.uploaded_by) != str(user_id) and user_role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this attachment"
        )

    attachment.deleted_at = utcnow()

    db.commit()

    logger.info(f"Attachment {attachment.id} deleted by user {user_id}")

    return None


# ============================================================================
# User Management (for ticket assignment)
# ============================================================================

@router.get("/users/assignable", response_model=List[dict])
async def get_assignable_users(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of users who can be assigned tickets

    Returns users with roles: DEVOPS_ENGINEER, SENIOR_ENGINEER, TEAM_LEAD, MANAGER, ADMIN
    Only active users are returned

    Requires authentication
    """
    from config import get_settings
    settings = get_settings()

    # Define assignable roles (exclude END_USER)
    assignable_roles = [
        "DEVOPS_ENGINEER",
        "SENIOR_ENGINEER",
        "TEAM_LEAD",
        "MANAGER",
        "ADMIN"
    ]

    try:
        # Extract bearer token from request headers
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )

        # Call auth service to get users
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Forward the authorization header
            headers = {"Authorization": auth_header}

            # Fetch all active users
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/admin/users",
                headers=headers,
                params={"is_active": True}
            )

            if response.status_code == 200:
                all_users = response.json()

                # Filter to only include assignable roles
                assignable_users = [
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user["email"],
                        "full_name": user.get("full_name", f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()),
                        "first_name": user.get("first_name", ""),
                        "last_name": user.get("last_name", ""),
                        "role": user["role"],
                        "department": user.get("department")
                    }
                    for user in all_users
                    if user.get("role") in assignable_roles
                ]

                # Sort by role hierarchy (ADMIN first, then MANAGER, etc.)
                role_order = {
                    "ADMIN": 0,
                    "MANAGER": 1,
                    "TEAM_LEAD": 2,
                    "SENIOR_ENGINEER": 3,
                    "DEVOPS_ENGINEER": 4
                }
                assignable_users.sort(key=lambda u: (role_order.get(u["role"], 99), u.get("full_name", "")))

                logger.info(f"Fetched {len(assignable_users)} assignable users")
                return assignable_users
            else:
                logger.error(f"Failed to fetch users from auth service: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to fetch users from auth service"
                )

    except httpx.TimeoutException:
        logger.error("Timeout calling auth service")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service timeout"
        )
    except Exception as e:
        logger.error(f"Error fetching assignable users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assignable users"
        )


# ============================================================================
# Escalation Workflow
# ============================================================================

@router.post("/tickets/{ticket_id}/escalate", response_model=TicketResponse)
async def escalate_ticket(
    request: Request,
    ticket: Ticket = Depends(can_view_ticket),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Escalate ticket to next level in hierarchy

    Role Hierarchy (Escalation Levels):
    - Level 0: END_USER (Ticket Creator)
    - Level 1: DEVOPS_ENGINEER
    - Level 2: SENIOR_ENGINEER
    - Level 3: TEAM_LEAD
    - Level 4: MANAGER
    - Level 5: ADMIN (Final level, cannot escalate further)

    Escalation Rules:
    - Only assigned user or higher level can escalate
    - Ticket must be OPEN, IN_PROGRESS, or ESCALATED status
    - Cannot escalate beyond ADMIN level
    - Auto-assigns to a user at next level (round-robin)
    """
    from config import get_settings
    settings = get_settings()

    user_id = current_user["id"]
    user_role = current_user.get("role", "END_USER")

    # Define role-to-level mapping
    role_levels = {
        "END_USER": 0,
        "DEVOPS_ENGINEER": 1,
        "SENIOR_ENGINEER": 2,
        "TEAM_LEAD": 3,
        "MANAGER": 4,
        "ADMIN": 5
    }

    level_to_role = {
        0: "END_USER",
        1: "DEVOPS_ENGINEER",
        2: "SENIOR_ENGINEER",
        3: "TEAM_LEAD",
        4: "MANAGER",
        5: "ADMIN"
    }

    # Validation: Check if ticket can be escalated
    if ticket.status not in [TicketStatus.OPEN.value, TicketStatus.IN_PROGRESS.value, TicketStatus.ESCALATED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot escalate ticket in {ticket.status} status. Ticket must be OPEN, IN_PROGRESS, or ESCALATED."
        )

    # Check current escalation level
    current_level = ticket.current_escalation_level
    if current_level >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is at maximum escalation level (ADMIN). Cannot escalate further."
        )

    # Permission check: Only assigned user or higher level can escalate
    user_level = role_levels.get(user_role, 0)
    if ticket.assigned_to:
        if str(ticket.assigned_to) != str(user_id) and user_level <= current_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned user or higher authority can escalate this ticket"
            )

    # Determine next escalation level
    next_level = current_level + 1
    next_role = level_to_role[next_level]

    logger.info(f"Escalating ticket {ticket.ticket_number} from level {current_level} ({level_to_role[current_level]}) to level {next_level} ({next_role})")

    # Fetch users at next level from auth service
    try:
        auth_header = request.headers.get("Authorization", "")
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": auth_header}
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/admin/users",
                headers=headers,
                params={"is_active": True, "role": next_role}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to fetch {next_role} users for escalation"
                )

            next_level_users = response.json()

            if not next_level_users:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No active {next_role} users available for escalation"
                )

            # Select user for assignment (simple: first user, can be enhanced with load balancing)
            selected_user = next_level_users[0]
            selected_user_id = UUID(selected_user["id"])

            logger.info(f"Assigning ticket to {selected_user['username']} ({next_role})")

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service timeout during escalation"
        )

    # Update ticket
    ticket.current_escalation_level = next_level
    ticket.escalation_count += 1
    ticket.last_escalated_at = utcnow()
    ticket.last_escalated_by = user_id
    ticket.assigned_to = selected_user_id
    ticket.status = TicketStatus.ESCALATED.value
    ticket.updated_at = utcnow()
    ticket.updated_by = user_id

    db.commit()
    db.refresh(ticket)

    # Log escalation in history
    create_ticket_history_entry(
        db=db,
        ticket_id=ticket.id,
        change_type=ChangeType.ESCALATED,
        changed_by=user_id,
        change_description=f"Escalated from {level_to_role[current_level]} (Level {current_level}) to {next_role} (Level {next_level})",
        change_metadata={
            "from_level": current_level,
            "to_level": next_level,
            "from_role": level_to_role[current_level],
            "to_role": next_role,
            "assigned_to": str(selected_user_id),
            "assigned_to_username": selected_user["username"]
        }
    )

    logger.info(f"Ticket {ticket.ticket_number} escalated successfully to level {next_level}")

    return TicketResponse.model_validate(ticket)
