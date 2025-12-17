import { useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { authApi } from '@/api/endpoints/auth.api'
import { ResetPasswordData } from '@/types/auth.types'
import toast from 'react-hot-toast'
import './ResetPasswordForm.css'

// Password validation regex (matching backend requirements)
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_+\-=\[\]{}|;:,.<>])[A-Za-z\d@$!%*?&#^()_+\-=\[\]{}|;:,.<>]{8,}$/

// Validation schema
const resetPasswordSchema = z.object({
  new_password: z.string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password must be less than 128 characters')
    .regex(passwordRegex, 'Password must contain uppercase, lowercase, number, and special character'),
  confirm_password: z.string()
    .min(1, 'Please confirm your password'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
})

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

interface ResetPasswordFormProps {
  onSuccess?: () => void
}

// Password strength calculator
const calculatePasswordStrength = (password: string): {
  score: number
  label: string
  color: string
} => {
  let score = 0

  if (password.length >= 8) score += 20
  if (password.length >= 12) score += 10
  if (/[a-z]/.test(password)) score += 20
  if (/[A-Z]/.test(password)) score += 20
  if (/\d/.test(password)) score += 15
  if (/[@$!%*?&#^()_+\-=\[\]{}|;:,.<>]/.test(password)) score += 15

  if (score <= 40) return { score, label: 'Weak', color: '#ef4444' }
  if (score <= 60) return { score, label: 'Fair', color: '#f59e0b' }
  if (score <= 80) return { score, label: 'Good', color: '#3b82f6' }
  return { score, label: 'Very Strong', color: '#10b981' }
}

// Password requirements checker
const checkPasswordRequirements = (password: string) => ({
  length: password.length >= 8,
  uppercase: /[A-Z]/.test(password),
  lowercase: /[a-z]/.test(password),
  number: /\d/.test(password),
  special: /[@$!%*?&#^()_+\-=\[\]{}|;:,.<>]/.test(password),
})

export const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({ onSuccess }) => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''

  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  })

  const password = watch('new_password') || ''
  const confirmPassword = watch('confirm_password') || ''
  const passwordStrength = calculatePasswordStrength(password)
  const passwordReqs = checkPasswordRequirements(password)
  const passwordsMatch = password && confirmPassword && password === confirmPassword

  // Check if token exists
  if (!token) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card error-state">
          <div className="error-icon">❌</div>
          <div className="reset-header">
            <h1 className="reset-title">Invalid Reset Link</h1>
            <p className="reset-subtitle">
              This password reset link is invalid or has expired.
            </p>
          </div>
          <div className="error-content">
            <Link to="/forgot-password" className="request-new-button">
              REQUEST NEW LINK
            </Link>
            <div className="form-footer">
              <Link to="/login" className="back-link">
                ← Back to Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const onSubmit = async (data: ResetPasswordFormData) => {
    setIsLoading(true)

    try {
      // Call reset password API
      await authApi.resetPassword({
        token,
        new_password: data.new_password,
      } as ResetPasswordData)

      // Show success message
      toast.success('Password reset successfully! You can now login.', {
        icon: '✅',
        duration: 5000,
      })

      // Callback
      if (onSuccess) {
        onSuccess()
      }

      // Navigate to login
      setTimeout(() => {
        navigate('/login')
      }, 1500)
    } catch (error: any) {
      console.error('Reset password error:', error)

      // Handle specific error cases
      if (error.response?.status === 400) {
        const detail = error.response.data?.detail || ''

        if (detail.includes('expired')) {
          toast.error('Reset link has expired. Please request a new one.', {
            icon: '⏱️',
            duration: 5000,
          })
          setTimeout(() => navigate('/forgot-password'), 2000)
        } else if (detail.includes('invalid')) {
          toast.error('Invalid reset link. Please request a new one.', {
            icon: '❌',
            duration: 5000,
          })
          setTimeout(() => navigate('/forgot-password'), 2000)
        } else if (detail.includes('password')) {
          toast.error('Password does not meet requirements', {
            icon: '⚠️',
            duration: 4000,
          })
        } else {
          toast.error(detail || 'Failed to reset password', {
            icon: '❌',
            duration: 4000,
          })
        }
      } else if (error.response?.status === 422) {
        toast.error('Please check your password and try again', {
          icon: '⚠️',
          duration: 4000,
        })
      } else {
        toast.error('Failed to reset password. Please try again.', {
          icon: '❌',
          duration: 4000,
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="reset-password-container">
      <div className="reset-password-card">
        {/* Icon */}
        <div className="reset-icon">🔐</div>

        {/* Header */}
        <div className="reset-header">
          <h1 className="reset-title">Reset Your Password</h1>
          <p className="reset-subtitle">Create a new secure password</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="reset-form">
          {/* New Password Field */}
          <div className="form-group">
            <label htmlFor="new_password" className="form-label">
              New Password
            </label>
            <div className="password-input-wrapper">
              <input
                id="new_password"
                type={showPassword ? 'text' : 'password'}
                className={`form-input ${errors.new_password ? 'input-error' : ''}`}
                placeholder="Enter your new password"
                {...register('new_password')}
                disabled={isLoading}
                autoFocus
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>

            {/* Password Strength Meter */}
            {password && (
              <div className="password-strength">
                <div className="strength-bar-container">
                  <div
                    className="strength-bar"
                    style={{
                      width: `${passwordStrength.score}%`,
                      backgroundColor: passwordStrength.color,
                    }}
                  ></div>
                </div>
                <span className="strength-label" style={{ color: passwordStrength.color }}>
                  {passwordStrength.label} ({passwordStrength.score}%)
                </span>
              </div>
            )}

            {errors.new_password && (
              <p className="error-message">{errors.new_password.message}</p>
            )}
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label htmlFor="confirm_password" className="form-label">
              Confirm Password
            </label>
            <div className="password-input-wrapper">
              <input
                id="confirm_password"
                type={showConfirmPassword ? 'text' : 'password'}
                className={`form-input ${errors.confirm_password ? 'input-error' : ''}`}
                placeholder="Confirm your new password"
                {...register('confirm_password')}
                disabled={isLoading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
              >
                {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>

            {/* Password Match Indicator */}
            {passwordsMatch && (
              <p className="match-message">✓ Passwords match</p>
            )}

            {errors.confirm_password && (
              <p className="error-message">{errors.confirm_password.message}</p>
            )}
          </div>

          {/* Password Requirements */}
          <div className="requirements-section">
            <p className="requirements-title">Requirements:</p>
            <div className="password-requirements">
              <div className={`requirement ${passwordReqs.length ? 'met' : ''}`}>
                {passwordReqs.length ? '✓' : '○'} At least 8 characters
              </div>
              <div className={`requirement ${passwordReqs.uppercase ? 'met' : ''}`}>
                {passwordReqs.uppercase ? '✓' : '○'} One uppercase letter
              </div>
              <div className={`requirement ${passwordReqs.lowercase ? 'met' : ''}`}>
                {passwordReqs.lowercase ? '✓' : '○'} One lowercase letter
              </div>
              <div className={`requirement ${passwordReqs.number ? 'met' : ''}`}>
                {passwordReqs.number ? '✓' : '○'} One number
              </div>
              <div className={`requirement ${passwordReqs.special ? 'met' : ''}`}>
                {passwordReqs.special ? '✓' : '○'} One special character
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="reset-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Resetting...
              </>
            ) : (
              'RESET PASSWORD'
            )}
          </button>

          {/* Back to Login Link */}
          <div className="form-footer">
            <Link to="/login" className="back-link">
              ← Back to Login
            </Link>
          </div>
        </form>

        {/* Wave Decoration */}
        <div className="wave-decoration">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none">
            <path
              d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"
              className="wave-path"
            ></path>
          </svg>
        </div>
      </div>
    </div>
  )
}

export default ResetPasswordForm
