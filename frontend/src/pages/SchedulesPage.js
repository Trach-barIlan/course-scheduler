import React, { useState, useEffect } from 'react';
import '../styles/SchedulesPage.css';

const SchedulesPage = ({ user }) => {
  const [savedSchedules, setSavedSchedules] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSchedule, setSelectedSchedule] = useState(null);

  useEffect(() => {
    // Simulate loading saved schedules
    // In a real app, this would fetch from your backend
    setTimeout(() => {
      setSavedSchedules([
        {
          id: 1,
          name: "Fall 2024 Schedule",
          created_at: "2024-01-15T10:30:00Z",
          courses: [
            { name: "CS101", lecture: "Mon 9-11", ta: "Wed 14-16" },
            { name: "MATH201", lecture: "Tue 10-12", ta: "Thu 15-17" }
          ]
        },
        {
          id: 2,
          name: "Spring 2024 Schedule",
          created_at: "2024-01-10T14:20:00Z",
          courses: [
            { name: "PHYS101", lecture: "Mon 14-16", ta: "Fri 10-12" },
            { name: "CHEM101", lecture: "Wed 9-11", ta: "Tue 13-15" }
          ]
        }
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDeleteSchedule = (scheduleId) => {
    setSavedSchedules(prev => prev.filter(s => s.id !== scheduleId));
  };

  const handleViewSchedule = (schedule) => {
    setSelectedSchedule(schedule);
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
                <h3 className="schedule-name">{schedule.name}</h3>
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
                  <strong>{schedule.courses.length} courses:</strong>
                  <ul>
                    {schedule.courses.map((course, index) => (
                      <li key={index}>{course.name}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedSchedule && (
        <div className="schedule-modal-overlay" onClick={() => setSelectedSchedule(null)}>
          <div className="schedule-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedSchedule.name}</h2>
              <button 
                className="close-btn"
                onClick={() => setSelectedSchedule(null)}
              >
                ×
              </button>
            </div>
            <div className="modal-content">
              <div className="schedule-details">
                {selectedSchedule.courses.map((course, index) => (
                  <div key={index} className="course-detail">
                    <h4>{course.name}</h4>
                    <div className="course-times">
                      <div className="time-slot">
                        <span className="time-label">Lecture:</span>
                        <span className="time-value">{course.lecture}</span>
                      </div>
                      <div className="time-slot">
                        <span className="time-label">TA Session:</span>
                        <span className="time-value">{course.ta}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SchedulesPage;