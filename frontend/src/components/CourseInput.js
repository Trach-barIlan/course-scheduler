import React, { useState, useEffect } from 'react';
import '../styles/CourseInput.css';

const CourseInput = ({ course, onChange, index, onRemove, canRemove, selectedUniversity, selectedSemester }) => {
    const [errors, setErrors] = useState({});
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [isLoadingCourse, setIsLoadingCourse] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

    const days = [
        { value: 'Sun', label: 'Sunday' },
        { value: 'Mon', label: 'Monday' },
        { value: 'Tue', label: 'Tuesday' },
        { value: 'Wed', label: 'Wednesday' },
        { value: 'Thu', label: 'Thursday' },
        { value: 'Fri', label: 'Friday' },
        { value: 'Sat', label: 'Saturday' }
    ];

    const hours = Array.from({ length: 14 }, (_, i) => {
        const hour = i + 8; // 8 AM to 9 PM
        return {
            value: hour,
            label: `${hour}:00`
        };
    });

    // Helper functions for value conversion
    const getDayValue = (day) => {
        const dayMap = {
            'Sunday': 'Sun',
            'Monday': 'Mon',
            'Tuesday': 'Tue', 
            'Wednesday': 'Wed',
            'Thursday': 'Thu',
            'Friday': 'Fri',
            'Saturday': 'Sat',
            'Sun': 'Sun',
            'Mon': 'Mon',
            'Tue': 'Tue',
            'Wed': 'Wed',
            'Thu': 'Thu',
            'Fri': 'Fri',
            'Sat': 'Sat'
        };
        return dayMap[day] || day;
    };

    const getTimeValue = (time) => {
        if (!time) return '';
        // If it's a string with ":", take only the first part
        if (typeof time === 'string' && time.includes(':')) {
            return parseInt(time.split(':')[0]);
        }
        // If it's a number, return it
        return parseInt(time);
    };

    // Autocomplete functions - Using hybrid approach for optimal performance
    const fetchSuggestions = async (query) => {
        if (!selectedUniversity || !selectedSemester || query.trim().length < 3) {
            setSuggestions([]);
            setShowSuggestions(false);
            return;
        }

        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                console.log('No auth token found');
                return;
            }

            // Use fast JSON-based autocomplete for better performance
            const response = await fetch(`${API_BASE_URL}/api/courses/fast-autocomplete?q=${encodeURIComponent(query)}&semester=${selectedSemester}&limit=8`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setSuggestions(data.suggestions || []);
                setShowSuggestions(true);
            }
        } catch (error) {
            console.error('Error fetching autocomplete suggestions:', error);
            setSuggestions([]);
            setShowSuggestions(false);
        }
    };

    const handleCourseNameChange = (value) => {
        onChange(index, "name", value);
        
        // Enhanced debounced autocomplete with faster JSON-based backend
        if (selectedUniversity) {
            clearTimeout(window.autocompleteTimeout);
            window.autocompleteTimeout = setTimeout(() => {
                fetchSuggestions(value);
            }, 250);  // Reduced from 300ms to 250ms since JSON is much faster
        }
    };

    const selectCourseFromSuggestion = async (suggestion) => {
        setIsLoadingCourse(true);
        setShowSuggestions(false);
        
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                console.log('No auth token found');
                return;
            }

            const response = await fetch(`${API_BASE_URL}/api/courses/course/${suggestion.id}${selectedSemester ? `?semester=${selectedSemester}` : ''}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log('📋 API response received:', responseData);
                
                // Extract course data from the API response
                const courseData = responseData.success ? responseData.course : responseData;
                console.log('📋 Course data extracted:', courseData);
                
                // Convert course data to scheduler format, preserving existing course structure
                const updatedCourse = {
                    ...course, // Keep existing course data
                    name: courseData.name || course.name,
                    hasLecture: false,
                    hasPractice: false,
                    lectures: [],
                    practices: []
                };

                console.log('📝 Initial updated course:', updatedCourse);

                // Process events to create time slots
                if (courseData.events && courseData.events.length > 0) {
                    console.log('🎯 Processing events:', courseData.events);
                    
                    // Use Sets to track unique time slots and avoid duplicates
                    const uniqueLectures = new Set();
                    const uniquePractices = new Set();
                    
                    courseData.events.forEach(event => {
                        console.log('📚 Processing event:', event);
                        if (event.timeSlots && event.timeSlots.length > 0) {
                            event.timeSlots.forEach(timeSlot => {
                                console.log('⏰ Processing time slot:', timeSlot);
                                const slot = {
                                    day: timeSlot.day || '',
                                    startTime: timeSlot.from ? timeSlot.from.split(':')[0] : '', // Extract hour from 'from'
                                    endTime: timeSlot.to ? timeSlot.to.split(':')[0] : '' // Extract hour from 'to'
                                };

                                console.log('✅ Created slot:', slot);
                                
                                // Create a unique key for this time slot to avoid duplicates
                                const slotKey = `${slot.day}-${slot.startTime}-${slot.endTime}`;

                                // Determine if it's a lecture or practice based on category
                                if (event.category && (event.category.includes('הרצאה') || event.category.includes('lecture'))) {
                                    console.log('📚 Adding as lecture');
                                    if (!uniqueLectures.has(slotKey)) {
                                        uniqueLectures.add(slotKey);
                                        updatedCourse.hasLecture = true;
                                        updatedCourse.lectures.push(slot);
                                    }
                                } else {
                                    console.log('👨‍🏫 Adding as practice');
                                    if (!uniquePractices.has(slotKey)) {
                                        uniquePractices.add(slotKey);
                                        updatedCourse.hasPractice = true;
                                        updatedCourse.practices.push(slot);
                                    }
                                }
                            });
                        }
                    });
                } else {
                    console.log('⚠️ No events found in course data');
                }

                // If no sessions were found, set defaults
                if (!updatedCourse.hasLecture && !updatedCourse.hasPractice) {
                    console.log('🔧 No sessions found, setting default lecture');
                    updatedCourse.hasLecture = true;
                    updatedCourse.lectures = [{ day: '', startTime: '', endTime: '' }];
                }

                console.log('🎯 Final updated course before onChange:', updatedCourse);

                // Update the course with all the new data at once to avoid controlled/uncontrolled issues
                // Instead of calling onChange multiple times, we'll update each property individually but synchronously
                onChange(index, "name", updatedCourse.name);
                onChange(index, "hasLecture", updatedCourse.hasLecture);
                onChange(index, "hasPractice", updatedCourse.hasPractice);
                onChange(index, "lectures", updatedCourse.lectures);
                onChange(index, "practices", updatedCourse.practices);
                
                console.log('✅ All onChange calls completed');
            } else {
                console.error('❌ API response not OK:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error fetching course details:', error);
        } finally {
            setIsLoadingCourse(false);
        }
    };

    // Close suggestions when clicking outside
    useEffect(() => {
        const handleClickOutside = () => setShowSuggestions(false);
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    const validateTimeSlot = (day, startTime, endTime, type, slotIndex) => {
        const newErrors = { ...errors };
        const errorKey = `${type}_${index}_${slotIndex}`;

        // Clear previous errors for this slot
        delete newErrors[errorKey];

        if (day && (startTime !== '' && startTime !== null) && (endTime !== '' && endTime !== null)) {
            const start = parseInt(startTime);
            const end = parseInt(endTime);

            if (end <= start) {
                newErrors[errorKey] = 'End time must be after start time';
            } else if (end - start > 6) {
                newErrors[errorKey] = 'Class duration cannot exceed 6 hours';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleLectureChange = (slotIndex, field, value) => {
        const newLectures = [...(course.lectures || [])];
        if (!newLectures[slotIndex]) {
            newLectures[slotIndex] = { day: '', startTime: '', endTime: '' };
        }
        newLectures[slotIndex][field] = value;

        // Validate when all fields are filled
        const slot = newLectures[slotIndex];
        if (slot.day && slot.startTime !== '' && slot.endTime !== '') {
            validateTimeSlot(slot.day, slot.startTime, slot.endTime, 'lecture', slotIndex);
        }

        onChange(index, 'lectures', newLectures);
    };

    const handlePracticeChange = (slotIndex, field, value) => {
        const newPractices = [...(course.practices || [])];
        if (!newPractices[slotIndex]) {
            newPractices[slotIndex] = { day: '', startTime: '', endTime: '' };
        }
        newPractices[slotIndex][field] = value;

        // Validate when all fields are filled
        const slot = newPractices[slotIndex];
        if (slot.day && slot.startTime !== '' && slot.endTime !== '') {
            validateTimeSlot(slot.day, slot.startTime, slot.endTime, 'practice', slotIndex);
        }

        onChange(index, 'practices', newPractices);
    };

    const addLectureSlot = () => {
        const newLectures = [...(course.lectures || [])];
        newLectures.push({ day: '', startTime: '', endTime: '' });
        onChange(index, 'lectures', newLectures);
        onChange(index, 'hasLecture', true);
    };

    const addPracticeSlot = () => {
        const newPractices = [...(course.practices || [])];
        newPractices.push({ day: '', startTime: '', endTime: '' });
        onChange(index, 'practices', newPractices);
        onChange(index, 'hasPractice', true);
    };

    const removeLectureSlot = (slotIndex) => {
        const newLectures = course.lectures.filter((_, i) => i !== slotIndex);
        onChange(index, 'lectures', newLectures);
        
        // Clear errors for this slot
        const newErrors = { ...errors };
        delete newErrors[`lecture_${index}_${slotIndex}`];
        setErrors(newErrors);

        // If no lectures left, disable lecture section
        if (newLectures.length === 0) {
            onChange(index, 'hasLecture', false);
        }
    };

    const removePracticeSlot = (slotIndex) => {
        const newPractices = course.practices.filter((_, i) => i !== slotIndex);
        onChange(index, 'practices', newPractices);
        
        // Clear errors for this slot
        const newErrors = { ...errors };
        delete newErrors[`practice_${index}_${slotIndex}`];
        setErrors(newErrors);

        // If no practices left, disable practice section
        if (newPractices.length === 0) {
            onChange(index, 'hasPractice', false);
        }
    };

    // New functions to delete entire session types
    const deleteAllLectures = () => {
        // Clear all lecture-related errors
        const newErrors = { ...errors };
        Object.keys(newErrors).forEach(key => {
            if (key.startsWith(`lecture_${index}_`)) {
                delete newErrors[key];
            }
        });
        setErrors(newErrors);

        // Remove all lectures
        onChange(index, 'lectures', []);
        onChange(index, 'hasLecture', false);
    };

    const deleteAllPractices = () => {
        // Clear all practice-related errors
        const newErrors = { ...errors };
        Object.keys(newErrors).forEach(key => {
            if (key.startsWith(`practice_${index}_`)) {
                delete newErrors[key];
            }
        });
        setErrors(newErrors);

        // Remove all practices
        onChange(index, 'practices', []);
        onChange(index, 'hasPractice', false);
    };

    const getAvailableEndTimes = (startTime) => {
        if (startTime === '' || startTime === null) return [];
        const start = parseInt(startTime);
        return hours.filter(hour => hour.value > start && hour.value <= start + 6);
    };

    const hasValidSession = () => {
        const lectureValid = course.hasLecture && 
            course.lectures && 
            course.lectures.length > 0 &&
            course.lectures.some(lecture => 
                lecture.day && 
                lecture.startTime !== '' && 
                lecture.endTime !== '' &&
                !errors[`lecture_${index}_${course.lectures.indexOf(lecture)}`]
            );
            
        const practiceValid = course.hasPractice && 
            course.practices && 
            course.practices.length > 0 &&
            course.practices.some(practice => 
                practice.day && 
                practice.startTime !== '' && 
                practice.endTime !== '' &&
                !errors[`practice_${index}_${course.practices.indexOf(practice)}`]
            );

        return lectureValid || practiceValid;
    };

    // Check if we can delete a session type (must have at least one type)
    const canDeleteLectures = () => {
        return course.hasPractice && 
               course.practices && 
               course.practices.length > 0 &&
               course.practices.some(practice => 
                   practice.day && practice.startTime !== '' && practice.endTime !== ''
               );
    };

    const canDeletePractices = () => {
        return course.hasLecture && 
               course.lectures && 
               course.lectures.length > 0 &&
               course.lectures.some(lecture => 
                   lecture.day && lecture.startTime !== '' && lecture.endTime !== ''
               );
    };

    const renderTimeSlot = (slot, slotIndex, type, onSlotChange, onSlotRemove) => {
        const errorKey = `${type}_${index}_${slotIndex}`;
        const canRemoveSlot = type === 'lecture' ? 
            (course.lectures && course.lectures.length > 1) : 
            (course.practices && course.practices.length > 1);

        return (
            <div key={slotIndex} className="time-slot-item">
                <div className="time-slot-header">
                    <span className="time-slot-number">
                        {type === 'lecture' ? '📚' : '👨‍🏫'} Session {slotIndex + 1}
                    </span>
                    {canRemoveSlot && (
                        <button
                            type="button"
                            className="remove-slot-btn"
                            onClick={() => onSlotRemove(slotIndex)}
                            title="Remove this time slot"
                        >
                            ×
                        </button>
                    )}
                </div>

                <div className="time-selector-row">
                    <div className="selector-group">
                        <label>Day</label>
                        <select
                            value={getDayValue(slot.day) || ''}
                            onChange={(e) => onSlotChange(slotIndex, 'day', e.target.value)}
                            className="day-selector"
                        >
                            <option value="">Select Day</option>
                            {days.map(day => (
                                <option key={day.value} value={day.value}>
                                    {day.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="selector-group">
                        <label>Start Time</label>
                        <select
                            value={getTimeValue(slot.startTime) || ''}
                            onChange={(e) => onSlotChange(slotIndex, 'startTime', e.target.value)}
                            className="time-selector"
                        >
                            <option value="">Start</option>
                            {hours.slice(0, -1).map(hour => (
                                <option key={hour.value} value={hour.value}>
                                    {hour.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="selector-group">
                        <label>End Time</label>
                        <select
                            value={getTimeValue(slot.endTime) || ''}
                            onChange={(e) => onSlotChange(slotIndex, 'endTime', e.target.value)}
                            className="time-selector"
                            disabled={!slot.startTime}
                        >
                            <option value="">End</option>
                            {getAvailableEndTimes(getTimeValue(slot.startTime)).map(hour => (
                                <option key={hour.value} value={hour.value}>
                                    {hour.label}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {errors[errorKey] && (
                    <div className="error-message">
                        {errors[errorKey]}
                    </div>
                )}

                {slot.day && slot.startTime && slot.endTime && !errors[errorKey] && (
                    <div className="time-preview">
                        {type === 'lecture' ? '📚' : '👨‍🏫'} {getDayValue(slot.day)} {getTimeValue(slot.startTime)}:00 - {getTimeValue(slot.endTime)}:00
                    </div>
                )}
            </div>
        );
    };

    // Generate a compact summary of the course sessions
    const getCourseSummary = () => {
        const lectureSummary = course.lectures && course.lectures.length > 0 
            ? course.lectures
                .filter(lecture => lecture.day && lecture.startTime && lecture.endTime)
                .map(lecture => `${getDayValue(lecture.day)} ${getTimeValue(lecture.startTime)}:00-${getTimeValue(lecture.endTime)}:00`)
                .join(', ')
            : '';
        
        const practiceSummary = course.practices && course.practices.length > 0 
            ? course.practices
                .filter(practice => practice.day && practice.startTime && practice.endTime)
                .map(practice => `${getDayValue(practice.day)} ${getTimeValue(practice.startTime)}:00-${getTimeValue(practice.endTime)}:00`)
                .join(', ')
            : '';

        return { lectureSummary, practiceSummary };
    };

    return (
        <div className={`course-block ${!hasValidSession() ? 'invalid' : ''} ${isExpanded ? 'expanded' : 'collapsed'}`}>
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
            
            <div className="course-header">
                <div className="input-group">
                    <label className="input-label" htmlFor={`course-name-${index}`}>
                        Course Name * {selectedUniversity && <span className="autocomplete-hint">(Type 3+ characters to search courses)</span>}
                    </label>
                    <div className="autocomplete-container">
                        <input
                            id={`course-name-${index}`}
                            type="text"
                            placeholder={selectedUniversity ? "Type 3+ characters for fast search..." : "e.g., CS101, Mathematics, Physics"}
                            value={course.name}
                            onChange={(e) => handleCourseNameChange(e.target.value)}
                            className="course-input"
                            required
                            disabled={isLoadingCourse}
                            onClick={(e) => e.stopPropagation()}
                        />
                        {isLoadingCourse && <div className="loading-indicator">Loading course details...</div>}
                        {showSuggestions && suggestions.length > 0 && (
                            <div className="autocomplete-suggestions">
                                {suggestions.map((suggestion) => (
                                    <div
                                        key={suggestion.id}
                                        className="autocomplete-suggestion"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            selectCourseFromSuggestion(suggestion);
                                        }}
                                    >
                                        <div className="suggestion-name">{suggestion.name}</div>
                                        {suggestion.lecturers && suggestion.lecturers.length > 0 && (
                                            <div className="suggestion-lecturers">
                                                {suggestion.lecturers.join(', ')}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {!isExpanded && course.name && (
                    <div className="course-summary">
                        {(() => {
                            const { lectureSummary, practiceSummary } = getCourseSummary();
                            return (
                                <div className="summary-content">
                                    {lectureSummary && (
                                        <div className="summary-item">
                                            <span className="summary-label">📚 Lectures:</span>
                                            <span className="summary-value">{lectureSummary}</span>
                                        </div>
                                    )}
                                    {practiceSummary && (
                                        <div className="summary-item">
                                            <span className="summary-label">👨‍🏫 Practice:</span>
                                            <span className="summary-value">{practiceSummary}</span>
                                        </div>
                                    )}
                                    {!lectureSummary && !practiceSummary && (
                                        <div className="summary-item no-sessions">
                                            <span className="summary-value">No sessions configured</span>
                                        </div>
                                    )}
                                </div>
                            );
                        })()}
                    </div>
                )}

                <button
                    type="button"
                    className="expand-toggle-btn"
                    onClick={() => setIsExpanded(!isExpanded)}
                    title={isExpanded ? "Collapse course details" : "Expand course details"}
                >
                    {isExpanded ? "▲ Collapse" : "▼ Edit Sessions"}
                </button>
            </div>

            {isExpanded && (
                <div className="sessions-container">
                    <div className="session-header">
                        <h4>Course Sessions</h4>
                        <p className="session-note">Add at least one lecture or practice session</p>
                    </div>

                {/* Lecture Section */}
                <div className="session-section">
                    <div className="session-type-header">
                        <h5 className="session-type-title">📚 Lectures</h5>
                        <div className="session-actions">
                            <button
                                type="button"
                                className="add-slot-btn"
                                onClick={addLectureSlot}
                                title="Add lecture time slot"
                            >
                                + Add Lecture
                            </button>
                            {course.lectures && course.lectures.length > 0 && canDeleteLectures() && (
                                <button
                                    type="button"
                                    className="delete-section-btn"
                                    onClick={deleteAllLectures}
                                    title="Delete all lectures"
                                >
                                    🗑️ Delete All
                                </button>
                            )}
                        </div>
                    </div>

                    {course.lectures && course.lectures.length > 0 ? (
                        <div className="time-slots-container">
                            {course.lectures.map((lecture, slotIndex) => 
                                renderTimeSlot(
                                    lecture, 
                                    slotIndex, 
                                    'lecture', 
                                    handleLectureChange, 
                                    removeLectureSlot
                                )
                            )}
                        </div>
                    ) : (
                        <div className="no-sessions-message">
                            No lecture sessions added. Click "Add Lecture" to add one.
                        </div>
                    )}
                </div>

                {/* Practice Section */}
                <div className="session-section">
                    <div className="session-type-header">
                        <h5 className="session-type-title">👨‍🏫 Practice/TA Sessions</h5>
                        <div className="session-actions">
                            <button
                                type="button"
                                className="add-slot-btn"
                                onClick={addPracticeSlot}
                                title="Add practice time slot"
                            >
                                + Add Practice
                            </button>
                            {course.practices && course.practices.length > 0 && canDeletePractices() && (
                                <button
                                    type="button"
                                    className="delete-section-btn"
                                    onClick={deleteAllPractices}
                                    title="Delete all practices"
                                >
                                    🗑️ Delete All
                                </button>
                            )}
                        </div>
                    </div>

                    {course.practices && course.practices.length > 0 ? (
                        <div className="time-slots-container">
                            {course.practices.map((practice, slotIndex) => 
                                renderTimeSlot(
                                    practice, 
                                    slotIndex, 
                                    'practice', 
                                    handlePracticeChange, 
                                    removePracticeSlot
                                )
                            )}
                        </div>
                    ) : (
                        <div className="no-sessions-message">
                            No practice sessions added. Click "Add Practice" to add one.
                        </div>
                    )}
                </div>

                {(!course.lectures || course.lectures.length === 0) && 
                 (!course.practices || course.practices.length === 0) && (
                    <div className="validation-warning">
                        ⚠️ Please add at least one lecture or practice session
                    </div>
                )}
                </div>
            )}
        </div>
    );
};

export default CourseInput;