/**
 * Ticket Type Definitions
 *
 * TypeScript interfaces matching backend Pydantic schemas
 * Reference: /backend/ticket/schemas.py, /backend/ticket/models.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum TicketStatus {
  NEW = 'NEW',
  OPEN = 'OPEN',
  IN_PROGRESS = 'IN_PROGRESS',
  PENDING_INFO = 'PENDING_INFO',
  RESOLVED = 'RESOLVED',
  CLOSED = 'CLOSED',
  REOPENED = 'REOPENED',
  ESCALATED = 'ESCALATED',
}

export enum TicketPriority {
  P1 = 'P1', // Critical
  P2 = 'P2', // High
  P3 = 'P3', // Medium
  P4 = 'P4', // Low
}

export enum TicketCategory {
  INCIDENT = 'INCIDENT',
  SERVICE_REQUEST = 'SERVICE_REQUEST',
  CHANGE_REQUEST = 'CHANGE_REQUEST',
  PROBLEM = 'PROBLEM',
  MAINTENANCE = 'MAINTENANCE',
}

export enum Environment {
  DEV = 'DEV',
  QA = 'QA',
  STAGING = 'STAGING',
  PRODUCTION = 'PRODUCTION',
  DR = 'DR',
  UNKNOWN = 'UNKNOWN',
}

export enum ImpactLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

export enum ClosureCode {
  RESOLVED = 'RESOLVED',
  WORKAROUND = 'WORKAROUND',
  DUPLICATE = 'DUPLICATE',
  CANNOT_REPRODUCE = 'CANNOT_REPRODUCE',
  NOT_AN_ISSUE = 'NOT_AN_ISSUE',
  CANCELLED = 'CANCELLED',
  DEFERRED = 'DEFERRED',
}

// ============================================================================
// Ticket Interfaces
// ============================================================================

export interface Ticket {
  id: string
  ticket_number: string
  title: string
  description: string
  category: TicketCategory
  subcategory: string | null
  status: TicketStatus
  priority: TicketPriority
  requestor_id: string
  assigned_to: string | null
  assigned_team: string | null
  environment: Environment | null
  affected_service: string | null
  impact_level: ImpactLevel | null
  tags: string[] | null
  due_date: string | null
  response_due_at: string | null
  resolution_due_at: string | null
  first_response_at: string | null
  resolved_at: string | null
  closed_at: string | null
  closed_by: string | null
  closure_code: ClosureCode | null
  resolution_notes: string | null
  created_at: string
  updated_at: string
  created_by: string | null
  updated_by: string | null
  deleted_at: string | null
}

export interface TicketCreate {
  title: string
  description: string
  category: TicketCategory
  subcategory?: string
  priority?: TicketPriority
  environment?: Environment
  affected_service?: string
  impact_level?: ImpactLevel
  tags?: string[]
  assigned_to?: string
  assigned_team?: string
}

export interface TicketUpdate {
  title?: string
  description?: string
  category?: TicketCategory
  subcategory?: string
  priority?: TicketPriority
  status?: TicketStatus
  assigned_to?: string
  assigned_team?: string
  environment?: Environment
  affected_service?: string
  impact_level?: ImpactLevel
  tags?: string[]
  resolution_notes?: string
  due_date?: string
}

export interface TicketListResponse {
  tickets: Ticket[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// ============================================================================
// Ticket Filters & Search
// ============================================================================

export interface TicketFilters {
  status?: TicketStatus | TicketStatus[]
  priority?: TicketPriority | TicketPriority[]
  category?: TicketCategory | TicketCategory[]
  assigned_to?: string
  requestor_id?: string
  search?: string
  tags?: string[]
  created_after?: string
  created_before?: string
  environment?: Environment
  impact_level?: ImpactLevel
}

export interface TicketSortOptions {
  sort_by?: 'created_at' | 'updated_at' | 'priority' | 'status' | 'due_date'
  order?: 'asc' | 'desc'
}

export interface TicketListParams extends TicketFilters, TicketSortOptions {
  page?: number
  page_size?: number
}

// ============================================================================
// Workflow Actions
// ============================================================================

export interface UpdateStatusRequest {
  status: TicketStatus
  notes?: string
}

export interface ResolveTicketRequest {
  resolution_notes: string
}

export interface CloseTicketRequest {
  closure_code: ClosureCode
  closure_notes?: string
}

export interface ReopenTicketRequest {
  reason: string
}

// ============================================================================
// UI State
// ============================================================================

export interface TicketState {
  tickets: Ticket[]
  selectedTicket: Ticket | null
  filters: TicketFilters
  sortOptions: TicketSortOptions
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
  loading: boolean
  error: string | null
}
