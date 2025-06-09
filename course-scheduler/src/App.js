import React, { useState } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import CourseInput from './components/CourseInput';
import WeeklyScheduler from './components/WeeklyScheduler';
import './styles/base.css';
import './styles/App.css';

function App({ setSchedule }) {
  const [preference, setPreference] = useState("crammed");
  const [courses, setCourses] = useState([
    { name: "", lectures: "", ta_times: "" },
  ]);
  const [constraints, setConstraints] = useState("");
  const [error, setError] = useState(null);

  const handleCourseChange = (index, field, value) => {
    const newCourses = [...courses];
    newCourses[index][field] = value;
    setCourses(newCourses);
  };

  const addCourse = () => {
    setCourses([...courses, { name: "", lectures: "", ta_times: "" }]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const formattedCourses = courses.map((c) => ({
        name: c.name,
        lectures: c.lectures.split(",").map((s) => s.trim()),
        ta_times: c.ta_times.split(",").map((s) => s.trim()),
      }));
      console.log("1")

      const parseRes = await fetch("http://127.0.0.1:5000/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: constraints }),
      });
      console.log("2")
      if (!parseRes.ok) {
        const errorData = await parseRes.json();
        throw new Error(errorData.error || 'Failed to parse constraints');
      }
      console.log("3")

      const parsedData = await parseRes.json();
      console.log("4")
      console.log("Parsed constraints:", parsedData.constraints);

      const scheduleRes = await fetch("http://127.0.0.1:5000/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preference,
          courses: formattedCourses,
          constraints: parsedData.constraints || []
        }),
      });
      console.log("5")
      if (!scheduleRes.ok) {
        const errorData = await scheduleRes.json();
        throw new Error(errorData.error || 'Failed to generate schedule');
      }

      const data = await scheduleRes.json();
      console.log("6")
      if (data.schedule) {
        setSchedule(data.schedule);
      } else {
        setError(data.error || 'No valid schedule found');
      }
      console.log("7")
      console.log("Schedule generated:", data.schedule);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend');
    }
  };

  return (
    <div className="course-scheduler">
      <h2>Course Scheduler</h2>
      <form onSubmit={handleSubmit}>
        <div className="schedule-preference">
          <label>Schedule Preference:</label>
          <select
            value={preference}
            onChange={(e) => setPreference(e.target.value)}
          >
            <option value="crammed">Crammed (fewer days, back-to-back)</option>
            <option value="spaced">Spaced Out (more days, fewer gaps)</option>
          </select>
        </div>

        {courses.map((course, i) => (
          <CourseInput
            key={i}
            course={course}
            onChange={handleCourseChange}
            index={i}
          />
        ))}

        <div className="constraints-section">
          <label htmlFor="constraints">Additional Constraints:</label>
          <textarea
            id="constraints"
            className="constraints-input"
            value={constraints}
            onChange={(e) => setConstraints(e.target.value)}
            placeholder="Enter your scheduling constraints here. For example:
                    - No classes before 9am
                    - No classes on Tuesday
                    - At least 1 hour break between classes
                    - Prefer morning classes"
            rows={6}
          />
        </div>

        <div className="button-group">
          <button type="button" onClick={addCourse} className="add-button">
            + Add Another Course
          </button>
          <button type="submit" className="submit-button">
            Generate Schedule
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

function AppWrapper() {
  const [schedule, setSchedule] = useState(null);

  return (
    <Router>
      <div className="app-wrapper">
        <App setSchedule={setSchedule} />
        <WeeklyScheduler schedule={schedule} />
      </div>
    </Router>
  );
}

export default AppWrapper;