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

// Use consistent API URL
const API_BASE_URL = 'http://127.0.0.1:5000';

function AppContent() {
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const navigate = useNavigate();

  // Enhanced authentication check with better session persistence
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        console.log('🔍 Checking authentication status...');
        
        // First, check if we have any session cookies
        const cookies = document.cookie;
        console.log('🍪 Current cookies:', cookies);
        
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
          method: 'GET',
          credentials: 'include', // This is crucial for sending cookies
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        console.log('Auth check response status:', response.status);
        console.log('Auth check response headers:', Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
          const data = await response.json();
          console.log('✅ User authenticated:', data.user?.username);
          setUser(data.user);
        } else {
          console.log('❌ No active session found');
          setUser(null);
          
          // Try to get more debug information
          try {
            const debugResponse = await fetch(`${API_BASE_URL}/api/test-session`, {
              credentials: 'include'
            });
            const debugData = await debugResponse.json();
            console.log('🔍 Session debug info:', debugData);
          } catch (debugError) {
            console.error('Debug check failed:', debugError);
          }
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
    
    // Verify the session was set correctly with enhanced debugging
    setTimeout(async () => {
      try {
        console.log('🔍 Post-auth verification...');
        
        // Check cookies after auth
        console.log('🍪 Cookies after auth:', document.cookie);
        
        // Check debug endpoint
        const debugResponse = await fetch(`${API_BASE_URL}/api/auth/debug`, {
          credentials: 'include'
        });
        const debugData = await debugResponse.json();
        console.log('🔍 Post-auth debug:', debugData);
        
        // Check test session endpoint
        const testResponse = await fetch(`${API_BASE_URL}/api/test-session`, {
          credentials: 'include'
        });
        const testData = await testResponse.json();
        console.log('🔍 Test session data:', testData);
        
        // Verify /me endpoint works
        const meResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
          credentials: 'include'
        });
        console.log('🔍 /me endpoint status:', meResponse.status);
        
        if (meResponse.ok) {
          const meData = await meResponse.json();
          console.log('✅ /me endpoint data:', meData);
          // Update user state if needed
          if (meData.user && !user) {
            setUser(meData.user);
          }
        } else {
          console.log('❌ /me endpoint failed after auth');
        }
        
      } catch (error) {
        console.error('Debug check failed:', error);
      }
    }, 1000);
  };

  const handleLogout = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
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