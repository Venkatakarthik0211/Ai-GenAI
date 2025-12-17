/**
 * User management API endpoints.
 */
import apiClient from './client'
import {
  User,
  UserCreate,
  UserUpdate,
  UserListResponse,
  PaginationParams,
  MessageResponse,
} from '../types/user'

/**
 * Get paginated list of users with optional filters.
 */
export async function getUsers(params?: PaginationParams): Promise<UserListResponse> {
  const response = await apiClient.get<UserListResponse>('/api/users/', { params })
  return response.data
}

/**
 * Get a single user by ID.
 */
export async function getUserById(userId: string): Promise<User> {
  const response = await apiClient.get<User>(`/api/users/${userId}`)
  return response.data
}

/**
 * Create a new user (admin only).
 */
export async function createUser(userData: UserCreate): Promise<User> {
  const response = await apiClient.post<User>('/api/users/', userData)
  return response.data
}

/**
 * Update a user's information.
 */
export async function updateUser(userId: string, userData: UserUpdate): Promise<User> {
  const response = await apiClient.put<User>(`/api/users/${userId}`, userData)
  return response.data
}

/**
 * Delete a user (soft delete by default).
 */
export async function deleteUser(userId: string, permanent: boolean = false): Promise<MessageResponse> {
  const response = await apiClient.delete<MessageResponse>(`/api/users/${userId}`, {
    params: { permanent },
  })
  return response.data
}
