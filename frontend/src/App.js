import React, { useState, useCallback, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import Navigation from './components/Navigation/Navigation';
import Sidebar from './components/Sidebar/Sidebar';
import HomePage from './pages/HomePage';
import SchedulerPage from './pages/SchedulerPage';
import AboutPage from './pages/AboutPage';
import LoginRegister from './components/Auth/LoginRegister';
import UserProfile from './components/UserProfile/UserProfile';
import ToastContainer from './components/ToastContainer/ToastContainer';
import useToast from './hooks/useToast';
import './styles/base.css';
import './styles/App.css';

function AppContent() {
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [authToken, setAuthToken] = useState(localStorage.getItem('auth_token'));
  const navigate = useNavigate();
  const { toasts, removeToast, success, error, warning, info } = useToast();

  // Enhanced authentication check with token-based auth
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        console.log('🔍 Checking authentication status...');
        
        const token = localStorage.getItem('auth_token');
        if (!token) {
          console.log('❌ No auth token found');
          setUser(null);
          setIsCheckingAuth(false);
          return;
        }
        
        console.log('🔑 Auth token found, validating...');
        
        const response = await fetch('/api/auth/me', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          }
        });
        
        console.log('Auth check response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('✅ User authenticated:', data.user?.username);
          setUser(data.user);
        } else {
          console.log('❌ Token invalid, removing from storage');
          localStorage.removeItem('auth_token');
          setAuthToken(null);
          setUser(null);
        }
      } catch (error) {
        console.error('❌ Auth check failed:', error);
        localStorage.removeItem('auth_token');
        setAuthToken(null);
        setUser(null);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuthStatus();
  }, [authToken]);

  const handleAuthSuccess = (userData, token) => {
    console.log('✅ Authentication successful:', userData?.username);
    
    // Store token in localStorage
    localStorage.setItem('auth_token', token);
    setAuthToken(token);
    setUser(userData);
    setShowAuth(false);
    
    // Show success toast
    success(`Welcome back, ${userData.first_name}!`, {
      title: 'Login Successful'
    });
    
    console.log('🔑 Token stored successfully');
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        const response = await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          }
        });
        
        if (response.ok) {
          console.log('✅ Logout successful');
          success('You have been signed out successfully', {
            title: 'Signed Out'
          });
        } else {
          console.error('❌ Logout failed');
          warning('There was an issue signing out, but you have been logged out locally');
        }
      }
    } catch (error) {
      console.error('Logout error:', error);
      warning('There was an issue signing out, but you have been logged out locally');
    }
    
    // Clear local state and storage
    localStorage.removeItem('auth_token');
    setAuthToken(null);
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
              element={<HomePage user={user} authToken={authToken} onQuickAction={handleQuickAction} />} 
            />
            <Route 
              path="/scheduler" 
              element={<SchedulerPage user={user} authToken={authToken} toast={{ success, error, warning, info }} />} 
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
          toast={{ success, error, warning, info }}
        />
      )}

      {showProfile && user && (
        <UserProfile 
          user={user}
          authToken={authToken}
          onLogout={handleLogout}
          onClose={() => setShowProfile(false)}
          toast={{ success, error, warning, info }}
        />
      )}

      {/* Toast Container */}
      <ToastContainer 
        toasts={toasts}
        onRemoveToast={removeToast}
        position="top-right"
      />
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