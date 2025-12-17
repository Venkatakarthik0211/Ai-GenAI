/**
 * TypeScript type definitions for User entities and API responses.
 */

export interface User {
  id: string
  email: string
  username: string
  full_name: string
  bio?: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  last_login?: string | null
}

export interface UserCreate {
  email: string
  username: string
  full_name: string
  password: string
  bio?: string
}

export interface UserUpdate {
  email?: string
  username?: string
  full_name?: string
  bio?: string
  password?: string
  is_active?: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  full_name: string
  password: string
  bio?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface MessageResponse {
  message: string
  detail?: string
}

export interface UserListResponse {
  users: User[]
  total: number
  skip: number
  limit: number
}

export interface PaginationParams {
  skip?: number
  limit?: number
  search?: string
  is_active?: boolean
}

export interface ApiError {
  detail: string | { msg: string; type: string }[]
  message?: string
}
