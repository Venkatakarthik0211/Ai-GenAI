import { useAppSelector } from '@/store/hooks'
import DashboardLayout from '@/components/layout/DashboardLayout/DashboardLayout'
import AdminDashboard from './AdminDashboard'
import ManagerDashboard from './ManagerDashboard'
import UserDashboard from './UserDashboard'

/**
 * Dashboard Page
 * Routes to appropriate dashboard based on user role
 */
const DashboardPage: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth)

  if (!user) return null

  // Route to role-specific dashboard
  const renderDashboard = () => {
    switch (user.role) {
      case 'ADMIN':
        return <AdminDashboard />

      case 'MANAGER':
      case 'TEAM_LEAD':
        return <ManagerDashboard />

      case 'DEVOPS_ENGINEER':
      case 'SENIOR_ENGINEER':
      case 'END_USER':
      default:
        return <UserDashboard />
    }
  }

  return <DashboardLayout>{renderDashboard()}</DashboardLayout>
}

export default DashboardPage
