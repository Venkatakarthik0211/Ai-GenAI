/**
 * Navigation bar component.
 */
import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const toggleMenu = () => {
    setMenuOpen(!menuOpen)
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">👥</span>
          UserHub
        </Link>

        {isAuthenticated && (
          <>
            <button
              className="navbar-toggle"
              onClick={toggleMenu}
              aria-label="Toggle navigation"
            >
              <span className="hamburger-icon">{menuOpen ? '✕' : '☰'}</span>
            </button>

            <div className={`navbar-menu ${menuOpen ? 'navbar-menu-open' : ''}`}>
              <div className="navbar-nav">
                <Link to="/users" className="nav-link" onClick={() => setMenuOpen(false)}>
                  Users
                </Link>
              </div>

              <div className="navbar-user">
                <div className="user-info">
                  <span className="user-name">{user?.full_name}</span>
                  <span className="user-email">{user?.email}</span>
                  {user?.is_superuser && <span className="user-badge">Admin</span>}
                </div>
                <button onClick={handleLogout} className="btn btn-logout">
                  Logout
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </nav>
  )
}
