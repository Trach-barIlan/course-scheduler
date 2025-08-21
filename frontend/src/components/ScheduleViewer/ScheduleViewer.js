import React, { useState, useCallback, useMemo } from 'react';
import './ScheduleViewer.css';

// Generate colors for courses (moved outside component to prevent re-creation)
const getColorForCourse = (courseName) => {
  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', 
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1'
  ];
  const hash = courseName.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0);
    return a & a;
  }, 0);
  return colors[Math.abs(hash) % colors.length];
};

// Convert WeeklyScheduler format to day-based format
const convertScheduleFormat = (scheduleData) => {
  if (!scheduleData) return {};
  
  // If it's already in day-based format, return as is
  if (!Array.isArray(scheduleData) && typeof scheduleData === 'object') {
    console.log('📊 Schedule is already in day-based format');
    return scheduleData;
  }
  
  // If it's in WeeklyScheduler array format, convert it
  if (Array.isArray(scheduleData)) {
    console.log('📊 Converting from WeeklyScheduler array format');
    const dayMap = {
      'Sun': 'Sunday',
      'Mon': 'Monday', 
      'Tue': 'Tuesday',
      'Wed': 'Wednesday',
      'Thu': 'Thursday',
      'Fri': 'Friday',
      'Sat': 'Saturday'
    };
    
    const converted = {};
    
    scheduleData.forEach(course => {
      console.log('📊 Processing course:', course);
      
      // Process lecture
      if (course.lecture && typeof course.lecture === 'string') {
        const lectureMatch = course.lecture.match(/^(\w+)\s+(\d+)-(\d+)$/);
        if (lectureMatch) {
          const [, shortDay, start, end] = lectureMatch;
          const fullDay = dayMap[shortDay] || shortDay;
          
          if (!converted[fullDay]) converted[fullDay] = [];
          converted[fullDay].push({
            course_name: course.name,
            type: 'Lecture',
            time: `${start}:00-${end}:00`,
            lecturer: course.lecturer || 'TBA',
            location: course.location || 'TBA'
          });
        }
      }
      
      // Process TA/Practice sessions
      if (course.ta && typeof course.ta === 'string') {
        const taMatch = course.ta.match(/^(\w+)\s+(\d+)-(\d+)$/);
        if (taMatch) {
          const [, shortDay, start, end] = taMatch;
          const fullDay = dayMap[shortDay] || shortDay;
          
          if (!converted[fullDay]) converted[fullDay] = [];
          converted[fullDay].push({
            course_name: course.name,
            type: 'Practice',
            time: `${start}:00-${end}:00`,
            lecturer: course.ta_instructor || course.lecturer || 'TBA',
            location: course.ta_location || course.location || 'TBA'
          });
        }
      }
    });
    
    console.log('📊 Converted schedule:', converted);
    return converted;
  }
  
  return {};
};

