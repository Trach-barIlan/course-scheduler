import React from 'react';
import './Navigation.css';

const Navigation = ({ currentPage, onNavigate, user }) => {
  const navItems = [
    { id: 'scheduler', label: 'Schedule Builder', icon: '📚' },
    { id: 'schedules', label: 'My Schedules', icon: '📅' },
    { id: 'profile', label: 'Profile', icon: '👤' }
  ];

  return (
    <nav className="main-navigation">
      <div className="nav-brand">
        <span className="nav-logo">📚</span>
        <span className="nav-title">Course Scheduler</span>
      </div>
      
      <div className="nav-items">
        {navItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </div>

      <div className="nav-user">
        {user ? (
          <div className="user-info">
            <div className="user-avatar">
              {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
            </div>
            <span className="user-name">{user.first_name}</span>
          </div>
        ) : (
          <button 
            className="auth-button"
            onClick={() => onNavigate('auth')}
          >
            Sign In
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navigation;