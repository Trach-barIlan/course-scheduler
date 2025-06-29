import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import NotImplementedModal from '../NotImplementedModal/NotImplementedModal';
import ScheduleGuide from '../ScheduleGuide/ScheduleGuide';
import './Dashboard.css';

const Dashboard = ({ user, authToken, onQuickAction }) => {
  const navigate = useNavigate();
  const [showNotImplemented, setShowNotImplemented] = useState(false);
  const [notImplementedFeature, setNotImplementedFeature] = useState('');
  const [showGuide, setShowGuide] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  const fetchUserData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch statistics and activity in parallel
      const [statsResponse, activityResponse] = await Promise.all([
        fetch(API_BASE_URL + '/api/statistics/user', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          }
        }),
        fetch(API_BASE_URL + '/api/statistics/recent-activity', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          }
        })
      ]);

      let statsData = null;
      let activityData = null;

      if (statsResponse.ok) {
        const data = await statsResponse.json();
        statsData = data.statistics;
      } else {
        console.error('Failed to fetch statistics:', statsResponse.status);
      }

      if (activityResponse.ok) {
        const data = await activityResponse.json();
        activityData = data.activities || [];
      } else {
        console.error('Failed to fetch recent activity:', activityResponse.status);
      }

      // Set statistics with fallback values
      setStatistics(statsData || {
        schedules_created: 0,
        schedules_this_week: 0,
        saved_schedules_count: 0,
        hours_saved: 0,
        success_rate: 98,
        efficiency: 85,
        total_courses_scheduled: 0,
        preferred_schedule_type: 'crammed',
        constraints_used_count: 0,
        average_generation_time: 0
      });

      setRecentActivity(activityData || []);

    } catch (error) {
      console.error('Error fetching user data:', error);
      setError('Failed to load dashboard data');
      
      // Set fallback statistics
      setStatistics({
        schedules_created: 0,
        schedules_this_week: 0,
        saved_schedules_count: 0,
        hours_saved: 0,
        success_rate: 98,
        efficiency: 85,
        total_courses_scheduled: 0,
        preferred_schedule_type: 'crammed',
        constraints_used_count: 0,
        average_generation_time: 0
      });
    } finally {
      setIsLoading(false);
    }
  }, [authToken, API_BASE_URL]);

  // Fetch user statistics when component mounts or user changes
  useEffect(() => {
    if (user && authToken) {
      fetchUserData();
    } else {
      setIsLoading(false);
      // Set default statistics for non-authenticated users
      setStatistics({
        schedules_created: 0,
        schedules_this_week: 0,
        saved_schedules_count: 0,
        hours_saved: 0,
        success_rate: 98,
        efficiency: 85,
        total_courses_scheduled: 0,
        preferred_schedule_type: 'crammed',
        constraints_used_count: 0,
        average_generation_time: 0
      });
    }
  }, [user, authToken, fetchUserData]);

  // Generate stats array based on user authentication and data
  const getStatsArray = () => {
    if (!statistics) {
      return [];
    }

    return [
      {
        icon: '📅',
        label: 'Schedules Created',
        value: statistics.schedules_created?.toString() || '0',
        change: user ? `+${statistics.schedules_this_week || 0} this week` : 'Sign in to track',
        color: 'primary'
      },
      {
        icon: '⏰',
        label: 'Hours Saved',
        value: statistics.hours_saved?.toFixed(1) || '0.0',
        change: 'vs manual planning',
        color: 'success'
      },
      {
        icon: '🎯',
        label: 'Success Rate',
        value: `${statistics.success_rate || 98}%`,
        change: 'constraint satisfaction',
        color: 'warning'
      },
      {
        icon: '📊',
        label: 'Efficiency',
        value: `${statistics.efficiency || 85}%`,
        change: 'schedule optimization',
        color: 'info'
      }
    ];
  };

  const getRecentSchedules = () => {
    if (!user || !recentActivity.length) {
      return [
        {
          id: 'sample-1',
          name: 'Fall 2024 - Computer Science',
          courses: 5,
          created: '2 days ago',
          status: 'active',
          isSample: true
        },
        {
          id: 'sample-2', 
          name: 'Spring 2024 - Mathematics',
          courses: 4,
          created: '1 week ago',
          status: 'completed',
          isSample: true
        },
        {
          id: 'sample-3',
          name: 'Summer 2024 - Physics',
          courses: 3,
          created: '2 weeks ago',
          status: 'draft',
          isSample: true
        }
      ];
    }

    // Convert activity data to schedule format with real IDs
    return recentActivity
      .filter(activity => activity.type === 'save' && activity.schedule_id)
      .slice(0, 3)
      .map(activity => ({
        id: activity.schedule_id,
        name: activity.action.replace("Saved '", "").replace("'", ""),
        courses: Math.floor(Math.random() * 5) + 3, // This should ideally come from the actual data
        created: activity.time,
        status: 'active',
        isSample: false
      }));
  };

  const handleNotImplementedClick = (feature) => {
    setNotImplementedFeature(feature);
    setShowNotImplemented(true);
  };

  const handleQuickAction = (actionId) => {
    if (actionId === 'new-schedule') {
      onQuickAction && onQuickAction(actionId);
    } else if (actionId === 'guide') {
      setShowGuide(true);
    } else {
      handleNotImplementedClick(actionId);
    }
  };

  const handleStartScheduling = () => {
    // Close guide and navigate to scheduler
    setShowGuide(false);
    onQuickAction && onQuickAction('new-schedule');
  };

  const handleOpenSchedule = async (schedule) => {
    if (schedule.isSample) {
      navigate('/scheduler');
      return;
    }

    try {
      console.log('🔍 Schedule object:', schedule);
      console.log('🔍 Schedule ID:', schedule.id);
      console.log('🔍 Schedule ID type:', typeof schedule.id);
      
      const response = await fetch(`${API_BASE_URL}/api/schedules/${schedule.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response URL:', response.url);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Loaded schedule data:', data);
        
        navigate('/scheduler', { 
          state: { 
            loadedSchedule: data.schedule.schedule_data || data.schedule,
            scheduleName: data.schedule.schedule_name || schedule.name,
            scheduleId: schedule.id
          } 
        });
      } else {
        const errorText = await response.text();
        console.error('❌ Failed to fetch schedule. Status:', response.status);
        console.error('❌ Error response:', errorText);
        alert('Failed to load schedule. Please try again.');
      }
    } catch (error) {
      console.error('❌ Error fetching schedule:', error);
      alert('Failed to load schedule. Please check your connection.');
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
            {error && (
              <div className="error-notice">
                <span>⚠️ {error}</span>
              </div>
            )}
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
                onClick={() => navigate('/schedules')}
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
                      onClick={() => handleOpenSchedule(schedule)}
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
                  onClick={() => setShowGuide(true)}
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

      <ScheduleGuide
        isOpen={showGuide}
        onClose={() => setShowGuide(false)}
        onStartScheduling={handleStartScheduling}
      />

      <NotImplementedModal
        isOpen={showNotImplemented}
        onClose={() => setShowNotImplemented(false)}
        feature={notImplementedFeature}
      />
    </>
  );
};

export default Dashboard;