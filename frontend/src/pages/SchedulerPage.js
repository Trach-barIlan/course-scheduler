import React, { useState, useCallback, useEffect } from "react";
import { useLocation, useNavigate } from 'react-router-dom';
import CourseInput from '../components/CourseInput';
import WeeklyScheduler from '../components/WeeklyScheduler';
import ConstraintsDisplay from '../components/ConstraintsDisplay';
import ScheduleErrorModal from '../components/ScheduleErrorModal';
import '../styles/SchedulerPage.css';

// Function to convert imported courses to the scheduler format
const convertImportedCoursesToSchedulerFormat = (importedCourses) => {
  return importedCourses.map(courseData => {
    const course = {
      name: courseData.name || courseData.courseName || "",
      hasLecture: false,
      hasPractice: false,
      lectures: [],
      practices: []
    };

    // If there are sections, we will convert them
    if (courseData.sections && courseData.sections.length > 0) {
      // Take the first section by default
      const section = courseData.sections[0];
      
      if (section.times) {
        section.times.forEach(timeSlot => {
          if (timeSlot.type === 'lecture') {
            course.hasLecture = true;
            course.lectures.push({
              day: timeSlot.day,
              startTime: timeSlot.startTime.toString(),
              endTime: timeSlot.endTime.toString()
            });
          } else if (timeSlot.type === 'lab' || timeSlot.type === 'practice') {
            course.hasPractice = true;
            course.practices.push({
              day: timeSlot.day,
              startTime: timeSlot.startTime.toString(),
              endTime: timeSlot.endTime.toString()
            });
          }
        });
      }
    }

    return course;
  });
};

// Convert the loaded schedule data to the format used by the courses state
const convertScheduleToCourses = (scheduleData) => {
  if (!Array.isArray(scheduleData)) {
    console.warn('Invalid schedule data format:', scheduleData);
    return [{ 
      name: "", 
      hasLecture: false,
      hasPractice: false,
      lectures: [],
      practices: []
    }];
  }

  const converted = scheduleData.map((courseData, index) => {
    
    const course = {
      name: courseData.name || "",
      hasLecture: false,
      hasPractice: false,
      lectures: [],
      practices: []
    };

    if (courseData.lecture) {
      const parts = courseData.lecture.split(' ');
      if (parts.length === 2) {
        const day = parts[0]; // Mon
        const timeRange = parts[1]; // 9-11
        const [start, end] = timeRange.split('-');
        
        course.hasLecture = true;
        course.lectures = [{
          day: day,
          startTime: start,
          endTime: end
        }];
      }
    }

    if (courseData.ta) {
      const parts = courseData.ta.split(' ');
      if (parts.length === 2) {
        const day = parts[0]; // Tue
        const timeRange = parts[1]; // 14-16
        const [start, end] = timeRange.split('-');
        
        course.hasPractice = true;
        course.practices = [{
          day: day,
          startTime: start,
          endTime: end
        }];
      }
    }

    return course;
  });

  return converted;
};

