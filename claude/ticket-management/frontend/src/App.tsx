import { Provider } from 'react-redux'
import { RouterProvider } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { store } from './store'
import { router } from './router'
import './App.css'

/**
 * Main App Component
 * Sets up routing and global providers
 */
function App() {
  return (
    <Provider store={store}>
      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1e293b',
            color: '#ffffff',
            border: '1px solid #2d3748',
            borderRadius: '8px',
            padding: '16px',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#ffffff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#ffffff',
            },
          },
        }}
      />

      {/* Router */}
      <RouterProvider router={router} />
    </Provider>
  )
}

export default App
