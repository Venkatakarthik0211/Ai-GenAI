/**
 * User list component with pagination and search.
 */
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useGetUsers, useDeleteUser } from '../../hooks/useUsers'
import { useAuth } from '../../contexts/AuthContext'
import LoadingSpinner from '../common/LoadingSpinner'
import ErrorMessage from '../common/ErrorMessage'

export default function UserList() {
  const { user: currentUser } = useAuth()
  const [search, setSearch] = useState('')
  const [skip, setSkip] = useState(0)
  const [limit] = useState(10)
  const [deleteUserId, setDeleteUserId] = useState<string | null>(null)

  const { data, isLoading, error, refetch } = useGetUsers({ skip, limit, search })
  const deleteMutation = useDeleteUser()

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setSkip(0)
    refetch()
  }

  const handleDelete = async (userId: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await deleteMutation.mutateAsync({ userId, permanent: false })
        setDeleteUserId(null)
      } catch (error) {
        // Error handled by mutation
      }
    }
  }

  const handlePageChange = (newSkip: number) => {
    setSkip(newSkip)
  }

  const totalPages = data ? Math.ceil(data.total / limit) : 0
  const currentPage = Math.floor(skip / limit) + 1

  if (isLoading) {
    return <LoadingSpinner size="large" message="Loading users..." />
  }

  if (error) {
    return (
      <ErrorMessage
        message="Failed to load users"
        onRetry={() => refetch()}
      />
    )
  }

  return (
    <div className="user-list-container">
      <div className="user-list-header">
        <h2>Users</h2>
        {currentUser?.is_superuser && (
          <Link to="/users/new" className="btn btn-primary">
            + Add User
          </Link>
        )}
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Search by name, email, or username..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="btn btn-secondary">
          Search
        </button>
      </form>

      {data && data.users.length === 0 ? (
        <div className="empty-state">
          <p>No users found</p>
        </div>
      ) : (
        <>
          <div className="user-table-wrapper">
            <table className="user-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Username</th>
                  <th>Status</th>
                  <th>Role</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.full_name}</td>
                    <td>{user.email}</td>
                    <td>{user.username}</td>
                    <td>
                      <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      {user.is_superuser ? (
                        <span className="badge badge-primary">Admin</span>
                      ) : (
                        <span className="badge badge-secondary">User</span>
                      )}
                    </td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                    <td className="actions-cell">
                      <Link to={`/users/${user.id}`} className="btn btn-sm btn-info">
                        View
                      </Link>
                      {(currentUser?.is_superuser || currentUser?.id === user.id) && (
                        <Link to={`/users/${user.id}/edit`} className="btn btn-sm btn-warning">
                          Edit
                        </Link>
                      )}
                      {currentUser?.is_superuser && currentUser.id !== user.id && (
                        <button
                          onClick={() => handleDelete(user.id)}
                          className="btn btn-sm btn-danger"
                          disabled={deleteMutation.isPending && deleteUserId === user.id}
                        >
                          {deleteMutation.isPending && deleteUserId === user.id ? 'Deleting...' : 'Delete'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => handlePageChange(skip - limit)}
                disabled={skip === 0}
                className="btn btn-secondary btn-sm"
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {currentPage} of {totalPages} ({data?.total} total users)
              </span>
              <button
                onClick={() => handlePageChange(skip + limit)}
                disabled={skip + limit >= (data?.total || 0)}
                className="btn btn-secondary btn-sm"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
