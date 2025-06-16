import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import NotImplementedModal from '../NotImplementedModal/NotImplementedModal';
import './Sidebar.css';

const Sidebar = ({ user, onQuickAction }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showNotImplemented, setShowNotImplemented] = useState(false);
  const [notImplementedFeature, setNotImplementedFeature] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  const quickActions = [
    {
      id: 'home',
      icon: '🏠',
      title: 'Home',
      description: 'Go to dashboard',
      color: 'primary',
      implemented: true,
      path: '/'
    },
    {
      id: 'new-schedule',
      icon: '📅',
      title: 'New Schedule',
      description: 'Create a fresh schedule',
      color: 'primary',
      implemented: true,
      path: '/scheduler'
    },
    {
      id: 'saved-schedules',
      icon: '💾',
      title: 'Saved Schedules',
      description: 'View your saved schedules',
      color: 'success',
      implemented: false
    },
    {
      id: 'templates',
      icon: '📋',
      title: 'Templates',
      description: 'Use pre-made templates',
      color: 'warning',
      implemented: false
    },
    {
      id: 'analytics',
      icon: '📊',
      title: 'Analytics',
      description: 'View scheduling insights',
      color: 'info',
      implemented: false
    }
  ];

  const recentActivity = [
    { action: 'Generated schedule for CS101', time: '2 hours ago' },
    { action: 'Saved "Fall 2024 Schedule"', time: '1 day ago' },
    { action: 'Updated constraints', time: '3 days ago' }
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
    // Smart back navigation based on current location
    if (location.pathname === '/scheduler') {
      navigate('/');
    } else if (location.pathname === '/about') {
      navigate('/');
    } else {
      // If we're on home or unknown route, go to home
      navigate('/');
    }
  };

  const getCurrentPageTitle = () => {
    switch (location.pathname) {
      case '/':
        return 'Dashboard';
      case '/scheduler':
        return 'Schedule Builder';
      case '/about':
        return 'About Schedgic';
      default:
        return 'Navigation';
    }
  };

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
                        }
                        {action.path === location.pathname && <span className="active-badge">Current</span>}
                        }
                      </h4>
                      <p className="action-description">{action.description}</p>
                    </div>
                  </button>
                ))}
              </div>

              {user && (
                <div className="sidebar-section">
                  <h3 className="section-title">Recent Activity</h3>
                  <div className="activity-list">
                    {recentActivity.map((activity, index) => (
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
                <h3 className="section-title">Tips & Tricks</h3>
                <div className="tips-list">
                  <div className="tip-item">
                    <span className="tip-icon">💡</span>
                    <p>Use natural language for constraints like "No classes before 9am"</p>
                  </div>
                  <div className="tip-item">
                    <span className="tip-icon">🎯</span>
                    <p>Drag and drop classes to alternative time slots</p>
                  </div>
                  <div className="tip-item">
                    <span className="tip-icon">📱</span>
                    <p>Export your schedule as PDF or share it</p>
                  </div>
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
                  }
                  {action.path === location.pathname && <span className="mini-active-badge">•</span>}
                  }
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