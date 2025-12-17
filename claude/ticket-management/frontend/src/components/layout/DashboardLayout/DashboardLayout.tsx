import { ReactNode, useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAppSelector, useAppDispatch } from '@/store/hooks'
import { logoutAsync } from '@/store/slices/authSlice'
import { UserRole } from '@/types/auth.types'
import toast from 'react-hot-toast'
import './DashboardLayout.css'

interface DashboardLayoutProps {
  children: ReactNode
}

interface NavItem {
  label: string
  path: string
  icon: string
  roles?: UserRole[]
}

/**
 * Dashboard Layout Component
 *
 * Provides consistent layout for all dashboard pages with:
 * - Sidebar navigation
 * - Top header with user menu
 * - Mobile responsive menu
 * - Role-based navigation items
 */
const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((state) => state.auth)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  // Navigation items based on user role
  const navItems: NavItem[] = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      icon: '📊',
      roles: undefined, // All roles
    },
    {
      label: 'Tickets',
      path: '/tickets',
      icon: '🎫',
      roles: undefined,
    },
    {
      label: 'My Tickets',
      path: '/tickets/my-tickets',
      icon: '📋',
      roles: ['END_USER', 'DEVOPS_ENGINEER', 'SENIOR_ENGINEER'],
    },
    {
      label: 'Users',
      path: '/users',
      icon: '👥',
      roles: ['ADMIN', 'MANAGER', 'TEAM_LEAD'],
    },
    {
      label: 'Reports',
      path: '/reports',
      icon: '📈',
      roles: ['ADMIN', 'MANAGER', 'TEAM_LEAD'],
    },
    {
      label: 'Audit Logs',
      path: '/audit-logs',
      icon: '📜',
      roles: ['ADMIN'],
    },
    {
      label: 'Settings',
      path: '/settings',
      icon: '⚙️',
      roles: ['ADMIN'],
    },
  ]

  // Filter nav items based on user role
  const visibleNavItems = navItems.filter((item) => {
    if (!item.roles) return true // Show to all roles
    return user && item.roles.includes(user.role)
  })

  const handleLogout = async () => {
    try {
      await dispatch(logoutAsync()).unwrap()
      toast.success('Logged out successfully', {
        icon: '👋',
        duration: 2000,
      })
      navigate('/login')
    } catch (error) {
      // Still navigate to login even if logout API fails
      navigate('/login')
    }
  }

  const getRoleBadgeColor = (role: UserRole): string => {
    const colors: Record<UserRole, string> = {
      ADMIN: 'role-badge-admin',
      MANAGER: 'role-badge-manager',
      TEAM_LEAD: 'role-badge-team-lead',
      SENIOR_ENGINEER: 'role-badge-senior',
      DEVOPS_ENGINEER: 'role-badge-devops',
      END_USER: 'role-badge-user',
    }
    return colors[role] || 'role-badge-user'
  }

  const getRoleLabel = (role: UserRole): string => {
    const labels: Record<UserRole, string> = {
      ADMIN: 'Admin',
      MANAGER: 'Manager',
      TEAM_LEAD: 'Team Lead',
      SENIOR_ENGINEER: 'Senior Engineer',
      DEVOPS_ENGINEER: 'DevOps Engineer',
      END_USER: 'User',
    }
    return labels[role] || role
  }

  if (!user) return null

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        {/* Logo */}
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="logo-icon">🎫</span>
            <span className="logo-text">TicketMS</span>
          </div>
          <button
            className="sidebar-close-btn"
            onClick={() => setSidebarOpen(false)}
          >
            ✕
          </button>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {visibleNavItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${
                location.pathname === item.path ? 'nav-item-active' : ''
              }`}
              onClick={() => setSidebarOpen(false)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User Info in Sidebar (Mobile) */}
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="user-avatar">
              {user.first_name[0]}
              {user.last_name[0]}
            </div>
            <div className="user-info">
              <p className="user-name">
                {user.first_name} {user.last_name}
              </p>
              <p className={`user-role ${getRoleBadgeColor(user.role)}`}>
                {getRoleLabel(user.role)}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Top Header */}
        <header className="top-header">
          {/* Mobile Menu Button */}
          <button
            className="mobile-menu-btn"
            onClick={() => setSidebarOpen(true)}
          >
            ☰
          </button>

          {/* Page Title */}
          <div className="header-title">
            <h1>Ticket Management System</h1>
          </div>

          {/* User Menu */}
          <div className="header-user">
            <button
              className="user-menu-btn"
              onClick={() => setUserMenuOpen(!userMenuOpen)}
            >
              <div className="user-avatar-small">
                {user.first_name[0]}
                {user.last_name[0]}
              </div>
              <span className="user-name-header">
                {user.first_name} {user.last_name}
              </span>
              <span className="dropdown-arrow">▼</span>
            </button>

            {/* Dropdown Menu */}
            {userMenuOpen && (
              <>
                <div
                  className="user-menu-overlay"
                  onClick={() => setUserMenuOpen(false)}
                ></div>
                <div className="user-menu-dropdown">
                  <div className="user-menu-header">
                    <p className="user-menu-name">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="user-menu-email">{user.email}</p>
                    <span className={`user-menu-role ${getRoleBadgeColor(user.role)}`}>
                      {getRoleLabel(user.role)}
                    </span>
                  </div>

                  <div className="user-menu-items">
                    <Link
                      to="/profile"
                      className="user-menu-item"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <span>👤</span>
                      <span>My Profile</span>
                    </Link>
                    <Link
                      to="/settings/account"
                      className="user-menu-item"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <span>⚙️</span>
                      <span>Account Settings</span>
                    </Link>
                    <Link
                      to="/settings/security"
                      className="user-menu-item"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <span>🔒</span>
                      <span>Security</span>
                    </Link>
                    <hr className="user-menu-divider" />
                    <button
                      className="user-menu-item user-menu-logout"
                      onClick={handleLogout}
                    >
                      <span>🚪</span>
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">{children}</main>
      </div>
    </div>
  )
}

export default DashboardLayout
