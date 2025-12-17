import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import ticketReducer from './slices/ticketSlice'

/**
 * Redux Store Configuration
 * Configured with Redux Toolkit
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    ticket: ticketReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types for serialization check
        ignoredActions: ['persist/PERSIST'],
      },
    }),
  devTools: import.meta.env.DEV, // Enable Redux DevTools in development
})

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export default store
