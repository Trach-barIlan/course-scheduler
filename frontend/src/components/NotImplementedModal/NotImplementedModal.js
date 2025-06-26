import React from 'react';
import './NotImplementedModal.css';

const NotImplementedModal = ({ isOpen, onClose, feature, description }) => {
  if (!isOpen) return null;

  const features = {
    'templates': {
      icon: '📋',
      title: 'Schedule Templates',
      description: 'Pre-made templates for common degree programs',
      comingSoon: 'Coming in v2.1'
    },
    'import': {
      icon: '📤',
      title: 'Import Schedule',
      description: 'Upload and optimize existing schedules',
      comingSoon: 'Coming in v2.1'
    },
    'export-calendar': {
      icon: '📅',
      title: 'Export to Calendar',
      description: 'Export your schedule to Google Calendar, Outlook, etc.',
      comingSoon: 'Coming in v1.5'
    },
    'collaboration': {
      icon: '👥',
      title: 'Schedule Collaboration',
      description: 'Share and collaborate on schedules with classmates',
      comingSoon: 'Coming in v2.3'
    },
    'ai-suggestions': {
      icon: '🤖',
      title: 'AI Schedule Suggestions',
      description: 'Get personalized schedule recommendations',
      comingSoon: 'Coming in v2.0'
    }
  };

  const featureInfo = features[feature] || {
    icon: '🚧',
    title: 'Feature Not Available',
    description: description || 'This feature is currently under development',
    comingSoon: 'Coming Soon'
  };

  return (
    <div className="not-implemented-overlay">
      <div className="not-implemented-container">
        <div className="not-implemented-header">
          <div className="feature-icon">{featureInfo.icon}</div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="not-implemented-content">
          <h2 className="feature-title">{featureInfo.title}</h2>
          <p className="feature-description">{featureInfo.description}</p>
          
          <div className="status-badge">
            <span className="status-icon">⏳</span>
            {featureInfo.comingSoon}
          </div>

          <div className="feature-preview">
            <h3>What to expect:</h3>
            <ul className="preview-list">
              {feature === 'saved-schedules' && (
                <>
                  <li>Save unlimited schedules to your account</li>
                  <li>Organize schedules by semester and year</li>
                  <li>Quick access to frequently used schedules</li>
                  <li>Share schedules with friends and advisors</li>
                </>
              )}
              {feature === 'templates' && (
                <>
                  <li>Pre-built templates for popular majors</li>
                  <li>Customizable template library</li>
                  <li>Community-shared templates</li>
                  <li>Smart template recommendations</li>
                </>
              )}
              {feature === 'analytics' && (
                <>
                  <li>Schedule optimization insights</li>
                  <li>Time utilization analytics</li>
                  <li>Productivity pattern analysis</li>
                  <li>Semester comparison reports</li>
                </>
              )}
              {feature === 'import' && (
                <>
                  <li>Import from CSV, Excel, or PDF files</li>
                  <li>Parse existing university schedules</li>
                  <li>Automatic conflict detection</li>
                  <li>Smart schedule optimization</li>
                </>
              )}
              {feature === 'export-calendar' && (
                <>
                  <li>Export to Google Calendar</li>
                  <li>Sync with Outlook and Apple Calendar</li>
                  <li>Automatic updates when schedule changes</li>
                  <li>Custom reminder settings</li>
                </>
              )}
              {!features[feature] && (
                <>
                  <li>Enhanced functionality</li>
                  <li>Improved user experience</li>
                  <li>Advanced customization options</li>
                  <li>Seamless integration</li>
                </>
              )}
            </ul>
          </div>

          <div className="notification-signup">
            <h3>Get notified when it's ready!</h3>
            <p>We'll send you an email when this feature becomes available.</p>
            <div className="email-signup">
              <input 
                type="email" 
                placeholder="Enter your email address"
                className="email-input"
              />
              <button className="notify-button">
                🔔 Notify Me
              </button>
            </div>
          </div>
        </div>

        <div className="not-implemented-actions">
          <button className="primary-action" onClick={onClose}>
            Got it, thanks!
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotImplementedModal;