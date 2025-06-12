import React, { useState } from 'react';
import './UserProfile.css';

const UserProfile = ({ user, onLogout, onClose }) => {
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        onLogout();
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getInitials = (firstName, lastName) => {
    return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
  };

  return (
    <div className="profile-overlay">
      <div className="profile-container">
        <div className="profile-header">
          <button className="profile-close" onClick={onClose}>×</button>
          <div className="profile-avatar">
            <div className="avatar-circle">
              {getInitials(user.first_name, user.last_name)}
            </div>
          </div>
          <h2 className="profile-name">
            {user.first_name} {user.last_name}
          </h2>
          <p className="profile-username">@{user.username}</p>
        </div>

        <div className="profile-content">
          <div className="profile-section">
            <h3 className="section-title">Account Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Email</span>
                <span className="info-value">{user.email}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Username</span>
                <span className="info-value">{user.username}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Member Since</span>
                <span className="info-value">{formatDate(user.created_at)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Last Login</span>
                <span className="info-value">{formatDate(user.last_login)}</span>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h3 className="section-title">Quick Stats</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📚</div>
                <div className="stat-content">
                  <div className="stat-number">0</div>
                  <div className="stat-label">Saved Schedules</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">⏰</div>
                <div className="stat-content">
                  <div className="stat-number">0</div>
                  <div className="stat-label">Generated This Week</div>
                </div>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h3 className="section-title">Preferences</h3>
            <div className="preferences-grid">
              <div className="preference-item">
                <span className="preference-label">Default Schedule Type</span>
                <span className="preference-value">Crammed</span>
              </div>
              <div className="preference-item">
                <span className="preference-label">Theme</span>
                <span className="preference-value">Light</span>
              </div>
            </div>
          </div>
        </div>

        <div className="profile-actions">
          <button 
            className="logout-btn"
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? (
              <>
                <div className="loading-spinner"></div>
                Signing Out...
              </>
            ) : (
              <>
                🚪 Sign Out
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;