import React, { useState, useEffect } from 'react';
import './UserProfile.css';

const UserProfile = ({ user, authToken, onLogout, onClose }) => {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL

  useEffect(() => {
    if (user && authToken) {
      const fetchUserStatistics = async () => {
        try {
          const response = await fetch(API_BASE_URL + '/api/statistics/user', {
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json',
            }
          });

          if (response.ok) {
            const data = await response.json();
            setStatistics(data.statistics);
          } else {
            console.error('Failed to fetch statistics for profile');
          }
        } catch (error) {
          console.error('Error fetching statistics for profile:', error);
        }
      };
      fetchUserStatistics();
    }
  }, [user, authToken, API_BASE_URL]);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      const response = await fetch(API_BASE_URL + '/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        onLogout();
      } else {
        onLogout();
      }
    } catch (error) {
      console.error('Logout error:', error);
      onLogout();
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
                  <div className="stat-number">
                    {statistics ? statistics.saved_schedules_count : 0}
                  </div>
                  <div className="stat-label">Saved Schedules</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">⏰</div>
                <div className="stat-content">
                  <div className="stat-number">
                    {statistics ? statistics.schedules_this_week : 0}
                  </div>
                  <div className="stat-label">Generated This Week</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🎯</div>
                <div className="stat-content">
                  <div className="stat-number">
                    {statistics ? statistics.total_courses_scheduled : 0}
                  </div>
                  <div className="stat-label">Total Courses</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-content">
                  <div className="stat-number">
                    {statistics ? `${statistics.success_rate}%` : '98%'}
                  </div>
                  <div className="stat-label">Success Rate</div>
                </div>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h3 className="section-title">Preferences</h3>
            <div className="preferences-grid">
              <div className="preference-item">
                <span className="preference-label">Default Schedule Type</span>
                <span className="preference-value">
                  {statistics ? statistics.preferred_schedule_type : 'Crammed'}
                </span>
              </div>
              <div className="preference-item">
                <span className="preference-label">Theme</span>
                <span className="preference-value">Light</span>
              </div>
              <div className="preference-item">
                <span className="preference-label">Avg Generation Time</span>
                <span className="preference-value">
                  {statistics ? `${statistics.average_generation_time}ms` : 'N/A'}
                </span>
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