import React from "react";

const CourseForm = ({ courses, onChange, onAdd }) => {
  return (
    <>
      {courses.map((course, i) => (
        <div key={i} style={{ border: "1px solid #ccc", padding: 10, marginBottom: 10, borderRadius: 5 }}>
          <input
            type="text"
            placeholder="Course Name"
            value={course.name}
            onChange={(e) => onChange(i, "name", e.target.value)}
            required
            style={{ width: "100%", marginBottom: 6 }}
          />
          <input
            type="text"
            placeholder="Lectures (e.g. Mon 9-11, Wed 10-12)"
            value={course.lectures}
            onChange={(e) => onChange(i, "lectures", e.target.value)}
            required
            style={{ width: "100%", marginBottom: 6 }}
          />
          <input
            type="text"
            placeholder="TA times (e.g. Tue 10-12, Thu 10-12)"
            value={course.ta_times}
            onChange={(e) => onChange(i, "ta_times", e.target.value)}
            required
            style={{ width: "100%" }}
          />
        </div>
      ))}
      <button type="button" onClick={onAdd}>+ Add Another Course</button>
    </>
  );
};

export default CourseForm;
