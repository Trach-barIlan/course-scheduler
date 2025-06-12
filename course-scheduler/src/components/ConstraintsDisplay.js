import React, { useState } from 'react';
import '../styles/ConstraintsDisplay.css';

const ConstraintsDisplay = ({ parsedConstraints, onConstraintsUpdate, isRegenerating }) => {
  const [constraints, setConstraints] = useState(parsedConstraints?.constraints || []);
  const [isEditing, setIsEditing] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [addForm, setAddForm] = useState({
    type: 'No Class Before',
    time: '',
    day: '',
    name: ''
  });

  // Update local state when props change
  React.useEffect(() => {
    if (parsedConstraints?.constraints) {
      setConstraints(parsedConstraints.constraints);
    }
  }, [parsedConstraints]);

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
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditForm({});
    setIsEditing(false);
  };

  const handleDelete = (index) => {
    const newConstraints = constraints.filter((_, i) => i !== index);
    setConstraints(newConstraints);
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
      } else if (newConstraint.type === 'Avoid TA') {
        delete newConstraint.time;
        delete newConstraint.day;
      }
      
      setConstraints([...constraints, newConstraint]);
      setAddForm({
        type: 'No Class Before',
        time: '',
        day: '',
        name: ''
      });
      setShowAddForm(false);
    }
  };

  const validateAddForm = () => {
    if (addForm.type === 'No Class Before' || addForm.type === 'No Class After') {
      return addForm.time && !isNaN(addForm.time) && addForm.time >= 0 && addForm.time <= 23;
    } else if (addForm.type === 'No Class Day') {
      return addForm.day && addForm.day.trim() !== '';
    } else if (addForm.type === 'Avoid TA') {
      return addForm.name && addForm.name.trim() !== '';
    }
    return false;
  };

  const handleRegenerateSchedule = () => {
    onConstraintsUpdate(constraints);
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
                <option value="Mon">Monday</option>
                <option value="Tue">Tuesday</option>
                <option value="Wed">Wednesday</option>
                <option value="Thu">Thursday</option>
                <option value="Fri">Friday</option>
              </select>
            </div>
          )}

          {editForm.type === 'Avoid TA' && (
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
                <option value="Mon">Monday</option>
                <option value="Tue">Tuesday</option>
                <option value="Wed">Wednesday</option>
                <option value="Thu">Thursday</option>
                <option value="Fri">Friday</option>
              </select>
            </div>
          )}

          {addForm.type === 'Avoid TA' && (
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
    <div className="constraints-display">
      <div className="constraints-header">
        <h3 className="constraints-title">
          🤖 AI Interpreted Constraints
        </h3>
        <div className="constraints-count">
          {constraints.length} constraint{constraints.length !== 1 ? 's' : ''} found
        </div>
      </div>
      
      <div className="constraints-list">
        {constraints.map((constraint, index) => (
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

      {renderAddForm()}

      <div className="constraints-controls">
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