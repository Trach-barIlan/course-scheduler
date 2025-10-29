import React, { useState } from 'react';
import '../styles/ConstraintsDisplay.css';

const ConstraintsDisplay = ({ parsedConstraints, onConstraintsChange, onConstraintsUpdate }) => {
    const [showAddForm, setShowAddForm] = useState(false);
    const [isRegenerating, setIsRegenerating] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);
    const [constraints, setConstraints] = useState(parsedConstraints?.constraints || []);
    const [editingIndex, setEditingIndex] = useState(null);
    const [editForm, setEditForm] = useState({});
    const [isEditing, setIsEditing] = useState(false);
    const [addForm, setAddForm] = useState({
        type: 'No Class Before',
        time: '',
        day: '',
        name: ''
    });  React.useEffect(() => {
    if (parsedConstraints?.constraints) {
      setConstraints(parsedConstraints.constraints);
    }
  }, [parsedConstraints]);

  // Always render the component, even with zero constraints
  const notifyChange = onConstraintsChange || onConstraintsUpdate;

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
      case 'Prefer TA':
        return '⭐';
      case 'No Gap':
        return '🔗';
      case 'Max Gap':
        return '⏱️';
      default:
        return '📋';
    }
  };

  const getConstraintColor = (type) => {
    switch (type) {
      case 'No Class Before':
      case 'No Class After':
        return 'time-constraint';
      case 'No Class Day':
        return 'day-constraint';
      case 'Avoid TA':
      case 'Prefer TA':
        return 'ta-constraint';
      case 'No Gap':
      case 'Max Gap':
        return 'gap-constraint';
      default:
        return 'default-constraint';
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
      case 'Prefer TA':
        return `Prefer TA ${constraint.name}`;
      case 'No Gap':
        return `No gaps between classes`;
      case 'Max Gap':
        return `Maximum ${constraint.hours} hour gap between classes`;
      default:
        return JSON.stringify(constraint);
    }
  };

  const getConstraintDescription = (constraint) => {
    switch (constraint.type) {
      case 'No Class Before':
        return 'Schedule will avoid any classes starting before this time';
      case 'No Class After':
        return 'Schedule will avoid any classes ending after this time';
      case 'No Class Day':
        return 'No classes will be scheduled on this day';
      case 'Avoid TA':
        return 'Will try to avoid this specific TA when possible';
      case 'Prefer TA':
        return 'Will prioritize this TA when multiple options are available';
      case 'No Gap':
        return 'Classes will be scheduled back-to-back without breaks';
      case 'Max Gap':
        return 'Limits the maximum time between consecutive classes';
      default:
        return 'Custom scheduling constraint';
    }
  };

  const handleEdit = (index) => {
    setEditingIndex(index);
    setEditForm({ ...constraints[index] });
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    const newConstraints = [...constraints];
    newConstraints[editingIndex] = editForm;
    setConstraints(newConstraints);
    setEditingIndex(null);
    setEditForm({});
    setIsEditing(false);
    
    // Notify parent component
    if (notifyChange) {
      notifyChange(newConstraints);
    }
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditForm({});
    setIsEditing(false);
  };

  const handleDelete = (index) => {
    const newConstraints = constraints.filter((_, i) => i !== index);
    setConstraints(newConstraints);
    
    // Notify parent component
    if (notifyChange) {
      notifyChange(newConstraints);
    }
  };

  const handleAdd = () => {
    if (validateAddForm()) {
      const newConstraint = { ...addForm };
      // Clean up the constraint based on type
      if (newConstraint.type === 'No Class Before' || newConstraint.type === 'No Class After') {
        delete newConstraint.day;
        delete newConstraint.name;
        newConstraint.time = parseInt(newConstraint.time);
      } else if (newConstraint.type === 'No Class Day') {
        delete newConstraint.time;
        delete newConstraint.name;
      } else if (newConstraint.type === 'Avoid TA' || newConstraint.type === 'Prefer TA') {
        delete newConstraint.time;
        delete newConstraint.day;
      }
      
      const newConstraints = [...constraints, newConstraint];
      setConstraints(newConstraints);
      setAddForm({
        type: 'No Class Before',
        time: '',
        day: '',
        name: ''
      });
      setShowAddForm(false);
      
      // Notify parent component
      if (notifyChange) {
        notifyChange(newConstraints);
      }
    }
  };

  const validateAddForm = () => {
    if (addForm.type === 'No Class Before' || addForm.type === 'No Class After') {
      return addForm.time && !isNaN(addForm.time) && addForm.time >= 0 && addForm.time <= 23;
    } else if (addForm.type === 'No Class Day') {
      return addForm.day && addForm.day.trim() !== '';
    } else if (addForm.type === 'Avoid TA' || addForm.type === 'Prefer TA') {
      return addForm.name && addForm.name.trim() !== '';
    }
    return false;
  };

  const handleRegenerateSchedule = async () => {
    if (onConstraintsChange) {
      setIsRegenerating(true);
      try {
        await onConstraintsChange(constraints);
      } finally {
        setIsRegenerating(false);
      }
    }
  };

  const renderEditForm = (constraint, index) => {
    if (editingIndex !== index) return null;

    return (
      <div className="edit-form">
        <div className="edit-form-content">
          <div className="form-group">
            <label>Type:</label>
            <select
              value={editForm.type || ''}
              onChange={(e) => setEditForm({ ...editForm, type: e.target.value })}
            >
              <option value="No Class Before">No Class Before</option>
              <option value="No Class After">No Class After</option>
              <option value="No Class Day">No Class Day</option>
              <option value="Avoid TA">Avoid TA</option>
              <option value="Prefer TA">Prefer TA</option>
            </select>
          </div>

          {(editForm.type === 'No Class Before' || editForm.type === 'No Class After') && (
            <div className="form-group">
              <label>Time (24-hour):</label>
              <input
                type="number"
                min="0"
                max="23"
                value={editForm.time || ''}
                onChange={(e) => setEditForm({ ...editForm, time: parseInt(e.target.value) })}
                placeholder="e.g., 9 for 9:00"
              />
            </div>
          )}

          {editForm.type === 'No Class Day' && (
            <div className="form-group">
              <label>Day:</label>
              <select
                value={editForm.day || ''}
                onChange={(e) => setEditForm({ ...editForm, day: e.target.value })}
              >
                <option value="">Select Day</option>
                <option value="Sun">Sunday</option>
                <option value="Mon">Monday</option>
                <option value="Tue">Tuesday</option>
                <option value="Wed">Wednesday</option>
                <option value="Thu">Thursday</option>
                <option value="Fri">Friday</option>
                <option value="Sat">Saturday</option>
              </select>
            </div>
          )}

          {(editForm.type === 'Avoid TA' || editForm.type === 'Prefer TA') && (
            <div className="form-group">
              <label>TA Name:</label>
              <input
                type="text"
                value={editForm.name || ''}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                placeholder="Enter TA name"
              />
            </div>
          )}
        </div>

        <div className="edit-form-actions">
          <button className="save-btn" onClick={handleSaveEdit}>
            ✓ Save
          </button>
          <button className="cancel-btn" onClick={handleCancelEdit}>
            ✕ Cancel
          </button>
        </div>
      </div>
    );
  };

  const renderAddForm = () => {
    if (!showAddForm) return null;

    return (
      <div className="add-form">
        <div className="add-form-header">
          <h4>Add New Constraint</h4>
        </div>
        
        <div className="add-form-content">
          <div className="form-group">
            <label>Type:</label>
            <select
              value={addForm.type}
              onChange={(e) => setAddForm({ ...addForm, type: e.target.value })}
            >
              <option value="No Class Before">No Class Before</option>
              <option value="No Class After">No Class After</option>
              <option value="No Class Day">No Class Day</option>
              <option value="Avoid TA">Avoid TA</option>
              <option value="Prefer TA">Prefer TA</option>
            </select>
          </div>

          {(addForm.type === 'No Class Before' || addForm.type === 'No Class After') && (
            <div className="form-group">
              <label>Time (24-hour):</label>
              <input
                type="number"
                min="0"
                max="23"
                value={addForm.time}
                onChange={(e) => setAddForm({ ...addForm, time: e.target.value })}
                placeholder="e.g., 9 for 9:00"
              />
            </div>
          )}

          {addForm.type === 'No Class Day' && (
            <div className="form-group">
              <label>Day:</label>
              <select
                value={addForm.day}
                onChange={(e) => setAddForm({ ...addForm, day: e.target.value })}
              >
                <option value="">Select Day</option>
                <option value="Sun">Sunday</option>
                <option value="Mon">Monday</option>
                <option value="Tue">Tuesday</option>
                <option value="Wed">Wednesday</option>
                <option value="Thu">Thursday</option>
                <option value="Fri">Friday</option>
                <option value="Sat">Saturday</option>
              </select>
            </div>
          )}

          {(addForm.type === 'Avoid TA' || addForm.type === 'Prefer TA') && (
            <div className="form-group">
              <label>TA Name:</label>
              <input
                type="text"
                value={addForm.name}
                onChange={(e) => setAddForm({ ...addForm, name: e.target.value })}
                placeholder="Enter TA name"
              />
            </div>
          )}
        </div>

        <div className="add-form-actions">
          <button 
            className="add-constraint-btn" 
            onClick={handleAdd}
            disabled={!validateAddForm()}
          >
            ✓ Add Constraint
          </button>
          <button className="cancel-add-btn" onClick={() => setShowAddForm(false)}>
            ✕ Cancel
          </button>
        </div>
      </div>
    );
  };

  return (
        <div 
          className={`constraints-display ${isExpanded ? 'expanded' : 'collapsed'}`}
          onClick={!isExpanded ? () => setIsExpanded(true) : undefined}
          style={{ cursor: !isExpanded ? 'pointer' : 'default' }}
        >
            <div className="constraints-header">
                <div className="constraints-title-section">
                    <h3 className="constraints-title">
                        Scheduling Constraints
                    </h3>
                    <p className="constraints-subtitle">
                        AI-parsed preferences and requirements from your input
                    </p>
                    {!isExpanded && (
                        <div className="constraints-summary">
                            {constraints.length > 0 ? (
                                <div>
                                    <span className="summary-text">
                                        {constraints.length} constraint{constraints.length !== 1 ? 's' : ''} found
                                        {constraints.some(c => c.type === 'No Class Before' || c.type === 'No Class After') && ' • Time preferences'}
                                        {constraints.some(c => c.type === 'No Class Day') && ' • Day preferences'}
                                        {constraints.some(c => c.type === 'Avoid TA' || c.type === 'Prefer TA') && ' • TA preferences'}
                                        {constraints.some(c => c.type === 'No Gap' || c.type === 'Max Gap') && ' • Gap constraints'}
                                    </span>
                                    <div className="constraints-preview">
                                        {constraints.slice(0, 3).map((constraint, index) => (
                                            <div key={index} className="constraint-preview-item">
                                                <span className="preview-icon">{getConstraintIcon(constraint.type)}</span>
                                                <span className="preview-text">{formatConstraintText(constraint)}</span>
                                            </div>
                                        ))}
                                        {constraints.length > 3 && (
                                            <div className="constraint-preview-more">
                                                +{constraints.length - 3} more constraint{constraints.length - 3 !== 1 ? 's' : ''}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                <span className="summary-text">No constraints found</span>
                            )}
                        </div>
                    )}
                </div>
                <div className="constraints-count">
                    {constraints.length} Found
                </div>
            </div>

            <button
                type="button"
                className="expand-toggle-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsExpanded(!isExpanded);
                }}
                title={isExpanded ? "Collapse constraints" : "Expand constraints"}
            >
                {isExpanded ? "▲ Collapse" : "▼ View Constraints"}
            </button>

            {isExpanded && (
            <div>
      <div className="constraints-controls top">
        {!showAddForm && !isEditing && (
          <button 
            className="add-new-btn" 
            onClick={() => setShowAddForm(true)}
          >
            ➕ Add New Constraint
          </button>
        )}
        
        <button 
          className="regenerate-btn" 
          onClick={handleRegenerateSchedule}
          disabled={isRegenerating || isEditing || showAddForm}
        >
          {isRegenerating ? (
            <>
              <div className="loading-spinner"></div>
              Regenerating...
            </>
          ) : (
            <>
              🔄 Update Schedule
            </>
          )}
        </button>
      </div>

      {renderAddForm()}

      <div className="constraints-list">
        {constraints.map((constraint, index) => (
          <div key={index} className={`constraint-item ${getConstraintColor(constraint.type)}`}>
            <div className="constraint-icon">
              {getConstraintIcon(constraint.type)}
            </div>
            <div className="constraint-content">
              <div className="constraint-main">
                <div className="constraint-text">
                  {formatConstraintText(constraint)}
                </div>
                <div className="constraint-type-badge">
                  {constraint.type}
                </div>
              </div>
              <div className="constraint-description">
                {getConstraintDescription(constraint)}
              </div>
              {renderEditForm(constraint, index)}
            </div>
            {!isEditing && (
              <div className="constraint-actions">
                <button 
                  className="edit-btn" 
                  onClick={() => handleEdit(index)}
                  title="Edit constraint"
                >
                  ✏️
                </button>
                <button 
                  className="delete-btn" 
                  onClick={() => handleDelete(index)}
                  title="Delete constraint"
                >
                  🗑️
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      </div>
      )}
      
    </div>
  );
};

export default ConstraintsDisplay;