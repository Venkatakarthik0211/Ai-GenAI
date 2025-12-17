import { useState, useRef, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAppDispatch } from '@/store/hooks'
import { loginAsync } from '@/store/slices/authSlice'
import { LoginCredentials } from '@/types/auth.types'
import toast from 'react-hot-toast'
import './LoginForm.css'

// Validation schema
const loginSchema = z.object({
  username: z.string()
    .min(1, 'Email or username is required')
    .max(100, 'Email or username is too long')
    .trim()
    .refine((val) => val.length >= 3, {
      message: 'Email or username must be at least 3 characters',
    }),
  password: z.string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password is too long'),
})

type LoginFormData = z.infer<typeof loginSchema>

interface LoginFormProps {
  onSuccess?: () => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isUsernameReadonly, setIsUsernameReadonly] = useState(true)
  const [isPasswordReadonly, setIsPasswordReadonly] = useState(true)
  const usernameInputRef = useRef<HTMLInputElement>(null)

  // Force remove autofill styling
  const handleUsernameFocus = () => {
    setIsUsernameReadonly(false)

    // Force override autofill styling with JavaScript
    setTimeout(() => {
      if (usernameInputRef.current) {
        usernameInputRef.current.style.backgroundColor = '#1e293b'
        usernameInputRef.current.style.color = '#ffffff'
        usernameInputRef.current.style.backgroundImage = 'none'
        usernameInputRef.current.style.transition = 'none'
      }
    }, 0)
  }

  // Continuously force dark background to override autofill
  useEffect(() => {
    const interval = setInterval(() => {
      if (usernameInputRef.current && !isUsernameReadonly) {
        usernameInputRef.current.style.backgroundColor = '#1e293b'
        usernameInputRef.current.style.color = '#ffffff'
        usernameInputRef.current.style.backgroundImage = 'none'
      }
    }, 50)

    return () => clearInterval(interval)
  }, [isUsernameReadonly])

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  // Show toast for validation errors
  useEffect(() => {
    if (errors.username) {
      toast.error(errors.username.message || 'Username is required', {
        icon: '⚠️',
        duration: 3000,
        position: 'top-center',
      })
    }
    if (errors.password) {
      toast.error(errors.password.message || 'Password is required', {
        icon: '⚠️',
        duration: 3000,
        position: 'top-center',
      })
    }
  }, [errors.username, errors.password])

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)

    try {
      // Dispatch login action to Redux
      const result = await dispatch(loginAsync(data as LoginCredentials)).unwrap()

      // Show success message
      toast.success(`Welcome back, ${result.user.first_name}!`, {
        icon: '👋',
        duration: 3000,
      })

      // Callback
      if (onSuccess) {
        onSuccess()
      }

      // Navigate to dashboard
      setTimeout(() => {
        navigate('/dashboard')
      }, 500)
    } catch (error: any) {
      // Extract error message from rejected thunk
      const errorMessage = typeof error === 'string' ? error :
                          error?.message ||
                          error?.payload ||
                          error?.error ||
                          String(error)

      // Check for specific error types
      const errorLower = errorMessage.toLowerCase()

      if (errorLower.includes('locked')) {
        toast.error('Account locked due to too many failed attempts', {
          icon: '🔒',
          duration: 5000,
          position: 'top-center',
        })
      } else if (errorLower.includes('inactive')) {
        toast.error('Account is inactive. Please contact support.', {
          icon: '⚠️',
          duration: 5000,
          position: 'top-center',
        })
      } else {
        // For any other error (including invalid credentials)
        toast.error('Invalid username or password', {
          icon: '❌',
          duration: 4000,
          position: 'top-center',
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-form-container">
      <div className="login-card">
        {/* Signup Link */}
        <div className="signup-link-container">
          <Link to="/register" className="signup-link">
            Signup →
          </Link>
        </div>

        {/* Header */}
        <div className="login-header">
          <h1 className="login-title">Here you can Login</h1>
          <p className="login-subtitle">Let's join us :)</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="login-form" autoComplete="off">
          {/* Email/Username Field */}
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Email
            </label>
            <input
              id="username"
              type="text"
              className={`form-input ${errors.username ? 'input-error' : ''}`}
              placeholder=""
              autoComplete="off"
              data-lpignore="true"
              data-form-type="other"
              readOnly={isUsernameReadonly}
              onFocus={handleUsernameFocus}
              {...register('username')}
              ref={(e) => {
                const regRef = register('username').ref
                if (typeof regRef === 'function') {
                  regRef(e)
                }
                // @ts-ignore
                usernameInputRef.current = e
              }}
              disabled={isLoading}
            />
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <div className="password-input-wrapper">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                className={`form-input ${errors.password ? 'input-error' : ''}`}
                placeholder=""
                autoComplete="off"
                data-lpignore="true"
                readOnly={isPasswordReadonly}
                onFocus={() => setIsPasswordReadonly(false)}
                {...register('password')}
                disabled={isLoading}
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
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Logging in...
              </>
            ) : (
              'LOGIN'
            )}
          </button>

          {/* Forgot Password Link */}
          <div className="form-footer">
            <Link to="/forgot-password" className="forgot-password-link">
              Forgot your password?
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

export default LoginForm
