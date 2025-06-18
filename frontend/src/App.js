import React, { useState, useCallback, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import Navigation from './components/Navigation/Navigation';
import Sidebar from './components/Sidebar/Sidebar';
import HomePage from './pages/HomePage';
import SchedulerPage from './pages/SchedulerPage';
import AboutPage from './pages/AboutPage';
import LoginRegister from './components/Auth/LoginRegister';
import UserProfile from './components/UserProfile/UserProfile';
import './styles/base.css';
import './styles/App.css';

function AppContent() {
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const navigate = useNavigate();

  // Enhanced authentication check
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        console.log('🔍 Checking authentication status...');
        
        const response = await fetch('http://127.0.0.1:5000/api/auth/me', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        console.log('Auth check response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('✅ User authenticated:', data.user?.username);
          setUser(data.user);
        } else {
          console.log('❌ No active session found');
          setUser(null);
        }
      } catch (error) {
        console.error('❌ Auth check failed:', error);
        setUser(null);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuthStatus();
  }, []);

  const handleAuthSuccess = (userData) => {
    console.log('✅ Authentication successful:', userData?.username);
    setUser(userData);
    setShowAuth(false);
    
    // Verify the session was set correctly
    setTimeout(async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/auth/debug', {
          credentials: 'include'
        });
        const debugData = await response.json();
        console.log('🔍 Post-auth debug:', debugData);
      } catch (error) {
        console.error('Debug check failed:', error);
      }
    }, 1000);
  };

  const handleLogout = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        console.log('✅ Logout successful');
      } else {
        console.error('❌ Logout failed');
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    setUser(null);
    setShowProfile(false);
    navigate('/');
  };

  const handleQuickAction = useCallback((actionId) => {
    switch (actionId) {
      case 'new-schedule':
        navigate('/scheduler');
        break;
      case 'home':
        navigate('/');
        break;
      default:
        console.log(`Quick action: ${actionId}`);
        break;
    }
  }, [navigate]);

  if (isCheckingAuth) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
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
          <Routes>
            <Route 
              path="/" 
              element={<HomePage user={user} onQuickAction={handleQuickAction} />} 
            />
            <Route 
              path="/scheduler" 
              element={<SchedulerPage user={user} />} 
            />
            <Route 
              path="/about" 
              element={<AboutPage />} 
            />
          </Routes>
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
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;