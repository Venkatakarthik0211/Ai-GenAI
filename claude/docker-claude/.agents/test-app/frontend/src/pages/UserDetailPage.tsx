/**
 * User detail page.
 */
import React from 'react'
import { useParams } from 'react-router-dom'
import { useGetUser } from '../hooks/useUsers'
import UserDetail from '../components/users/UserDetail'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorMessage from '../components/common/ErrorMessage'

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: user, isLoading, error, refetch } = useGetUser(id!)

  if (isLoading) {
    return (
      <div className="page-container">
        <LoadingSpinner size="large" message="Loading user..." />
      </div>
    )
  }

  if (error || !user) {
    return (
      <div className="page-container">
        <ErrorMessage
          message="Failed to load user details"
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return (
    <div className="page-container">
      <UserDetail user={user} />
    </div>
  )
}
