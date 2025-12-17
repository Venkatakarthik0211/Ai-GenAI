/**
 * User create/edit page.
 */
import React from 'react'
import { useParams } from 'react-router-dom'
import { useGetUser } from '../hooks/useUsers'
import UserForm from '../components/users/UserForm'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorMessage from '../components/common/ErrorMessage'

export default function UserFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEditMode = !!id

  const { data: user, isLoading, error, refetch } = useGetUser(id!, {
    enabled: isEditMode,
  })

  if (isEditMode && isLoading) {
    return (
      <div className="page-container">
        <LoadingSpinner size="large" message="Loading user..." />
      </div>
    )
  }

  if (isEditMode && (error || !user)) {
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
      <UserForm user={user} mode={isEditMode ? 'edit' : 'create'} />
    </div>
  )
}
