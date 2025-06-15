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
      // For now, we'll save to localStorage since backend isn't fully implemented
      const savedSchedules = JSON.parse(localStorage.getItem('savedSchedules') || '[]');
      
      const newSchedule = {
        id: Date.now().toString(),
        name: scheduleName.trim(),
        description: description.trim(),
        schedule: schedule,
        isPublic: isPublic,
        userId: user.id,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      savedSchedules.push(newSchedule);
      localStorage.setItem('savedSchedules', JSON.stringify(savedSchedules));

      onSave(newSchedule);
      onClose();
      
      // Reset form
      setScheduleName('');
      setDescription('');
      setIsPublic(false);
    } catch (err) {
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