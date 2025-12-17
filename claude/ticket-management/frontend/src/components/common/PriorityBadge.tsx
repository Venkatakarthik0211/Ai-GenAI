/**
 * PriorityBadge Component
 * Displays ticket priority with appropriate styling
 */

import { FC } from 'react'
import { TicketPriority } from '@/types/ticket.types'
import './Badge.css'

interface PriorityBadgeProps {
  priority: TicketPriority
  size?: 'sm' | 'md' | 'lg'
}

const PRIORITY_CONFIG = {
  [TicketPriority.P1]: { label: 'P1 - Critical', className: 'priority-p1' },
  [TicketPriority.P2]: { label: 'P2 - High', className: 'priority-p2' },
  [TicketPriority.P3]: { label: 'P3 - Medium', className: 'priority-p3' },
  [TicketPriority.P4]: { label: 'P4 - Low', className: 'priority-p4' },
}

export const PriorityBadge: FC<PriorityBadgeProps> = ({ priority, size = 'md' }) => {
  const config = PRIORITY_CONFIG[priority]

  return (
    <span className={`badge ${config.className} badge-${size}`}>
      {config.label}
    </span>
  )
}

export default PriorityBadge
