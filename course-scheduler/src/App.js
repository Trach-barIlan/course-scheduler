import React, { useState } from "react";
import CourseForm from "./components/CourseForm";
import WeeklySchedule from "./components/WeeklySchedule";
import './App.css';

function App() {
  const [courses, setCourses] = useState([{ name: "", lectures: "", ta_times: "" }]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [screen, setScreen] = useState("input");

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
    setResult(null);
    setError(null);

    const payload = {
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
          setScreen("result");
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
    <div style={{ maxWidth: 800, margin: "auto", padding: 20 }}>
      <h2>Course Scheduler</h2>

      {screen === "input" && (
        <form onSubmit={handleSubmit}>
          <CourseForm courses={courses} onChange={handleCourseChange} onAdd={addCourse} />
          <br />
          <button type="submit">Generate Schedule</button>
        </form>
      )}

      {error && <div style={{ color: "red", marginTop: 20 }}><strong>Error:</strong> {error}</div>}

      {screen === "result" && result && (
        <div>
          <h3>Weekly Schedule:</h3>
          <WeeklySchedule schedule={result} />
          <br />
          <button onClick={() => setScreen("input")}>← Back</button>
        </div>
      )}
    </div>
  );
}

export default App;