const ScheduleViewer = ({ schedule, title, backButton }) => {
  const [hoveredCourse, setHoveredCourse] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);

  // Debug the incoming schedule
  console.log('🔍 ScheduleViewer received schedule:', schedule);
  console.log('🔍 Schedule type:', typeof schedule);
  console.log('🔍 Is Array:', Array.isArray(schedule));

  // Time slots from 8 AM to 8 PM (12 hours)
  const timeSlots = Array.from({ length: 25 }, (_, i) => {
    const hour = 8 + Math.floor(i / 2);
    const minute = i % 2 === 0 ? '00' : '30';
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
    const ampm = hour >= 12 ? 'PM' : 'AM';
    return {
      time: `${hour.toString().padStart(2, '0')}:${minute}`,
      display: `${displayHour}:${minute} ${ampm}`
    };
  });

  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  // Convert schedule to a more workable format
  const processedSchedule = useMemo(() => {
    const convertedSchedule = convertScheduleFormat(schedule);
    
    if (!convertedSchedule || Object.keys(convertedSchedule).length === 0) return {};
    
    // Debug the converted schedule structure
    console.log('📊 Converted schedule data:', convertedSchedule);
    console.log('📊 Converted schedule keys:', Object.keys(convertedSchedule));
    
    return Object.entries(convertedSchedule).reduce((acc, [day, courses]) => {
      // Debug log to understand the data structure
      console.log('Processing day:', day, 'courses:', courses, 'type:', typeof courses);
      
      // Handle different possible data structures
      let coursesArray;
      if (Array.isArray(courses)) {
        coursesArray = courses;
      } else if (courses && typeof courses === 'object') {
        // If courses is an object, try to extract values
        coursesArray = Object.values(courses);
      } else {
        // If courses is neither array nor object, skip this day
        console.warn(`Skipping day ${day} - courses is not an array or object:`, courses);
        return acc;
      }

      console.log('📊 Courses array for', day, ':', coursesArray);
      
      acc[day] = coursesArray.map(course => {
        console.log('📊 Individual course:', course);
        
        return {
          ...course,
          startTime: course.time ? course.time.split('-')[0].trim() : '',
          endTime: course.time ? course.time.split('-')[1].trim() : '',
          id: `${course.course_name || course.name || 'Unknown'}-${course.type || 'Unknown'}-${day}-${course.time || 'Unknown'}`,
          color: getColorForCourse(course.course_name || course.name || 'Unknown')
        };
      });
      return acc;
    }, {});
  }, [schedule]);

  // Get all unique courses for the course list
  const getAllCourses = useCallback(() => {
    const coursesMap = new Map();
    
    console.log('📊 Processing schedule for course list:', processedSchedule);
    
    Object.entries(processedSchedule).forEach(([day, courses]) => {
      // Add safety check for courses array
      if (Array.isArray(courses)) {
        courses.forEach(course => {
          console.log('📊 Processing course for list:', course);
          
          const courseName = course.course_name || course.name || course.courseName || 'Unknown Course';
          const courseType = course.type || course.courseType || 'Unknown Type';
          const lecturer = course.lecturer || course.instructor || course.teacher || 'TBA';
          const location = course.location || course.room || course.classroom || 'TBA';
          
          console.log('📊 Extracted data - name:', courseName, 'type:', courseType, 'lecturer:', lecturer, 'location:', location);
          
          const key = `${courseName}-${courseType}`;
          
          if (!coursesMap.has(key)) {
            coursesMap.set(key, {
              courseName: courseName,
              type: courseType,
              lecturer: lecturer,
              location: location,
              color: course.color,
              sessions: []
            });
          }
          coursesMap.get(key).sessions.push({
            day,
            time: course.time || 'TBA',
            location: location
          });
        });
      }
    });

    const result = Array.from(coursesMap.values());
    console.log('📊 Final course list:', result);
    return result;
  }, [processedSchedule]);

  // Check if a time slot should show a course
  const getCourseAtTime = (day, timeSlot) => {
    if (!processedSchedule[day] || !Array.isArray(processedSchedule[day])) return null;
    
    return processedSchedule[day].find(course => {
      if (!course.startTime || !course.endTime) return false;
      
      const courseStart = parseTime(course.startTime);
      const courseEnd = parseTime(course.endTime);
      const slotTime = parseTime(timeSlot.time);
      
      return slotTime >= courseStart && slotTime < courseEnd;
    });
  };

  // Parse time string to minutes for comparison
  const parseTime = (timeStr) => {
    if (!timeStr || typeof timeStr !== 'string') return 0;
    
    const timeParts = timeStr.split(':');
    if (timeParts.length !== 2) return 0;
    
    const hours = parseInt(timeParts[0], 10);
    const minutes = parseInt(timeParts[1], 10);
    
    if (isNaN(hours) || isNaN(minutes)) return 0;
    
    return hours * 60 + minutes;
  };

  // Calculate the span of a course in the grid
  const getCourseSpan = (course) => {
    const startTime = parseTime(course.startTime);
    const endTime = parseTime(course.endTime);
    return (endTime - startTime) / 30; // Each slot is 30 minutes
  };

  // Check if course should be highlighted
  const shouldHighlight = (course) => {
    if (!course) return false;
    
    const courseName = course.course_name || course.name || '';
    const courseType = course.type || '';
    
    if (selectedCourse) {
      return courseName === selectedCourse.courseName && courseType === selectedCourse.type;
    }
    if (hoveredCourse) {
      return courseName === hoveredCourse.courseName && courseType === hoveredCourse.type;
    }
    return false;
  };

  const handleCourseHover = (course, isEntering) => {
    if (isEntering) {
      setHoveredCourse(course);
    } else {
      setHoveredCourse(null);
    }
  };

  const handleCourseClick = (course) => {
    setSelectedCourse(selectedCourse?.courseName === course.courseName && selectedCourse?.type === course.type ? null : course);
  };

  if (!schedule || Object.keys(schedule).length === 0) {
    return (
      <div className="schedule-viewer">
        <div className="schedule-viewer-header">
          {backButton && <div className="header-back-button">{backButton}</div>}
          <h2>{title}</h2>
        </div>
        <div className="no-schedule">
          <div className="no-schedule-icon">📅</div>
          <h3>No schedule to display</h3>
          <p>Generate a schedule to see it visualized here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="schedule-viewer">
      <div className="schedule-viewer-header">
        {backButton && <div className="header-back-button">{backButton}</div>}
        <h2>{title}</h2>
        <div className="schedule-stats">
          <div className="stat">
            <span className="stat-number">{getAllCourses().length}</span>
            <span className="stat-label">Courses</span>
          </div>
          <div className="stat">
            <span className="stat-number">
              {Object.values(processedSchedule).reduce((acc, courses) => acc + courses.length, 0)}
            </span>
            <span className="stat-label">Sessions</span>
          </div>
        </div>
      </div>

      <div className="schedule-content">
        <div className="schedule-grid-container">
          <div className="schedule-grid">
            {/* Time labels */}
            <div className="time-column">
              <div className="time-header"></div>
              {timeSlots.map((slot, index) => (
                <div key={slot.time} className={`time-slot ${index % 2 === 0 ? 'hour-mark' : 'half-hour'}`}>
                  {index % 2 === 0 && <span className="time-label">{slot.display}</span>}
                </div>
              ))}
            </div>

            {/* Day columns */}
            {days.map(day => (
              <div key={day} className="day-column">
                <div className="day-header">{day}</div>
                {timeSlots.map((slot, slotIndex) => {
                  const course = getCourseAtTime(day, slot);
                  const isFirstSlotOfCourse = course && getCourseAtTime(day, timeSlots[slotIndex - 1]) !== course;
                  
                  if (course && isFirstSlotOfCourse) {
                    const span = getCourseSpan(course);
                    return (
                      <div
                        key={`${day}-${slot.time}`}
                        className={`course-block ${shouldHighlight(course) ? 'highlighted' : ''}`}
                        style={{
                          backgroundColor: course.color,
                          gridRow: `span ${span}`,
                          '--course-color': course.color
                        }}
                        onMouseEnter={() => handleCourseHover({
                          courseName: course.course_name,
                          type: course.type
                        }, true)}
                        onMouseLeave={() => handleCourseHover(null, false)}
                        onClick={() => handleCourseClick({
                          courseName: course.course_name,
                          type: course.type,
                          lecturer: course.lecturer,
                          location: course.location
                        })}
                      >
                        <div className="course-info">
                          <div className="course-name">{course.course_name}</div>
                          <div className="course-details">
                            <span className="course-type">{course.type}</span>
                            <span className="course-time">{course.time}</span>
                          </div>
                          {course.location && (
                            <div className="course-location">📍 {course.location}</div>
                          )}
                          {course.lecturer && (
                            <div className="course-lecturer">👨‍🏫 {course.lecturer}</div>
                          )}
                        </div>
                      </div>
                    );
                  } else if (!course) {
                    return (
                      <div key={`${day}-${slot.time}`} className="empty-slot"></div>
                    );
                  }
                  return null;
                })}
              </div>
            ))}
          </div>
        </div>

        <div className="course-list-container">
          <h3>Course List</h3>
          <div className="course-list">
            {getAllCourses().map((course, index) => (
              <div
                key={`${course.courseName}-${course.type}`}
                className={`course-card ${
                  (selectedCourse?.courseName === course.courseName && selectedCourse?.type === course.type) ? 'selected' : ''
                } ${
                  (hoveredCourse?.courseName === course.courseName && hoveredCourse?.type === course.type) ? 'hovered' : ''
                }`}
                style={{ '--course-color': course.color }}
                onMouseEnter={() => handleCourseHover(course, true)}
                onMouseLeave={() => handleCourseHover(null, false)}
                onClick={() => handleCourseClick(course)}
              >
                <div className="course-card-header">
                  <div 
                    className="course-color-indicator"
                    style={{ backgroundColor: course.color }}
                  ></div>
                  <div className="course-title">
                    <h4>{course.courseName}</h4>
                    <span className="course-type-badge">{course.type}</span>
                  </div>
                </div>
                
                {course.lecturer && (
                  <div className="course-detail">
                    <span className="detail-icon">👨‍🏫</span>
                    <span>{course.lecturer}</span>
                  </div>
                )}
                
                <div className="course-sessions">
                  {course.sessions.map((session, sessionIndex) => (
                    <div key={sessionIndex} className="session-info">
                      <span className="session-day">{session.day}</span>
                      <span className="session-time">{session.time}</span>
                      {session.location && (
                        <span className="session-location">📍 {session.location}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScheduleViewer;
