import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import WeeklyScheduler from '../components/WeeklyScheduler';
import '../styles/SchedulesPage.css';

const SchedulesPage = ({ user, authToken }) => {
  const location = useLocation();
  const [savedSchedules, setSavedSchedules] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [showScheduleView, setShowScheduleView] = useState(false);
  
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  // בדוק אם יש מערכת שנשלחה מ-Dashboard
  useEffect(() => {
    if (location.state?.selectedSchedule) {
      setSelectedSchedule(location.state.selectedSchedule);
      setShowScheduleView(true);
    }
  }, [location.state]);

  // טען מערכות שמורות מה-backend
  useEffect(() => {
    const fetchSavedSchedules = async () => {
      if (!user || !authToken) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/schedules/list`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          }
        });

        if (response.ok) {
          const data = await response.json();
          setSavedSchedules(data.schedules || []);
        } else {
          console.error('Failed to fetch schedules:', response.status);
          // Fallback to sample data
          setSavedSchedules([
            {
              id: 1,
              schedule_name: "Fall 2024 Schedule",
              created_at: "2024-01-15T10:30:00Z",
              schedule_data: [
                { name: "CS101", lecture: "Mon 9-11", ta: "Wed 14-16" },
                { name: "MATH201", lecture: "Tue 10-12", ta: "Thu 15-17" }
              ]
            }
          ]);
        }
      } catch (error) {
        console.error('Error fetching schedules:', error);
        setSavedSchedules([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSavedSchedules();
  }, [user, authToken, API_BASE_URL]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (!confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/schedules/${scheduleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        setSavedSchedules(prev => prev.filter(s => s.id !== scheduleId));
      } else {
        alert('Failed to delete schedule. Please try again.');
      }
    } catch (error) {
      console.error('Error deleting schedule:', error);
      alert('Failed to delete schedule. Please check your connection.');
    }
  };

  const handleViewSchedule = async (schedule) => {
    // אם יש כבר נתוני מערכת, הצג אותם
    if (schedule.schedule_data) {
      setSelectedSchedule(schedule);
      setShowScheduleView(true);
      return;
    }

    // אחרת, טען מה-backend
    try {
      const response = await fetch(`${API_BASE_URL}/api/schedules/${schedule.id}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedSchedule(data.schedule);
        setShowScheduleView(true);
      } else {
        alert('Failed to load schedule. Please try again.');
      }
    } catch (error) {
      console.error('Error fetching schedule:', error);
      alert('Failed to load schedule. Please check your connection.');
    }
  };

  const handleCloseScheduleView = () => {
    setShowScheduleView(false);
    setSelectedSchedule(null);
  };

  if (!user) {
    return (
      <div className="schedules-page">
        <div className="auth-required">
          <div className="auth-required-icon">🔒</div>
          <h2>Sign In Required</h2>
          <p>Please sign in to view and manage your saved schedules.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="schedules-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your schedules...</p>
        </div>
      </div>
    );
  }

  // הצג את המערכת הנבחרת
  if (showScheduleView && selectedSchedule) {
    return (
      <div className="schedules-page">
        <div className="schedule-view-header">
          <button 
            className="back-button"
            onClick={handleCloseScheduleView}
          >
            ← Back to Schedules
          </button>
          <h1>{selectedSchedule.schedule_name || 'Schedule View'}</h1>
          <div className="schedule-meta">
            Created: {formatDate(selectedSchedule.created_at)}
          </div>
        </div>
        
        <WeeklyScheduler 
          user={user} 
          authToken={authToken} 
          schedule={selectedSchedule.schedule_data} 
          isLoading={false}
        />
      </div>
    );
  }

  return (
    <div className="schedules-page">
      <div className="schedules-header">
        <h1>My Schedules</h1>
        <p>Manage and view your saved course schedules</p>
      </div>

      {savedSchedules.length === 0 ? (
        <div className="empty-schedules">
          <div className="empty-icon">📅</div>
          <h3>No Saved Schedules</h3>
          <p>You haven't saved any schedules yet. Create a schedule in the Schedule Builder to get started!</p>
        </div>
      ) : (
        <div className="schedules-grid">
          {savedSchedules.map(schedule => (
            <div key={schedule.id} className="schedule-card">
              <div className="schedule-card-header">
                <h3 className="schedule-name">{schedule.schedule_name}</h3>
                <div className="schedule-actions">
                  <button 
                    className="action-btn view-btn"
                    onClick={() => handleViewSchedule(schedule)}
                    title="View Schedule"
                  >
                    👁️
                  </button>
                  <button 
                    className="action-btn delete-btn"
                    onClick={() => handleDeleteSchedule(schedule.id)}
                    title="Delete Schedule"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              
              <div className="schedule-info">
                <div className="schedule-date">
                  Created: {formatDate(schedule.created_at)}
                </div>
                <div className="schedule-courses">
                  <strong>
                    {Array.isArray(schedule.schedule_data) 
                      ? schedule.schedule_data.length 
                      : 'Unknown'} courses
                  </strong>
                  {Array.isArray(schedule.schedule_data) && (
                    <ul>
                      {schedule.schedule_data.slice(0, 3).map((course, index) => (
                        <li key={index}>{course.name}</li>
                      ))}
                      {schedule.schedule_data.length > 3 && (
                        <li>+{schedule.schedule_data.length - 3} more...</li>
                      )}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SchedulesPage;