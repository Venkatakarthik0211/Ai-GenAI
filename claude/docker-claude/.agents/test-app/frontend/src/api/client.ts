/**
 * Axios HTTP client configuration with interceptors.
 */
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { toast } from 'react-toastify'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: Add JWT token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor: Handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // Try to refresh the token
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token: newRefreshToken } = response.data

          // Update tokens in localStorage
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', newRefreshToken)

          // Retry the original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }

          return apiClient(originalRequest)
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')

          toast.error('Session expired. Please login again.')

          // Redirect to login page
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }

          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')

        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }

    // Handle other errors
    if (error.response) {
      // Server responded with error status
      const errorMessage = getErrorMessage(error)

      // Don't show toast for certain endpoints
      const silentEndpoints = ['/api/auth/login', '/api/auth/register']
      const isSilent = silentEndpoints.some(endpoint =>
        originalRequest.url?.includes(endpoint)
      )

      if (!isSilent && error.response.status >= 500) {
        toast.error(errorMessage)
      }
    } else if (error.request) {
      // Request made but no response received
      toast.error('Network error. Please check your connection.')
    } else {
      // Something else happened
      toast.error('An unexpected error occurred.')
    }

    return Promise.reject(error)
  }
)

/**
 * Extract error message from axios error response.
 */
function getErrorMessage(error: AxiosError): string {
  if (error.response?.data) {
    const data = error.response.data as any

    if (data.detail) {
      if (typeof data.detail === 'string') {
        return data.detail
      } else if (Array.isArray(data.detail)) {
        return data.detail.map((err: any) => err.msg).join(', ')
      }
    }

    if (data.message) {
      return data.message
    }
  }

  return error.message || 'An error occurred'
}

export default apiClient
