import React, { useState, useEffect } from 'react';
import '../styles/CourseCatalog.css';

const CourseCatalog = ({ university, semester, year, onCoursesSelected, onBack }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCourses, setSelectedCourses] = useState([]);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    department: '',
    level: '',
    credits: '',
    timeOfDay: ''
  });

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  // Mock course data - replace with real API calls
  const mockCourses = [
    {
      id: 'cs101',
      code: 'CS 101',
      name: 'Introduction to Computer Science',
      department: 'Computer Science',
      credits: 3,
      professor: 'Dr. Sarah Chen',
      description: 'Fundamental concepts in computer science and programming.',
      sections: [
        {
          id: 'cs101-001',
          section: '001',
          times: [
            { type: 'lecture', day: 'Mon', startTime: 9, endTime: 11 },
            { type: 'lecture', day: 'Wed', startTime: 9, endTime: 11 },
            { type: 'lab', day: 'Fri', startTime: 14, endTime: 16 }
          ],
          professor: 'Dr. Sarah Chen',
          capacity: 120,
          enrolled: 85,
          location: 'Science Building 101'
        },
        {
          id: 'cs101-002', 
          section: '002',
          times: [
            { type: 'lecture', day: 'Tue', startTime: 13, endTime: 15 },
            { type: 'lecture', day: 'Thu', startTime: 13, endTime: 15 },
            { type: 'lab', day: 'Fri', startTime: 16, endTime: 18 }
          ],
          professor: 'Prof. Michael Rodriguez',
          capacity: 120,
          enrolled: 92,
          location: 'Science Building 102'
        }
      ]
    },
    {
      id: 'math201',
      code: 'MATH 201',
      name: 'Calculus I',
      department: 'Mathematics',
      credits: 4,
      professor: 'Dr. Emily Watson',
      description: 'Limits, derivatives, and applications of differential calculus.',
      sections: [
        {
          id: 'math201-001',
          section: '001',
          times: [
            { type: 'lecture', day: 'Mon', startTime: 10, endTime: 12 },
            { type: 'lecture', day: 'Wed', startTime: 10, endTime: 12 },
            { type: 'lecture', day: 'Fri', startTime: 10, endTime: 11 }
          ],
          professor: 'Dr. Emily Watson',
          capacity: 200,
          enrolled: 178,
          location: 'Math Building 201'
        }
      ]
    },
    {
      id: 'eng102',
      code: 'ENG 102', 
      name: 'Academic Writing',
      department: 'English',
      credits: 3,
      professor: 'Prof. David Kim',
      description: 'Advanced writing skills for academic and professional contexts.',
      sections: [
        {
          id: 'eng102-001',
          section: '001',
          times: [
            { type: 'lecture', day: 'Tue', startTime: 11, endTime: 12 },
            { type: 'lecture', day: 'Thu', startTime: 11, endTime: 12 }
          ],
          professor: 'Prof. David Kim',
          capacity: 25,
          enrolled: 23,
          location: 'Humanities 150'
        },
        {
          id: 'eng102-002',
          section: '002', 
          times: [
            { type: 'lecture', day: 'Mon', startTime: 14, endTime: 15 },
            { type: 'lecture', day: 'Wed', startTime: 14, endTime: 15 }
          ],
          professor: 'Dr. Lisa Park',
          capacity: 25,
          enrolled: 20,
          location: 'Humanities 152'
        }
      ]
    }
  ];

  useEffect(() => {
    const fetchCourses = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/university/courses?universityId=${university.id}&semester=${semester}&year=${year}`);
        
        if (response.ok) {
          const data = await response.json();
          setAvailableCourses(data.courses || mockCourses);
        } else {
          console.error('Failed to fetch courses, using mock data');
          setAvailableCourses(mockCourses);
        }
      } catch (error) {
        console.error('Error fetching courses:', error);
        setAvailableCourses(mockCourses);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCourses();
  }, [university, semester, year, API_BASE_URL]);

  const filteredCourses = availableCourses.filter(course => {
    const matchesSearch = course.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         course.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         course.professor.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesDepartment = !filters.department || course.department === filters.department;
    const matchesCredits = !filters.credits || course.credits.toString() === filters.credits;
    
    return matchesSearch && matchesDepartment && matchesCredits;
  });

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
      setSelectedCourses(selectedCourses.filter(
        selected => selected.sectionId !== section.id
      ));
    } else {
      // Remove other sections of the same course
      const withoutOtherSections = selectedCourses.filter(
        selected => selected.courseId !== course.id
      );
      setSelectedCourses([...withoutOtherSections, courseSelection]);
    }
  };

  const handleContinue = () => {
    if (onCoursesSelected && selectedCourses.length > 0) {
      onCoursesSelected(selectedCourses);
    }
  };

  const getEnrollmentStatus = (section) => {
    const percentage = (section.enrolled / section.capacity) * 100;
    if (percentage >= 95) return { status: 'full', color: 'error' };
    if (percentage >= 85) return { status: 'almost-full', color: 'warning' };
    return { status: 'available', color: 'success' };
  };

  const formatTimeSlot = (times) => {
    return times.map(time => 
      `${time.day} ${time.startTime}:00-${time.endTime}:00 (${time.type})`
    ).join(', ');
  };

  if (isLoading) {
    return (
      <div className="course-catalog-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <h3>Loading course catalog...</h3>
          <p>Fetching courses from {university.name}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="course-catalog-container">
      <div className="catalog-header">
        <button className="back-button" onClick={onBack}>
          ← Back to University Selection
        </button>
        <h1>Course Catalog</h1>
        <p>{university.name} - {semester} {year}</p>
      </div>

      <div className="search-and-filters">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search courses by name, code, or professor..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="course-search-input"
          />
        </div>
        
        <div className="filters">
          <select
            value={filters.department}
            onChange={(e) => setFilters({...filters, department: e.target.value})}
            className="filter-select"
          >
            <option value="">All Departments</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Mathematics">Mathematics</option>
            <option value="English">English</option>
          </select>
          
          <select
            value={filters.credits}
            onChange={(e) => setFilters({...filters, credits: e.target.value})}
            className="filter-select"
          >
            <option value="">All Credits</option>
            <option value="1">1 Credit</option>
            <option value="2">2 Credits</option>
            <option value="3">3 Credits</option>
            <option value="4">4 Credits</option>
          </select>
        </div>
      </div>

      <div className="selected-courses-summary">
        <h3>Selected Courses ({selectedCourses.length})</h3>
        {selectedCourses.length > 0 ? (
          <div className="selected-courses-list">
            {selectedCourses.map(selection => (
              <div key={selection.sectionId} className="selected-course-item">
                <span>{selection.course.code} - {selection.course.name}</span>
                <span className="section-info">Section {selection.section.section}</span>
                <button 
                  onClick={() => handleCourseSelect(selection.course, selection.section)}
                  className="remove-course-btn"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-courses-selected">No courses selected yet</p>
        )}
      </div>

      <div className="courses-list">
        {filteredCourses.map(course => (
          <div key={course.id} className="course-card">
            <div className="course-info">
              <div className="course-header">
                <h3 className="course-title">{course.code} - {course.name}</h3>
                <span className="course-credits">{course.credits} credits</span>
              </div>
              <p className="course-description">{course.description}</p>
              <div className="course-meta">
                <span className="department">{course.department}</span>
                <span className="professor">{course.professor}</span>
              </div>
            </div>
            
            <div className="course-sections">
              <h4>Available Sections:</h4>
              {course.sections.map(section => {
                const enrollmentStatus = getEnrollmentStatus(section);
                const isSelected = selectedCourses.some(
                  selected => selected.sectionId === section.id
                );
                
                return (
                  <div 
                    key={section.id} 
                    className={`section-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleCourseSelect(course, section)}
                  >
                    <div className="section-header">
                      <span className="section-number">Section {section.section}</span>
                      <span className={`enrollment-badge ${enrollmentStatus.color}`}>
                        {section.enrolled}/{section.capacity}
                      </span>
                    </div>
                    <div className="section-details">
                      <p className="section-times">{formatTimeSlot(section.times)}</p>
                      <p className="section-professor">{section.professor}</p>
                      <p className="section-location">{section.location}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {selectedCourses.length > 0 && (
        <div className="continue-section">
          <button className="continue-btn" onClick={handleContinue}>
            Continue with {selectedCourses.length} Selected Course{selectedCourses.length !== 1 ? 's' : ''}
          </button>
        </div>
      )}
    </div>
  );
};

export default CourseCatalog;
