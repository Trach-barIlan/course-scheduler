import React, { useState, useCallback } from "react";
import CourseInput from '../components/CourseInput';
import WeeklyScheduler from '../components/WeeklyScheduler';
import ConstraintsDisplay from '../components/ConstraintsDisplay';
import '../styles/SchedulerPage.css';

const SchedulerPage = ({ user, authToken }) => {
  const [preference, setPreference] = useState("crammed");
  const [courses, setCourses] = useState([
    { name: "", lectures: "", ta_times: "" },
  ]);
  const [constraints, setConstraints] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [schedule, setSchedule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parsedConstraints, setParsedConstraints] = useState(null);
  const [constraintsUpdateFunction, setConstraintsUpdateFunction] = useState(null);
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL

  const handleCourseChange = (index, field, value) => {
    const newCourses = [...courses];
    newCourses[index][field] = value;
    setCourses(newCourses);
  };

  const addCourse = () => {
    setCourses([...courses, { name: "", lectures: "", ta_times: "" }]);
  };

  const removeCourse = (index) => {
    if (courses.length > 1) {
      setCourses(courses.filter((_, i) => i !== index));
    }
  };

  const validateForm = useCallback(() => {
    for (const course of courses) {
      if (!course.name.trim()) {
        throw new Error("Please fill in all course names");
      }
      if (!course.lectures.trim()) {
        throw new Error(`Please add lecture times for ${course.name}`);
      }
      if (!course.ta_times.trim()) {
        throw new Error(`Please add TA session times for ${course.name}`);
      }
    }
  }, [courses]);

const generateScheduleWithConstraints = useCallback(async (constraintsToUse) => {
  try {
    validateForm(); // Using validateForm inside useCallback

    const formattedCourses = courses.map((c) => ({
      name: c.name.trim(),
      lectures: c.lectures.split(",").map((s) => s.trim()).filter(s => s),
      ta_times: c.ta_times.split(",").map((s) => s.trim()).filter(s => s),
    }));

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

    if (!scheduleRes.ok) {
      const errorData = await scheduleRes.json();
      throw new Error(errorData.error || 'Failed to generate schedule');
    }

    const data = await scheduleRes.json();
    
    if (data.schedule) {
      setSchedule(data.schedule);
      setError(null);
    } else {
      const errorMessage = data.error || 'No valid schedule found with the given constraints. Try adjusting your requirements.';
      setError(errorMessage);
    }
  } catch (err) {
    const errorMessage = err.message || 'Failed to connect to backend. Please make sure the server is running.';
    setError(errorMessage);
  }
}, [courses, preference, validateForm, user, authToken, API_BASE_URL]);

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

        if (!parseRes.ok) {
          const errorData = await parseRes.json();
          throw new Error(errorData.error || 'Failed to parse constraints');
        }

        constraintsData = await parseRes.json();
        parsedConstraints = constraintsData.constraints || [];
        setParsedConstraints(constraintsData);
      }

      await generateScheduleWithConstraints(parsedConstraints);
    } catch (err) {
      const errorMessage = err.message || 'Failed to connect to backend. Please make sure the server is running.';
      setError(errorMessage);
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
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="schedule-preference">
                <label htmlFor="preference">Schedule Preference</label>
                <select
                  id="preference"
                  value={preference}
                  onChange={(e) => setPreference(e.target.value)}
                >
                  <option value="crammed">Crammed (fewer days, back-to-back classes)</option>
                  <option value="spaced">Spaced Out (more days, fewer gaps)</option>
                </select>
              </div>

              {courses.map((course, i) => (
                <CourseInput
                  key={i}
                  course={course}
                  onChange={handleCourseChange}
                  onRemove={removeCourse}
                  index={i}
                  canRemove={courses.length > 1}
                />
              ))}

              <div className="constraints-section">
                <label htmlFor="constraints">Additional Constraints</label>
                <textarea
                  id="constraints"
                  className="constraints-input"
                  value={constraints}
                  onChange={(e) => setConstraints(e.target.value)}
                  placeholder="Enter your scheduling preferences in natural language:

• No classes before 9am
• No classes on Tuesday  
• Avoid TA Smith
• No classes after 5pm
• Prefer morning sessions"
                  rows={6}
                />
              </div>

              <div className="button-group">
                <button 
                  type="button" 
                  onClick={addCourse} 
                  className="add-button"
                  disabled={isSubmitting}
                >
                  + Add Another Course
                </button>
                <button 
                  type="submit" 
                  className="submit-button"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <div className="loading-spinner"></div>
                      Generating Schedule...
                    </>
                  ) : (
                    'Generate Schedule'
                  )}
                </button>
              </div>
            </form>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        </div>

        <div className="right-panel">
          <ConstraintsDisplay 
            parsedConstraints={parsedConstraints} 
            onConstraintsUpdate={handleConstraintsUpdate}
            isRegenerating={isLoading}
          />
          <WeeklyScheduler user={user} authToken={authToken} schedule={schedule} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default SchedulerPage;