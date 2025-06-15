import React, { useState } from 'react';
import './Sidebar.css';

const Sidebar = ({ user, onQuickAction }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const quickActions = [
    {
      id: 'new-schedule',
      icon: '📅',
      title: 'New Schedule',
      description: 'Create a fresh schedule',
      color: 'primary'
    },
    {
      id: 'saved-schedules',
      icon: '💾',
      title: 'Saved Schedules',
      description: 'View your saved schedules',
      color: 'success'
    },
    {
      id: 'templates',
      icon: '📋',
      title: 'Templates',
      description: 'Use pre-made templates',
      color: 'warning'
    },
    {
      id: 'analytics',
      icon: '📊',
      title: 'Analytics',
      description: 'View scheduling insights',
      color: 'info'
    }
  ];

  const recentActivity = [
    { action: 'Generated schedule for CS101', time: '2 hours ago' },
    { action: 'Saved "Fall 2024 Schedule"', time: '1 day ago' },
    { action: 'Updated constraints', time: '3 days ago' }
  ];

  return (
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
            <div className="quick-actions">
              {quickActions.map((action) => (
                <button
                  key={action.id}
                  className={`quick-action-card ${action.color}`}
                  onClick={() => onQuickAction(action.id)}
                >
                  <div className="action-icon">{action.icon}</div>
                  <div className="action-content">
                    <h4 className="action-title">{action.title}</h4>
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
                className="collapsed-action"
                onClick={() => onQuickAction(action.id)}
                title={action.title}
              >
                {action.icon}
              </button>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;