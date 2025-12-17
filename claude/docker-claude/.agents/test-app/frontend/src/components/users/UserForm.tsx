/**
 * User create/edit form component.
 */
import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate } from 'react-router-dom'
import { userSchema, UserFormData } from '../../utils/validators'
import { useCreateUser, useUpdateUser } from '../../hooks/useUsers'
import { User } from '../../types/user'

interface UserFormProps {
  user?: User
  mode: 'create' | 'edit'
}

export default function UserForm({ user, mode }: UserFormProps) {
  const navigate = useNavigate()
  const createMutation = useCreateUser()
  const updateMutation = useUpdateUser()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: user
      ? {
          email: user.email,
          username: user.username,
          full_name: user.full_name,
          bio: user.bio || '',
          password: '',
        }
      : undefined,
  })

  const onSubmit = async (data: UserFormData) => {
    try {
      if (mode === 'create') {
        if (!data.password) {
          throw new Error('Password is required for new users')
        }
        await createMutation.mutateAsync({
          ...data,
          password: data.password,
          bio: data.bio || undefined,
        })
      } else if (user) {
        const updateData: any = {
          email: data.email,
          username: data.username,
          full_name: data.full_name,
          bio: data.bio || undefined,
        }
        if (data.password) {
          updateData.password = data.password
        }
        await updateMutation.mutateAsync({
          userId: user.id,
          userData: updateData,
        })
      }
      navigate('/users')
    } catch (error) {
      // Error handled by mutation hooks
    }
  }

  return (
    <div className="form-container">
      <div className="form-card">
        <h2 className="form-title">{mode === 'create' ? 'Create User' : 'Edit User'}</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="form">
          <div className="form-group">
            <label htmlFor="full_name" className="form-label">
              Full Name
            </label>
            <input
              id="full_name"
              type="text"
              className={`form-input ${errors.full_name ? 'form-input-error' : ''}`}
              placeholder="John Doe"
              autoFocus
              {...register('full_name')}
            />
            {errors.full_name && <p className="form-error">{errors.full_name.message}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              id="username"
              type="text"
              className={`form-input ${errors.username ? 'form-input-error' : ''}`}
              placeholder="johndoe"
              {...register('username')}
            />
            {errors.username && <p className="form-error">{errors.username.message}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              className={`form-input ${errors.email ? 'form-input-error' : ''}`}
              placeholder="john.doe@example.com"
              {...register('email')}
            />
            {errors.email && <p className="form-error">{errors.email.message}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password {mode === 'edit' && '(leave blank to keep current)'}
            </label>
            <input
              id="password"
              type="password"
              className={`form-input ${errors.password ? 'form-input-error' : ''}`}
              placeholder={mode === 'create' ? 'Min 8 chars, 1 uppercase, 1 number' : 'Leave blank to keep current'}
              {...register('password')}
            />
            {errors.password && <p className="form-error">{errors.password.message}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="bio" className="form-label">
              Bio (Optional)
            </label>
            <textarea
              id="bio"
              className={`form-input form-textarea ${errors.bio ? 'form-input-error' : ''}`}
              placeholder="Tell us about yourself"
              rows={3}
              {...register('bio')}
            />
            {errors.bio && <p className="form-error">{errors.bio.message}</p>}
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create User' : 'Update User'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/users')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
