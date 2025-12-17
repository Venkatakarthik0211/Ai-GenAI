import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { authApi } from '@/api/endpoints/auth.api'
import { RegisterData } from '@/types/auth.types'
import toast from 'react-hot-toast'
import './RegisterForm.css'

// Password validation regex (matching backend requirements)
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_+\-=\[\]{}|;:,.<>])[A-Za-z\d@$!%*?&#^()_+\-=\[\]{}|;:,.<>]{8,}$/

// Phone number validation regex (E.164 format: +[country code][number])
// Matches: +1234567890 to +123456789012345 (7-15 digits after +)
const phoneRegex = /^\+[1-9]\d{6,14}$/

// Validation schema
const registerSchema = z.object({
  first_name: z.string()
    .min(1, 'First name is required')
    .max(50, 'First name must be less than 50 characters')
    .regex(/^[a-zA-Z\s'-]+$/, 'First name can only contain letters, spaces, hyphens, and apostrophes'),
  last_name: z.string()
    .min(1, 'Last name is required')
    .max(50, 'Last name must be less than 50 characters')
    .regex(/^[a-zA-Z\s'-]+$/, 'Last name can only contain letters, spaces, hyphens, and apostrophes'),
  email: z.string()
    .min(1, 'Email is required')
    .email('Invalid email address')
    .max(100, 'Email must be less than 100 characters')
    .toLowerCase(),
  username: z.string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be less than 50 characters')
    .regex(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, underscores, and hyphens')
    .regex(/^[a-zA-Z]/, 'Username must start with a letter'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password must be less than 128 characters')
    .regex(passwordRegex, 'Password must contain uppercase, lowercase, number, and special character'),
  confirm_password: z.string().min(1, 'Please confirm your password'),
  phone_number: z.string()
    .optional()
    .refine((val) => !val || val === '' || phoneRegex.test(val), {
      message: 'Phone must be in format: +[country code][number] (e.g., +1234567890, minimum 10 digits)',
    }),
  department: z.string()
    .optional()
    .refine((val) => !val || val === '' || val.length <= 100, {
      message: 'Department must be less than 100 characters',
    }),
  terms: z.boolean().refine(val => val === true, {
    message: 'You must accept the terms and conditions',
  }),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
})

type RegisterFormData = z.infer<typeof registerSchema>

interface RegisterFormProps {
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
  return { score, label: 'Strong', color: '#10b981' }
}

// Password requirements checker
const checkPasswordRequirements = (password: string) => ({
  length: password.length >= 8,
  uppercase: /[A-Z]/.test(password),
  lowercase: /[a-z]/.test(password),
  number: /\d/.test(password),
  special: /[@$!%*?&#^()_+\-=\[\]{}|;:,.<>]/.test(password),
})

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [passwordFocused, setPasswordFocused] = useState(false)
  const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null)
  const [checkingUsername, setCheckingUsername] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const password = watch('password') || ''
  const username = watch('username') || ''
  const passwordStrength = calculatePasswordStrength(password)
  const passwordReqs = checkPasswordRequirements(password)

  // Check username availability (debounced)
  const checkUsernameAvailability = async (username: string) => {
    if (username.length < 3) {
      setUsernameAvailable(null)
      return
    }

    setCheckingUsername(true)
    try {
      // Note: This endpoint would need to be added to backend
      // For now, we'll simulate it
      await new Promise(resolve => setTimeout(resolve, 500))

      // Simulate check (in production, call actual API)
      const unavailableUsernames = ['admin', 'test', 'user', 'root']
      const isAvailable = !unavailableUsernames.includes(username.toLowerCase())

      setUsernameAvailable(isAvailable)
    } catch (error) {
      setUsernameAvailable(null)
    } finally {
      setCheckingUsername(false)
    }
  }

  // Debounce username check
  useState(() => {
    const timer = setTimeout(() => {
      if (username.length >= 3) {
        checkUsernameAvailability(username)
      }
    }, 500)
    return () => clearTimeout(timer)
  })

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true)

    try {
      // Remove confirm_password and terms from data
      const { confirm_password, terms, ...registerData } = data

      // Call register API
      await authApi.register(registerData as RegisterData)

      // Show success message
      toast.success(
        'Account created successfully! Please check your email to verify your account.',
        {
          icon: '🎉',
          duration: 5000,
        }
      )

      // Callback
      if (onSuccess) {
        onSuccess()
      }

      // Navigate to login
      setTimeout(() => {
        navigate('/login')
      }, 1500)
    } catch (error: any) {
      console.error('Registration error:', error)

      // Handle specific error cases
      if (error.response?.status === 400) {
        const detail = error.response.data?.detail || ''

        if (detail.includes('email') && detail.includes('already registered')) {
          toast.error('This email is already registered', {
            icon: '❌',
            duration: 4000,
          })
        } else if (detail.includes('username') && detail.includes('already exists')) {
          toast.error('This username is already taken', {
            icon: '❌',
            duration: 4000,
          })
        } else if (detail.includes('password')) {
          toast.error('Password does not meet requirements', {
            icon: '⚠️',
            duration: 4000,
          })
        } else {
          toast.error(detail || 'Registration failed. Please check your input.', {
            icon: '❌',
            duration: 4000,
          })
        }
      } else if (error.response?.status === 422) {
        toast.error('Please check all fields and try again', {
          icon: '⚠️',
          duration: 4000,
        })
      } else {
        toast.error('Registration failed. Please try again.', {
          icon: '❌',
          duration: 4000,
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="register-form-container">
      <div className="register-card">
        {/* Header */}
        <div className="register-header">
          <h1 className="register-title">Create Your Account</h1>
          <p className="register-subtitle">Join us and start managing tickets</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="register-form">
          {/* Name Fields - Two Column */}
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name" className="form-label">
                First Name
              </label>
              <input
                id="first_name"
                type="text"
                className={`form-input ${errors.first_name ? 'input-error' : ''}`}
                placeholder="John"
                {...register('first_name')}
                disabled={isLoading}
              />
              {errors.first_name && (
                <p className="error-message">{errors.first_name.message}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="last_name" className="form-label">
                Last Name
              </label>
              <input
                id="last_name"
                type="text"
                className={`form-input ${errors.last_name ? 'input-error' : ''}`}
                placeholder="Doe"
                {...register('last_name')}
                disabled={isLoading}
              />
              {errors.last_name && (
                <p className="error-message">{errors.last_name.message}</p>
              )}
            </div>
          </div>

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
            />
            {errors.email && (
              <p className="error-message">{errors.email.message}</p>
            )}
          </div>

          {/* Username Field with Availability Check */}
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <div className="username-input-wrapper">
              <input
                id="username"
                type="text"
                className={`form-input ${errors.username ? 'input-error' : ''}`}
                placeholder="john.doe"
                {...register('username')}
                disabled={isLoading}
              />
              {checkingUsername && (
                <span className="username-status checking">Checking...</span>
              )}
              {!checkingUsername && usernameAvailable === true && username.length >= 3 && (
                <span className="username-status available">✓ Available</span>
              )}
              {!checkingUsername && usernameAvailable === false && username.length >= 3 && (
                <span className="username-status unavailable">✗ Taken</span>
              )}
            </div>
            {errors.username && (
              <p className="error-message">{errors.username.message}</p>
            )}
          </div>

          {/* Password Field with Strength Meter */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <div className="password-input-wrapper">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                className={`form-input ${errors.password ? 'input-error' : ''}`}
                placeholder="Enter your password"
                {...register('password')}
                disabled={isLoading}
                onFocus={() => setPasswordFocused(true)}
                onBlur={() => setPasswordFocused(false)}
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

            {/* Password Requirements */}
            {(passwordFocused || password) && (
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
            )}

            {errors.password && (
              <p className="error-message">{errors.password.message}</p>
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
                placeholder="Confirm your password"
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
            {errors.confirm_password && (
              <p className="error-message">{errors.confirm_password.message}</p>
            )}
          </div>

          {/* Phone Number Field (Optional) */}
          <div className="form-group">
            <label htmlFor="phone_number" className="form-label">
              Phone Number <span className="optional-label">(Optional)</span>
            </label>
            <input
              id="phone_number"
              type="tel"
              className={`form-input ${errors.phone_number ? 'input-error' : ''}`}
              placeholder="+1234567890 (country code + number)"
              {...register('phone_number')}
              disabled={isLoading}
            />
            {errors.phone_number && (
              <p className="error-message">{errors.phone_number.message}</p>
            )}
            <p className="field-hint">Format: +[country code][number] (e.g., +911234567890 for India)</p>
          </div>

          {/* Department Field (Optional) */}
          <div className="form-group">
            <label htmlFor="department" className="form-label">
              Department <span className="optional-label">(Optional)</span>
            </label>
            <select
              id="department"
              className="form-input form-select"
              {...register('department')}
              disabled={isLoading}
            >
              <option value="">Select a department</option>
              <option value="Engineering">Engineering</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="DevOps">DevOps</option>
              <option value="Support">Support</option>
              <option value="Operations">Operations</option>
              <option value="Security">Security</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Terms and Conditions */}
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                className="form-checkbox"
                {...register('terms')}
                disabled={isLoading}
              />
              <span>
                I agree to the{' '}
                <Link to="/terms" className="link-purple">
                  Terms & Conditions
                </Link>
              </span>
            </label>
            {errors.terms && (
              <p className="error-message">{errors.terms.message}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="register-button"
            disabled={isLoading || usernameAvailable === false}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Creating Account...
              </>
            ) : (
              'CREATE ACCOUNT'
            )}
          </button>

          {/* Login Link */}
          <div className="form-footer">
            <p className="footer-text">
              Already have an account?{' '}
              <Link to="/login" className="login-link">
                Login here
              </Link>
            </p>
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

export default RegisterForm
