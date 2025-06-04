import React from 'react';
import '../styles/CourseInput.css';

const ScheduleResult = ({ schedule }) => {
  return (
    <div className="result">
      <h3>Schedule Result:</h3>
      <ul>
        {schedule.map(({ name, lecture, ta }, i) => (
          <li key={i}>
            <strong>{name}</strong>
            <div className="time-slot">Lecture: {lecture}</div>
            <div className="time-slot">TA: {ta}</div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ScheduleResult;