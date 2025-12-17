// User Roles (matching backend)
export type UserRole =
  | 'END_USER'
  | 'DEVOPS_ENGINEER'
  | 'SENIOR_ENGINEER'
  | 'TEAM_LEAD'
  | 'MANAGER'
  | 'ADMIN'

// User Status (matching backend)
export type UserStatus = 'ACTIVE' | 'INACTIVE' | 'LOCKED' | 'PENDING_ACTIVATION'

// User Interface
export interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  phone_number?: string
  department?: string
  role: UserRole
  status: UserStatus
  is_active: boolean
  is_email_verified: boolean
  mfa_enabled: boolean
  created_at: string
  updated_at: string
  last_login?: string
}

// Login Request
export interface LoginCredentials {
  username: string
  password: string
}

// Login Response
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

// Register Request
export interface RegisterData {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  phone_number?: string
  department?: string
}

// Token Refresh Request
export interface RefreshTokenRequest {
  refresh_token: string
}

// Change Password Request
export interface ChangePasswordData {
  old_password: string
  new_password: string
}

// Forgot Password Request
export interface ForgotPasswordData {
  email: string
}

// Reset Password Request
export interface ResetPasswordData {
  token: string
  new_password: string
}

// Update Profile Request
export interface UpdateProfileData {
  first_name?: string
  last_name?: string
  phone_number?: string
  department?: string
}

// API Error Response
export interface ApiError {
  detail: string
  status_code?: number
}

// Auth State
export interface AuthState {
  user: User | null
  access_token: string | null
  refresh_token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}
