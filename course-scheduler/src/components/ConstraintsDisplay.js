import React from 'react';
import '../styles/ConstraintsDisplay.css';

const ConstraintsDisplay = ({ parsedConstraints }) => {
  if (!parsedConstraints || !parsedConstraints.constraints || parsedConstraints.constraints.length === 0) {
    return null;
  }

  const getConstraintIcon = (type) => {
    switch (type) {
      case 'No Class Before':
        return '🌅';
      case 'No Class After':
        return '🌙';
      case 'No Class Day':
        return '📅';
      case 'Avoid TA':
        return '👤';
      default:
        return '📋';
    }
  };

  const formatConstraintText = (constraint) => {
    switch (constraint.type) {
      case 'No Class Before':
        return `No classes before ${constraint.time}:00`;
      case 'No Class After':
        return `No classes after ${constraint.time}:00`;
      case 'No Class Day':
        return `No classes on ${constraint.day}`;
      case 'Avoid TA':
        return `Avoid TA ${constraint.name}`;
      default:
        return JSON.stringify(constraint);
    }
  };

  return (
    <div className="constraints-display">
      <div className="constraints-header">
        <h3 className="constraints-title">
          🤖 AI Interpreted Constraints
        </h3>
        <div className="constraints-count">
          {parsedConstraints.constraints.length} constraint{parsedConstraints.constraints.length !== 1 ? 's' : ''} found
        </div>
      </div>
      
      <div className="constraints-list">
        {parsedConstraints.constraints.map((constraint, index) => (
          <div key={index} className="constraint-item">
            <div className="constraint-icon">
              {getConstraintIcon(constraint.type)}
            </div>
            <div className="constraint-content">
              <div className="constraint-text">
                {formatConstraintText(constraint)}
              </div>
              <div className="constraint-type">
                {constraint.type}
              </div>
            </div>
          </div>
        ))}
      </div>

      {parsedConstraints.entities && parsedConstraints.entities.length > 0 && (
        <details className="raw-entities">
          <summary className="entities-summary">
            View Raw Entities ({parsedConstraints.entities.length})
          </summary>
          <div className="entities-list">
            {parsedConstraints.entities.map((entity, index) => (
              <div key={index} className="entity-item">
                <span className="entity-text">"{entity.specifics}"</span>
                <span className="entity-label">{entity.label}</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
};

export default ConstraintsDisplay;