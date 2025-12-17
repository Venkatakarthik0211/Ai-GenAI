import { useAppSelector } from '@/store/hooks'
import './Dashboard.css'

/**
 * Manager/Team Lead Dashboard
 * Team performance metrics and ticket overview
 */
const ManagerDashboard: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth)

  // Mock data - replace with actual API calls
  const stats = {
    teamMembers: 12,
    activeTickets: 45,
    completedThisWeek: 78,
    avgResponseTime: '2.5h',
  }

  const teamMembers = [
    { name: 'John Doe', role: 'DevOps Engineer', active: 5, completed: 23, status: 'online' },
    { name: 'Jane Smith', role: 'Senior Engineer', active: 3, completed: 31, status: 'online' },
    { name: 'Mike Johnson', role: 'Engineer', active: 4, completed: 18, status: 'away' },
    { name: 'Sarah Williams', role: 'Engineer', active: 2, completed: 15, status: 'offline' },
  ]

  const recentTickets = [
    { id: '#1234', title: 'Server downtime issue', priority: 'High', assignee: 'John Doe', status: 'In Progress' },
    { id: '#1233', title: 'Database optimization', priority: 'Medium', assignee: 'Jane Smith', status: 'Review' },
    { id: '#1232', title: 'API endpoint error', priority: 'High', assignee: 'Mike Johnson', status: 'Open' },
    { id: '#1231', title: 'UI bug fix', priority: 'Low', assignee: 'Sarah Williams', status: 'Testing' },
  ]

  const getPriorityClass = (priority: string) => {
    const classes = {
      High: 'priority-high',
      Medium: 'priority-medium',
      Low: 'priority-low',
    }
    return classes[priority as keyof typeof classes] || 'priority-medium'
  }

  const getStatusClass = (status: string) => {
    const classes = {
      online: 'status-online',
      away: 'status-away',
      offline: 'status-offline',
    }
    return classes[status as keyof typeof classes] || 'status-offline'
  }

  return (
    <div className="dashboard-container">
      {/* Welcome Section */}
      <div className="dashboard-welcome">
        <div>
          <h1 className="dashboard-title">Welcome back, {user?.first_name}!</h1>
          <p className="dashboard-subtitle">
            Manage your team and track performance
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
        <div className="stat-card stat-card-blue">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <p className="stat-label">Team Members</p>
            <p className="stat-value">{stats.teamMembers}</p>
            <p className="stat-change positive">All active</p>
          </div>
        </div>

        <div className="stat-card stat-card-orange">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <p className="stat-label">Active Tickets</p>
            <p className="stat-value">{stats.activeTickets}</p>
            <p className="stat-change negative">+3 from yesterday</p>
          </div>
        </div>

        <div className="stat-card stat-card-green">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <p className="stat-label">Completed This Week</p>
            <p className="stat-value">{stats.completedThisWeek}</p>
            <p className="stat-change positive">+15% from last week</p>
          </div>
        </div>

        <div className="stat-card stat-card-purple">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <p className="stat-label">Avg Response Time</p>
            <p className="stat-value">{stats.avgResponseTime}</p>
            <p className="stat-change positive">20% faster</p>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="dashboard-grid">
        {/* Team Members */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Team Performance</h2>
            <button className="card-action-btn">View All</button>
          </div>
          <div className="team-list">
            {teamMembers.map((member, index) => (
              <div key={index} className="team-member-item">
                <div className="team-member-avatar">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="team-member-info">
                  <div className="team-member-header">
                    <p className="team-member-name">{member.name}</p>
                    <span className={`team-member-status ${getStatusClass(member.status)}`}>
                      {member.status}
                    </span>
                  </div>
                  <p className="team-member-role">{member.role}</p>
                  <div className="team-member-stats">
                    <span>Active: {member.active}</span>
                    <span>•</span>
                    <span>Completed: {member.completed}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Tickets */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Recent Tickets</h2>
            <button className="card-action-btn">View All</button>
          </div>
          <div className="ticket-list">
            {recentTickets.map((ticket) => (
              <div key={ticket.id} className="ticket-item">
                <div className="ticket-header">
                  <span className="ticket-id">{ticket.id}</span>
                  <span className={`ticket-priority ${getPriorityClass(ticket.priority)}`}>
                    {ticket.priority}
                  </span>
                </div>
                <p className="ticket-title-text">{ticket.title}</p>
                <div className="ticket-footer">
                  <span className="ticket-assignee">👤 {ticket.assignee}</span>
                  <span className="ticket-status">{ticket.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Performance Chart Placeholder */}
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">Team Performance Trend</h2>
          <div className="chart-controls">
            <button className="chart-control-btn active">Week</button>
            <button className="chart-control-btn">Month</button>
            <button className="chart-control-btn">Year</button>
          </div>
        </div>
        <div className="chart-placeholder">
          <div className="chart-bars">
            <div className="chart-bar" style={{ height: '60%' }}>
              <div className="chart-bar-fill"></div>
              <span className="chart-bar-label">Mon</span>
            </div>
            <div className="chart-bar" style={{ height: '75%' }}>
              <div className="chart-bar-fill"></div>
              <span className="chart-bar-label">Tue</span>
            </div>
            <div className="chart-bar" style={{ height: '85%' }}>
              <div className="chart-bar-fill"></div>
              <span className="chart-bar-label">Wed</span>
            </div>
            <div className="chart-bar" style={{ height: '70%' }}>
              <div className="chart-bar-fill"></div>
              <span className="chart-bar-label">Thu</span>
            </div>
            <div className="chart-bar" style={{ height: '90%' }}>
              <div className="chart-bar-fill"></div>
              <span className="chart-bar-label">Fri</span>
            </div>
            <div className="chart-bar" style={{ height: '40%' }}>
              <div className="chart-bar-fill chart-bar-weekend"></div>
              <span className="chart-bar-label">Sat</span>
            </div>
            <div className="chart-bar" style={{ height: '30%' }}>
              <div className="chart-bar-fill chart-bar-weekend"></div>
              <span className="chart-bar-label">Sun</span>
            </div>
          </div>
          <p className="chart-description">Tickets completed per day</p>
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
            <span>Create Ticket</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>📊</span>
            <span>Generate Report</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>👥</span>
            <span>Manage Team</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>⚙️</span>
            <span>Settings</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ManagerDashboard
