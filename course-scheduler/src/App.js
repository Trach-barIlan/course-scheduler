import React, { useState } from "react";
import './App.css';


function App() {
  const [preference, setPreference] = useState("crammed");
  const [courses, setCourses] = useState([
    { name: "", lectures: "", ta_times: "" },
  ]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Handle input changes for course fields
  const handleCourseChange = (index, field, value) => {
    const newCourses = [...courses];
    newCourses[index][field] = value;
    setCourses(newCourses);
  };

  // Add a new empty course input row
  const addCourse = () => {
    setCourses([...courses, { name: "", lectures: "", ta_times: "" }]);
  };

  // Submit to Flask API
  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setError(null);

    // Prepare data in expected format
    const payload = {
      preference,
      courses: courses.map((c) => ({
        name: c.name,
        lectures: c.lectures.split(",").map((s) => s.trim()),
        ta_times: c.ta_times.split(",").map((s) => s.trim()),
      })),
    };
    

    try {
      const res = await fetch("http://127.0.0.1:5000/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok) {
        if (data.schedule) {
          setResult(data.schedule);
        } else if (data.error) {
          setError(data.error);
        }
      } else {
        setError("Server error");
      }
    } catch (err) {
      setError("Failed to connect to backend");
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
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
          <div
            key={i}
            style={{
              border: "1px solid #ccc",
              padding: 10,
              marginBottom: 10,
              borderRadius: 5,
            }}
          >
            <input
              type="text"
              placeholder="Course Name"
              value={course.name}
              onChange={(e) => handleCourseChange(i, "name", e.target.value)}
              required
              style={{ width: "100%", marginBottom: 6 }}
            />
            <input
              type="text"
              placeholder="Lectures (e.g. Mon 9-11, Wed 10-12)"
              value={course.lectures}
              onChange={(e) => handleCourseChange(i, "lectures", e.target.value)}
              required
              style={{ width: "100%", marginBottom: 6 }}
            />
            <input
              type="text"
              placeholder="TA times (e.g. Tue 10-12, Thu 10-12)"
              value={course.ta_times}
              onChange={(e) => handleCourseChange(i, "ta_times", e.target.value)}
              required
              style={{ width: "100%" }}
            />
          </div>
        ))}

        <button type="button" onClick={addCourse}>
          + Add Another Course
        </button>
        <br />
        <br />
        <button type="submit">Generate Schedule</button>
      </form>

      {error && (
        <div style={{ color: "red", marginTop: 20 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Schedule Result:</h3>
          <ul>
            {result.map(({ name, lecture, ta }, i) => (
              <li key={i}>
                <strong>{name}</strong>: Lecture - {lecture}, TA - {ta}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
