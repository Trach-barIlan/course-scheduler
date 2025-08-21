import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import NotImplementedModal from '../NotImplementedModal/NotImplementedModal';
import ScheduleGuide from '../ScheduleGuide/ScheduleGuide';
import { getCached, setCached, getScheduleDetail, setScheduleDetail } from '../../utils/cache';
import './Dashboard.css';

const Dashboard = ({ user, authToken, onQuickAction }) => {

  const ENABLE_STATS = true; // Flag to enable/disable statistics
  const navigate = useNavigate();
  const [showNotImplemented, setShowNotImplemented] = useState(false);
  const [notImplementedFeature, setNotImplementedFeature] = useState('');
  const [showGuide, setShowGuide] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [savedSchedules, setSavedSchedules] = useState([]);
  const [isStatsLoading, setIsStatsLoading] = useState(true);
  const [isActivityLoading, setIsActivityLoading] = useState(true);
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
  const SCHEDULES_CACHE_KEY = 'saved_schedules_list';
  const CACHE_TTL_MS = 60 * 60 * 1000;          // 1 hour
  const CACHE_NEAR_EXPIRY_MS = 30 * 1000;      
  const LAST_FETCH_KEY = user ? `cs_${user.id}_saved_schedules_fetched_at` : null;
  const STATS_CACHE_KEY = 'user_stats';
  const STATS_CACHE_TTL_MS = 60 * 60 * 1000;    // 1 hour
  const LAST_STATS_FETCH_KEY = user ? `cs_${user.id}_stats_fetched_at` : null;
  const PREFETCH_COUNT = 4;
  const prefetchingRef = useRef(new Set());

  const fetchUserStats = useCallback(async (force = false) => {
    if (!ENABLE_STATS || !user || !authToken) {
      setIsStatsLoading(false);
      return;
    }

    let cached = null;
    try { cached = getCached(STATS_CACHE_KEY, user.id); } catch {}
    if (cached && !force) {
      setStatistics(cached);
      setIsStatsLoading(false);
      try {
        const lastFetch = parseInt(localStorage.getItem(LAST_STATS_FETCH_KEY) || '0', 10);
        const age = Date.now() - lastFetch;
        const remaining = STATS_CACHE_TTL_MS - age;
        if (remaining <= CACHE_NEAR_EXPIRY_MS) {
          setTimeout(() => fetchUserStats(true), 0); // רענון ברקע
        }
      } catch {}
      return;
    }

    setIsStatsLoading(true);
    try {
      const statsResponse = await fetch(API_BASE_URL + '/api/statistics/user', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });
      if (statsResponse.ok) {
        const data = await statsResponse.json();
        const statsObj = data.statistics || null;
        setStatistics(statsObj);
        if (statsObj) {
          setCached(STATS_CACHE_KEY, user.id, statsObj, STATS_CACHE_TTL_MS);
          localStorage.setItem(LAST_STATS_FETCH_KEY, Date.now().toString());
        }
      } else {
        const fallback = {
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
        };
        setStatistics(fallback);
        setCached(STATS_CACHE_KEY, user.id, fallback, STATS_CACHE_TTL_MS);
        localStorage.setItem(LAST_STATS_FETCH_KEY, Date.now().toString());
      }
    } catch (e) {
      console.error('Stats fetch error', e);
      if (!cached) {
        const fallback = {
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
        };
        setStatistics(fallback);
      }
    } finally {
      setIsStatsLoading(false);
    }
  }, [ENABLE_STATS, user, authToken, API_BASE_URL, CACHE_NEAR_EXPIRY_MS, LAST_STATS_FETCH_KEY, STATS_CACHE_TTL_MS]);

  const fetchSavedSchedules = useCallback(async (force = false) => {
    if (!user || !authToken) {
      setSavedSchedules([]);
      setIsActivityLoading(false);
      return;
    }
    setIsActivityLoading(true);

    let cached = null;
    try {
      cached = getCached(SCHEDULES_CACHE_KEY, user.id); // מחזיר רק אם לא פג
    } catch {}

    if (cached && !force) {
      setSavedSchedules(cached);

      // בדיקה אם כמעט פג (רק אז נעשה רענון ברקע)
      try {
        const lastFetch = parseInt(localStorage.getItem(LAST_FETCH_KEY) || '0', 10);
        const age = Date.now() - lastFetch;
        const remaining = CACHE_TTL_MS - age;
        if (remaining <= CACHE_NEAR_EXPIRY_MS) {
          // רענון ברקע קליל
          setTimeout(() => fetchSavedSchedules(true), 0);
        }
      } catch {}
      setIsActivityLoading(false);
      return;
    }

    try {
      const resp = await fetch(`${API_BASE_URL}/api/schedules/list`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (resp.ok) {
        const data = await resp.json();
        const list = (data.schedules || []).map(s => ({
          id: s.id,
          name: s.schedule_name,
          courseCount: s.course_count || (s.schedule_data?.length || 0),
          created: s.created_at,
          status: 'active'
        }));
        setSavedSchedules(list);
        setCached(SCHEDULES_CACHE_KEY, user.id, list, CACHE_TTL_MS);
        localStorage.setItem(LAST_FETCH_KEY, Date.now().toString());
      } else {
        setSavedSchedules([]);
      }
    } catch {
      // אם אין רשת ועדיין היה cache – כבר הצגנו
    } finally {
      setIsActivityLoading(false);
    }
  }, [user, authToken, API_BASE_URL, SCHEDULES_CACHE_KEY, LAST_FETCH_KEY, CACHE_NEAR_EXPIRY_MS, CACHE_TTL_MS]);

  // החלף fetchRecentActivity בקריאה לזו:
  useEffect(() => {
    fetchUserStats();
    fetchSavedSchedules();
  }, [fetchUserStats, fetchSavedSchedules]);

  // Prefetch first few schedule DETAILS (only if not already cached)
  const prefetchScheduleDetails = useCallback(() => {
    if (!user || !authToken || !savedSchedules.length) return;

    const targets = savedSchedules.slice(0, PREFETCH_COUNT);
    const toFetch = targets.filter(s => {
      const cached = getScheduleDetail(user.id, s.id);
      return !cached && !prefetchingRef.current.has(s.id);
    });
    if (!toFetch.length) return; // הכל כבר קיים

    toFetch.forEach(s => prefetchingRef.current.add(s.id));

    const doFetch = () => {
      Promise.all(
        toFetch.map(async (s) => {
          try {
            const resp = await fetch(`${API_BASE_URL}/api/schedules/${s.id}`, {
              headers: { 'Authorization': `Bearer ${authToken}` }
            });
            if (resp.ok) {
              const data = await resp.json();
              const normalized = {
                schedule_id: s.id,
                schedule_name: data.schedule.schedule_name || s.name,
                schedule_data: data.schedule.schedule_data || data.schedule,
                original_course_options: data.schedule.original_course_options || []
              };
              setScheduleDetail(user.id, s.id, normalized); // שמירה בקאש
            }
          } catch (e) {
            // שקט: prefetch רק ברקע
          } finally {
            prefetchingRef.current.delete(s.id);
          }
        })
      );
    };

    if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
      window.requestIdleCallback(doFetch, { timeout: 3000 });
    } else {
      setTimeout(doFetch, 300); // דחייה קלה שלא תחסום UI
    }
  }, [user, authToken, savedSchedules, API_BASE_URL]);

  // Trigger prefetch whenever savedSchedules list changes (after initial fetch or refresh)
  useEffect(() => {
    prefetchScheduleDetails();
  }, [prefetchScheduleDetails]);

  // Generate stats array based on user authentication and data
  const getStatsArray = () => {
    if (isStatsLoading) {
      // Return skeleton data while loading
      return [
        {
          icon: '📅',
          label: 'Schedules Created',
          value: '---',
          change: 'Loading...',
          color: 'primary',
          isLoading: true
        },
        {
          icon: '⏰',
          label: 'Hours Saved',
          value: '---',
          change: 'Loading...',
          color: 'success',
          isLoading: true
        },
        {
          icon: '🎯',
          label: 'Success Rate',
          value: '--%',
          change: 'Loading...',
          color: 'warning',
          isLoading: true
        },
        {
          icon: '📊',
          label: 'Efficiency',
          value: '--%',
          change: 'Loading...',
          color: 'info',
          isLoading: true
        }
      ];
    }

    if (!statistics) {
      return [];
    }

    return [
      {
        icon: '📅',
        label: 'Schedules Created',
        value: statistics.schedules_created?.toString() || '0',
        change: user ? `+${statistics.schedules_this_week || 0} this week` : 'Sign in to track',
        color: 'primary',
        isLoading: false
      },
      {
        icon: '⏰',
        label: 'Hours Saved',
        value: statistics.hours_saved?.toFixed(1) || '0.0',
        change: 'vs manual planning',
        color: 'success',
        isLoading: false
      },
      {
        icon: '🎯',
        label: 'Success Rate',
        value: `${statistics.success_rate || 98}%`,
        change: 'constraint satisfaction',
        color: 'warning',
        isLoading: false
      },
      {
        icon: '📊',
        label: 'Efficiency',
        value: `${statistics.efficiency || 85}%`,
        change: 'schedule optimization',
        color: 'info',
        isLoading: false
      }
    ];
  };

  const getRecentSchedules = () => {
    if (isActivityLoading) {
      return Array.from({ length: 3 }).map((_, i) => ({
        id: `loading-${i}`,
        name: 'Loading...',
        courseCount: '---',
        created: 'Loading...',
        status: 'loading',
        isLoading: true
      }));
    }
    if (!user || !savedSchedules.length) {
      return [
        { id: 'sample-1', name: 'Sample Schedule A', courseCount: 4, created: '—', status: 'sample', isSample: true },
        { id: 'sample-2', name: 'Sample Schedule B', courseCount: 5, created: '—', status: 'sample', isSample: true },
      ];
    }
    return savedSchedules.slice(0, 5).map(s => ({
      id: s.id,
      name: s.name,
      courseCount: s.courseCount,
      created: s.created,
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
    // קודם בדוק בקאש
    const cached = getScheduleDetail(user?.id, schedule.id);
    if (cached) {
      navigate('/scheduler', {
        state: {
          loadedSchedule: cached.schedule_data,
          scheduleName: cached.schedule_name || schedule.name,
          scheduleId: schedule.id,
          originalCourseOptions: cached.original_course_options || []
        }
      });
      return; // אין צורך ב-API
    }

    // אם אין בקאש – שלוף עכשיו ושמור
    try {
      const response = await fetch(`${API_BASE_URL}/api/schedules/${schedule.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });
      if (response.ok) {
        const data = await response.json();
        const normalized = {
          schedule_id: schedule.id,
          schedule_name: data.schedule.schedule_name || schedule.name,
          schedule_data: data.schedule.schedule_data || data.schedule,
          original_course_options: data.schedule.original_course_options || []
        };
        setScheduleDetail(user?.id, schedule.id, normalized); // שמירה לעתיד
        navigate('/scheduler', {
          state: {
            loadedSchedule: normalized.schedule_data,
            scheduleName: normalized.schedule_name,
            scheduleId: schedule.id,
            originalCourseOptions: normalized.original_course_options
          }
        });
      } else {
        alert('Failed to load schedule. Please try again.');
      }
    } catch (error) {
      console.error('❌ Error fetching schedule:', error);
      alert('Failed to load schedule. Please check your connection.');
    }
  };

  const handleViewEnhancedSchedule = async (schedule) => {
    if (schedule.isSample) {
      // For sample schedules, we might not have real data
      setShowNotImplemented(true);
      setNotImplementedFeature('saved-schedules');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/schedules/${schedule.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        navigate('/schedule-viewer', {
          state: {
            schedule: data.schedule.schedule_data || data.schedule,
            scheduleName: data.schedule.schedule_name || schedule.name,
            scheduleId: schedule.id,
            from: '/'
          }
        });
      } else {
        alert('Failed to load schedule. Please try again.');
      }
    } catch (error) {
      console.error('❌ Error fetching schedule:', error);
      alert('Failed to load schedule. Please check your connection.');
    }
  };

  const stats = ENABLE_STATS ? getStatsArray() : [];

  const recentSchedules = useMemo(() => getRecentSchedules(), [getRecentSchedules, isActivityLoading, savedSchedules, user]);

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

        {ENABLE_STATS && (
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <div key={index} className={`stat-card ${stat.color} ${stat.isLoading ? 'loading' : ''}`}>
                <div className="stat-icon">{stat.icon}</div>
                <div className="stat-content">
                  <div className={`stat-value ${stat.isLoading ? 'skeleton' : ''}`}>
                    {stat.isLoading ? (
                      <div className="skeleton-bar skeleton-value"></div>
                    ) : (
                      stat.value
                    )}
                  </div>
                  <div className="stat-label">{stat.label}</div>
                  <div className={`stat-change ${stat.isLoading ? 'skeleton' : ''}`}>
                    {stat.isLoading ? (
                      <div className="skeleton-bar skeleton-change"></div>
                    ) : (
                      stat.change
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

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
                <div key={index} className={`schedule-card ${schedule.isLoading ? 'loading' : ''}`}>
                  <div className="schedule-info">
                    <h3 className={`schedule-name ${schedule.isLoading ? 'skeleton' : ''}`}>
                      {schedule.isLoading ? (
                        <div className="skeleton-bar skeleton-schedule-name"></div>
                      ) : (
                        schedule.name
                      )}
                    </h3>
                    <div className="schedule-meta">
                      <span className={`course-count ${schedule.isLoading ? 'skeleton' : ''}`}>
                        {schedule.isLoading ? (
                          <div className="skeleton-bar skeleton-meta"></div>
                        ) : (
                          `${schedule.courseCount} courses`
                        )}
                      </span>
                      <span className={`schedule-date ${schedule.isLoading ? 'skeleton' : ''}`}>
                        {schedule.isLoading ? (
                          <div className="skeleton-bar skeleton-meta"></div>
                        ) : (
                          schedule.created
                        )}
                      </span>
                    </div>
                  </div>
                  <div className="schedule-actions">
                    <span className={`status-badge ${schedule.status} ${schedule.isLoading ? 'skeleton' : ''}`}>
                      {schedule.isLoading ? (
                        <div className="skeleton-bar skeleton-status"></div>
                      ) : (
                        schedule.status
                      )}
                    </span>
                    <div className="schedule-buttons">
                      <button 
                        className={`schedule-action secondary ${schedule.isLoading ? 'loading' : ''}`}
                        onClick={() => !schedule.isLoading && handleViewEnhancedSchedule(schedule)}
                        disabled={schedule.isLoading}
                        title="View Enhanced Schedule"
                      >
                        {schedule.isLoading ? '...' : '✨'}
                      </button>
                      <button 
                        className={`schedule-action primary ${schedule.isLoading ? 'loading' : ''}`}
                        onClick={() => !schedule.isLoading && handleOpenSchedule(schedule)}
                        disabled={schedule.isLoading}
                      >
                        {schedule.isLoading ? '...' : 'Edit'}
                      </button>
                    </div>
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

        {user && (
          <div className="content-section">
            <div className="section-header">
              <h2 className="section-title">Recent Activity</h2>
            </div>
            <div className="activity-list">
              {isActivityLoading ? (
                // Show skeleton loading for activity
                Array.from({ length: 3 }).map((_, index) => (
                  <div key={`loading-${index}`} className="activity-item loading">
                    <div className="activity-dot skeleton"></div>
                    <div className="activity-content">
                      <div className="activity-action skeleton">
                        <div className="skeleton-bar" style={{ width: '200px', height: '1rem' }}></div>
                      </div>
                      <div className="activity-time skeleton">
                        <div className="skeleton-bar" style={{ width: '100px', height: '0.875rem' }}></div>
                      </div>
                    </div>
                  </div>
                ))
              ) : recentActivity.length > 0 ? (
                recentActivity.slice(0, 5).map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className={`activity-dot ${activity.success ? 'success' : 'error'}`}></div>
                    <div className="activity-content">
                      <div className="activity-action">{activity.action}</div>
                      <div className="activity-time">{activity.time}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="activity-item">
                  <div className="activity-dot success"></div>
                  <div className="activity-content">
                    <div className="activity-action">No recent activity</div>
                    <div className="activity-time">Start creating schedules to see activity</div>
                  </div>
                </div>
              )}
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