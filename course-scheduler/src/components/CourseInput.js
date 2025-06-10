import React from 'react';
import '../styles/CourseInput.css';

const CourseInput = ({ course, onChange, index, onRemove, canRemove }) => {
    return (
        <div className="course-block">
            {canRemove && (
                <button 
                    type="button"
                    className="remove-course-btn"
                    onClick={() => onRemove(index)}
                    aria-label="Remove course"
                    title="Remove this course"
                >
                    ×
                </button>
            )}
            
            <div className="input-group">
                <label className="input-label" htmlFor={`course-name-${index}`}>
                    Course Name
                </label>
                <input
                    id={`course-name-${index}`}
                    type="text"
                    placeholder="e.g., CS101, Mathematics, Physics"
                    value={course.name}
                    onChange={(e) => onChange(index, "name", e.target.value)}
                    className="course-input"
                    required
                />
            </div>
            
            <div className="input-group">
                <label className="input-label" htmlFor={`lectures-${index}`}>
                    Lecture Times
                </label>
                <textarea
                    id={`lectures-${index}`}
                    placeholder="Monday 9-11, Wednesday 10-12, Friday 14-16"
                    value={course.lectures}
                    onChange={(e) => onChange(index, "lectures", e.target.value)}
                    className="time-input"
                    rows={3}
                    required
                />
            </div>
            
            <div className="input-group">
                <label className="input-label" htmlFor={`ta-times-${index}`}>
                    TA Session Times
                </label>
                <textarea
                    id={`ta-times-${index}`}
                    placeholder="Tuesday 10-12, Thursday 13-15"
                    value={course.ta_times}
                    onChange={(e) => onChange(index, "ta_times", e.target.value)}
                    className="time-input"
                    rows={3}
                    required
                />
            </div>
        </div>
    );
};

export default CourseInput;