import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import ScheduleViewer from '../components/ScheduleViewer/ScheduleViewer';
import './ScheduleViewerPage.css';

const ScheduleViewerPage = ({ user, authToken }) => {
  const { scheduleId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [schedule, setSchedule] = useState(null);
  const [scheduleName, setScheduleName] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

  const loadScheduleFromAPI = useCallback(async () => {
    if (!user || !authToken) {
      setError('Please log in to view saved schedules');
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/schedules/${scheduleId}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to load schedule: ${response.status}`);
      }

      const data = await response.json();
      setSchedule(data.schedule_data);
      setScheduleName(data.schedule_name || 'Saved Schedule');
    } catch (err) {
      console.error('Error loading schedule:', err);
      setError(`Failed to load schedule: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [user, authToken, scheduleId, API_BASE_URL]);

  useEffect(() => {
    // Check if schedule data was passed via state (from generation page)
    if (location.state?.schedule) {
      setSchedule(location.state.schedule);
      setScheduleName(location.state.scheduleName || 'Generated Schedule');
      setIsLoading(false);
      return;
    }

    // If no schedule in state and no scheduleId, show error
    if (!scheduleId) {
      setError('No schedule to display');
      setIsLoading(false);
      return;
    }

    // Load schedule from API if scheduleId is provided
    loadScheduleFromAPI();
  }, [scheduleId, location.state, loadScheduleFromAPI]);

  const handleBackClick = () => {
    // Go back to where they came from, or dashboard if no referrer
    if (location.state?.from) {
      navigate(location.state.from);
    } else {
      navigate('/dashboard');
    }
  };

  const handleEditSchedule = () => {
    // Navigate to scheduler page with this schedule data
    navigate('/scheduler', {
      state: {
        schedule,
        scheduleName,
        scheduleId
      }
    });
  };

  if (isLoading) {
    return (
      <div className="schedule-viewer-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h3>Loading Schedule...</h3>
          <p>Preparing your schedule visualization</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="schedule-viewer-page">
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h3>Unable to Load Schedule</h3>
          <p>{error}</p>
          <button className="back-button" onClick={handleBackClick}>
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="schedule-viewer-page">
      <div className="page-header">
        <div className="header-left">
          <button className="back-button" onClick={handleBackClick}>
            ← Back
          </button>
          <div className="page-title">
            <h1>Schedule Viewer</h1>
            <p>Enhanced visualization of your course schedule</p>
          </div>
        </div>
        
        <div className="header-actions">
          {scheduleId && (
            <button className="edit-button" onClick={handleEditSchedule}>
              ✏️ Edit Schedule
            </button>
          )}
          <button 
            className="share-button"
            onClick={() => {
              // Copy current URL to clipboard
              navigator.clipboard.writeText(window.location.href);
              // You could show a toast notification here
              alert('Schedule URL copied to clipboard!');
            }}
          >
            🔗 Share
          </button>
        </div>
      </div>

      <div className="schedule-content">
        <ScheduleViewer 
          schedule={schedule}
          title={scheduleName}
        />
      </div>
    </div>
  );
};

export default ScheduleViewerPage;
