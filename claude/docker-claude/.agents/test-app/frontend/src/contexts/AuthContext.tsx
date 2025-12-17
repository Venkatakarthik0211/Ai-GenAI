/**
 * Authentication context for managing user authentication state.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { toast } from 'react-toastify'
import { User, LoginRequest, RegisterRequest } from '../types/user'
import * as authApi from '../api/auth'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  register: (userData: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check for existing user on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      const storedUser = localStorage.getItem('user')

      if (token && storedUser) {
        try {
          // Verify token is still valid by fetching current user
          const currentUser = await authApi.getCurrentUser()
          setUser(currentUser)
        } catch (error) {
          // Token is invalid, clear storage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          setUser(null)
        }
      }

      setIsLoading(false)
    }

    checkAuth()
  }, [])

  /**
   * Login user with email and password.
   */
  const login = async (credentials: LoginRequest) => {
    try {
      setIsLoading(true)

      // Get tokens
      await authApi.login(credentials)

      // Fetch user data
      const currentUser = await authApi.getCurrentUser()
      setUser(currentUser)

      toast.success('Login successful!')
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed. Please try again.'
      toast.error(errorMessage)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Register a new user account.
   */
  const register = async (userData: RegisterRequest) => {
    try {
      setIsLoading(true)

      // Register user
      await authApi.register(userData)

      // Auto-login after registration
      await login({
        email: userData.email,
        password: userData.password,
      })

      toast.success('Registration successful! Welcome to UserHub.')
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.'
      toast.error(errorMessage)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Logout current user.
   */
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      // Ignore logout errors, still clear local state
    } finally {
      setUser(null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      toast.info('Logged out successfully')
    }
  }

  /**
   * Refresh user data from server.
   */
  const refreshUser = async () => {
    try {
      const currentUser = await authApi.getCurrentUser()
      setUser(currentUser)
    } catch (error) {
      // If refresh fails, logout user
      await logout()
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Custom hook to use auth context.
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}
