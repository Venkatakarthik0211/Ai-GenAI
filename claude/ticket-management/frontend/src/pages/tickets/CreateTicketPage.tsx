/**
 * CreateTicketPage Component
 * Form for creating new tickets with validation
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { createTicket } from '@/store/slices/ticketSlice'
import DashboardLayout from '@/components/layout/DashboardLayout/DashboardLayout'
import {
  TicketCategory,
  TicketPriority,
  Environment,
  ImpactLevel
} from '@/types/ticket.types'
import { ticketApi } from '@/api/endpoints/ticket.api'
import { ArrowLeft, Save } from 'lucide-react'
import toast from 'react-hot-toast'
import './CreateTicketPage.css'

// User interface for assignable users
interface AssignableUser {
  id: string
  username: string
  email: string
  full_name: string
  first_name: string
  last_name: string
  role: string
  department: string | null
}

// Validation schema matching backend requirements
const createTicketSchema = z.object({
  title: z.string()
    .min(10, 'Title must be at least 10 characters')
    .max(255, 'Title cannot exceed 255 characters')
    .refine(val => val.trim().length >= 10, {
      message: 'Title must be at least 10 characters (excluding whitespace)'
    }),
  description: z.string()
    .min(20, 'Description must be at least 20 characters')
    .refine(val => val.trim().length >= 20, {
      message: 'Description must be at least 20 characters (excluding whitespace)'
    }),
  category: z.nativeEnum(TicketCategory, { required_error: 'Category is required' }),
  subcategory: z.string()
    .max(50, 'Subcategory cannot exceed 50 characters')
    .optional()
    .or(z.literal('')),
  priority: z.nativeEnum(TicketPriority, { required_error: 'Priority is required' }),
  environment: z.nativeEnum(Environment).optional().or(z.literal('')),
  affected_service: z.string()
    .max(100, 'Affected service cannot exceed 100 characters')
    .optional()
    .or(z.literal('')),
  impact_level: z.nativeEnum(ImpactLevel).optional().or(z.literal('')),
  assigned_to: z.string().optional().or(z.literal('')),
  assigned_team: z.string()
    .max(100, 'Assigned team cannot exceed 100 characters')
    .optional()
    .or(z.literal('')),
  tags: z.array(z.string()
    .max(50, 'Each tag cannot exceed 50 characters')
    .regex(/^[a-z0-9-_]+$/, 'Tags can only contain lowercase letters, numbers, hyphens, and underscores')
  ).max(10, 'Maximum 10 tags allowed').optional(),
})

type CreateTicketFormData = z.infer<typeof createTicketSchema>

const CreateTicketPage = () => {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { loading } = useAppSelector(state => state.ticket)

  const [tagInput, setTagInput] = useState('')
  const [assignableUsers, setAssignableUsers] = useState<AssignableUser[]>([])
  const [loadingUsers, setLoadingUsers] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    reset,
  } = useForm<CreateTicketFormData>({
    resolver: zodResolver(createTicketSchema),
    defaultValues: {
      priority: TicketPriority.P3,
      category: TicketCategory.INCIDENT,
      tags: [],
    },
  })

  const tags = watch('tags') || []

  // Fetch assignable users on component mount
  useEffect(() => {
    const fetchAssignableUsers = async () => {
      setLoadingUsers(true)
      try {
        const response = await ticketApi.getAssignableUsers()
        setAssignableUsers(response.data)
      } catch (error) {
        console.error('Failed to fetch assignable users:', error)
        toast.error('Failed to load assignable users')
      } finally {
        setLoadingUsers(false)
      }
    }

    fetchAssignableUsers()
  }, [])

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase()
    // Validate tag format: only lowercase letters, numbers, hyphens, and underscores
    const tagPattern = /^[a-z0-9-_]+$/

    if (!trimmedTag) {
      return
    }

    if (!tagPattern.test(trimmedTag)) {
      toast.error('Tags can only contain lowercase letters, numbers, hyphens, and underscores')
      return
    }

    if (trimmedTag.length > 50) {
      toast.error('Tag cannot exceed 50 characters')
      return
    }

    if (tags.includes(trimmedTag)) {
      toast.error('Tag already added')
      return
    }

    if (tags.length >= 10) {
      toast.error('Maximum 10 tags allowed')
      return
    }

    setValue('tags', [...tags, trimmedTag])
    setTagInput('')
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setValue('tags', tags.filter(tag => tag !== tagToRemove))
  }

  const onSubmit = async (data: CreateTicketFormData) => {
    try {
      // Clean the data - remove empty strings and convert to proper types
      const cleanedData = {
        ...data,
        title: data.title.trim(),
        description: data.description.trim(),
        subcategory: data.subcategory && data.subcategory.trim() ? data.subcategory.trim() : undefined,
        environment: data.environment ? data.environment : undefined,
        affected_service: data.affected_service && data.affected_service.trim() ? data.affected_service.trim() : undefined,
        impact_level: data.impact_level ? data.impact_level : undefined,
        // assigned_to is already a UUID from the dropdown, or empty string for unassigned
        assigned_to: data.assigned_to && data.assigned_to.trim() ? data.assigned_to.trim() : undefined,
        assigned_team: data.assigned_team && data.assigned_team.trim() ? data.assigned_team.trim() : undefined,
        tags: data.tags && data.tags.length > 0 ? data.tags : undefined,
      }

      console.log('Form data before cleaning:', data)
      console.log('Cleaned data being sent:', cleanedData)
      console.log('Cleaned data JSON:', JSON.stringify(cleanedData, null, 2))

      const result = await dispatch(createTicket(cleanedData)).unwrap()

      toast.success('Ticket created successfully!')
      navigate(`/tickets/${result.id}`)
    } catch (error: any) {
      console.error('Create ticket error:', error)

      // Display specific validation errors
      if (error?.detail) {
        if (Array.isArray(error.detail)) {
          error.detail.forEach((err: any) => {
            toast.error(`${err.loc?.join(' > ') || 'Validation'}: ${err.msg}`)
          })
        } else if (typeof error.detail === 'string') {
          toast.error(error.detail)
        } else {
          toast.error(JSON.stringify(error.detail))
        }
      } else if (typeof error === 'string') {
        toast.error(error)
      } else {
        toast.error('Failed to create ticket. Please check all required fields.')
      }
    }
  }

  const handleCancel = () => {
    if (window.confirm('Are you sure you want to cancel? All unsaved changes will be lost.')) {
      navigate('/tickets')
    }
  }

  return (
    <DashboardLayout>
      <div className="create-ticket-page">
        {/* Header */}
        <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/tickets')}>
          <ArrowLeft size={20} />
          Back to Tickets
        </button>
        <h1>Create New Ticket</h1>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="ticket-form">
        {/* Basic Information */}
        <div className="form-section">
          <h2>Basic Information</h2>

          <div className="form-group">
            <label htmlFor="title">
              Title <span className="required">*</span>
            </label>
            <input
              id="title"
              type="text"
              placeholder="Brief summary of the issue (min. 10 characters)"
              {...register('title')}
              className={errors.title ? 'error' : ''}
            />
            {errors.title && <span className="error-message">{errors.title.message}</span>}
            <span className="form-hint">Provide a clear, concise title for the ticket</span>
          </div>

          <div className="form-group">
            <label htmlFor="description">
              Description <span className="required">*</span>
            </label>
            <textarea
              id="description"
              rows={8}
              placeholder="Detailed description of the issue (min. 20 characters)"
              {...register('description')}
              className={errors.description ? 'error' : ''}
            />
            {errors.description && (
              <span className="error-message">{errors.description.message}</span>
            )}
            <span className="form-hint">
              Include steps to reproduce, expected vs actual behavior, and any error messages
            </span>
          </div>
        </div>

        {/* Categorization */}
        <div className="form-section">
          <h2>Categorization</h2>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category">
                Category <span className="required">*</span>
              </label>
              <select
                id="category"
                {...register('category')}
                className={errors.category ? 'error' : ''}
              >
                <option value={TicketCategory.INCIDENT}>Incident</option>
                <option value={TicketCategory.SERVICE_REQUEST}>Service Request</option>
                <option value={TicketCategory.CHANGE_REQUEST}>Change Request</option>
                <option value={TicketCategory.PROBLEM}>Problem</option>
                <option value={TicketCategory.MAINTENANCE}>Maintenance</option>
              </select>
              {errors.category && (
                <span className="error-message">{errors.category.message}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="subcategory">Subcategory</label>
              <input
                id="subcategory"
                type="text"
                placeholder="e.g., Network, Database, Application"
                {...register('subcategory')}
              />
              <span className="form-hint">Optional: Specify a subcategory</span>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="priority">
                Priority <span className="required">*</span>
              </label>
              <select
                id="priority"
                {...register('priority')}
                className={errors.priority ? 'error' : ''}
              >
                <option value={TicketPriority.P1}>P1 - Critical (Immediate attention)</option>
                <option value={TicketPriority.P2}>P2 - High (Urgent)</option>
                <option value={TicketPriority.P3}>P3 - Medium (Normal)</option>
                <option value={TicketPriority.P4}>P4 - Low (Can wait)</option>
              </select>
              {errors.priority && (
                <span className="error-message">{errors.priority.message}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="impact_level">Impact Level</label>
              <select id="impact_level" {...register('impact_level')}>
                <option value="">Select impact level</option>
                <option value={ImpactLevel.LOW}>Low - Single user</option>
                <option value={ImpactLevel.MEDIUM}>Medium - Multiple users</option>
                <option value={ImpactLevel.HIGH}>High - Department</option>
                <option value={ImpactLevel.CRITICAL}>Critical - Organization-wide</option>
              </select>
              <span className="form-hint">How many users are affected?</span>
            </div>
          </div>
        </div>

        {/* Technical Details */}
        <div className="form-section">
          <h2>Technical Details</h2>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="environment">Environment</label>
              <select id="environment" {...register('environment')}>
                <option value="">Select environment</option>
                <option value={Environment.DEV}>Development</option>
                <option value={Environment.QA}>QA / Testing</option>
                <option value={Environment.STAGING}>Staging</option>
                <option value={Environment.PRODUCTION}>Production</option>
                <option value={Environment.DR}>Disaster Recovery</option>
              </select>
              <span className="form-hint">Where is the issue occurring?</span>
            </div>

            <div className="form-group">
              <label htmlFor="affected_service">Affected Service</label>
              <input
                id="affected_service"
                type="text"
                placeholder="e.g., Web Application, API, Database"
                {...register('affected_service')}
              />
              <span className="form-hint">Which service is impacted?</span>
            </div>
          </div>
        </div>

        {/* Assignment */}
        <div className="form-section">
          <h2>Assignment</h2>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="assigned_to">Assign To</label>
              <select id="assigned_to" {...register('assigned_to')} disabled={loadingUsers}>
                <option value="">-- Unassigned --</option>
                {loadingUsers ? (
                  <option disabled>Loading users...</option>
                ) : (
                  assignableUsers.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.full_name || `${user.first_name} ${user.last_name}`.trim() || user.username}
                      {' '}({user.role.replace('_', ' ')})
                      {user.department ? ` - ${user.department}` : ''}
                    </option>
                  ))
                )}
              </select>
              <span className="form-hint">
                {loadingUsers
                  ? 'Loading assignable users...'
                  : assignableUsers.length > 0
                    ? `${assignableUsers.length} engineers/managers available`
                    : 'Only engineers, team leads, managers, and admins can be assigned'}
              </span>
            </div>

            <div className="form-group">
              <label htmlFor="assigned_team">Assign Team</label>
              <input
                id="assigned_team"
                type="text"
                placeholder="e.g., DevOps, Support, Engineering"
                {...register('assigned_team')}
              />
              <span className="form-hint">Optional: Assign to a specific team</span>
            </div>
          </div>
        </div>

        {/* Tags */}
        <div className="form-section">
          <h2>Tags</h2>

          <div className="form-group">
            <label htmlFor="tag-input">Add Tags (Optional)</label>
            <div className="tag-input-container">
              <input
                id="tag-input"
                type="text"
                placeholder="e.g., production, urgent, network"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleAddTag()
                  }
                }}
              />
              <button
                type="button"
                className="btn-secondary"
                onClick={handleAddTag}
                disabled={!tagInput.trim() || tags.length >= 10}
              >
                Add Tag
              </button>
            </div>
            {errors.tags && <span className="error-message">{errors.tags.message}</span>}
            <span className="form-hint">Use lowercase letters, numbers, hyphens, and underscores only (max 10 tags)</span>

            {tags.length > 0 && (
              <div className="tags-list">
                {tags.map((tag, index) => (
                  <span key={index} className="tag">
                    {tag}
                    <button
                      type="button"
                      className="tag-remove"
                      onClick={() => handleRemoveTag(tag)}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Form Actions */}
        <div className="form-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={handleCancel}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="button"
            className="btn-outline"
            onClick={() => reset()}
            disabled={loading}
          >
            Reset Form
          </button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <>
                <div className="spinner-small"></div>
                Creating...
              </>
            ) : (
              <>
                <Save size={18} />
                Create Ticket
              </>
            )}
          </button>
        </div>
      </form>
    </div>
    </DashboardLayout>
  )
}

export default CreateTicketPage
