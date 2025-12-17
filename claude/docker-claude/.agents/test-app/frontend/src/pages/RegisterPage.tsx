/**
 * Registration page.
 */
import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import RegisterForm from '../components/auth/RegisterForm'

export default function RegisterPage() {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return <Navigate to="/users" replace />
  }

  return (
    <div className="page-container">
      <RegisterForm />
    </div>
  )
}
