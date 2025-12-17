/**
 * Login page.
 */
import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import LoginForm from '../components/auth/LoginForm'

export default function LoginPage() {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return <Navigate to="/users" replace />
  }

  return (
    <div className="page-container">
      <LoginForm />
    </div>
  )
}
