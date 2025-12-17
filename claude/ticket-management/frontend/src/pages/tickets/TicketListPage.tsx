/**
 * TicketListPage Component
 * Displays list of tickets with filtering, sorting, and pagination
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import {
  fetchTickets,
  setFilters,
  setSortOptions,
  setPagination,
  clearFilters
} from '@/store/slices/ticketSlice'
import DashboardLayout from '@/components/layout/DashboardLayout/DashboardLayout'
import StatusBadge from '@/components/common/StatusBadge'
import PriorityBadge from '@/components/common/PriorityBadge'
import { TicketStatus, TicketPriority, TicketCategory } from '@/types/ticket.types'
import { Plus, Search, Filter, X } from 'lucide-react'
import './TicketListPage.css'

const TicketListPage = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { tickets, loading, error, filters, sortOptions, pagination } = useAppSelector(
    state => state.ticket
  )

  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [localFilters, setLocalFilters] = useState<{
    status: TicketStatus[]
    priority: TicketPriority[]
    category: TicketCategory | ''
  }>({
    status: Array.isArray(filters.status) ? filters.status : filters.status ? [filters.status] : [],
    priority: Array.isArray(filters.priority) ? filters.priority : filters.priority ? [filters.priority] : [],
    category: (Array.isArray(filters.category) ? filters.category[0] : filters.category) || '',
  })

  useEffect(() => {
    dispatch(fetchTickets({
      ...filters,
      ...sortOptions,
      page: pagination.page,
      page_size: pagination.pageSize,
    }))
  }, [dispatch, filters, sortOptions, pagination.page, pagination.pageSize])

  const handleSearch = () => {
    dispatch(setFilters({ ...filters, search: searchTerm }))
  }

  const handleApplyFilters = () => {
    dispatch(setFilters({
      ...filters,
      status: localFilters.status.length > 0 ? localFilters.status : undefined,
      priority: localFilters.priority.length > 0 ? localFilters.priority : undefined,
      category: localFilters.category !== '' ? localFilters.category : undefined,
    }))
    setShowFilters(false)
  }

  const handleClearFilters = () => {
    setLocalFilters({ status: [], priority: [], category: '' })
    setSearchTerm('')
    dispatch(clearFilters())
  }

  const handleSort = (field: string) => {
    const newOrder = sortOptions.sort_by === field && sortOptions.order === 'asc' ? 'desc' : 'asc'
    dispatch(setSortOptions({ sort_by: field as any, order: newOrder }))
  }

  const handlePageChange = (newPage: number) => {
    dispatch(setPagination({ page: newPage }))
  }

  const handleTicketClick = (ticketId: string) => {
    navigate(`/tickets/${ticketId}`)
  }

  const handleCreateTicket = () => {
    navigate('/tickets/create')
  }

  const toggleStatusFilter = (status: TicketStatus) => {
    setLocalFilters(prev => ({
      ...prev,
      status: prev.status.includes(status)
        ? prev.status.filter(s => s !== status)
        : [...prev.status, status]
    }))
  }

  const togglePriorityFilter = (priority: TicketPriority) => {
    setLocalFilters(prev => ({
      ...prev,
      priority: prev.priority.includes(priority)
        ? prev.priority.filter(p => p !== priority)
        : [...prev.priority, priority]
    }))
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="ticket-list-page">
          <div className="error-message">
            <p>Error loading tickets: {error}</p>
            <button onClick={() => dispatch(fetchTickets({}))}>Retry</button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="ticket-list-page">
      {/* Header */}
      <div className="page-header">
        <h1>Tickets</h1>
        <button className="btn-primary" onClick={handleCreateTicket}>
          <Plus size={20} />
          Create Ticket
        </button>
      </div>

      {/* Search and Filters Bar */}
      <div className="toolbar">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search tickets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>
            <Search size={18} />
          </button>
        </div>

        <div className="toolbar-actions">
          <button
            className={`btn-filter ${showFilters ? 'active' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={18} />
            Filters
            {(filters.status?.length || filters.priority?.length || filters.category) && (
              <span className="filter-badge">
                {(filters.status?.length || 0) + (filters.priority?.length || 0) + (filters.category ? 1 : 0)}
              </span>
            )}
          </button>

          {(filters.status?.length || filters.priority?.length || filters.category || searchTerm) && (
            <button className="btn-clear" onClick={handleClearFilters}>
              <X size={18} />
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filter-section">
            <h3>Status</h3>
            <div className="filter-options">
              {Object.values(TicketStatus).map(status => (
                <label key={status} className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={localFilters.status.includes(status)}
                    onChange={() => toggleStatusFilter(status)}
                  />
                  <StatusBadge status={status} size="sm" />
                </label>
              ))}
            </div>
          </div>

          <div className="filter-section">
            <h3>Priority</h3>
            <div className="filter-options">
              {Object.values(TicketPriority).map(priority => (
                <label key={priority} className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={localFilters.priority.includes(priority)}
                    onChange={() => togglePriorityFilter(priority)}
                  />
                  <PriorityBadge priority={priority} size="sm" />
                </label>
              ))}
            </div>
          </div>

          <div className="filter-section">
            <h3>Category</h3>
            <select
              value={localFilters.category}
              onChange={(e) => setLocalFilters(prev => ({ ...prev, category: e.target.value as TicketCategory | '' }))}
            >
              <option value="">All Categories</option>
              {Object.values(TicketCategory).map(category => (
                <option key={category} value={category}>
                  {category.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-actions">
            <button className="btn-secondary" onClick={() => setShowFilters(false)}>
              Cancel
            </button>
            <button className="btn-primary" onClick={handleApplyFilters}>
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {/* Tickets Table */}
      <div className="tickets-table-container">
        {loading ? (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading tickets...</p>
          </div>
        ) : tickets.length === 0 ? (
          <div className="empty-state">
            <p>No tickets found</p>
            <button className="btn-primary" onClick={handleCreateTicket}>
              Create your first ticket
            </button>
          </div>
        ) : (
          <>
            <table className="tickets-table">
              <thead>
                <tr>
                  <th>
                    Ticket #
                  </th>
                  <th>
                    Title
                  </th>
                  <th onClick={() => handleSort('status')} className="sortable">
                    Status
                    {sortOptions.sort_by === 'status' && (
                      <span className="sort-indicator">{sortOptions.order === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th onClick={() => handleSort('priority')} className="sortable">
                    Priority
                    {sortOptions.sort_by === 'priority' && (
                      <span className="sort-indicator">{sortOptions.order === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                  <th>Category</th>
                  <th>Assigned To</th>
                  <th onClick={() => handleSort('created_at')} className="sortable">
                    Created
                    {sortOptions.sort_by === 'created_at' && (
                      <span className="sort-indicator">{sortOptions.order === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </th>
                </tr>
              </thead>
              <tbody>
                {tickets.map(ticket => (
                  <tr
                    key={ticket.id}
                    onClick={() => handleTicketClick(ticket.id)}
                    className="ticket-row"
                  >
                    <td className="ticket-number">{ticket.ticket_number}</td>
                    <td className="ticket-title">{ticket.title}</td>
                    <td>
                      <StatusBadge status={ticket.status as TicketStatus} size="sm" />
                    </td>
                    <td>
                      <PriorityBadge priority={ticket.priority as TicketPriority} size="sm" />
                    </td>
                    <td className="ticket-category">
                      {ticket.category.replace(/_/g, ' ')}
                    </td>
                    <td className="ticket-assignee">
                      {ticket.assigned_to || <span className="unassigned">Unassigned</span>}
                    </td>
                    <td className="ticket-date">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="pagination">
              <div className="pagination-info">
                Showing {(pagination.page - 1) * pagination.pageSize + 1} to{' '}
                {Math.min(pagination.page * pagination.pageSize, pagination.total)} of{' '}
                {pagination.total} tickets
              </div>
              <div className="pagination-controls">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page === 1}
                  className="btn-page"
                >
                  Previous
                </button>

                {Array.from({ length: pagination.totalPages }, (_, i) => i + 1)
                  .filter(page => {
                    // Show first, last, current, and adjacent pages
                    return (
                      page === 1 ||
                      page === pagination.totalPages ||
                      Math.abs(page - pagination.page) <= 1
                    )
                  })
                  .map((page, index, array) => {
                    // Add ellipsis
                    const prevPage = array[index - 1]
                    const showEllipsis = prevPage && page - prevPage > 1

                    return (
                      <div key={page} style={{ display: 'flex', alignItems: 'center' }}>
                        {showEllipsis && <span className="pagination-ellipsis">...</span>}
                        <button
                          onClick={() => handlePageChange(page)}
                          className={`btn-page ${page === pagination.page ? 'active' : ''}`}
                        >
                          {page}
                        </button>
                      </div>
                    )
                  })}

                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page === pagination.totalPages}
                  className="btn-page"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
    </DashboardLayout>
  )
}

export default TicketListPage
