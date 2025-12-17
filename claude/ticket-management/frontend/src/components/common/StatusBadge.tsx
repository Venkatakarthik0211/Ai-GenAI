/**
 * StatusBadge Component
 * Displays ticket status with appropriate styling
 */

import { FC } from 'react'
import { TicketStatus } from '@/types/ticket.types'
import './Badge.css'

interface StatusBadgeProps {
  status: TicketStatus
  size?: 'sm' | 'md' | 'lg'
}

const STATUS_CONFIG = {
  [TicketStatus.NEW]: { label: 'New', className: 'status-new' },
  [TicketStatus.OPEN]: { label: 'Open', className: 'status-open' },
  [TicketStatus.IN_PROGRESS]: { label: 'In Progress', className: 'status-in-progress' },
  [TicketStatus.PENDING_INFO]: { label: 'Pending Info', className: 'status-pending' },
  [TicketStatus.RESOLVED]: { label: 'Resolved', className: 'status-resolved' },
  [TicketStatus.CLOSED]: { label: 'Closed', className: 'status-closed' },
  [TicketStatus.REOPENED]: { label: 'Reopened', className: 'status-reopened' },
  [TicketStatus.ESCALATED]: { label: 'Escalated', className: 'status-escalated' },
}

export const StatusBadge: FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const config = STATUS_CONFIG[status]

  return (
    <span className={`badge ${config.className} badge-${size}`}>
      {config.label}
    </span>
  )
}

export default StatusBadge
