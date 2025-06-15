import React, { useState } from 'react';
import './SaveScheduleModal.css';

const SaveScheduleModal = ({ isOpen, onClose, onSave, schedule, user }) => {
  const [scheduleName, setScheduleName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!scheduleName.trim()) {
      setError('Please enter a schedule name');
      return;
    }

    if (!user) {
      setError('You must be logged in to save schedules');
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      console.log('Attempting to save schedule with user:', user);
      console.log('Schedule data:', schedule);

      // First, verify authentication status
      const authCheck = await fetch('http://127.0.0.1:5000/api/auth/me', {
        credentials: 'include'
      });

      if (!authCheck.ok) {
        setError('Authentication expired. Please sign in again.');
        return;
      }

      const authData = await authCheck.json();
      console.log('Auth check result:', authData);

      // Save to database via API
      const response = await fetch('http://127.0.0.1:5000/api/schedules/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: scheduleName.trim(),
          description: description.trim(),
          schedule: schedule,
          isPublic: isPublic,
          constraints: [] // TODO: Include constraints if available
        })
      });

      console.log('Save response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Save successful:', data);
        onSave(data.schedule);
        onClose();
        
        // Reset form
        setScheduleName('');
        setDescription('');
        setIsPublic(false);
      } else {
        const errorData = await response.json();
        console.error('Save failed:', errorData);
        setError(errorData.error || 'Failed to save schedule');
      }
    } catch (err) {
      console.error('Error saving schedule:', err);
      setError('Failed to save schedule. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = () => {
    setScheduleName('');
    setDescription('');
    setIsPublic(false);
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h2 className="modal-title">💾 Save Schedule</h2>
          <button className="modal-close" onClick={handleClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {/* Debug info - remove in production */}
          {process.env.NODE_ENV === 'development' && (
            <div className="debug-info" style={{ 
              background: '#f0f0f0', 
              padding: '10px', 
              marginBottom: '15px', 
              fontSize: '12px',
              borderRadius: '5px'
            }}>
              <strong>Debug Info:</strong><br/>
              User: {user ? `${user.first_name} (ID: ${user.id})` : 'Not logged in'}<br/>
              Schedule: {schedule ? `${schedule.length} courses` : 'No schedule'}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="scheduleName">Schedule Name *</label>
            <input
              type="text"
              id="scheduleName"
              value={scheduleName}
              onChange={(e) => setScheduleName(e.target.value)}
              placeholder="e.g., Fall 2024 - Computer Science"
              className={error && !scheduleName.trim() ? 'error' : ''}
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description (Optional)</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add notes about this schedule..."
              rows={3}
              maxLength={500}
            />
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
              />
              <span className="checkbox-custom"></span>
              Make this schedule public (others can view and copy)
            </label>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="modal-actions">
            <button 
              type="button" 
              className="cancel-button"
              onClick={handleClose}
              disabled={isSaving}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="save-button"
              disabled={isSaving || !scheduleName.trim()}
            >
              {isSaving ? (
                <>
                  <div className="loading-spinner"></div>
                  Saving...
                </>
              ) : (
                <>
                  💾 Save Schedule
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SaveScheduleModal;