/**
 * TicketDetailPage Component
 * Displays complete ticket information with comments, attachments, and history
 */

import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import {
  fetchTicketById,
  deleteTicket,
  changeTicketStatus,
  resolveTicket,
  closeTicket,
  reopenTicket
} from '@/store/slices/ticketSlice'
import { ticketApi } from '@/api/endpoints/ticket.api'
import DashboardLayout from '@/components/layout/DashboardLayout/DashboardLayout'
import StatusBadge from '@/components/common/StatusBadge'
import PriorityBadge from '@/components/common/PriorityBadge'
import {
  TicketStatus,
  TicketPriority,
  ClosureCode
} from '@/types/ticket.types'
import { Comment, CommentType } from '@/types/comment.types'
import { Attachment } from '@/types/attachment.types'
import { TicketHistory } from '@/types/history.types'
import {
  ArrowLeft,
  Edit,
  Trash2,
  Clock,
  User,
  Tag,
  MessageSquare,
  Paperclip,
  History,
  AlertCircle,
  CheckCircle,
  XCircle,
  RotateCcw,
  Upload,
  Download,
  Send
} from 'lucide-react'
import toast from 'react-hot-toast'
import './TicketDetailPage.css'

const TicketDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { selectedTicket, loading, error } = useAppSelector(state => state.ticket)
  const { user } = useAppSelector(state => state.auth)

  // Local state for sections
  const [comments, setComments] = useState<Comment[]>([])
  const [attachments, setAttachments] = useState<Attachment[]>([])
  const [history, setHistory] = useState<TicketHistory[]>([])
  const [loadingComments, setLoadingComments] = useState(false)
  const [loadingAttachments, setLoadingAttachments] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)

  // Modal states
  const [showResolveModal, setShowResolveModal] = useState(false)
  const [showCloseModal, setShowCloseModal] = useState(false)
  const [showReopenModal, setShowReopenModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  // Form states
  const [commentText, setCommentText] = useState('')
  const [commentType, setCommentType] = useState<CommentType>(CommentType.COMMENT)
  const [isInternal, setIsInternal] = useState(false)
  const [resolutionNotes, setResolutionNotes] = useState('')
  const [closureCode, setClosureCode] = useState<ClosureCode>(ClosureCode.RESOLVED)
  const [closureNotes, setClosureNotes] = useState('')
  const [reopenReason, setReopenReason] = useState('')
  const [uploadProgress, setUploadProgress] = useState<number>(0)

  useEffect(() => {
    if (id) {
      dispatch(fetchTicketById(id))
    }
  }, [dispatch, id])

  useEffect(() => {
    if (selectedTicket) {
      loadComments()
      loadAttachments()
      loadHistory()
    }
  }, [selectedTicket])

  const loadComments = async () => {
    if (!id) return
    setLoadingComments(true)
    try {
      const response = await ticketApi.listComments(id, true)
      setComments(response.data.comments)
    } catch (error: any) {
      toast.error('Failed to load comments')
    } finally {
      setLoadingComments(false)
    }
  }

  const loadAttachments = async () => {
    if (!id) return
    setLoadingAttachments(true)
    try {
      const response = await ticketApi.listAttachments(id)
      setAttachments(response.data.attachments)
    } catch (error: any) {
      toast.error('Failed to load attachments')
    } finally {
      setLoadingAttachments(false)
    }
  }

  const loadHistory = async () => {
    if (!id) return
    setLoadingHistory(true)
    try {
      const response = await ticketApi.getHistory(id)
      setHistory(response.data.history)
    } catch (error: any) {
      toast.error('Failed to load history')
    } finally {
      setLoadingHistory(false)
    }
  }

  const handleAddComment = async () => {
    if (!id || !commentText.trim()) return

    try {
      await ticketApi.addComment(id, {
        content: commentText,
        comment_type: commentType,
        is_internal: isInternal,
      })
      setCommentText('')
      setCommentType(CommentType.COMMENT)
      setIsInternal(false)
      toast.success('Comment added successfully')
      loadComments()
      loadHistory()
    } catch (error: any) {
      toast.error('Failed to add comment')
    }
  }

  const handleDeleteComment = async (commentId: string) => {
    if (!id) return

    try {
      await ticketApi.deleteComment(id, commentId)
      toast.success('Comment deleted')
      loadComments()
      loadHistory()
    } catch (error: any) {
      toast.error('Failed to delete comment')
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!id || !event.target.files || event.target.files.length === 0) return

    const file = event.target.files[0]

    // Check file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB')
      return
    }

    try {
      setUploadProgress(0)
      await ticketApi.uploadAttachment(id, file, (progress) => {
        setUploadProgress(progress)
      })
      toast.success('File uploaded successfully')
      loadAttachments()
      loadHistory()
      setUploadProgress(0)
    } catch (error: any) {
      toast.error('Failed to upload file')
      setUploadProgress(0)
    }
  }

  const handleDownloadAttachment = async (attachmentId: string, filename: string) => {
    if (!id) return

    try {
      const response = await ticketApi.downloadAttachment(id, attachmentId)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      toast.error('Failed to download file')
    }
  }

  const handleDeleteAttachment = async (attachmentId: string) => {
    if (!id) return

    try {
      await ticketApi.deleteAttachment(id, attachmentId)
      toast.success('Attachment deleted')
      loadAttachments()
      loadHistory()
    } catch (error: any) {
      toast.error('Failed to delete attachment')
    }
  }

  const handleResolve = async () => {
    if (!id || !resolutionNotes.trim()) {
      toast.error('Please provide resolution notes')
      return
    }

    try {
      await dispatch(resolveTicket({ id, data: { resolution_notes: resolutionNotes } })).unwrap()
      toast.success('Ticket resolved successfully')
      setShowResolveModal(false)
      setResolutionNotes('')
      loadHistory()
    } catch (error: any) {
      toast.error('Failed to resolve ticket')
    }
  }

  const handleClose = async () => {
    if (!id || !closureNotes.trim()) {
      toast.error('Please provide closure notes')
      return
    }

    try {
      await dispatch(closeTicket({
        id,
        data: { closure_code: closureCode, closure_notes: closureNotes }
      })).unwrap()
      toast.success('Ticket closed successfully')
      setShowCloseModal(false)
      setClosureNotes('')
      loadHistory()
    } catch (error: any) {
      toast.error('Failed to close ticket')
    }
  }

  const handleReopen = async () => {
    if (!id || !reopenReason.trim()) {
      toast.error('Please provide a reason for reopening')
      return
    }

    try {
      await dispatch(reopenTicket({ id, data: { reason: reopenReason } })).unwrap()
      toast.success('Ticket reopened successfully')
      setShowReopenModal(false)
      setReopenReason('')
      loadHistory()
    } catch (error: any) {
      toast.error('Failed to reopen ticket')
    }
  }

  const handleDelete = async () => {
    if (!id) return

    try {
      await dispatch(deleteTicket(id)).unwrap()
      toast.success('Ticket deleted successfully')
      navigate('/tickets')
    } catch (error: any) {
      toast.error('Failed to delete ticket')
    }
  }

  const canTransitionTo = (targetStatus: TicketStatus): boolean => {
    if (!selectedTicket) return false

    const validTransitions: Record<TicketStatus, TicketStatus[]> = {
      [TicketStatus.NEW]: [TicketStatus.OPEN, TicketStatus.ESCALATED],
      [TicketStatus.OPEN]: [TicketStatus.IN_PROGRESS, TicketStatus.PENDING_INFO, TicketStatus.ESCALATED],
      [TicketStatus.IN_PROGRESS]: [TicketStatus.RESOLVED, TicketStatus.PENDING_INFO, TicketStatus.ESCALATED],
      [TicketStatus.PENDING_INFO]: [TicketStatus.IN_PROGRESS, TicketStatus.ESCALATED],
      [TicketStatus.RESOLVED]: [TicketStatus.CLOSED, TicketStatus.REOPENED],
      [TicketStatus.CLOSED]: [TicketStatus.REOPENED],
      [TicketStatus.REOPENED]: [TicketStatus.OPEN, TicketStatus.IN_PROGRESS],
      [TicketStatus.ESCALATED]: [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED],
    }

    return validTransitions[selectedTicket.status as TicketStatus]?.includes(targetStatus) || false
  }

  const handleStatusChange = async (newStatus: TicketStatus) => {
    if (!id) return

    try {
      await dispatch(changeTicketStatus({ id, data: { status: newStatus } })).unwrap()
      toast.success(`Status changed to ${newStatus}`)
      loadHistory()
    } catch (error: any) {
      toast.error('Failed to change status')
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="ticket-detail-page">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading ticket details...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !selectedTicket) {
    return (
      <DashboardLayout>
        <div className="ticket-detail-page">
          <div className="error-message">
            <p>{error || 'Ticket not found'}</p>
            <button onClick={() => navigate('/tickets')}>Back to Tickets</button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="ticket-detail-page">
      {/* Header */}
      <div className="ticket-header">
        <button className="btn-back" onClick={() => navigate('/tickets')}>
          <ArrowLeft size={20} />
          Back to Tickets
        </button>

        <div className="header-main">
          <div className="header-info">
            <div className="ticket-number-title">
              <span className="ticket-number">{selectedTicket.ticket_number}</span>
              <h1 className="ticket-title">{selectedTicket.title}</h1>
            </div>
            <div className="ticket-badges">
              <StatusBadge status={selectedTicket.status as TicketStatus} />
              <PriorityBadge priority={selectedTicket.priority as TicketPriority} />
            </div>
          </div>

          <div className="header-actions">
            <button className="btn-secondary" onClick={() => navigate(`/tickets/${id}/edit`)}>
              <Edit size={18} />
              Edit
            </button>
            <button className="btn-danger" onClick={() => setShowDeleteModal(true)}>
              <Trash2 size={18} />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ticket-content">
        {/* Left Column */}
        <div className="content-main">
          {/* Description */}
          <div className="section">
            <h2>Description</h2>
            <div className="ticket-description">{selectedTicket.description}</div>
          </div>

          {/* Status Workflow */}
          <div className="section">
            <h2>Actions</h2>
            <div className="workflow-actions">
              {canTransitionTo(TicketStatus.OPEN) && (
                <button
                  className="btn-workflow"
                  onClick={() => handleStatusChange(TicketStatus.OPEN)}
                >
                  <CheckCircle size={18} />
                  Open
                </button>
              )}
              {canTransitionTo(TicketStatus.IN_PROGRESS) && (
                <button
                  className="btn-workflow"
                  onClick={() => handleStatusChange(TicketStatus.IN_PROGRESS)}
                >
                  <Clock size={18} />
                  Start Progress
                </button>
              )}
              {canTransitionTo(TicketStatus.PENDING_INFO) && (
                <button
                  className="btn-workflow"
                  onClick={() => handleStatusChange(TicketStatus.PENDING_INFO)}
                >
                  <AlertCircle size={18} />
                  Pending Info
                </button>
              )}
              {(selectedTicket.status === TicketStatus.IN_PROGRESS ||
                selectedTicket.status === TicketStatus.ESCALATED) && (
                <button
                  className="btn-workflow btn-success"
                  onClick={() => setShowResolveModal(true)}
                >
                  <CheckCircle size={18} />
                  Resolve
                </button>
              )}
              {selectedTicket.status === TicketStatus.RESOLVED && (
                <button
                  className="btn-workflow btn-success"
                  onClick={() => setShowCloseModal(true)}
                >
                  <XCircle size={18} />
                  Close
                </button>
              )}
              {(selectedTicket.status === TicketStatus.RESOLVED ||
                selectedTicket.status === TicketStatus.CLOSED) && (
                <button
                  className="btn-workflow btn-warning"
                  onClick={() => setShowReopenModal(true)}
                >
                  <RotateCcw size={18} />
                  Reopen
                </button>
              )}
              {canTransitionTo(TicketStatus.ESCALATED) && (
                <button
                  className="btn-workflow btn-danger"
                  onClick={() => handleStatusChange(TicketStatus.ESCALATED)}
                >
                  <AlertCircle size={18} />
                  Escalate
                </button>
              )}
            </div>
          </div>

          {/* Comments */}
          <div className="section">
            <h2>
              <MessageSquare size={20} />
              Comments ({comments.length})
            </h2>

            <div className="comment-form">
              <textarea
                placeholder="Add a comment..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                rows={4}
              />
              <div className="comment-form-controls">
                <div className="comment-options">
                  <select value={commentType} onChange={(e) => setCommentType(e.target.value as CommentType)}>
                    <option value={CommentType.COMMENT}>Comment</option>
                    <option value={CommentType.NOTE}>Note</option>
                    <option value={CommentType.SOLUTION}>Solution</option>
                    <option value={CommentType.WORKAROUND}>Workaround</option>
                  </select>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={isInternal}
                      onChange={(e) => setIsInternal(e.target.checked)}
                    />
                    Internal
                  </label>
                </div>
                <button
                  className="btn-primary"
                  onClick={handleAddComment}
                  disabled={!commentText.trim()}
                >
                  <Send size={18} />
                  Add Comment
                </button>
              </div>
            </div>

            {loadingComments ? (
              <div className="loading-small">Loading comments...</div>
            ) : (
              <div className="comments-list">
                {comments.map((comment) => (
                  <div key={comment.id} className={`comment-item ${comment.is_internal ? 'internal' : ''}`}>
                    <div className="comment-header">
                      <div className="comment-author">
                        <User size={16} />
                        {comment.author_id}
                      </div>
                      <div className="comment-meta">
                        <span className="comment-type">{comment.comment_type}</span>
                        {comment.is_internal && <span className="internal-badge">Internal</span>}
                        <span className="comment-date">
                          {new Date(comment.created_at).toLocaleString()}
                        </span>
                        {comment.author_id === user?.id && (
                          <button
                            className="btn-icon-danger"
                            onClick={() => handleDeleteComment(comment.id)}
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="comment-content">{comment.content}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Attachments */}
          <div className="section">
            <h2>
              <Paperclip size={20} />
              Attachments ({attachments.length})
            </h2>

            <div className="attachment-upload">
              <input
                type="file"
                id="file-upload"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
              <label htmlFor="file-upload" className="btn-secondary">
                <Upload size={18} />
                Upload File
              </label>
              {uploadProgress > 0 && (
                <div className="upload-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
                  </div>
                  <span>{uploadProgress}%</span>
                </div>
              )}
            </div>

            {loadingAttachments ? (
              <div className="loading-small">Loading attachments...</div>
            ) : (
              <div className="attachments-list">
                {attachments.map((attachment) => (
                  <div key={attachment.id} className="attachment-item">
                    <div className="attachment-icon">
                      <Paperclip size={20} />
                    </div>
                    <div className="attachment-info">
                      <div className="attachment-name">{attachment.filename}</div>
                      <div className="attachment-meta">
                        {(attachment.file_size / 1024).toFixed(2)} KB •{' '}
                        {new Date(attachment.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="attachment-actions">
                      <button
                        className="btn-icon"
                        onClick={() => handleDownloadAttachment(attachment.id, attachment.filename)}
                      >
                        <Download size={18} />
                      </button>
                      <button
                        className="btn-icon-danger"
                        onClick={() => handleDeleteAttachment(attachment.id)}
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* History */}
          <div className="section">
            <h2>
              <History size={20} />
              History ({history.length})
            </h2>
            {loadingHistory ? (
              <div className="loading-small">Loading history...</div>
            ) : (
              <div className="history-timeline">
                {history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-icon">
                      <div className="history-dot"></div>
                    </div>
                    <div className="history-content">
                      <div className="history-header">
                        <span className="history-type">{item.change_type}</span>
                        <span className="history-date">
                          {new Date(item.created_at).toLocaleString()}
                        </span>
                      </div>
                      <div className="history-description">
                        {item.change_description || `${item.field_name} changed from "${item.old_value}" to "${item.new_value}"`}
                      </div>
                      {item.changed_by && (
                        <div className="history-user">
                          <User size={14} />
                          {item.changed_by}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Metadata */}
        <div className="content-sidebar">
          <div className="metadata-card">
            <h3>Details</h3>

            <div className="metadata-item">
              <label>Category</label>
              <span>{selectedTicket.category.replace(/_/g, ' ')}</span>
            </div>

            {selectedTicket.subcategory && (
              <div className="metadata-item">
                <label>Subcategory</label>
                <span>{selectedTicket.subcategory}</span>
              </div>
            )}

            {selectedTicket.environment && (
              <div className="metadata-item">
                <label>Environment</label>
                <span>{selectedTicket.environment}</span>
              </div>
            )}

            <div className="metadata-item">
              <label>Requestor</label>
              <span>{selectedTicket.requestor_id}</span>
            </div>

            <div className="metadata-item">
              <label>Assigned To</label>
              <span>{selectedTicket.assigned_to || 'Unassigned'}</span>
            </div>

            {selectedTicket.assigned_team && (
              <div className="metadata-item">
                <label>Assigned Team</label>
                <span>{selectedTicket.assigned_team}</span>
              </div>
            )}

            <div className="metadata-item">
              <label>Created</label>
              <span>{new Date(selectedTicket.created_at).toLocaleString()}</span>
            </div>

            <div className="metadata-item">
              <label>Updated</label>
              <span>{new Date(selectedTicket.updated_at).toLocaleString()}</span>
            </div>

            {selectedTicket.response_due_at && (
              <div className="metadata-item">
                <label>Response Due</label>
                <span>{new Date(selectedTicket.response_due_at).toLocaleString()}</span>
              </div>
            )}

            {selectedTicket.resolution_due_at && (
              <div className="metadata-item">
                <label>Resolution Due</label>
                <span>{new Date(selectedTicket.resolution_due_at).toLocaleString()}</span>
              </div>
            )}

            {selectedTicket.tags && selectedTicket.tags.length > 0 && (
              <div className="metadata-item">
                <label>Tags</label>
                <div className="tags-list">
                  {selectedTicket.tags.map((tag, index) => (
                    <span key={index} className="tag">
                      <Tag size={12} />
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showResolveModal && (
        <div className="modal-overlay" onClick={() => setShowResolveModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Resolve Ticket</h3>
            <textarea
              placeholder="Enter resolution notes..."
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              rows={6}
            />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowResolveModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleResolve}>
                Resolve Ticket
              </button>
            </div>
          </div>
        </div>
      )}

      {showCloseModal && (
        <div className="modal-overlay" onClick={() => setShowCloseModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Close Ticket</h3>
            <select
              value={closureCode}
              onChange={(e) => setClosureCode(e.target.value as ClosureCode)}
            >
              <option value={ClosureCode.RESOLVED}>Resolved</option>
              <option value={ClosureCode.WORKAROUND}>Workaround</option>
              <option value={ClosureCode.DUPLICATE}>Duplicate</option>
              <option value={ClosureCode.CANNOT_REPRODUCE}>Cannot Reproduce</option>
              <option value={ClosureCode.NOT_AN_ISSUE}>Not an Issue</option>
              <option value={ClosureCode.CANCELLED}>Cancelled</option>
              <option value={ClosureCode.DEFERRED}>Deferred</option>
            </select>
            <textarea
              placeholder="Enter closure notes..."
              value={closureNotes}
              onChange={(e) => setClosureNotes(e.target.value)}
              rows={6}
            />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowCloseModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleClose}>
                Close Ticket
              </button>
            </div>
          </div>
        </div>
      )}

      {showReopenModal && (
        <div className="modal-overlay" onClick={() => setShowReopenModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Reopen Ticket</h3>
            <textarea
              placeholder="Enter reason for reopening..."
              value={reopenReason}
              onChange={(e) => setReopenReason(e.target.value)}
              rows={6}
            />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowReopenModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleReopen}>
                Reopen Ticket
              </button>
            </div>
          </div>
        </div>
      )}

      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Delete Ticket</h3>
            <p>Are you sure you want to delete this ticket? This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowDeleteModal(false)}>
                Cancel
              </button>
              <button className="btn-danger" onClick={handleDelete}>
                Delete Ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </DashboardLayout>
  )
}

export default TicketDetailPage
