import { ReactNode, useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAppSelector, useAppDispatch } from '@/store/hooks'
import { getCurrentUserAsync } from '@/store/slices/authSlice'
import { UserRole } from '@/types/auth.types'
import './ProtectedRoute.css'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRoles?: UserRole[]
}

/**
 * Protected Route Component
 *
 * Handles authentication and role-based authorization
 *
 * Features:
 * - Redirects to login if not authenticated
 * - Checks if user has required role(s)
 * - Fetches current user if authenticated but user data missing
 * - Shows loading state while checking auth
 *
 * @param children - Component to render if authorized
 * @param requiredRoles - Optional array of roles that can access this route
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles
}) => {
  const location = useLocation()
  const dispatch = useAppDispatch()
  const { isAuthenticated, user, loading, access_token } = useAppSelector(
    (state) => state.auth
  )

  // If we have a token but no user data, fetch the user
  useEffect(() => {
    if (access_token && !user && !loading) {
      dispatch(getCurrentUserAsync())
    }
  }, [access_token, user, loading, dispatch])

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="auth-loading-container">
        <div className="auth-loading-spinner"></div>
        <p>Verifying authentication...</p>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !access_token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Wait for user data to load
  if (!user) {
    return (
      <div className="auth-loading-container">
        <div className="auth-loading-spinner"></div>
        <p>Loading user data...</p>
      </div>
    )
  }

  // Check role-based access if requiredRoles specified
  if (requiredRoles && requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.includes(user.role)

    if (!hasRequiredRole) {
      // User doesn't have required role - redirect to their dashboard
      return <Navigate to="/dashboard" replace />
    }
  }

  // User is authenticated and authorized
  return <>{children}</>
}

export default ProtectedRoute
