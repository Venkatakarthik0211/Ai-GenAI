/**
 * Registration form component.
 */
import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { registerSchema, RegisterFormData } from '../../utils/validators'

export default function RegisterForm() {
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      const { confirmPassword, ...userData } = data
      await registerUser(userData)
      navigate('/users')
    } catch (error) {
      // Error is handled in AuthContext with toast
    }
  }

  return (
    <div className="form-container">
      <div className="form-card">
        <h2 className="form-title">Create Account</h2>
        <p className="form-subtitle">Register for a new UserHub account</p>

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
              Password
            </label>
            <input
              id="password"
              type="password"
              className={`form-input ${errors.password ? 'form-input-error' : ''}`}
              placeholder="Min 8 chars, 1 uppercase, 1 number"
              {...register('password')}
            />
            {errors.password && <p className="form-error">{errors.password.message}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              className={`form-input ${errors.confirmPassword ? 'form-input-error' : ''}`}
              placeholder="Re-enter your password"
              {...register('confirmPassword')}
            />
            {errors.confirmPassword && (
              <p className="form-error">{errors.confirmPassword.message}</p>
            )}
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

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div className="form-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="form-link">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
