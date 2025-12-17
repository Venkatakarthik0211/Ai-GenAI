import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { authApi } from '@/api/endpoints/auth.api'
import { ForgotPasswordData } from '@/types/auth.types'
import toast from 'react-hot-toast'
import './ForgotPasswordForm.css'

// Validation schema
const forgotPasswordSchema = z.object({
  email: z.string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address')
    .max(100, 'Email must be less than 100 characters')
    .toLowerCase()
    .trim(),
})

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>

interface ForgotPasswordFormProps {
  onSuccess?: () => void
}

export const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({ onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)
  const [sentEmail, setSentEmail] = useState('')
  const [resendTimer, setResendTimer] = useState(0)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true)

    try {
      // Call forgot password API
      await authApi.forgotPassword(data as ForgotPasswordData)

      // Show success state
      setEmailSent(true)
      setSentEmail(data.email)

      // Start resend timer (60 seconds)
      setResendTimer(60)
      const interval = setInterval(() => {
        setResendTimer((prev) => {
          if (prev <= 1) {
            clearInterval(interval)
            return 0
          }
          return prev - 1
        })
      }, 1000)

      // Show success toast
      toast.success('Password reset link sent! Check your email.', {
        icon: '📧',
        duration: 5000,
      })

      // Callback
      if (onSuccess) {
        onSuccess()
      }
    } catch (error: any) {
      console.error('Forgot password error:', error)

      // Handle specific error cases
      if (error.response?.status === 404) {
        toast.error('No account found with this email address', {
          icon: '❌',
          duration: 4000,
        })
      } else if (error.response?.status === 429) {
        toast.error('Too many requests. Please try again later.', {
          icon: '⏱️',
          duration: 4000,
        })
      } else {
        toast.error('Failed to send reset link. Please try again.', {
          icon: '❌',
          duration: 4000,
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleResend = async () => {
    if (resendTimer > 0) return

    setIsLoading(true)
    try {
      await authApi.forgotPassword({ email: sentEmail })

      toast.success('Reset link sent again!', {
        icon: '📧',
        duration: 3000,
      })

      // Restart timer
      setResendTimer(60)
      const interval = setInterval(() => {
        setResendTimer((prev) => {
          if (prev <= 1) {
            clearInterval(interval)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } catch (error) {
      toast.error('Failed to resend email', {
        icon: '❌',
        duration: 3000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (emailSent) {
    return (
      <div className="forgot-password-container">
        <div className="forgot-password-card success-state">
          {/* Success Icon */}
          <div className="success-icon">✅</div>

          {/* Success Header */}
          <div className="forgot-header">
            <h1 className="forgot-title">Email Sent Successfully!</h1>
          </div>

          {/* Success Message */}
          <div className="success-content">
            <p className="success-message">
              We've sent a password reset link to:
            </p>
            <p className="sent-email">{sentEmail}</p>
            <p className="success-note">
              Please check your inbox and spam folder.
              <br />
              The link will expire in 15 minutes.
            </p>

            {/* Back to Login Button */}
            <Link to="/login" className="back-to-login-button">
              BACK TO LOGIN
            </Link>

            {/* Resend Link */}
            <div className="resend-section">
              {resendTimer > 0 ? (
                <p className="resend-timer">
                  Didn't receive email? Resend in {resendTimer}s
                </p>
              ) : (
                <button
                  type="button"
                  className="resend-link"
                  onClick={handleResend}
                  disabled={isLoading}
                >
                  Didn't receive email? Click to resend
                </button>
              )}
            </div>
          </div>

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

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        {/* Icon */}
        <div className="forgot-icon">🔑</div>

        {/* Header */}
        <div className="forgot-header">
          <h1 className="forgot-title">Forgot Your Password?</h1>
          <p className="forgot-subtitle">No worries! Enter your email below</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="forgot-form">
          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              className={`form-input ${errors.email ? 'input-error' : ''}`}
              placeholder="john.doe@example.com"
              {...register('email')}
              disabled={isLoading}
              autoFocus
            />
            {errors.email && (
              <p className="error-message">{errors.email.message}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="forgot-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Sending...
              </>
            ) : (
              'SEND RESET LINK'
            )}
          </button>

          {/* Info Message */}
          <div className="info-message">
            <span className="info-icon">ℹ️</span>
            <div className="info-text">
              <p>We'll send you a password reset link</p>
              <p>Link expires in 15 minutes</p>
            </div>
          </div>

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

      {/* Login Link - Top Right */}
      <div className="login-link-container">
        <Link to="/login" className="login-link">
          Login →
        </Link>
      </div>
    </div>
  )
}

export default ForgotPasswordForm
