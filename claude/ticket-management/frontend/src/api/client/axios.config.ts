import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// API Base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1'

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from localStorage
    const token = localStorage.getItem('access_token')

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`📤 ${config.method?.toUpperCase()} ${config.url}`)
    }

    return config
  },
  (error: AxiosError) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - Handle responses and errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`)
    }
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized - Token expired or invalid
    // BUT skip interceptor logic for login/register endpoints (they return 401 for invalid credentials)
    const isAuthEndpoint = originalRequest.url?.includes('/auth/login') ||
                          originalRequest.url?.includes('/auth/register')

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true

      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem('refresh_token')

        if (!refreshToken) {
          // No refresh token, redirect to login
          redirectToLogin()
          return Promise.reject(error)
        }

        // Call refresh token endpoint
        const response = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        )

        const { access_token, refresh_token: new_refresh_token } = response.data

        // Update tokens in localStorage
        localStorage.setItem('access_token', access_token)
        if (new_refresh_token) {
          localStorage.setItem('refresh_token', new_refresh_token)
        }

        // Update Authorization header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }

        // Retry original request
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh token failed, logout user
        console.error('❌ Token refresh failed:', refreshError)
        handleLogout()
        return Promise.reject(refreshError)
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error('❌ Access Denied - Insufficient permissions')
      // You can dispatch a notification or redirect here
    }

    // Handle 500 Server Error
    if (error.response?.status === 500) {
      console.error('❌ Server Error:', error.response.data)
    }

    // Log error in development
    if (import.meta.env.DEV) {
      console.error(
        `❌ ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status}`,
        error.response?.data
      )
    }

    return Promise.reject(error)
  }
)

// Helper function to redirect to login
function redirectToLogin() {
  // Clear tokens
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')

  // Redirect to login page
  window.location.href = '/login'
}

// Helper function to handle logout
function handleLogout() {
  // Clear all stored data
  localStorage.clear()

  // Redirect to login
  window.location.href = '/login'
}

// Export helper to manually trigger logout
export const logout = handleLogout

export default apiClient
