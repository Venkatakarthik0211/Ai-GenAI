import { useAppSelector } from '@/store/hooks'
import './Dashboard.css'

/**
 * Admin Dashboard
 * Full system overview with user management, system stats, and audit logs
 */
const AdminDashboard: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth)

  // Mock data - replace with actual API calls
  const stats = {
    totalUsers: 1247,
    activeUsers: 892,
    totalTickets: 3456,
    openTickets: 234,
    closedToday: 45,
    avgResolutionTime: '4.2h',
  }

  const recentActivity = [
    { id: 1, user: 'John Doe', action: 'Created ticket #1234', time: '5 min ago' },
    { id: 2, user: 'Jane Smith', action: 'Closed ticket #1233', time: '12 min ago' },
    { id: 3, user: 'Admin', action: 'Updated user permissions', time: '25 min ago' },
    { id: 4, user: 'System', action: 'Backup completed', time: '1 hour ago' },
  ]

  const topUsers = [
    { name: 'John Doe', tickets: 89, resolved: 87, rating: 4.9 },
    { name: 'Jane Smith', tickets: 76, resolved: 74, rating: 4.8 },
    { name: 'Mike Johnson', tickets: 65, resolved: 63, rating: 4.7 },
  ]

  return (
    <div className="dashboard-container">
      {/* Welcome Section */}
      <div className="dashboard-welcome">
        <div>
          <h1 className="dashboard-title">Welcome back, {user?.first_name}!</h1>
          <p className="dashboard-subtitle">
            Here's what's happening with your system today
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
            <p className="stat-label">Total Users</p>
            <p className="stat-value">{stats.totalUsers.toLocaleString()}</p>
            <p className="stat-change positive">+12% from last month</p>
          </div>
        </div>

        <div className="stat-card stat-card-green">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <p className="stat-label">Active Users</p>
            <p className="stat-value">{stats.activeUsers.toLocaleString()}</p>
            <p className="stat-change positive">{((stats.activeUsers / stats.totalUsers) * 100).toFixed(1)}% active</p>
          </div>
        </div>

        <div className="stat-card stat-card-purple">
          <div className="stat-icon">🎫</div>
          <div className="stat-content">
            <p className="stat-label">Total Tickets</p>
            <p className="stat-value">{stats.totalTickets.toLocaleString()}</p>
            <p className="stat-change positive">+8% from last week</p>
          </div>
        </div>

        <div className="stat-card stat-card-orange">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <p className="stat-label">Open Tickets</p>
            <p className="stat-value">{stats.openTickets}</p>
            <p className="stat-change negative">-5% from yesterday</p>
          </div>
        </div>

        <div className="stat-card stat-card-teal">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <p className="stat-label">Closed Today</p>
            <p className="stat-value">{stats.closedToday}</p>
            <p className="stat-change positive">Great progress!</p>
          </div>
        </div>

        <div className="stat-card stat-card-indigo">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <p className="stat-label">Avg Resolution</p>
            <p className="stat-value">{stats.avgResolutionTime}</p>
            <p className="stat-change positive">15% faster</p>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="dashboard-grid">
        {/* Recent Activity */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Recent Activity</h2>
            <button className="card-action-btn">View All</button>
          </div>
          <div className="activity-list">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="activity-item">
                <div className="activity-icon">📍</div>
                <div className="activity-content">
                  <p className="activity-text">
                    <strong>{activity.user}</strong> {activity.action}
                  </p>
                  <p className="activity-time">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Performers */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Top Performers</h2>
            <button className="card-action-btn">View All</button>
          </div>
          <div className="user-list">
            {topUsers.map((user, index) => (
              <div key={index} className="user-item">
                <div className="user-rank">{index + 1}</div>
                <div className="user-details">
                  <p className="user-name-text">{user.name}</p>
                  <p className="user-stats">
                    {user.tickets} tickets • {user.resolved} resolved • ⭐ {user.rating}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="dashboard-card">
        <div className="card-header">
          <h2 className="card-title">System Health</h2>
          <span className="health-badge health-excellent">Excellent</span>
        </div>
        <div className="health-grid">
          <div className="health-item">
            <div className="health-label">API Response Time</div>
            <div className="health-bar">
              <div className="health-bar-fill health-bar-green" style={{ width: '95%' }}></div>
            </div>
            <div className="health-value">45ms (95%)</div>
          </div>
          <div className="health-item">
            <div className="health-label">Database Performance</div>
            <div className="health-bar">
              <div className="health-bar-fill health-bar-green" style={{ width: '92%' }}></div>
            </div>
            <div className="health-value">12ms (92%)</div>
          </div>
          <div className="health-item">
            <div className="health-label">Server CPU Usage</div>
            <div className="health-bar">
              <div className="health-bar-fill health-bar-yellow" style={{ width: '68%' }}></div>
            </div>
            <div className="health-value">68%</div>
          </div>
          <div className="health-item">
            <div className="health-label">Memory Usage</div>
            <div className="health-bar">
              <div className="health-bar-fill health-bar-green" style={{ width: '54%' }}></div>
            </div>
            <div className="health-value">54%</div>
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
            <span>Create User</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>📧</span>
            <span>Send Announcement</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>📊</span>
            <span>Generate Report</span>
          </button>
          <button className="action-button action-button-secondary">
            <span>💾</span>
            <span>Backup System</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
