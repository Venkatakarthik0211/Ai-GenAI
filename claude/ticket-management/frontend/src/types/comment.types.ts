/**
 * Comment Type Definitions
 *
 * TypeScript interfaces for ticket comments
 * Reference: /backend/ticket/schemas.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum CommentType {
  COMMENT = 'COMMENT',
  NOTE = 'NOTE',
  SOLUTION = 'SOLUTION',
  WORKAROUND = 'WORKAROUND',
  STATUS_CHANGE = 'STATUS_CHANGE',
  ASSIGNMENT_CHANGE = 'ASSIGNMENT_CHANGE',
  ESCALATION = 'ESCALATION',
}

// ============================================================================
// Comment Interfaces
// ============================================================================

export interface Comment {
  id: string
  ticket_id: string
  author_id: string
  content: string
  comment_type: CommentType
  is_internal: boolean
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface CommentCreate {
  content: string
  comment_type?: CommentType
  is_internal?: boolean
}

export interface CommentListResponse {
  comments: Comment[]
  total: number
}
