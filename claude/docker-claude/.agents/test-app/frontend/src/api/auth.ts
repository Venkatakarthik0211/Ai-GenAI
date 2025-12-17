/**
 * Authentication API endpoints.
 */
import apiClient from './client'
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  RefreshTokenRequest,
  User,
  MessageResponse,
} from '../types/user'

/**
 * Login user and get JWT tokens.
 */
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/api/auth/login', credentials)

  // Store tokens in localStorage
  localStorage.setItem('access_token', response.data.access_token)
  localStorage.setItem('refresh_token', response.data.refresh_token)

  return response.data
}

/**
 * Register a new user account.
 */
export async function register(userData: RegisterRequest): Promise<User> {
  const response = await apiClient.post<User>('/api/auth/register', userData)
  return response.data
}

/**
 * Refresh access token using refresh token.
 */
export async function refreshToken(refreshData: RefreshTokenRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/api/auth/refresh', refreshData)

  // Update tokens in localStorage
  localStorage.setItem('access_token', response.data.access_token)
  localStorage.setItem('refresh_token', response.data.refresh_token)

  return response.data
}

/**
 * Get current authenticated user information.
 */
export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>('/api/auth/me')

  // Store user info in localStorage
  localStorage.setItem('user', JSON.stringify(response.data))

  return response.data
}

/**
 * Logout current user.
 */
export async function logout(): Promise<MessageResponse> {
  try {
    const response = await apiClient.post<MessageResponse>('/api/auth/logout')
    return response.data
  } finally {
    // Always clear local storage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
}
