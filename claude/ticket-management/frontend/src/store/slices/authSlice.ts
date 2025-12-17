import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authApi } from '@/api/endpoints/auth.api'
import type {
  User,
  LoginCredentials,
  LoginResponse,
  RegisterData,
  ChangePasswordData,
  UpdateProfileData,
  AuthState,
} from '@/types/auth.types'

/**
 * Initial Auth State
 * Load from localStorage if available
 */
const loadInitialState = (): AuthState => {
  try {
    const token = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null

    return {
      user,
      access_token: token,
      refresh_token: refreshToken,
      isAuthenticated: !!token && !!user,
      loading: false,
      error: null,
    }
  } catch (error) {
    return {
      user: null,
      access_token: null,
      refresh_token: null,
      isAuthenticated: false,
      loading: false,
      error: null,
    }
  }
}

const initialState: AuthState = loadInitialState()

/**
 * Async Thunks
 */

// Login
export const loginAsync = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await authApi.login(credentials)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed')
    }
  }
)

// Register
export const registerAsync = createAsyncThunk(
  'auth/register',
  async (data: RegisterData, { rejectWithValue }) => {
    try {
      const response = await authApi.register(data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Registration failed')
    }
  }
)

// Get Current User
export const getCurrentUserAsync = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authApi.getCurrentUser()
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user')
    }
  }
)

// Update Profile
export const updateProfileAsync = createAsyncThunk(
  'auth/updateProfile',
  async (data: UpdateProfileData, { rejectWithValue }) => {
    try {
      const response = await authApi.updateProfile(data)
      return response.data
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update profile')
    }
  }
)

// Change Password
export const changePasswordAsync = createAsyncThunk(
  'auth/changePassword',
  async (data: ChangePasswordData, { rejectWithValue }) => {
    try {
      await authApi.changePassword(data)
      return true
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to change password')
    }
  }
)

// Logout
export const logoutAsync = createAsyncThunk(
  'auth/logout',
  async () => {
    try {
      await authApi.logout()
      return true
    } catch (error: any) {
      // Still logout locally even if API call fails
      return true
    }
  }
)

/**
 * Auth Slice
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Set tokens (used by token refresh)
    setTokens: (
      state,
      action: PayloadAction<{ access_token: string; refresh_token: string }>
    ) => {
      state.access_token = action.payload.access_token
      state.refresh_token = action.payload.refresh_token
      localStorage.setItem('access_token', action.payload.access_token)
      localStorage.setItem('refresh_token', action.payload.refresh_token)
    },

    // Update user
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
      localStorage.setItem('user', JSON.stringify(action.payload))
    },

    // Clear error
    clearError: (state) => {
      state.error = null
    },

    // Local logout (clear state without API call)
    localLogout: (state) => {
      state.user = null
      state.access_token = null
      state.refresh_token = null
      state.isAuthenticated = false
      state.error = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loginAsync.fulfilled, (state, action: PayloadAction<LoginResponse>) => {
        state.loading = false
        state.isAuthenticated = true
        state.user = action.payload.user
        state.access_token = action.payload.access_token
        state.refresh_token = action.payload.refresh_token
        state.error = null

        // Persist to localStorage
        localStorage.setItem('access_token', action.payload.access_token)
        localStorage.setItem('refresh_token', action.payload.refresh_token)
        localStorage.setItem('user', JSON.stringify(action.payload.user))
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
        state.isAuthenticated = false
      })

    // Register
    builder
      .addCase(registerAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(registerAsync.fulfilled, (state) => {
        state.loading = false
        state.error = null
      })
      .addCase(registerAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Get Current User
    builder
      .addCase(getCurrentUserAsync.pending, (state) => {
        state.loading = true
      })
      .addCase(getCurrentUserAsync.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false
        state.user = action.payload
        state.isAuthenticated = true
        localStorage.setItem('user', JSON.stringify(action.payload))
      })
      .addCase(getCurrentUserAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
        // If token is invalid, clear auth
        state.isAuthenticated = false
        state.user = null
        state.access_token = null
        state.refresh_token = null
        localStorage.clear()
      })

    // Update Profile
    builder
      .addCase(updateProfileAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(updateProfileAsync.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false
        state.user = action.payload
        localStorage.setItem('user', JSON.stringify(action.payload))
      })
      .addCase(updateProfileAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Change Password
    builder
      .addCase(changePasswordAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(changePasswordAsync.fulfilled, (state) => {
        state.loading = false
        state.error = null
      })
      .addCase(changePasswordAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })

    // Logout
    builder
      .addCase(logoutAsync.pending, (state) => {
        state.loading = true
      })
      .addCase(logoutAsync.fulfilled, (state) => {
        state.loading = false
        state.user = null
        state.access_token = null
        state.refresh_token = null
        state.isAuthenticated = false
        state.error = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
      })
      .addCase(logoutAsync.rejected, (state) => {
        // Logout locally even if API fails
        state.loading = false
        state.user = null
        state.access_token = null
        state.refresh_token = null
        state.isAuthenticated = false
        state.error = null
        localStorage.clear()
      })
  },
})

export const { setTokens, setUser, clearError, localLogout } = authSlice.actions
export default authSlice.reducer
