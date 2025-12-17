"""
Ticket Management Pydantic Schemas

This module defines Pydantic models for request/response validation.
Reference: /backend/ticket/README.md
"""

import re
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

from models import (
    TicketStatus, TicketPriority, TicketCategory, Environment,
    ImpactLevel, ClosureCode, CommentType, ChangeType
)


# ============================================================================
# Ticket Schemas
# ============================================================================

class TicketBase(BaseModel):
    """Base ticket schema with common fields"""
    title: str = Field(..., min_length=10, max_length=255, description="Ticket title")
    description: str = Field(..., min_length=20, description="Detailed ticket description")
    category: TicketCategory = Field(..., description="Ticket category")
    subcategory: Optional[str] = Field(None, max_length=50, description="Ticket subcategory")
    priority: TicketPriority = Field(default=TicketPriority.P3, description="Ticket priority")
    environment: Optional[Environment] = Field(None, description="Affected environment")
    affected_service: Optional[str] = Field(None, max_length=100, description="Affected service name")
    impact_level: Optional[ImpactLevel] = Field(None, description="Impact level")
    tags: Optional[List[str]] = Field(default=None, description="Ticket tags")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title format and length"""
        if len(v.strip()) < 10:
            raise ValueError('Title must be at least 10 characters long')
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description length"""
        if len(v.strip()) < 20:
            raise ValueError('Description must be at least 20 characters long')
        if not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate tags format"""
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        # Clean and validate each tag
        cleaned_tags = []
        for tag in v:
            tag = tag.strip().lower()
            if not tag:
                continue
            if len(tag) > 50:
                raise ValueError('Tag length cannot exceed 50 characters')
            if not re.match(r'^[a-z0-9-_]+$', tag):
                raise ValueError('Tags can only contain lowercase letters, numbers, hyphens, and underscores')
            cleaned_tags.append(tag)
        return cleaned_tags if cleaned_tags else None


class TicketCreate(TicketBase):
    """Schema for creating a new ticket"""
    assigned_to: Optional[UUID] = Field(None, description="User ID to assign ticket to")
    assigned_team: Optional[str] = Field(None, max_length=100, description="Team to assign ticket to")


class TicketUpdate(TicketBase):
    """Schema for full ticket update"""
    status: Optional[TicketStatus] = Field(None, description="Ticket status")
    assigned_to: Optional[UUID] = Field(None, description="Assigned user ID")
    assigned_team: Optional[str] = Field(None, max_length=100, description="Assigned team")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    due_date: Optional[datetime] = Field(None, description="Due date")


class TicketPatch(BaseModel):
    """Schema for partial ticket update"""
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    description: Optional[str] = Field(None, min_length=20)
    category: Optional[TicketCategory] = None
    subcategory: Optional[str] = Field(None, max_length=50)
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to: Optional[UUID] = None
    assigned_team: Optional[str] = Field(None, max_length=100)
    environment: Optional[Environment] = None
    affected_service: Optional[str] = Field(None, max_length=100)
    impact_level: Optional[ImpactLevel] = None
    tags: Optional[List[str]] = None
    resolution_notes: Optional[str] = None
    due_date: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided"""
        if v is not None:
            if len(v.strip()) < 10:
                raise ValueError('Title must be at least 10 characters long')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided"""
        if v is not None:
            if len(v.strip()) < 20:
                raise ValueError('Description must be at least 20 characters long')
            return v.strip()
        return v


class TicketResponse(BaseModel):
    """Schema for ticket response"""
    id: UUID
    ticket_number: str
    title: str
    description: str
    category: str
    subcategory: Optional[str]
    status: str
    priority: str
    requestor_id: UUID
    assigned_to: Optional[UUID]
    assigned_team: Optional[str]
    environment: Optional[str]
    affected_service: Optional[str]
    impact_level: Optional[str]
    tags: Optional[List[str]]
    due_date: Optional[datetime]
    response_due_at: Optional[datetime]
    resolution_due_at: Optional[datetime]
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    closed_by: Optional[UUID]
    closure_code: Optional[str]
    # Escalation fields
    current_escalation_level: int = Field(default=0, description="Current escalation level (0-5)")
    escalation_count: int = Field(default=0, description="Number of times escalated")
    last_escalated_at: Optional[datetime] = Field(None, description="When last escalated")
    last_escalated_by: Optional[UUID] = Field(None, description="Who escalated last")
    # Timestamps
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[UUID]
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    """Schema for detailed ticket response with related data"""
    comment_count: int = Field(default=0, description="Number of comments")
    attachment_count: int = Field(default=0, description="Number of attachments")
    is_overdue: bool = Field(default=False, description="Whether ticket is overdue")


class TicketListResponse(BaseModel):
    """Schema for paginated ticket list"""
    tickets: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AssignTicketRequest(BaseModel):
    """Schema for ticket assignment"""
    assignee_id: UUID = Field(..., description="User ID to assign ticket to")
    notes: Optional[str] = Field(None, description="Assignment notes")


class UpdateStatusRequest(BaseModel):
    """Schema for status update"""
    status: TicketStatus = Field(..., description="New ticket status")
    notes: Optional[str] = Field(None, description="Status change notes")


class ResolveTicketRequest(BaseModel):
    """Schema for resolving ticket"""
    resolution_notes: str = Field(..., min_length=20, description="Detailed resolution description")

    @field_validator('resolution_notes')
    @classmethod
    def validate_resolution(cls, v: str) -> str:
        """Validate resolution notes"""
        if len(v.strip()) < 20:
            raise ValueError('Resolution notes must be at least 20 characters long')
        return v.strip()


class CloseTicketRequest(BaseModel):
    """Schema for closing ticket"""
    closure_code: ClosureCode = Field(..., description="Closure code")
    closure_notes: Optional[str] = Field(None, description="Closure notes")


class ReopenTicketRequest(BaseModel):
    """Schema for reopening ticket"""
    reason: str = Field(..., min_length=20, description="Reason for reopening")

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Validate reopen reason"""
        if len(v.strip()) < 20:
            raise ValueError('Reopen reason must be at least 20 characters long')
        return v.strip()


