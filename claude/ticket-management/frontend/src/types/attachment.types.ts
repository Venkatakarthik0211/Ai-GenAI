/**
 * Attachment Type Definitions
 *
 * TypeScript interfaces for file attachments
 * Reference: /backend/ticket/schemas.py
 */

// ============================================================================
// Enums
// ============================================================================

export enum StorageType {
  LOCAL = 'LOCAL',
  S3 = 'S3',
  AZURE_BLOB = 'AZURE_BLOB',
}

export enum ScanStatus {
  PENDING = 'PENDING',
  CLEAN = 'CLEAN',
  INFECTED = 'INFECTED',
  ERROR = 'ERROR',
  SKIPPED = 'SKIPPED',
}

// ============================================================================
// Attachment Interfaces
// ============================================================================

export interface Attachment {
  id: string
  ticket_id: string
  uploaded_by: string
  filename: string
  original_filename: string
  file_size: number
  file_type: string
  file_path: string
  file_hash: string
  storage_type: StorageType
  scan_status: ScanStatus
  scan_result: string | null
  download_url: string | null
  created_at: string
}

export interface AttachmentListResponse {
  attachments: Attachment[]
  total: number
}

export interface AttachmentUploadProgress {
  filename: string
  progress: number
  status: 'uploading' | 'success' | 'error'
  error?: string
}
