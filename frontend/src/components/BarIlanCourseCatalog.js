import React, { useState, useEffect, useCallback } from 'react';
import '../styles/BarIlanCourseCatalog.css';

const BarIlanCourseCatalog = ({ university, semester, year, onCoursesSelected, onBack }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState('cs');
  const [showHebrew, setShowHebrew] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  // Bar-Ilan departments
  const departments = [
    { id: 'cs', name: 'מדעי המחשב', name_en: 'Computer Science' },
    { id: 'math', name: 'מתמטיקה', name_en: 'Mathematics' },
    { id: 'physics', name: 'פיזיקה', name_en: 'Physics' },
    { id: 'chemistry', name: 'כימיה', name_en: 'Chemistry' },
    { id: 'business', name: 'ניהול', name_en: 'Business' },
    { id: 'psychology', name: 'פסיכולוגיה', name_en: 'Psychology' },
    { id: 'education', name: 'חינוך', name_en: 'Education' }
  ];

  const fetchCourses = useCallback(async () => {
    setIsLoading(true);
    try {
      let url;
      if (searchQuery.trim()) {
        // Use search endpoint if there's a query
        url = `${API_BASE_URL}/api/university/bar-ilan/search?q=${encodeURIComponent(searchQuery)}&department=${selectedDepartment}&year=${year}`;
      } else {
        // Use regular courses endpoint for department browsing
        url = `${API_BASE_URL}/api/university/bar-ilan/courses?semester=${semester}&year=${year}&department=${selectedDepartment}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (searchQuery.trim()) {
          setAvailableCourses(data.results || []);
        } else {
          setAvailableCourses(data.courses || []);
        }
      } else {
        console.error('Failed to fetch Bar-Ilan courses');
        setAvailableCourses([]);
      }
    } catch (error) {
      console.error('Error fetching Bar-Ilan courses:', error);
      setAvailableCourses([]);
    } finally {
      setIsLoading(false);
    }
  }, [API_BASE_URL, searchQuery, selectedDepartment, semester, year]);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  const handleSearch = () => {
    if (searchQuery.trim()) {
      fetchCourses();
    } else {
      // If search is cleared, fetch all courses for the department
      fetchCourses();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleCourseSelect = (course, section) => {
    const courseSelection = {
      courseId: course.id,
      sectionId: section.id,
      course: course,
      section: section
    };

    const isAlreadySelected = selectedCourses.some(
      selected => selected.sectionId === section.id
    );

    if (isAlreadySelected) {
      setSelectedCourses(prev => prev.filter(selected => selected.sectionId !== section.id));
    } else {
      // Remove other sections of the same course
      const otherSections = selectedCourses.filter(
        selected => selected.courseId !== course.id
      );
      setSelectedCourses([...otherSections, courseSelection]);
    }
  };

  const handleContinue = () => {
    if (selectedCourses.length > 0) {
      onCoursesSelected(selectedCourses);
    }
  };

  const getDepartmentName = () => {
    const dept = departments.find(d => d.id === selectedDepartment);
    return showHebrew ? dept?.name : dept?.name_en;
  };

  const getEnrollmentStatus = (enrolled, maxStudents) => {
    if (maxStudents === 0) return 'unknown';
    const ratio = enrolled / maxStudents;
    if (ratio >= 1) return 'full';
    if (ratio >= 0.8) return 'limited';
    return 'available';
  };

  const getEnrollmentStatusText = (status) => {
    const texts = {
      'available': showHebrew ? 'פנוי' : 'Available',
      'limited': showHebrew ? 'מוגבל' : 'Limited',
      'full': showHebrew ? 'מלא' : 'Full',
      'unknown': showHebrew ? 'לא ידוע' : 'Unknown'
    };
    return texts[status] || texts.unknown;
  };

  const renderCourseCard = (course) => (
    <div key={course.id} className="course-card">
      <div className="course-header">
        <div className="course-code">{course.code}</div>
        <div className="course-credits">
          {course.credits} {showHebrew ? "נק'" : "credits"}
        </div>
      </div>
      
      <div className={`course-title ${showHebrew ? 'hebrew' : ''}`}>
        {showHebrew ? course.name : course.name_en}
      </div>
      
      {(course.lecturer || course.lecturer_en) && (
        <div className={`course-lecturer ${showHebrew ? 'hebrew' : ''}`}>
          👨‍🏫 {showHebrew ? course.lecturer : course.lecturer_en}
        </div>
      )}
      
      {(course.description || course.description_en) && (
        <div className={`course-description ${showHebrew ? 'hebrew' : ''}`}>
          {showHebrew ? course.description : course.description_en}
        </div>
      )}
      
      {course.sections && course.sections.length > 0 && (
        <div className="sections-list">
          <div className="sections-title">
            {showHebrew ? "קבוצות:" : "Sections:"}
          </div>
          {course.sections.map((section, idx) => {
            const isSelected = selectedCourses.some(
              selected => selected.courseId === course.id && selected.sectionId === section.section
            );
            const enrollmentStatus = getEnrollmentStatus(section.enrolled, section.max_students);
            
            return (
              <div key={idx} className="section-item">
                <div className="section-info">
                  <div className="section-type">
                    {section.section} - {showHebrew ? section.type : section.type_en}
                  </div>
                  {section.schedule && (
                    <div className="section-schedule">
                      🕐 {section.schedule}
                    </div>
                  )}
                  {section.location && (
                    <div className="section-location">
                      📍 {section.location}
                    </div>
                  )}
                  {section.max_students > 0 && (
                    <div className="enrollment-status">
                      <div className={`enrollment-indicator enrollment-${enrollmentStatus}`}></div>
                      <span>
                        {section.enrolled}/{section.max_students} - {getEnrollmentStatusText(enrollmentStatus)}
                      </span>
                    </div>
                  )}
                </div>
                <button
                  className={`section-select-btn ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleCourseSelect(course, {
                    id: section.section,
                    section: section.section,
                    type: section.type,
                    type_en: section.type_en,
                    schedule: section.schedule,
                    parsed_schedule: section.parsed_schedule,
                    location: section.location,
                    enrolled: section.enrolled,
                    max_students: section.max_students
                  })}
                  disabled={enrollmentStatus === 'full'}
                >
                  {isSelected 
                    ? (showHebrew ? "נבחר" : "Selected")
                    : enrollmentStatus === 'full' 
                      ? (showHebrew ? "מלא" : "Full")
                      : (showHebrew ? "בחר" : "Select")
                  }
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  return (
    <div className="bar-ilan-catalog-container">
      <div className="catalog-header">
        <button className="back-button" onClick={onBack}>
          ← חזרה
        </button>
        <div className="header-content">
          <h1>קטלוג קורסים - אוניברסיטת בר־אילן</h1>
          <h2>Bar-Ilan University Course Catalog</h2>
          <p>{getDepartmentName()} • {semester} {year}</p>
        </div>
        <div className="language-toggle">
          <button
            className={`lang-btn ${showHebrew ? 'active' : ''}`}
            onClick={() => setShowHebrew(true)}
          >
            עב
          </button>
          <button
            className={`lang-btn ${!showHebrew ? 'active' : ''}`}
            onClick={() => setShowHebrew(false)}
          >
            EN
          </button>
        </div>
      </div>

      <div className="catalog-controls">
        <div className="search-section">
          <input
            type="text"
            placeholder={showHebrew ? "חפש קורסים..." : "Search courses..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            className="search-input"
          />
          <button onClick={handleSearch} className="search-button">
            {showHebrew ? "חפש" : "Search"}
          </button>
        </div>

        <div className="department-filter">
          <label>{showHebrew ? "חוג:" : "Department:"}</label>
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="department-select"
          >
            {departments.map(dept => (
              <option key={dept.id} value={dept.id}>
                {showHebrew ? dept.name : dept.name_en}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedCourses.length > 0 && (
        <div className="selected-summary">
          <p>
            {showHebrew ? "נבחרו" : "Selected"}: {selectedCourses.length} {showHebrew ? "קורסים" : "courses"}
          </p>
          <button onClick={handleContinue} className="continue-button">
            {showHebrew ? "המשך לבניית מערכת" : "Continue to Schedule Builder"}
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">
            {showHebrew ? "טוען קורסים..." : "Loading courses..."}
          </div>
        </div>
      ) : (
        <div className="courses-grid">
          {availableCourses.map(course => renderCourseCard(course))}

          {availableCourses.length === 0 && (
            <div className="no-courses">
              <div className="no-courses-icon">📚</div>
              <h3>{showHebrew ? "לא נמצאו קורסים" : "No courses found"}</h3>
              <p>
                {showHebrew 
                  ? "נסה לשנות את החיפוש או החוג"
                  : "Try changing your search or department"
                }
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BarIlanCourseCatalog;
