import { createBrowserRouter, Navigate } from 'react-router-dom'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage'
import DashboardPage from '@/pages/dashboard/DashboardPage'
import TicketListPage from '@/pages/tickets/TicketListPage'
import TicketDetailPage from '@/pages/tickets/TicketDetailPage'
import CreateTicketPage from '@/pages/tickets/CreateTicketPage'
import ProtectedRoute from './ProtectedRoute'

/**
 * Application Router Configuration
 *
 * Uses React Router v6 with createBrowserRouter for data router features
 */
export const router = createBrowserRouter([
  // Root redirect to dashboard if authenticated, else login
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },

  // Authentication Routes (Public)
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPasswordPage />,
  },
  {
    path: '/reset-password',
    element: <ResetPasswordPage />,
  },

  // Protected Routes (Require Authentication)
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/tickets',
    element: (
      <ProtectedRoute>
        <TicketListPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/tickets/create',
    element: (
      <ProtectedRoute>
        <CreateTicketPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/tickets/:id',
    element: (
      <ProtectedRoute>
        <TicketDetailPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/tickets/my-tickets',
    element: (
      <ProtectedRoute>
        <div>My Tickets Page - Coming Soon</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/users',
    element: (
      <ProtectedRoute requiredRoles={['ADMIN', 'MANAGER', 'TEAM_LEAD']}>
        <div>Users Page - Coming Soon</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/reports',
    element: (
      <ProtectedRoute requiredRoles={['ADMIN', 'MANAGER', 'TEAM_LEAD']}>
        <div>Reports Page - Coming Soon</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/audit-logs',
    element: (
      <ProtectedRoute requiredRoles={['ADMIN']}>
        <div>Audit Logs Page - Coming Soon</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings',
    element: (
      <ProtectedRoute requiredRoles={['ADMIN']}>
        <div>Settings Page - Coming Soon</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/profile',
    element: (
      <ProtectedRoute>
        <div>Profile Page - Coming Soon</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/account',
    element: (
      <ProtectedRoute>
        <div>Account Settings - Coming Soon</div>
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings/security',
    element: (
      <ProtectedRoute>
        <div>Security Settings - Coming Soon</div>
      </ProtectedRoute>
    ),
  },

  // Catch-all route - 404
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
])

export default router
