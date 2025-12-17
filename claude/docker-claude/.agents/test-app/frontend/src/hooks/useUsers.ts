/**
 * Custom hooks for user data management using React Query.
 */
import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import {
  User,
  UserCreate,
  UserUpdate,
  UserListResponse,
  PaginationParams,
  MessageResponse,
} from '../types/user'
import * as usersApi from '../api/users'

/**
 * Query key factory for users.
 */
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (params?: PaginationParams) => [...userKeys.lists(), params] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
}

/**
 * Hook to fetch paginated list of users.
 */
export function useGetUsers(params?: PaginationParams): UseQueryResult<UserListResponse, Error> {
  return useQuery({
    queryKey: userKeys.list(params),
    queryFn: () => usersApi.getUsers(params),
    staleTime: 30000, // 30 seconds
  })
}

/**
 * Hook to fetch a single user by ID.
 */
export function useGetUser(userId: string): UseQueryResult<User, Error> {
  return useQuery({
    queryKey: userKeys.detail(userId),
    queryFn: () => usersApi.getUserById(userId),
    enabled: !!userId,
    staleTime: 30000,
  })
}

/**
 * Hook to create a new user.
 */
export function useCreateUser(): UseMutationResult<User, Error, UserCreate> {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (userData: UserCreate) => usersApi.createUser(userData),
    onSuccess: () => {
      // Invalidate and refetch user lists
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      toast.success('User created successfully')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 'Failed to create user'
      toast.error(errorMessage)
    },
  })
}

/**
 * Hook to update a user.
 */
export function useUpdateUser(): UseMutationResult<
  User,
  Error,
  { userId: string; userData: UserUpdate }
> {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, userData }) => usersApi.updateUser(userId, userData),
    onSuccess: (data, variables) => {
      // Invalidate user lists
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      // Update cached user detail
      queryClient.setQueryData(userKeys.detail(variables.userId), data)
      toast.success('User updated successfully')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 'Failed to update user'
      toast.error(errorMessage)
    },
  })
}

/**
 * Hook to delete a user.
 */
export function useDeleteUser(): UseMutationResult<
  MessageResponse,
  Error,
  { userId: string; permanent?: boolean }
> {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, permanent = false }) => usersApi.deleteUser(userId, permanent),
    onSuccess: (data, variables) => {
      // Invalidate user lists
      queryClient.invalidateQueries({ queryKey: userKeys.lists() })
      // Remove user from cache
      queryClient.removeQueries({ queryKey: userKeys.detail(variables.userId) })
      toast.success(data.message || 'User deleted successfully')
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 'Failed to delete user'
      toast.error(errorMessage)
    },
  })
}