# ============================================================================
# Comment Schemas
# ============================================================================

class CommentBase(BaseModel):
    """Base comment schema"""
    content: str = Field(..., min_length=1, description="Comment content")
    comment_type: CommentType = Field(default=CommentType.COMMENT, description="Comment type")
    is_internal: bool = Field(default=False, description="Internal comment (not visible to requestor)")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content"""
        if not v.strip():
            raise ValueError('Comment content cannot be empty or whitespace only')
        return v.strip()


class CommentCreate(CommentBase):
    """Schema for creating a comment"""
    pass


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: str = Field(..., min_length=1, description="Updated comment content")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content"""
        if not v.strip():
            raise ValueError('Comment content cannot be empty or whitespace only')
        return v.strip()


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: UUID
    ticket_id: UUID
    author_id: UUID
    content: str
    comment_type: str
    is_internal: bool
    is_system_generated: bool
    has_attachments: bool
    edited_at: Optional[datetime]
    edited_by: Optional[UUID]
    created_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    """Schema for comment list"""
    comments: List[CommentResponse]
    total: int


# ============================================================================
# Attachment Schemas
# ============================================================================

class AttachmentResponse(BaseModel):
    """Schema for attachment response"""
    id: UUID
    ticket_id: Optional[UUID]
    comment_id: Optional[UUID]
    uploaded_by: UUID
    file_name: str
    file_size: int
    file_type: str
    file_extension: Optional[str]
    storage_type: str
    is_scanned: bool
    scan_status: Optional[str]
    content_hash: Optional[str]
    thumbnail_path: Optional[str]
    created_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)


class AttachmentListResponse(BaseModel):
    """Schema for attachment list"""
    attachments: List[AttachmentResponse]
    total: int


# ============================================================================
# Ticket History Schemas
# ============================================================================

class TicketHistoryResponse(BaseModel):
    """Schema for ticket history response"""
    id: UUID
    ticket_id: UUID
    changed_by: Optional[UUID]
    change_type: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    change_description: Optional[str]
    change_metadata: Optional[dict]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketHistoryListResponse(BaseModel):
    """Schema for ticket history list"""
    history: List[TicketHistoryResponse]
    total: int


# ============================================================================
# Generic Response Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Error code")


# ============================================================================
# Filter/Search Schemas
# ============================================================================

class TicketFilters(BaseModel):
    """Schema for ticket filtering"""
    status: Optional[List[TicketStatus]] = None
    priority: Optional[List[TicketPriority]] = None
    category: Optional[List[TicketCategory]] = None
    assigned_to: Optional[UUID] = None
    requestor_id: Optional[UUID] = None
    environment: Optional[Environment] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = Field(None, description="Full-text search")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    sort_by: str = Field(default="created_at", description="Field to sort by")
    order: str = Field(default="desc", description="Sort order (asc/desc)")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=100, description="Items per page")

    @field_validator('order')
    @classmethod
    def validate_order(cls, v: str) -> str:
        """Validate sort order"""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('Order must be asc or desc')
        return v.lower()

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort field"""
        allowed_fields = [
            'created_at', 'updated_at', 'priority', 'status',
            'due_date', 'ticket_number'
        ]
        if v not in allowed_fields:
            raise ValueError(f'Sort field must be one of: {", ".join(allowed_fields)}')
        return v
