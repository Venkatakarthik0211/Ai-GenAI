/**
 * User detail component.
 */
import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User } from '../../types/user'
import { useAuth } from '../../contexts/AuthContext'
import { useDeleteUser } from '../../hooks/useUsers'

interface UserDetailProps {
  user: User
}

export default function UserDetail({ user }: UserDetailProps) {
  const { user: currentUser } = useAuth()
  const navigate = useNavigate()
  const deleteMutation = useDeleteUser()

  const canEdit = currentUser?.is_superuser || currentUser?.id === user.id
  const canDelete = currentUser?.is_superuser && currentUser.id !== user.id

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await deleteMutation.mutateAsync({ userId: user.id, permanent: false })
        navigate('/users')
      } catch (error) {
        // Error handled by mutation
      }
    }
  }

  return (
    <div className="user-detail-container">
      <div className="user-detail-header">
        <h2>User Details</h2>
        <div className="user-detail-actions">
          {canEdit && (
            <Link to={`/users/${user.id}/edit`} className="btn btn-primary">
              Edit Profile
            </Link>
          )}
          {canDelete && (
            <button
              onClick={handleDelete}
              className="btn btn-danger"
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete User'}
            </button>
          )}
          <Link to="/users" className="btn btn-secondary">
            Back to List
          </Link>
        </div>
      </div>

      <div className="user-detail-card">
        <div className="user-detail-avatar">
          <div className="avatar-circle">
            {user.full_name.charAt(0).toUpperCase()}
          </div>
        </div>

        <div className="user-detail-info">
          <div className="info-row">
            <div className="info-label">Full Name</div>
            <div className="info-value">{user.full_name}</div>
          </div>

          <div className="info-row">
            <div className="info-label">Username</div>
            <div className="info-value">{user.username}</div>
          </div>

          <div className="info-row">
            <div className="info-label">Email</div>
            <div className="info-value">{user.email}</div>
          </div>

          <div className="info-row">
            <div className="info-label">Status</div>
            <div className="info-value">
              <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          <div className="info-row">
            <div className="info-label">Role</div>
            <div className="info-value">
              {user.is_superuser ? (
                <span className="badge badge-primary">Admin</span>
              ) : (
                <span className="badge badge-secondary">User</span>
              )}
            </div>
          </div>

          {user.bio && (
            <div className="info-row">
              <div className="info-label">Bio</div>
              <div className="info-value">{user.bio}</div>
            </div>
          )}

          <div className="info-row">
            <div className="info-label">Created At</div>
            <div className="info-value">
              {new Date(user.created_at).toLocaleString()}
            </div>
          </div>

          <div className="info-row">
            <div className="info-label">Last Updated</div>
            <div className="info-value">
              {new Date(user.updated_at).toLocaleString()}
            </div>
          </div>

          {user.last_login && (
            <div className="info-row">
              <div className="info-label">Last Login</div>
              <div className="info-value">
                {new Date(user.last_login).toLocaleString()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
