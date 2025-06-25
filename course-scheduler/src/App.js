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
        console.log('🔍 Checking auth status...');
        const response = await fetch('http://127.0.0.1:5000/api/auth/me', {
          method: 'GET',
          credentials: 'include', // Include cookies
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest', // Add this header
          }
        });
        
        console.log('Auth check response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('✅ Auth check successful:', data);
          setUser(data.user);
        } else {
          console.log('❌ Auth check failed:', response.status);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    // Add a small delay to ensure the backend is ready
    setTimeout(checkAuthStatus, 100);
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

  const handleAuthSuccess = async (userData) => {
    console.log('✅ Authentication successful:', userData.first_name);
    setUser(userData);
    setShowAuth(false);
    
    // Debug: Check session after setting user
    try {
      console.log('🔍 Post-auth verification...');
      
      // Check cookies
      console.log('🍪 Cookies after auth:', document.cookie);
      
      // Test session endpoint
      const debugResponse = await fetch('http://127.0.0.1:5000/api/debug/session', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        }
      });
      
      if (debugResponse.ok) {
        const debugData = await debugResponse.json();
        console.log('🔍 Post-auth debug:', debugData);
      }
      
      // Test /me endpoint
      const testResponse = await fetch('http://127.0.0.1:5000/api/auth/me', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        }
      });
      
      if (testResponse.ok) {
        const testData = await testResponse.json();
        console.log('🔍 Test session data:', testData);
      } else {
        console.log('❌ Test session failed:', testResponse.status);
      }
      
    } catch (error) {
      console.error('Post-auth verification failed:', error);
    }
    
    // If user was trying to access a protected page, navigate there
    if (currentPage === 'scheduler' && (window.location.hash === '#schedules' || window.location.hash === '#profile')) {
      setCurrentPage(window.location.hash.substring(1));
    }
  };

  const handleLogout = async () => {
    try {
      console.log('🔄 Logging out...');
      const response = await fetch('http://127.0.0.1:5000/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        }
      });
      
      console.log('Logout response status:', response.status);
      
      if (response.ok) {
        setUser(null);
        setCurrentPage('scheduler');
        console.log('✅ Logout successful');
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear the user state even if the request fails
      setUser(null);
      setCurrentPage('scheduler');
    }
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