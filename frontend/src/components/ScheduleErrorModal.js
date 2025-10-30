import React from 'react';
import './ScheduleErrorModal.css';

const ScheduleErrorModal = ({ isOpen, onClose, error, onTryAgain, user, onAuthClick }) => {
  if (!isOpen || !error) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Special sentinel for auth-required flow
  const isAuthRequired = error === 'AUTH_REQUIRED';
  const isConstraintError = String(error).includes('No valid schedule found');
  const isNetworkError = String(error).includes('connect to the server') || String(error).includes('NetworkError');

  return (
    <div className="schedule-error-modal-overlay" onClick={handleOverlayClick}>
      <div className="schedule-error-modal">
        <div className="schedule-error-modal-header">
          <div className="error-icon">
            {isNetworkError ? '🌐' : '⚠️'}
          </div>
          <h3 className="error-title">
            {isNetworkError ? 'Connection Error' : isAuthRequired ? 'Sign In Required' : 'Schedule Generation Failed'}
          </h3>
          <button className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="schedule-error-modal-body">
          <p className="error-description">
            {isAuthRequired && !user
              ? 'You are currently not signed in. Please sign in to use the AI constraints parsing feature.'
              : error}
          </p>

          {isConstraintError && (
            <div className="error-suggestions">
              <h4>💡 Try these solutions:</h4>
              <ul>
                <li>Remove some course options to reduce conflicts</li>
                <li>Adjust your time preferences (allow more time slots)</li>
                <li>Consider removing strict constraints like "no back-to-back classes"</li>
                <li>Check if any courses have overlapping required times</li>
                <li>Reduce the number of courses if you have too many selected</li>
              </ul>
            </div>
          )}

          {isNetworkError && (
            <div className="error-suggestions">
              <h4>🔧 Try these solutions:</h4>
              <ul>
                <li>Check your internet connection</li>
                <li>Refresh the page and try again</li>
                <li>Make sure the backend server is running</li>
                <li>Contact support if the problem persists</li>
              </ul>
            </div>
          )}
        </div>

        <div className="schedule-error-modal-footer">
          <button className="modal-btn modal-btn-secondary" onClick={onClose}>
            Cancel
          </button>
          {isAuthRequired && !user && onAuthClick && (
            <button
              className="modal-btn modal-btn-primary"
              onClick={() => {
                onAuthClick();
                onClose();
              }}
            >
              Sign In
            </button>
          )}
          {onTryAgain && !isAuthRequired && (
            <button className="modal-btn modal-btn-primary" onClick={() => {
              onClose();
              onTryAgain();
            }}>
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScheduleErrorModal;
