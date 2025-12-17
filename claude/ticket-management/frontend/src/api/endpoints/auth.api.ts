/**
 * Authentication API Endpoints
 * Based on Postman Collection: Ticket Management System - Complete API
 * Backend: http://localhost:8001/api/v1/auth
 */

import apiClient from '../client/axios.config'
import type {
  LoginCredentials,
  LoginResponse,
  RegisterData,
  User,
  RefreshTokenRequest,
  ChangePasswordData,
  ForgotPasswordData,
  ResetPasswordData,
  UpdateProfileData,
} from '@/types/auth.types'

/**
 * Authentication Service
 * Matches endpoints from backend/auth/routes.py
 */
export const authApi = {
  /**
   * Register a new user
   * POST /auth/register
   * Password Requirements: 8+ chars, uppercase, lowercase, digit, special char
   */
  register: (data: RegisterData) => {
    return apiClient.post<User>('/auth/register', data)
  },

  /**
   * Login user
   * POST /auth/login
   * Returns access_token (15 min validity) and refresh_token (7 days validity)
   * Account locks after 5 failed attempts for 30 minutes
   */
  login: (credentials: LoginCredentials) => {
    return apiClient.post<LoginResponse>('/auth/login', credentials)
  },

  /**
   * Logout user
   * POST /auth/logout
   * Requires: Bearer token
   * Invalidates current refresh token and terminates session
   */
  logout: () => {
    return apiClient.post('/auth/logout')
  },

  /**
   * Refresh access token
   * POST /auth/refresh
   * Requires: Valid refresh_token
   * Returns: New access_token and optionally new refresh_token
   */
  refreshToken: (data: RefreshTokenRequest) => {
    return apiClient.post<LoginResponse>('/auth/refresh', data)
  },

  /**
   * Get current user profile
   * GET /auth/me
   * Requires: Bearer token
   * Returns: Current user information
   */
  getCurrentUser: () => {
    return apiClient.get<User>('/auth/me')
  },

  /**
   * Update user profile
   * PUT /auth/profile
   * Requires: Bearer token
   * Updates: first_name, last_name, phone_number, department
   */
  updateProfile: (data: UpdateProfileData) => {
    return apiClient.put<User>('/auth/profile', data)
  },

  /**
   * Change password
   * POST /auth/change-password
   * Requires: Bearer token, old_password, new_password
   * Logs out all other sessions
   */
  changePassword: (data: ChangePasswordData) => {
    return apiClient.post('/auth/change-password', data)
  },

  /**
   * Forgot password - Request reset link
   * POST /auth/forgot-password
   * Sends password reset link to email
   * Link expires in 15 minutes
   */
  forgotPassword: (data: ForgotPasswordData) => {
    return apiClient.post('/auth/forgot-password', data)
  },

  /**
   * Reset password with token
   * POST /auth/reset-password
   * Requires: reset token from email, new_password
   * Token is single-use
   */
  resetPassword: (data: ResetPasswordData) => {
    return apiClient.post('/auth/reset-password', data)
  },

  /**
   * Verify email address
   * POST /auth/verify-email
   * Requires: verification token from email
   */
  verifyEmail: (token: string) => {
    return apiClient.post('/auth/verify-email', { token })
  },

  /**
   * Resend verification email
   * POST /auth/resend-verification
   * Requires: Bearer token
   * Sends new verification email
   */
  resendVerification: () => {
    return apiClient.post('/auth/resend-verification')
  },
}

// Export individual functions for easier imports
export const {
  register,
  login,
  logout: logoutApi,
  refreshToken,
  getCurrentUser,
  updateProfile,
  changePassword,
  forgotPassword,
  resetPassword,
  verifyEmail,
  resendVerification,
} = authApi

export default authApi
