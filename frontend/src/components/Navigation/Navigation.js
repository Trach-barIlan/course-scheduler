import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation = ({ user, onAuthClick, onProfileClick }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavClick = (path) => {
    navigate(path);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="main-navigation">
      <div className="nav-container">
        <div className="nav-brand" onClick={() => handleNavClick('/')}>
          <div className="brand-icon">
            <img 
              src="/schedgic.png" 
              alt="Schedgic Logo" 
              className="brand-logo"
            />
          </div>
          <div className="brand-content">
            <h1 className="brand-title">Schedgic</h1>
            <span className="brand-subtitle">Smart Academic Planning</span>
          </div>
        </div>

        <div className="nav-menu">
          <div className="nav-links">
            <button 
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
              onClick={() => handleNavClick('/')}
            >
              Home
            </button>
            <button 
              className={`nav-link ${isActive('/scheduler') ? 'active' : ''}`}
              onClick={() => handleNavClick('/scheduler')}
            >
              Scheduler
            </button>
            <button 
              className={`nav-link ${isActive('/about') ? 'active' : ''}`}
              onClick={() => handleNavClick('/about')}
            >
              About
            </button>
          </div>

          <div className="nav-actions">
            {user ? (
              <div className="user-menu">
                <button 
                  className="user-button"
                  onClick={onProfileClick}
                >
                  <div className="user-avatar">
                    {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
                  </div>
                  <div className="user-info">
                    <span className="user-name">{user.first_name}</span>
                    <span className="user-role">Student</span>
                  </div>
                  <div className="user-chevron">▼</div>
                </button>
              </div>
            ) : (
              <button 
                className="auth-button"
                onClick={onAuthClick}
              >
                <span className="auth-icon">👤</span>
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>
          <a
              href="https://bolt.new"
              target="_blank"
              rel="noopener noreferrer"
              className="bolt-link"
              title="Go to bolt.new"
              style={{
                marginLeft: '16px',
                display: 'flex',
                alignItems: 'center',
                textDecoration: 'none',
                cursor: 'pointer'
              }}
            >
              <img
                src="/BoltBadge.png"
                alt="Bolt Logo"
                style={{ width: 'clamp(1.5em, 2.5vw, 2.2em)', height: 'clamp(1.5em, 2.5vw, 2.2em)', objectFit: 'contain' }}
              />
            </a>
    </nav>
  );
};

export default Navigation;