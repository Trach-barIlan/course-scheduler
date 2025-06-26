import React, { useState } from 'react';
import '../styles/ProfilePage.css';

const ProfilePage = ({ user, onLogout }) => {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      const response = await fetch(API_BASE_URL + '/api/auth/logout', {
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

  if (!user) {
    return (
      <div className="profile-page">
        <div className="auth-required">
          <div className="auth-required-icon">🔒</div>
          <h2>Sign In Required</h2>
          <p>Please sign in to view your profile.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {getInitials(user.first_name, user.last_name)}
            </div>
          </div>
          <h1 className="profile-name">
            {user.first_name} {user.last_name}
          </h1>
          <p className="profile-username">@{user.username}</p>
        </div>

        <div className="profile-content">
          <div className="profile-section">
            <h2 className="section-title">Account Information</h2>
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
            <h2 className="section-title">Quick Stats</h2>
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
            <h2 className="section-title">Preferences</h2>
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

export default ProfilePage;