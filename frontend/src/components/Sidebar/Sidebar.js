import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import NotImplementedModal from '../NotImplementedModal/NotImplementedModal';
import './Sidebar.css';

const Sidebar = ({ user, onQuickAction }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showNotImplemented, setShowNotImplemented] = useState(false);
  const [notImplementedFeature, setNotImplementedFeature] = useState('');
  const [recentActivity, setRecentActivity] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

  const fetchRecentActivity = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      const response = await fetch(API_BASE_URL + '/api/statistics/recent-activity', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRecentActivity(data.activities || []);
      }
    } catch (error) {
      console.error('Error fetching recent activity:', error);
    }
  }, [API_BASE_URL]);

  // Fetch recent activity when user is available
  useEffect(() => {
    if (user) {
      fetchRecentActivity();
    }
  }, [user, fetchRecentActivity]);

  const quickActions = [
    {
      id: 'home',
      icon: '🏠',
      title: 'Dashboard',
      description: 'View overview',
      color: 'primary',
      implemented: true,
      path: '/'
    },
    {
      id: 'new-schedule',
      icon: '✨',
      title: 'New Schedule',
      description: 'Create schedule',
      color: 'primary',
      implemented: true,
      path: '/scheduler'
    },
    {
      id: 'templates',
      icon: '📋',
      title: 'Templates',
      description: 'Use templates',
      color: 'warning',
      implemented: false
    }
  ];

  const handleQuickAction = (actionId) => {
    const action = quickActions.find(a => a.id === actionId);
    
    if (action && action.implemented) {
      if (action.path) {
        navigate(action.path);
      } else if (onQuickAction) {
        onQuickAction(actionId);
      }
    } else {
      setNotImplementedFeature(actionId);
      setShowNotImplemented(true);
    }
  };

  const handleBackNavigation = () => {
    if (location.pathname === '/scheduler') {
      navigate('/');
    } else if (location.pathname === '/about') {
      navigate('/');
    } else {
      navigate('/');
    }
  };

  const getCurrentPageTitle = () => {
    switch (location.pathname) {
      case '/':
        return 'Dashboard';
      case '/scheduler':
        return 'Scheduler';
      case '/about':
        return 'About';
      default:
        return 'Navigation';
    }
  };

  const tips = [
    {
      icon: '💡',
      text: 'Use natural language for constraints'
    },
    {
      icon: '🎯',
      text: 'Drag classes to alternative slots'
    },
    {
      icon: '📱',
      text: 'Export schedules as PDF'
    }
  ];

  return (
    <>
      <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <button 
            className="collapse-button"
            onClick={() => setIsCollapsed(!isCollapsed)}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? '→' : '←'}
          </button>
          {!isCollapsed && (
            <div className="sidebar-title">
              <span className="title-icon">⚡</span>
              Quick Actions
            </div>
          )}
        </div>

        <div className="sidebar-content">
          {!isCollapsed && (
            <>
              {/* Navigation Section */}
              <div className="navigation-section">
                <div className="current-page">
                  <span className="page-indicator">📍</span>
                  <span className="page-title">{getCurrentPageTitle()}</span>
                </div>
                
                {location.pathname !== '/' && (
                  <button 
                    className="back-navigation-button"
                    onClick={handleBackNavigation}
                    title="Go back"
                  >
                    <span className="back-icon">←</span>
                    <span className="back-text">Back to Home</span>
                  </button>
                )}
              </div>

              <div className="quick-actions">
                {quickActions.map((action) => (
                  <button
                    key={action.id}
                    className={`quick-action-card ${action.color} ${!action.implemented ? 'not-implemented' : ''} ${
                      action.path === location.pathname ? 'active' : ''
                    }`}
                    onClick={() => handleQuickAction(action.id)}
                  >
                    <div className="action-icon">{action.icon}</div>
                    <div className="action-content">
                      <h4 className="action-title">
                        {action.title}
                        {!action.implemented && <span className="coming-soon-badge">Soon</span>}
                        {action.path === location.pathname && <span className="active-badge">Current</span>}
                      </h4>
                      <p className="action-description">{action.description}</p>
                    </div>
                  </button>
                ))}
              </div>

              {user && recentActivity.length > 0 && (
                <div className="sidebar-section">
                  <h3 className="section-title">Recent Activity</h3>
                  <div className="activity-list">
                    {recentActivity.slice(0, 3).map((activity, index) => (
                      <div key={index} className="activity-item">
                        <div className="activity-dot"></div>
                        <div className="activity-content">
                          <p className="activity-action">{activity.action}</p>
                          <span className="activity-time">{activity.time}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="sidebar-section">
                <h3 className="section-title">Tips</h3>
                <div className="tips-list">
                  {tips.map((tip, index) => (
                    <div key={index} className="tip-item">
                      <span className="tip-icon">{tip.icon}</span>
                      <p>{tip.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {isCollapsed && (
            <div className="collapsed-actions">
              {quickActions.map((action) => (
                <button
                  key={action.id}
                  className={`collapsed-action ${!action.implemented ? 'not-implemented' : ''} ${
                    action.path === location.pathname ? 'active' : ''
                  }`}
                  onClick={() => handleQuickAction(action.id)}
                  title={action.title}
                >
                  {action.icon}
                  {!action.implemented && <span className="mini-badge">!</span>}
                  {action.path === location.pathname && <span className="mini-active-badge">•</span>}
                </button>
              ))}
              
              {location.pathname !== '/' && (
                <button
                  className="collapsed-action back-action"
                  onClick={handleBackNavigation}
                  title="Go back"
                >
                  ←
                </button>
              )}
            </div>
          )}
        </div>
      </aside>

      <NotImplementedModal
        isOpen={showNotImplemented}
        onClose={() => setShowNotImplemented(false)}
        feature={notImplementedFeature}
      />
    </>
  );
};

export default Sidebar;