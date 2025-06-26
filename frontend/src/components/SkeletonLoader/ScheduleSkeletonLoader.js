import React from 'react';
import './ScheduleSkeletonLoader.css';

const ScheduleSkeletonLoader = ({ progress = 0, estimatedTime = 0, currentStep = '' }) => {
  const days = React.useMemo(() => ["Mon", "Tue", "Wed", "Thu", "Fri"], []);
  const hours = React.useMemo(() => Array.from({ length: 12 }, (_, i) => i + 8), []);

  // Generate random skeleton blocks to simulate schedule layout
  const skeletonBlocks = React.useMemo(() => {
    const blocks = [];
    const blockCount = Math.floor(Math.random() * 8) + 6; // 6-14 blocks
    for (let i = 0; i < blockCount; i++) {
      const day = days[Math.floor(Math.random() * days.length)];
      const startHour = hours[Math.floor(Math.random() * (hours.length - 2))];
      const duration = Math.floor(Math.random() * 3) + 1; // 1-3 hours
      const type = Math.random() > 0.5 ? 'lecture' : 'ta';
      blocks.push({
        id: i,
        day,
        startHour,
        duration,
        type,
        delay: i * 0.1 // Staggered animation
      });
    }
    return blocks;
  }, [days, hours]);

  const formatTime = (seconds) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  };

  return (
    <div className="skeleton-loader-container">
      <div className="skeleton-header">
        <div className="skeleton-title">
          <div className="skeleton-title-text"></div>
          <div className="skeleton-subtitle"></div>
        </div>
        <div className="skeleton-actions">
          <div className="skeleton-button"></div>
          <div className="skeleton-button"></div>
          <div className="skeleton-button"></div>
        </div>
      </div>

      {/* Progress Section */}
      <div className="progress-section">
        <div className="progress-header">
          <h3 className="progress-title">Generating Your Schedule</h3>
          <div className="progress-stats">
            <span className="progress-percentage">{Math.round(progress)}%</span>
            {estimatedTime > 0 && (
              <span className="estimated-time">~{formatTime(estimatedTime)} remaining</span>
            )}
          </div>
        </div>
        
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
        
        {currentStep && (
          <div className="current-step">
            <div className="step-indicator">
              <div className="step-dot active"></div>
              <div className="step-line"></div>
            </div>
            <span className="step-text">{currentStep}</span>
          </div>
        )}
      </div>

      {/* Skeleton Schedule Table */}
      <div className="skeleton-table-container">
        <table className="skeleton-table">
          <thead>
            <tr>
              <th className="skeleton-time-header">
                <div className="skeleton-text skeleton-text-sm"></div>
              </th>
              {days.map((day) => (
                <th key={day} className="skeleton-day-header">
                  <div className="skeleton-text skeleton-text-sm"></div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {hours.map((hour) => (
              <tr key={hour}>
                <td className="skeleton-time-cell">
                  <div className="skeleton-text skeleton-text-xs"></div>
                </td>
                {days.map((day) => {
                  // Check if there's a skeleton block for this cell
                  const block = skeletonBlocks.find(
                    b => b.day === day && hour >= b.startHour && hour < b.startHour + b.duration
                  );
                  
                  if (block && hour === block.startHour) {
                    return (
                      <td 
                        key={day} 
                        rowSpan={block.duration}
                        className={`skeleton-class-cell skeleton-${block.type}`}
                        style={{ animationDelay: `${block.delay}s` }}
                      >
                        <div className="skeleton-class-content">
                          <div className="skeleton-class-name"></div>
                          <div className="skeleton-class-type"></div>
                        </div>
                      </td>
                    );
                  } else if (block) {
                    // This cell is part of a multi-row block, skip it
                    return null;
                  } else {
                    return (
                      <td key={day} className="skeleton-empty-cell">
                        <div className="skeleton-empty-shimmer"></div>
                      </td>
                    );
                  }
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Loading Steps */}
      <div className="loading-steps">
        <div className="step-item">
          <div className="step-icon">🔍</div>
          <span>Analyzing course options</span>
        </div>
        <div className="step-item">
          <div className="step-icon">🧠</div>
          <span>Processing constraints</span>
        </div>
        <div className="step-item">
          <div className="step-icon">⚡</div>
          <span>Optimizing schedule</span>
        </div>
        <div className="step-item">
          <div className="step-icon">✨</div>
          <span>Finalizing layout</span>
        </div>
      </div>
    </div>
  );
};

export default ScheduleSkeletonLoader;