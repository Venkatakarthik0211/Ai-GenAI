import { useState } from 'react'
import Button from './components/Button/Button'
import Counter from './components/Counter/Counter'
import './App.css'

function App() {
  const [theme, setTheme] = useState('light')
  const [notifications, setNotifications] = useState([])

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  const addNotification = (message) => {
    const id = Date.now()
    setNotifications([...notifications, { id, message }])
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 3000)
  }

  return (
    <div className={`app ${theme}`}>
      <header className="app-header">
        <h1>🚀 React Admin Dashboard</h1>
        <Button 
          variant="secondary" 
          onClick={toggleTheme}
          className="theme-toggle"
        >
          {theme === 'light' ? '🌙' : '☀️'} {theme === 'light' ? 'Dark' : 'Light'} Mode
        </Button>
      </header>

      <main className="app-main">
        <div className="dashboard-grid">
          <div className="card">
            <h2>Interactive Counter</h2>
            <Counter />
          </div>

          <div className="card">
            <h2>Button Playground</h2>
            <div className="button-group">
              <Button 
                variant="primary" 
                onClick={() => addNotification('Primary button clicked!')}
              >
                Primary Button
              </Button>
              <Button 
                variant="success" 
                onClick={() => addNotification('Success! 🎉')}
              >
                Success Button
              </Button>
              <Button 
                variant="danger" 
                onClick={() => addNotification('Danger! ⚠️')}
              >
                Danger Button
              </Button>
              <Button 
                variant="outline" 
                onClick={() => addNotification('Outline clicked')}
              >
                Outline Button
              </Button>
            </div>
          </div>

          <div className="card">
            <h2>Quick Stats</h2>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-number">1,234</div>
                <div className="stat-label">Users</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">5,678</div>
                <div className="stat-label">Orders</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">$12,345</div>
                <div className="stat-label">Revenue</div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Notifications */}
      <div className="notifications">
        {notifications.map(notification => (
          <div key={notification.id} className="notification">
            {notification.message}
          </div>
        ))}
      </div>
    </div>
  )
}

export default App