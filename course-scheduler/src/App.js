import React, { useState, useCallback, useEffect } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import Navigation from './components/Navigation/Navigation';
import Sidebar from './components/Sidebar/Sidebar';
import Dashboard from './components/Dashboard/Dashboard';
import CourseInput from './components/CourseInput';
import WeeklyScheduler from './components/WeeklyScheduler';
import ConstraintsDisplay from './components/ConstraintsDisplay';
import LoginRegister from './components/Auth/LoginRegister';
import UserProfile from './components/UserProfile/UserProfile';
import './styles/base.css';
import './styles/App.css';

function App({ setSchedule, setIsLoading, setParsedConstraints, parsedConstraints, onConstraintsUpdate, user, setUser }) {
  const [preference, setPreference] = useState("crammed");
  const [courses, setCourses] = useState([
    { name: "", lectures: "", ta_times: "" },
  ]);
  const [constraints, setConstraints] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');

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

  const generateScheduleWithConstraints = useCallback(async (constraintsToUse) => {
    try {
      // Validate form
      validateForm();

      const formattedCourses = courses.map((c) => ({
        name: c.name.trim(),
        lectures: c.lectures.split(",").map((s) => s.trim()).filter(s => s),
        ta_times: c.ta_times.split(",").map((s) => s.trim()).filter(s => s),
      }));

      // Store original course options in localStorage for drag and drop functionality
      localStorage.setItem('originalCourseOptions', JSON.stringify(formattedCourses));

      // Generate schedule
      const scheduleRes = await fetch("http://127.0.0.1:5000/api/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
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
        setCurrentView('scheduler'); // Switch to scheduler view when schedule is generated
      } else {
        setError(data.error || 'No valid schedule found with the given constraints. Try adjusting your requirements.');
      }
    } catch (err) {
      setError(err.message || 'Failed to connect to backend. Please make sure the server is running.');
    }
  }, [courses, preference, setSchedule, setError]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    setIsLoading(true);
    setParsedConstraints(null); // Clear previous constraints

    try {
      // Parse constraints
      let parsedConstraints = [];
      let constraintsData = null;
      if (constraints.trim()) {
        const parseRes = await fetch("http://127.0.0.1:5000/api/parse", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: 'include',
          body: JSON.stringify({ text: constraints }),
        });

        if (!parseRes.ok) {
          const errorData = await parseRes.json();
          throw new Error(errorData.error || 'Failed to parse constraints');
        }

        constraintsData = await parseRes.json();
        parsedConstraints = constraintsData.constraints || [];
        
        // Set the parsed constraints for display
        setParsedConstraints(constraintsData);
      }

      await generateScheduleWithConstraints(parsedConstraints);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend. Please make sure the server is running.');
      setParsedConstraints(null);
    } finally {
      setIsSubmitting(false);
      setIsLoading(false);
    }
  };

  // Expose the constraints update function - use useCallback to prevent infinite loops
  React.useEffect(() => {
    if (onConstraintsUpdate) {
      onConstraintsUpdate(generateScheduleWithConstraints);
    }
  }, [onConstraintsUpdate, generateScheduleWithConstraints]);

  const handleQuickAction = (actionId) => {
    switch (actionId) {
      case 'new-schedule':
        setCurrentView('scheduler');
        break;
      case 'saved-schedules':
        // TODO: Implement saved schedules view
        console.log('Saved schedules view');
        break;
      case 'templates':
        // TODO: Implement templates view
        console.log('Templates view');
        break;
      case 'analytics':
        // TODO: Implement analytics view
        console.log('Analytics view');
        break;
      default:
        break;
    }
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard user={user} />;
      case 'scheduler':
        return (
          <div className="scheduler-view">
            <div className="scheduler-content">
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
              
              <div className="right-panel">
                <ConstraintsDisplay 
                  parsedConstraints={parsedConstraints} 
                  onConstraintsUpdate={handleConstraintsUpdate}
                  isRegenerating={isLoading}
                />
                <WeeklyScheduler schedule={schedule} isLoading={isLoading} />
              </div>
            </div>
          </div>
        );
      default:
        return <Dashboard user={user} />;
    }
  };

  return (
    <div className="app-main">
      {renderCurrentView()}
    </div>
  );
}

function AppWrapper() {
  const [schedule, setSchedule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parsedConstraints, setParsedConstraints] = useState(null);
  const [constraintsUpdateFunction, setConstraintsUpdateFunction] = useState(null);
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard');

  // Check if user is already logged in on app start
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/auth/me', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          setUser(data.user);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuthStatus();
  }, []);

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

  const handleSetConstraintsUpdateFunction = useCallback((func) => {
    setConstraintsUpdateFunction(() => func);
  }, []);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuth(false);
  };

  const handleLogout = () => {
    setUser(null);
    setShowProfile(false);
    setCurrentView('dashboard');
    // Clear any user-specific data
    setSchedule(null);
    setParsedConstraints(null);
  };

  const handleQuickAction = (actionId) => {
    switch (actionId) {
      case 'new-schedule':
        setCurrentView('scheduler');
        break;
      case 'saved-schedules':
        // TODO: Implement saved schedules view
        console.log('Saved schedules view');
        break;
      case 'templates':
        // TODO: Implement templates view
        console.log('Templates view');
        break;
      case 'analytics':
        // TODO: Implement analytics view
        console.log('Analytics view');
        break;
      default:
        break;
    }
  };

  if (isCheckingAuth) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="app-wrapper">
        <Navigation 
          user={user}
          onAuthClick={() => setShowAuth(true)}
          onProfileClick={() => setShowProfile(true)}
        />

        <div className="app-layout">
          <Sidebar 
            user={user}
            onQuickAction={handleQuickAction}
          />
          
          <main className="main-content">
            <App 
              setSchedule={setSchedule} 
              setIsLoading={setIsLoading}
              setParsedConstraints={setParsedConstraints}
              parsedConstraints={parsedConstraints}
              onConstraintsUpdate={handleSetConstraintsUpdateFunction}
              user={user}
              setUser={setUser}
              schedule={schedule}
              isLoading={isLoading}
              handleConstraintsUpdate={handleConstraintsUpdate}
            />
          </main>
        </div>

        {showAuth && (
          <LoginRegister 
            onAuthSuccess={handleAuthSuccess}
            onClose={() => setShowAuth(false)}
          />
        )}

        {showProfile && user && (
          <UserProfile 
            user={user}
            onLogout={handleLogout}
            onClose={() => setShowProfile(false)}
          />
        )}
      </div>
    </Router>
  );
}

export default AppWrapper;