import { useAppSelector } from '@/store/hooks'
import './Dashboard.css'

/**
 * User Dashboard (END_USER, DEVOPS_ENGINEER, SENIOR_ENGINEER)
 * Personal ticket view and profile overview
 */
const UserDashboard: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth)

  // Mock data - replace with actual API calls
  const stats = {
    myOpenTickets: 8,
    assignedToMe: 5,
    completedThisWeek: 12,
    avgResolutionTime: '3.2h',
  }

  const myTickets = [
    { id: '#1234', title: 'Server downtime issue', priority: 'High', status: 'In Progress', updated: '2 hours ago' },
    { id: '#1233', title: 'Database optimization needed', priority: 'Medium', status: 'Open', updated: '5 hours ago' },
    { id: '#1231', title: 'UI bug in dashboard', priority: 'Low', status: 'Review', updated: '1 day ago' },
    { id: '#1228', title: 'API rate limit issue', priority: 'High', status: 'Testing', updated: '2 days ago' },
  ]

  const recentActivity = [
    { action: 'Updated ticket #1234', time: '2 hours ago', icon: '✏️' },
    { action: 'Commented on ticket #1233', time: '5 hours ago', icon: '💬' },
    { action: 'Closed ticket #1230', time: '1 day ago', icon: '✅' },
    { action: 'Created ticket #1231', time: '2 days ago', icon: '➕' },
  ]

  const getPriorityClass = (priority: string) => {
    const classes = {
      High: 'priority-high',
      Medium: 'priority-medium',
      Low: 'priority-low',
    }
    return classes[priority as keyof typeof classes] || 'priority-medium'
  }

  const getStatusBadgeClass = (status: string) => {
    const classes = {
      'Open': 'status-badge-open',
      'In Progress': 'status-badge-progress',
      'Review': 'status-badge-review',
      'Testing': 'status-badge-testing',
      'Closed': 'status-badge-closed',
    }
    return classes[status as keyof typeof classes] || 'status-badge-open'
  }

  return (
    <div className="dashboard-container">
      {/* Welcome Section */}
      <div className="dashboard-welcome">
        <div>
          <h1 className="dashboard-title">Welcome back, {user?.first_name}!</h1>
          <p className="dashboard-subtitle">
            Here's an overview of your tickets and activity
          </p>
        </div>
        <div className="dashboard-date">{new Date().toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })}</div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card stat-card-orange">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <p className="stat-label">My Open Tickets</p>
            <p className="stat-value">{stats.myOpenTickets}</p>
            <p className="stat-change negative">+2 from yesterday</p>
          </div>
        </div>

        <div className="stat-card stat-card-blue">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <p className="stat-label">Assigned to Me</p>
            <p className="stat-value">{stats.assignedToMe}</p>
            <p className="stat-change positive">3 high priority</p>
          </div>
        </div>

        <div className="stat-card stat-card-green">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <p className="stat-label">Completed This Week</p>
            <p className="stat-value">{stats.completedThisWeek}</p>
            <p className="stat-change positive">+25% from last week</p>
          </div>
        </div>

        <div className="stat-card stat-card-purple">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <p className="stat-label">Avg Resolution Time</p>
            <p className="stat-value">{stats.avgResolutionTime}</p>
            <p className="stat-change positive">15% faster</p>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="dashboard-grid">
        {/* My Tickets */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">My Recent Tickets</h2>
            <button className="card-action-btn">View All</button>
          </div>
          <div className="ticket-list">
            {myTickets.map((ticket) => (
              <div key={ticket.id} className="ticket-item">
                <div className="ticket-header">
                  <span className="ticket-id">{ticket.id}</span>
                  <span className={`ticket-priority ${getPriorityClass(ticket.priority)}`}>
                    {ticket.priority}
                  </span>
                </div>
                <p className="ticket-title-text">{ticket.title}</p>
                <div className="ticket-footer">
                  <span className={`ticket-status-badge ${getStatusBadgeClass(ticket.status)}`}>
                    {ticket.status}
                  </span>
                  <span className="ticket-updated">Updated {ticket.updated}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Recent Activity</h2>
            <button className="card-action-btn">View All</button>
          </div>
          <div className="activity-list">
            {recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">{activity.icon}</div>
                <div className="activity-content">
                  <p className="activity-text">{activity.action}</p>
                  <p className="activity-time">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Profile Summary */}
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">My Profile</h2>
          <button className="card-action-btn">Edit Profile</button>
        </div>
        <div className="profile-summary">
          <div className="profile-avatar-large">
            {user?.first_name[0]}{user?.last_name[0]}
          </div>
          <div className="profile-info-grid">
            <div className="profile-info-item">
              <span className="profile-info-label">Name</span>
              <span className="profile-info-value">
                {user?.first_name} {user?.last_name}
              </span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Email</span>
              <span className="profile-info-value">{user?.email}</span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Role</span>
              <span className="profile-info-value">
                {user?.role.replace(/_/g, ' ')}
              </span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Department</span>
              <span className="profile-info-value">
                {user?.department || 'Not specified'}
              </span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Status</span>
              <span className="profile-info-value">
                <span className="status-badge-active">{user?.status}</span>
              </span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Member Since</span>
              <span className="profile-info-value">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">Quick Actions</h2>
        </div>
        <div className="quick-actions">
          <button className="action-button action-button-primary">
            <span>➕</span>
            <span>Create New Ticket</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>🔍</span>
            <span>Search Tickets</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>👤</span>
            <span>Edit Profile</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>🔒</span>
            <span>Change Password</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default UserDashboard
