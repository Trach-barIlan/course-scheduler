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
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

  // Determine if this is a saved schedule or a new one
  const isExistingSchedule = Boolean(scheduleId);
  const isNewSchedule = Boolean(location.state?.schedule && !scheduleId);

  // Handle schedule updates from ScheduleViewer
  const handleScheduleUpdate = useCallback(async (updatedSchedule) => {
    try {
      // Update local state immediately
      setSchedule(updatedSchedule);
      
      // Clear any save errors since the schedule has changed
      setSaveError(null);
      
      // If you want to auto-save changes to the API, uncomment the following:
      /*
      if (user && authToken && scheduleId) {
        await fetch(`${API_BASE_URL}/api/schedules/${scheduleId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            schedule: updatedSchedule,
            name: scheduleName
          })
        });
      }
      */
    } catch (error) {
      console.error('❌ Error updating schedule:', error);
    }
  }, []); // Empty dependency array since we're only using setSchedule and setSaveError

  // Save new schedule or update existing one
  const handleSaveSchedule = useCallback(async () => {
    if (!user || !authToken) {
      setSaveError('Please log in to save schedules');
      return;
    }

    if (!schedule) {
      setSaveError('No schedule to save');
      return;
    }

    try {
      setIsSaving(true);
      setSaveError(null);

      const endpoint = isExistingSchedule 
        ? `${API_BASE_URL}/api/schedules/${scheduleId}`
        : `${API_BASE_URL}/api/schedules`;
      
      const method = isExistingSchedule ? 'PUT' : 'POST';

      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          schedule_data: schedule,
          schedule_name: scheduleName || 'Untitled Schedule',
          user_id: user.id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to ${isExistingSchedule ? 'update' : 'save'} schedule`);
      }

      const data = await response.json();
      
      // If this was a new schedule, redirect to the saved schedule URL
      if (!isExistingSchedule && data.schedule_id) {
        navigate(`/schedule-viewer/${data.schedule_id}`, { replace: true });
      }

    } catch (err) {
      console.error(`Error ${isExistingSchedule ? 'updating' : 'saving'} schedule:`, err);
      setSaveError(`Failed to ${isExistingSchedule ? 'update' : 'save'} schedule: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  }, [user, authToken, schedule, scheduleName, isExistingSchedule, scheduleId, API_BASE_URL, navigate]);

  // Handle schedule name changes
  const handleScheduleNameChange = (newName) => {
    setScheduleName(newName);
    setSaveError(null); // Clear any previous save errors
  };

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
    try {
      // Go back to where they came from with proper state preservation
      if (location.state?.from) {
        // If coming from scheduler, preserve the courses and state
        if (location.state.from === '/scheduler' && location.state.schedulerState) {
          navigate('/scheduler', {
            state: {
              preserveState: true,
              ...location.state.schedulerState
            }
          });
        } else if (location.state.from === '/' || location.state.from === '/dashboard') {
          // Handle both home page and any dashboard references
          navigate('/', { replace: true });
        } else {
          // Navigate back to the specified page
          navigate(location.state.from, { replace: true });
        }
      } else {
        // Default fallback - always go home
        navigate('/', { replace: true });
      }
    } catch (error) {
      console.error('Navigation error:', error);
      // Ultimate fallback - just go home
      window.location.href = '/';
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
      {/* Page header/banner removed to declutter the enhanced schedule viewer */}

      {/* Save error display */}
      {saveError && (
        <div className="error-message">
          <span className="error-icon">❌</span>
          {saveError}
        </div>
      )}

      <div className="schedule-content">
        <ScheduleViewer 
          schedule={schedule}
          title={scheduleName}
          onScheduleUpdate={handleScheduleUpdate}
          backButton={
            <button className="back-button" onClick={handleBackClick}>
              ← Back
            </button>
          }
          allowMove={false}
        />
      </div>
    </div>
  );
};

export default ScheduleViewerPage;
