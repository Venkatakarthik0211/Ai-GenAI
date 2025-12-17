/**
 * Ticket API Endpoints
 *
 * API calls for ticket management
 * Base URL: http://localhost:8002/api/v1
 */

import apiClient from '../client/axios.config'
import type {
  Ticket,
  TicketCreate,
  TicketUpdate,
  TicketListResponse,
  TicketListParams,
  UpdateStatusRequest,
  ResolveTicketRequest,
  CloseTicketRequest,
  ReopenTicketRequest,
} from '@/types/ticket.types'
import type { CommentCreate, CommentListResponse } from '@/types/comment.types'
import type { AttachmentListResponse } from '@/types/attachment.types'
import type { TicketHistoryListResponse } from '@/types/history.types'

// Base URL for ticket service
const TICKET_BASE_URL = import.meta.env.VITE_TICKET_API_URL || 'http://localhost:8002/api/v1'

// ============================================================================
// Ticket CRUD Operations
// ============================================================================

export const ticketApi = {
  /**
   * List tickets with filters, pagination, sorting
   */
  list: (params?: TicketListParams) => {
    return apiClient.get<TicketListResponse>(`${TICKET_BASE_URL}/tickets`, { params })
  },

  /**
   * Get ticket by ID
   */
  getById: (id: string) => {
    return apiClient.get<Ticket>(`${TICKET_BASE_URL}/tickets/${id}`)
  },

  /**
   * Create new ticket
   */
  create: (data: TicketCreate) => {
    return apiClient.post<Ticket>(`${TICKET_BASE_URL}/tickets`, data)
  },

  /**
   * Full update of ticket (PUT)
   */
  update: (id: string, data: TicketUpdate) => {
    return apiClient.put<Ticket>(`${TICKET_BASE_URL}/tickets/${id}`, data)
  },

  /**
   * Partial update of ticket (PATCH)
   */
  patch: (id: string, data: Partial<TicketUpdate>) => {
    return apiClient.patch<Ticket>(`${TICKET_BASE_URL}/tickets/${id}`, data)
  },

  /**
   * Delete ticket (soft delete)
   */
  delete: (id: string) => {
    return apiClient.delete(`${TICKET_BASE_URL}/tickets/${id}`)
  },

  // ============================================================================
  // Workflow Operations
  // ============================================================================

  /**
   * Change ticket status
   */
  changeStatus: (id: string, data: UpdateStatusRequest) => {
    return apiClient.patch<Ticket>(`${TICKET_BASE_URL}/tickets/${id}/status`, data)
  },

  /**
   * Resolve ticket
   */
  resolve: (id: string, data: ResolveTicketRequest) => {
    return apiClient.post<Ticket>(`${TICKET_BASE_URL}/tickets/${id}/resolve`, data)
  },

  /**
   * Close ticket
   */
  close: (id: string, data: CloseTicketRequest) => {
    return apiClient.post<Ticket>(`${TICKET_BASE_URL}/tickets/${id}/close`, data)
  },

  /**
   * Reopen ticket
   */
  reopen: (id: string, data: ReopenTicketRequest) => {
    return apiClient.post<Ticket>(`${TICKET_BASE_URL}/tickets/${id}/reopen`, data)
  },

  // ============================================================================
  // Comments
  // ============================================================================

  /**
   * List comments for a ticket
   */
  listComments: (ticketId: string, includeInternal?: boolean) => {
    return apiClient.get<CommentListResponse>(`${TICKET_BASE_URL}/tickets/${ticketId}/comments`, {
      params: { include_internal: includeInternal },
    })
  },

  /**
   * Add comment to ticket
   */
  addComment: (ticketId: string, data: CommentCreate) => {
    return apiClient.post(`${TICKET_BASE_URL}/tickets/${ticketId}/comments`, data)
  },

  /**
   * Delete comment
   */
  deleteComment: (ticketId: string, commentId: string) => {
    return apiClient.delete(`${TICKET_BASE_URL}/tickets/${ticketId}/comments/${commentId}`)
  },

  // ============================================================================
  // Attachments
  // ============================================================================

  /**
   * List attachments for a ticket
   */
  listAttachments: (ticketId: string) => {
    return apiClient.get<AttachmentListResponse>(`${TICKET_BASE_URL}/tickets/${ticketId}/attachments`)
  },

  /**
   * Upload attachment to ticket
   */
  uploadAttachment: (ticketId: string, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)

    return apiClient.post(`${TICKET_BASE_URL}/tickets/${ticketId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },

  /**
   * Delete attachment
   */
  deleteAttachment: (ticketId: string, attachmentId: string) => {
    return apiClient.delete(`${TICKET_BASE_URL}/tickets/${ticketId}/attachments/${attachmentId}`)
  },

  /**
   * Download attachment
   */
  downloadAttachment: (ticketId: string, attachmentId: string) => {
    return apiClient.get(`${TICKET_BASE_URL}/tickets/${ticketId}/attachments/${attachmentId}/download`, {
      responseType: 'blob',
    })
  },

  // ============================================================================
  // History
  // ============================================================================

  /**
   * Get ticket history
   */
  getHistory: (ticketId: string) => {
    return apiClient.get<TicketHistoryListResponse>(`${TICKET_BASE_URL}/tickets/${ticketId}/history`)
  },

  // ============================================================================
  // User Management (for assignment)
  // ============================================================================

  /**
   * Get list of assignable users (engineers, team leads, managers, admins)
   */
  getAssignableUsers: () => {
    return apiClient.get<Array<{
      id: string
      username: string
      email: string
      full_name: string
      first_name: string
      last_name: string
      role: string
      department: string | null
    }>>(`${TICKET_BASE_URL}/users/assignable`)
  },
}

export default ticketApi
