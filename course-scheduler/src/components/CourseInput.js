import React from 'react';
import '../styles/CourseInput.css';

const CourseInput = ({ course, onChange, index }) => {
    return (
        <div className="course-block">
          <input
            type="text"
            placeholder="Course Name (e.g., CS101)"
            value={course.name}
            onChange={(e) => onChange(index, "name", e.target.value)}
            className="course-input"
            required
          />
          <textarea
            placeholder="Lectures (e.g., Monday 9-11, Wednesday 10-12)"
            value={course.lectures}
            onChange={(e) => onChange(index, "lectures", e.target.value)}
            className="time-input"
            rows={3}
            required
          />
          <textarea
            placeholder="TA Times (e.g., Tuesday 10-12, Thursday 10-12)"
            value={course.ta_times}
            onChange={(e) => onChange(index, "ta_times", e.target.value)}
            className="time-input"
            rows={3}
            required
          />
        </div>
      );
};

export default CourseInput;