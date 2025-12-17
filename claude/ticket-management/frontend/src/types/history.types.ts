/**
 * History Type Definitions
 *
 * TypeScript interfaces for ticket history/audit trail
 * Reference: /backend/ticket/schemas.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum ChangeType {
  CREATED = 'CREATED',
  STATUS_CHANGE = 'STATUS_CHANGE',
  PRIORITY_CHANGE = 'PRIORITY_CHANGE',
  ASSIGNMENT_CHANGE = 'ASSIGNMENT_CHANGE',
  FIELD_UPDATE = 'FIELD_UPDATE',
  COMMENT_ADDED = 'COMMENT_ADDED',
  ATTACHMENT_ADDED = 'ATTACHMENT_ADDED',
  RESOLVED = 'RESOLVED',
  CLOSED = 'CLOSED',
  REOPENED = 'REOPENED',
  ESCALATED = 'ESCALATED',
}

// ============================================================================
// History Interfaces
// ============================================================================

export interface TicketHistory {
  id: string
  ticket_id: string
  changed_by: string | null
  change_type: ChangeType
  field_name: string | null
  old_value: string | null
  new_value: string | null
  change_description: string | null
  change_metadata: Record<string, any> | null
  created_at: string
  ip_address: string | null
  user_agent: string | null
}

export interface TicketHistoryListResponse {
  history: TicketHistory[]
  total: number
}
