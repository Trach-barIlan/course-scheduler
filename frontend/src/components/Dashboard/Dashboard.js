import React, { useState, useEffect } from 'react';
import NotImplementedModal from '../NotImplementedModal/NotImplementedModal';
import './Dashboard.css';

const Dashboard = ({ user, onQuickAction }) => {
  const [showNotImplemented, setShowNotImplemented] = useState(false);
  const [notImplementedFeature, setNotImplementedFeature] = useState('');
  const [statistics, setStatistics] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user statistics when component mounts or user changes
  useEffect(() => {
    if (user) {
      fetchUserStatistics();
      fetchRecentActivity();
    } else {
      setIsLoading(false);
    }
  }, [user]);

  const fetchUserStatistics = async () => {
    try {
      // Using relative URL since we have a proxy configured
      const response = await fetch('/api/statistics/user', {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setStatistics(data.statistics);
      } else {
        console.error('Failed to fetch statistics');
        // Set default statistics if fetch fails
        setStatistics({
          schedules_created: 0,
          schedules_this_week: 0,
          saved_schedules_count: 0,
          hours_saved: 0,
          success_rate: 98,
          efficiency: 85
        });
      }
    } catch (error) {
      console.error('Error fetching statistics:', error);
      // Set default statistics if fetch fails
      setStatistics({
        schedules_created: 0,
        schedules_this_week: 0,
        saved_schedules_count: 0,
        hours_saved: 0,
        success_rate: 98,
        efficiency: 85
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRecentActivity = async () => {
    try {
      // Using relative URL since we have a proxy configured
      const response = await fetch('/api/statistics/recent-activity', {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setRecentActivity(data.activities || []);
      } else {
        console.error('Failed to fetch recent activity');
      }
    } catch (error) {
      console.error('Error fetching recent activity:', error);
    }
  };

  // Default statistics for non-authenticated users
  const defaultStats = [
    {
      icon: '📅',
      label: 'Schedules Created',
      value: '0',
      change: 'Sign in to track',
      color: 'primary'
    },
    {
      icon: '⏰',
      label: 'Hours Saved',
      value: '0',
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

  // Generate stats array based on user authentication and data
  const getStatsArray = () => {
    if (!user || !statistics) {
      return defaultStats;
    }

    return [
      {
        icon: '📅',
        label: 'Schedules Created',
        value: statistics.schedules_created.toString(),
        change: `+${statistics.schedules_this_week} this week`,
        color: 'primary'
      },
      {
        icon: '⏰',
        label: 'Hours Saved',
        value: statistics.hours_saved.toString(),
        change: 'vs manual planning',
        color: 'success'
      },
      {
        icon: '🎯',
        label: 'Success Rate',
        value: `${statistics.success_rate}%`,
        change: 'constraint satisfaction',
        color: 'warning'
      },
      {
        icon: '📊',
        label: 'Efficiency',
        value: `${statistics.efficiency}%`,
        change: 'schedule optimization',
        color: 'info'
      }
    ];
  };

  const getRecentSchedules = () => {
    if (!user || !recentActivity.length) {
      return [
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
    }

    // Convert activity data to schedule format
    return recentActivity
      .filter(activity => activity.type === 'save')
      .slice(0, 3)
      .map(activity => ({
        name: activity.action.replace("Saved '", "").replace("'", ""),
        courses: Math.floor(Math.random() * 5) + 3, // Placeholder
        created: activity.time,
        status: 'active'
      }));
  };

  const handleNotImplementedClick = (feature) => {
    setNotImplementedFeature(feature);
    setShowNotImplemented(true);
  };

  const handleQuickAction = (actionId) => {
    if (actionId === 'new-schedule') {
      onQuickAction && onQuickAction(actionId);
    } else {
      handleNotImplementedClick(actionId);
    }
  };

  const stats = getStatsArray();
  const recentSchedules = getRecentSchedules();

  if (isLoading && user) {
    return (
      <div className="dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="dashboard">
        <div className="dashboard-header">
          <div className="welcome-section">
            <h1 className="welcome-title">
              Welcome back, {user?.first_name || 'Student'}! 👋
            </h1>
            <p className="welcome-subtitle">
              {user 
                ? "Ready to create your perfect schedule? Let's make this semester amazing."
                : "Sign in to track your scheduling progress and save your schedules."
              }
            </p>
          </div>
          <div className="header-actions">
            <button 
              className="primary-action"
              onClick={() => handleQuickAction('new-schedule')}
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
              <h2 className="section-title">
                {user ? 'Recent Schedules' : 'Sample Schedules'}
              </h2>
              <button 
                className="section-action"
                onClick={() => handleNotImplementedClick('saved-schedules')}
              >
                View All
              </button>
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
                    <button 
                      className="schedule-action"
                      onClick={() => handleNotImplementedClick('saved-schedules')}
                    >
                      Open
                    </button>
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
                  onClick={() => handleQuickAction('new-schedule')}
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
                  onClick={() => handleQuickAction('templates')}
                >
                  Browse Templates
                </button>
              </div>
              <div className="quick-start-card">
                <div className="card-icon">📤</div>
                <h3>Import Schedule</h3>
                <p>Upload your existing schedule and let AI optimize it</p>
                <button 
                  className="card-action"
                  onClick={() => handleNotImplementedClick('import')}
                >
                  Import Now
                </button>
              </div>
            </div>
          </div>
        </div>

        {user && recentActivity.length > 0 && (
          <div className="content-section">
            <div className="section-header">
              <h2 className="section-title">Recent Activity</h2>
            </div>
            <div className="activity-list">
              {recentActivity.slice(0, 5).map((activity, index) => (
                <div key={index} className="activity-item">
                  <div className={`activity-dot ${activity.success ? 'success' : 'error'}`}></div>
                  <div className="activity-content">
                    <div className="activity-action">{activity.action}</div>
                    <div className="activity-time">{activity.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <NotImplementedModal
        isOpen={showNotImplemented}
        onClose={() => setShowNotImplemented(false)}
        feature={notImplementedFeature}
      />
    </>
  );
};

export default Dashboard;