import React, { useState, useEffect } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import Navigation from './components/Navigation/Navigation';
import SchedulerPage from './pages/SchedulerPage';
import SchedulesPage from './pages/SchedulesPage';
import ProfilePage from './pages/ProfilePage';
import LoginRegister from './components/Auth/LoginRegister';
import './styles/base.css';
import './styles/App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('scheduler');
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

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

  const handleNavigate = (page) => {
    if (page === 'auth') {
      setShowAuth(true);
    } else if ((page === 'schedules' || page === 'profile') && !user) {
      setShowAuth(true);
    } else {
      setCurrentPage(page);
    }
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuth(false);
    // If user was trying to access a protected page, navigate there
    if (currentPage === 'scheduler' && (window.location.hash === '#schedules' || window.location.hash === '#profile')) {
      setCurrentPage(window.location.hash.substring(1));
    }
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage('scheduler');
    // Clear any user-specific data
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'scheduler':
        return <SchedulerPage user={user} />;
      case 'schedules':
        return <SchedulesPage user={user} />;
      case 'profile':
        return <ProfilePage user={user} onLogout={handleLogout} />;
      default:
        return <SchedulerPage user={user} />;
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
          currentPage={currentPage}
          onNavigate={handleNavigate}
          user={user}
        />

        <div className="app-content">
          {renderCurrentPage()}
        </div>

        {showAuth && (
          <LoginRegister 
            onAuthSuccess={handleAuthSuccess}
            onClose={() => setShowAuth(false)}
          />
        )}
      </div>
    </Router>
  );
}

export default App;