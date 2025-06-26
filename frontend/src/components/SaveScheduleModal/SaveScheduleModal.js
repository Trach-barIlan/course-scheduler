import React, { useState } from 'react';
import './SaveScheduleModal.css';

const SaveScheduleModal = ({ isOpen, onClose, onSave, schedule, user, authToken }) => {
  const [scheduleName, setScheduleName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!scheduleName.trim()) {
      setError('Please enter a schedule name');
      return;
    }

    if (!user) {
      const errorMessage = 'You must be logged in to save schedules';
      setError(errorMessage);
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      console.log('🔄 Starting save process...');

      // Step 1: Verify current authentication status
      console.log('📋 Step 1: Verifying authentication...');
      const authCheck = await fetch(API_BASE_URL + '/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });

      if (!authCheck.ok) {
        console.log('❌ Auth check failed, user may need to sign in again');
        const errorMessage = 'Your session has expired. Please refresh the page and sign in again.';
        setError(errorMessage);
        return;
      }

      const authData = await authCheck.json();
      console.log('✅ Authentication verified for user:', authData.user?.username);

      // Step 2: Save the schedule
      console.log('💾 Step 2: Saving schedule...');
      const response = await fetch(API_BASE_URL + '/api/schedules/save', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: scheduleName.trim(),
          description: description.trim(),
          schedule: schedule,
          isPublic: isPublic,
          constraints: []
        })
      });

      console.log('Save response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Save successful:', data);
        
        onSave(data.schedule);
        onClose();
        
        // Reset form
        setScheduleName('');
        setDescription('');
        setIsPublic(false);
      } else {
        const errorData = await response.json();
        console.error('❌ Save failed:', errorData);
        
        const errorMessage = response.status === 401 
          ? 'Your session has expired. Please refresh the page and sign in again.'
          : errorData.error || 'Failed to save schedule';
        
        setError(errorMessage);
      }
    } catch (err) {
      console.error('❌ Error saving schedule:', err);
      const errorMessage = 'Failed to save schedule. Please check your connection and try again.';
      setError(errorMessage);
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