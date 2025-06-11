import React, { useState } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import CourseInput from './components/CourseInput';
import WeeklyScheduler from './components/WeeklyScheduler';
import './styles/base.css';
import './styles/App.css';

function App({ setSchedule, setIsLoading }) {
  const [preference, setPreference] = useState("crammed");
  const [courses, setCourses] = useState([
    { name: "", lectures: "", ta_times: "" },
  ]);
  const [constraints, setConstraints] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const validateForm = () => {
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
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    setIsLoading(true);

    try {
      // Validate form
      validateForm();

      const formattedCourses = courses.map((c) => ({
        name: c.name.trim(),
        lectures: c.lectures.split(",").map((s) => s.trim()).filter(s => s),
        ta_times: c.ta_times.split(",").map((s) => s.trim()).filter(s => s),
      }));

      // Parse constraints
      let parsedConstraints = [];
      if (constraints.trim()) {
        const parseRes = await fetch("http://127.0.0.1:5000/api/parse", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: constraints }),
        });

        if (!parseRes.ok) {
          const errorData = await parseRes.json();
          throw new Error(errorData.error || 'Failed to parse constraints');
        }

        const parsedData = await parseRes.json();
        parsedConstraints = parsedData.constraints || [];
      }

      // Generate schedule
      const scheduleRes = await fetch("http://127.0.0.1:5000/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preference,
          courses: formattedCourses,
          constraints: parsedConstraints
        }),
      });

      if (!scheduleRes.ok) {
        const errorData = await scheduleRes.json();
        throw new Error(errorData.error || 'Failed to generate schedule');
      }

      const data = await scheduleRes.json();
      
      if (data.schedule) {
        setSchedule(data.schedule);
      } else {
        setError(data.error || 'No valid schedule found with the given constraints. Try adjusting your requirements.');
      }
    } catch (err) {
      setError(err.message || 'Failed to connect to backend. Please make sure the server is running.');
    } finally {
      setIsSubmitting(false);
      setIsLoading(false);
    }
  };

  return (
    <div className="course-scheduler">
      <h2>Course Scheduler</h2>
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
  );
}

function AppWrapper() {
  const [schedule, setSchedule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <Router>
      <div className="app-wrapper">
        <App setSchedule={setSchedule} setIsLoading={setIsLoading} />
        <WeeklyScheduler schedule={schedule} isLoading={isLoading} />
      </div>
    </Router>
  );
}

export default AppWrapper;