const SchedulerPage = ({ user, authToken }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { universityConfig, importedCourses } = location.state || {};
  
  const [preference, setPreference] = useState("crammed");
  const [courses, setCourses] = useState([]);
  const [constraints, setConstraints] = useState("");
  const [error, setError] = useState(null);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [schedule, setSchedule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parsedConstraints, setParsedConstraints] = useState(null);
  const [constraintsUpdateFunction, setConstraintsUpdateFunction] = useState(null);
  const [selectedUniversity, setSelectedUniversity] = useState("");
  const [selectedSemester, setSelectedSemester] = useState("");
  
  const [loadedScheduleName, setLoadedScheduleName] = useState(null);
  const [loadedScheduleId, setLoadedScheduleId] = useState(null);
  
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  useEffect(() => {
    // Handle restored state from schedule viewer
    if (location.state?.preserveState) {
      setCourses(location.state.courses || []);
      setPreference(location.state.preference || "crammed");
      setConstraints(location.state.constraints || "");
      setSelectedUniversity(location.state.selectedUniversity || "");
      setSelectedSemester(location.state.selectedSemester || "");
      setLoadedScheduleName(location.state.loadedScheduleName || null);
      setLoadedScheduleId(location.state.loadedScheduleId || null);
      return; // Don't process other state
    }

    if (location.state?.loadedSchedule) {
      
      setSchedule(location.state.loadedSchedule);
      setLoadedScheduleName(location.state.scheduleName);
      setLoadedScheduleId(location.state.scheduleId);
      setError(null);

      // Check if we have original course options (preferred) or need to convert from schedule data
      if (location.state.originalCourseOptions && location.state.originalCourseOptions.length > 0) {
        // Convert backend format to frontend format
        const convertedCourses = location.state.originalCourseOptions.map(courseData => {
          return {
            name: courseData.name || "",
            hasLecture: (courseData.lectures && courseData.lectures.length > 0),
            hasPractice: (courseData.ta_times && courseData.ta_times.length > 0),
            lectures: (courseData.lectures || []).map(lectureStr => {
              const parts = lectureStr.split(' ');
              if (parts.length === 2) {
                const day = parts[0];
                const timeRange = parts[1];
                const [start, end] = timeRange.split('-');
                return { day, startTime: start, endTime: end };
              }
              return { day: "", startTime: "", endTime: "" };
            }),
            practices: (courseData.ta_times || []).map(practiceStr => {
              const parts = practiceStr.split(' ');
              if (parts.length === 2) {
                const day = parts[0];
                const timeRange = parts[1];
                const [start, end] = timeRange.split('-');
                return { day, startTime: start, endTime: end };
              }
              return { day: "", startTime: "", endTime: "" };
            })
          };
        });
        setCourses(convertedCourses);
      } else {
        const loadedCourses = convertScheduleToCourses(location.state.loadedSchedule);
        setCourses(loadedCourses);
      }
      
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Initialize courses from imported university data
  useEffect(() => {
    if (importedCourses && importedCourses.length > 0) {
      const convertedCourses = convertImportedCoursesToSchedulerFormat(importedCourses);
      setCourses(convertedCourses);
    }
  }, [importedCourses]);

  const handleCourseChange = (index, field, value) => {
    const newCourses = [...courses];
    newCourses[index][field] = value;
    
    // Update hasLecture and hasPractice flags based on array contents
    if (field === 'lectures') {
      newCourses[index].hasLecture = value.length > 0;
    }
    if (field === 'practices') {
      newCourses[index].hasPractice = value.length > 0;
    }
    
    setCourses(newCourses);
  };

  const addCourse = () => {
    setCourses([...courses, { 
      name: "", 
      hasLecture: false,
      hasPractice: false,
      lectures: [],
      practices: []
    }]);
  };

  const removeCourse = (index) => {
    if (courses.length > 1) {
      setCourses(courses.filter((_, i) => i !== index));
    }
  };

  // הוסף פונקציה לניקוי המערכת הנטענת
  const clearLoadedSchedule = () => {
    setLoadedScheduleName(null);
    setLoadedScheduleId(null);
    setSchedule(null);
    setCourses([{ 
      name: "", 
      hasLecture: false,
      hasPractice: false,
      lectures: [],
      practices: []
    }]);
    setConstraints("");
    setError(null);
    setParsedConstraints(null);
  };

  const validateForm = useCallback(() => {
    for (let i = 0; i < courses.length; i++) {
      const course = courses[i];
      
      if (!course.name.trim()) {
        throw new Error(`Please fill in the name for course ${i + 1}`);
      }

      // Check if at least one session type has valid time slots
      const hasValidLectures = course.lectures && course.lectures.length > 0 && 
        course.lectures.some(lecture => 
          lecture.day && lecture.startTime !== '' && lecture.endTime !== ''
        );
      
      const hasValidPractices = course.practices && course.practices.length > 0 && 
        course.practices.some(practice => 
          practice.day && practice.startTime !== '' && practice.endTime !== ''
        );

      if (!hasValidLectures && !hasValidPractices) {
        throw new Error(`Course "${course.name}" must have at least one complete lecture or practice session`);
      }

      // Validate all lecture time slots
      if (course.lectures && course.lectures.length > 0) {
        for (let j = 0; j < course.lectures.length; j++) {
          const lecture = course.lectures[j];
          if (lecture.day || lecture.startTime !== '' || lecture.endTime !== '') {
            // If any field is filled, all must be filled
            if (!lecture.day || lecture.startTime === '' || lecture.endTime === '') {
              throw new Error(`Please complete all details for lecture ${j + 1} in "${course.name}"`);
            }
            
            const lectureStart = parseInt(lecture.startTime);
            const lectureEnd = parseInt(lecture.endTime);
            
            if (lectureEnd <= lectureStart) {
              throw new Error(`Lecture ${j + 1} end time must be after start time for "${course.name}"`);
            }
          }
        }
      }

      // Validate all practice time slots
      if (course.practices && course.practices.length > 0) {
        for (let j = 0; j < course.practices.length; j++) {
          const practice = course.practices[j];
          if (practice.day || practice.startTime !== '' || practice.endTime !== '') {
            // If any field is filled, all must be filled
            if (!practice.day || practice.startTime === '' || practice.endTime === '') {
              throw new Error(`Please complete all details for practice session ${j + 1} in "${course.name}"`);
            }
            
            const practiceStart = parseInt(practice.startTime);
            const practiceEnd = parseInt(practice.endTime);
            
            if (practiceEnd <= practiceStart) {
              throw new Error(`Practice session ${j + 1} end time must be after start time for "${course.name}"`);
            }
          }
        }
      }
    }
  }, [courses]);

  const formatCourseForAPI = useCallback((course) => {
    const formattedCourse = {
      name: course.name.trim(),
      lectures: [],
      ta_times: []
    };

    // Add all valid lecture time slots
    if (course.lectures && course.lectures.length > 0) {
      course.lectures.forEach(lecture => {
        if (lecture.day && lecture.startTime !== '' && lecture.endTime !== '') {
          formattedCourse.lectures.push(`${lecture.day} ${lecture.startTime}-${lecture.endTime}`);
        }
      });
    }

    // Add all valid practice time slots
    if (course.practices && course.practices.length > 0) {
      course.practices.forEach(practice => {
        if (practice.day && practice.startTime !== '' && practice.endTime !== '') {
          formattedCourse.ta_times.push(`${practice.day} ${practice.startTime}-${practice.endTime}`);
        }
      });
    }

    return formattedCourse;
  }, []);

  const generateScheduleWithConstraints = useCallback(async (constraintsToUse) => {
    try {
      validateForm();

      const formattedCourses = courses.map(formatCourseForAPI);

      localStorage.setItem('originalCourseOptions', JSON.stringify(formattedCourses));

      const headers = {
        "Content-Type": "application/json"
      };

      // Add authorization header if user is authenticated
      if (user && authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }

      const scheduleRes = await fetch(API_BASE_URL + "/api/schedule", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          preference,
          courses: formattedCourses,
          constraints: constraintsToUse
        }),
      });

      // Check if response is actually JSON
      const contentType = scheduleRes.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const responseText = await scheduleRes.text();
        console.error('Non-JSON response received:', responseText);
        throw new Error(`Server returned non-JSON response. Status: ${scheduleRes.status}. This usually means the backend server is not running or the API endpoint is incorrect.`);
      }

      if (!scheduleRes.ok) {
        const errorData = await scheduleRes.json();
        console.error('API Error:', errorData);
        throw new Error(errorData.error || `Server error: ${scheduleRes.status}`);
      }

      const data = await scheduleRes.json();
      
      if (data.schedule) {
        setSchedule(data.schedule);
        setError(null);
      } else {
        const errorMessage = data.error || 'No valid schedule found with the given constraints. Try adjusting your requirements.';
        setError(errorMessage);
        setShowErrorModal(true);
      }
    } catch (err) {
      console.error('Schedule generation error:', err);
      let errorMessage = err.message;
      
      // Provide more helpful error messages
      if (err.message.includes('Failed to fetch')) {
        errorMessage = 'Unable to connect to the server. Please check if the backend is running and try again.';
      } else if (err.message.includes('NetworkError')) {
        errorMessage = 'Network error. Please check your internet connection and try again.';
      }
      
      setError(errorMessage);
      setShowErrorModal(true);
    }
  }, [courses, preference, validateForm, user, authToken, API_BASE_URL, formatCourseForAPI]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    setIsLoading(true);
    setParsedConstraints(null);

    try {
      let parsedConstraints = [];
      let constraintsData = null;
      
      if (constraints.trim()) {
        const headers = {
          "Content-Type": "application/json"
        };

        // Add authorization header if user is authenticated
        if (user && authToken) {
          headers['Authorization'] = `Bearer ${authToken}`;
        }

        const parseRes = await fetch(API_BASE_URL + "/api/parse", {
          method: "POST",
          headers: headers,
          body: JSON.stringify({ text: constraints }),
        });

        // Check if response is actually JSON
        const contentType = parseRes.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          const responseText = await parseRes.text();
          console.error('Non-JSON response from parse endpoint:', responseText);
          throw new Error(`Constraints parsing failed. Server returned non-JSON response. This usually means the backend server is not running.`);
        }

        if (!parseRes.ok) {
          const errorData = await parseRes.json();
          console.error('Parse error:', errorData);
          throw new Error(errorData.error || 'Failed to parse constraints');
        }

        constraintsData = await parseRes.json();
        parsedConstraints = constraintsData[0]?.constraints || [];
        
        // Enhanced constraints data with original text and entities
        const enhancedConstraintsData = {
          constraints: parsedConstraints,
          entities: constraintsData[0]?.entities || [],
          originalText: constraints.trim(),
          parsedAt: new Date().toISOString()
        };
        
        setParsedConstraints(enhancedConstraintsData);
      }

      await generateScheduleWithConstraints(parsedConstraints);
    } catch (err) {
      console.error('Submit error:', err);
      let errorMessage = err.message;
      
      // Provide more helpful error messages
      if (err.message.includes('Failed to fetch')) {
        errorMessage = 'Unable to connect to the server. Please make sure the backend is running on the correct port and try again.';
      }
      
      setError(errorMessage);
      setShowErrorModal(true);
      setParsedConstraints(null);
    } finally {
      setIsSubmitting(false);
      setIsLoading(false);
    }
  };

  const handleConstraintsUpdate = useCallback(async (updatedConstraints) => {
    if (constraintsUpdateFunction) {
      setIsLoading(true);
      try {
        await constraintsUpdateFunction(updatedConstraints);
      } catch (err) {
        console.error('Error updating constraints:', err);
      } finally {
        setIsLoading(false);
      }
    }
  }, [constraintsUpdateFunction]);

  React.useEffect(() => {
    setConstraintsUpdateFunction(() => generateScheduleWithConstraints);
  }, [generateScheduleWithConstraints]);

  return (
    <div className="scheduler-page">
      <div className="scheduler-content">
        <div className="left-panel">
          <div className="course-scheduler">
            <div className="scheduler-header-section">
              <h2>Course Scheduler</h2>
              {user && (
                <div className="user-welcome">
                  Welcome back, <strong>{user.first_name}</strong>!
                </div>
              )}
              
              {/* Compact notification sections */}
              {loadedScheduleName && (
                <div className="loaded-schedule-info">
                  <span className="loaded-schedule-label">📂 {loadedScheduleName}</span>
                  <button 
                    type="button" 
                    className="clear-loaded-button"
                    onClick={clearLoadedSchedule}
                    title="Clear loaded schedule and start new"
                  >
                    ✖
                  </button>
                </div>
              )}
              
              {universityConfig && (
                <div className="imported-courses-info">
                  <span className="imported-courses-label">🏫 {universityConfig.university.name}</span>
                  {universityConfig.semester && universityConfig.year && (
                    <span className="semester-info">({universityConfig.semester} {universityConfig.year})</span>
                  )}
                  <span className="import-stats">{importedCourses?.length || 0} courses</span>
                </div>
              )}
            </div>
            
            {/* Compact settings header */}
            <div className="scheduler-settings">
              <div className="settings-row">
                <div className="setting-group">
                  <label htmlFor="preference">Schedule Type</label>
                  <select
                    id="preference"
                    value={preference}
                    onChange={(e) => setPreference(e.target.value)}
                    className="compact-select"
                  >
                    <option value="crammed">Crammed</option>
                    <option value="spaced">Spaced Out</option>
                  </select>
                </div>
                
                <div className="setting-group">
                  <label htmlFor="university">University</label>
                  <select
                    id="university"
                    value={selectedUniversity}
                    onChange={(e) => setSelectedUniversity(e.target.value)}
                    className="compact-select"
                  >
                    <option value="">No autocomplete</option>
                    <option value="Bar-Ilan">Bar-Ilan</option>
                  </select>
                </div>
                
                {selectedUniversity && (
                  <div className="setting-group">
                    <label htmlFor="semester">Semester</label>
                    <select
                      id="semester"
                      value={selectedSemester}
                      onChange={(e) => setSelectedSemester(e.target.value)}
                      className="compact-select"
                    >
                      <option value="">All</option>
                      <option value="A">A</option>
                      <option value="B">B</option>
                    </select>
                  </div>
                )}
              </div>
              
              {selectedUniversity && (
                <div className="autocomplete-status">
                  ✨ Autocomplete enabled for {selectedUniversity}
                  {selectedSemester && ` (Semester ${selectedSemester})`}
                </div>
              )}
            </div>
            
            <form onSubmit={handleSubmit}>
              {/* Courses Section - Now more prominent */}
              <div className="courses-section">
                <div className="courses-header">
                  <h3>📚 Your Courses</h3>
                  <button 
                    type="button" 
                    onClick={addCourse} 
                    className="add-course-button"
                    disabled={isSubmitting}
                  >
                    + Add Course
                  </button>
                </div>
                
                <div className="courses-list">
                  {courses.map((course, i) => (
                    <CourseInput
                      key={i}
                      course={course}
                      onChange={handleCourseChange}
                      onRemove={removeCourse}
                      index={i}
                      canRemove={courses.length > 1}
                      selectedUniversity={selectedUniversity}
                      selectedSemester={selectedSemester}
                    />
                  ))}
                </div>
              </div>

              {/* Constraints - More compact */}
              <div className="constraints-section-compact">
                <h3>🎯 Additional Preferences</h3>
                <textarea
                  id="constraints"
                  className="constraints-input-compact"
                  value={constraints}
                  onChange={(e) => setConstraints(e.target.value)}
                  placeholder="Optional: No classes before 9am, Avoid TA Smith, etc."
                  rows={3}
                />
              </div>

              <button 
                type="submit" 
                className="generate-schedule-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="loading-spinner"></div>
                    {loadedScheduleName ? 'Updating...' : 'Generating...'}
                  </>
                ) : (
                  <>
                    🚀 {loadedScheduleName ? 'Update Schedule' : 'Generate Schedule'}
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        <div className="right-panel">
          {schedule && (
            <div className="enhanced-view-section">
              <button 
                className="enhanced-view-button"
                onClick={() => {
                  navigate('/schedule-viewer', {
                    state: {
                      schedule: schedule,
                      scheduleName: loadedScheduleName || "Generated Schedule",
                      scheduleId: loadedScheduleId,
                      from: '/scheduler',
                      schedulerState: {
                        courses: courses,
                        preference: preference,
                        constraints: constraints,
                        selectedUniversity: selectedUniversity,
                        selectedSemester: selectedSemester,
                        loadedScheduleName: loadedScheduleName,
                        loadedScheduleId: loadedScheduleId
                      }
                    }
                  });
                }}
              >
                ✨ View Enhanced Schedule
              </button>
            </div>
          )}

          <ConstraintsDisplay 
            parsedConstraints={parsedConstraints} 
            onConstraintsUpdate={handleConstraintsUpdate}
            isRegenerating={isLoading}
          />
          
          <WeeklyScheduler 
            user={user} 
            authToken={authToken} 
            schedule={schedule} 
            isLoading={isLoading}
            scheduleName={loadedScheduleName}
            scheduleId={loadedScheduleId}
          />
        </div>
      </div>

      <ScheduleErrorModal 
        isOpen={showErrorModal}
        error={error}
        onClose={() => {
          setShowErrorModal(false);
          setError(null);
        }}
        onTryAgain={() => {
          generateScheduleWithConstraints();
        }}
      />
    </div>
  );
};

export default SchedulerPage;