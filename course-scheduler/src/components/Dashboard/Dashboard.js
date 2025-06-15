import React from 'react';
import './Dashboard.css';

const Dashboard = ({ user, onQuickAction }) => {
  const stats = [
    {
      icon: '📅',
      label: 'Schedules Created',
      value: '12',
      change: '+3 this week',
      color: 'primary'
    },
    {
      icon: '⏰',
      label: 'Hours Saved',
      value: '24',
      change: 'vs manual planning',
      color: 'success'
    },
    {
      icon: '🎯',
      label: 'Success Rate',
      value: '98%',
      change: 'constraint satisfaction',
      color: 'warning'
    },
    {
      icon: '📊',
      label: 'Efficiency',
      value: '85%',
      change: 'schedule optimization',
      color: 'info'
    }
  ];

  const recentSchedules = [
    {
      name: 'Fall 2024 - Computer Science',
      courses: 5,
      created: '2 days ago',
      status: 'active'
    },
    {
      name: 'Spring 2024 - Mathematics',
      courses: 4,
      created: '1 week ago',
      status: 'completed'
    },
    {
      name: 'Summer 2024 - Physics',
      courses: 3,
      created: '2 weeks ago',
      status: 'draft'
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1 className="welcome-title">
            Welcome back, {user?.first_name || 'Student'}! 👋
          </h1>
          <p className="welcome-subtitle">
            Ready to create your perfect schedule? Let's make this semester amazing.
          </p>
        </div>
        <div className="header-actions">
          <button 
            className="primary-action"
            onClick={() => onQuickAction && onQuickAction('new-schedule')}
          >
            <span className="action-icon">✨</span>
            Create New Schedule
          </button>
        </div>
      </div>

      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className={`stat-card ${stat.color}`}>
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-content">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
              <div className="stat-change">{stat.change}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-content">
        <div className="content-section">
          <div className="section-header">
            <h2 className="section-title">Recent Schedules</h2>
            <button className="section-action">View All</button>
          </div>
          <div className="schedules-list">
            {recentSchedules.map((schedule, index) => (
              <div key={index} className="schedule-card">
                <div className="schedule-info">
                  <h3 className="schedule-name">{schedule.name}</h3>
                  <div className="schedule-meta">
                    <span className="course-count">{schedule.courses} courses</span>
                    <span className="schedule-date">{schedule.created}</span>
                  </div>
                </div>
                <div className="schedule-actions">
                  <span className={`status-badge ${schedule.status}`}>
                    {schedule.status}
                  </span>
                  <button className="schedule-action">Open</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="content-section">
          <div className="section-header">
            <h2 className="section-title">Quick Start</h2>
          </div>
          <div className="quick-start-cards">
            <div className="quick-start-card">
              <div className="card-icon">🚀</div>
              <h3>First Time?</h3>
              <p>Follow our step-by-step guide to create your first schedule</p>
              <button 
                className="card-action"
                onClick={() => onQuickAction && onQuickAction('new-schedule')}
              >
                Get Started
              </button>
            </div>
            <div className="quick-start-card">
              <div className="card-icon">📋</div>
              <h3>Use Template</h3>
              <p>Start with a pre-made template for common degree programs</p>
              <button 
                className="card-action"
                onClick={() => onQuickAction && onQuickAction('templates')}
              >
                Browse Templates
              </button>
            </div>
            <div className="quick-start-card">
              <div className="card-icon">📤</div>
              <h3>Import Schedule</h3>
              <p>Upload your existing schedule and let AI optimize it</p>
              <button className="card-action">Import Now</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;