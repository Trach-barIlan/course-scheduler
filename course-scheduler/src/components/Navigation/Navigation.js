import React from 'react';
import './Navigation.css';

const Navigation = ({ user, onAuthClick, onProfileClick }) => {
  return (
    <nav className="main-navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <div className="brand-icon">
            <img 
              src="/ChatGPT Image Jun 15, 2025, 02_51_46 PM.png" 
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
            <a href="#features" className="nav-link">Features</a>
            <a href="#how-it-works" className="nav-link">How It Works</a>
            <a href="#about" className="nav-link">About</a>
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
    </nav>
  );
};

export default Navigation;