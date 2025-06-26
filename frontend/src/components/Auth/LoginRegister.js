import React, { useState } from 'react';
import './Auth.css';

const LoginRegister = ({ onAuthSuccess, onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (isLogin) {
      // Login validation
      if (!formData.username.trim()) {
        newErrors.username = 'Username or email is required';
      }
      if (!formData.password) {
        newErrors.password = 'Password is required';
      }
    } else {
      // Registration validation
      if (!formData.username.trim()) {
        newErrors.username = 'Username is required';
      } else if (formData.username.length < 3) {
        newErrors.username = 'Username must be at least 3 characters';
      } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
        newErrors.username = 'Username can only contain letters, numbers, and underscores';
      }

      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Please enter a valid email address';
      }

      if (!formData.password) {
        newErrors.password = 'Password is required';
      } else if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters';
      } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
        newErrors.password = 'Password must contain at least one letter and one number';
      }

      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }

      if (!formData.firstName.trim()) {
        newErrors.firstName = 'First name is required';
      } else if (formData.firstName.length < 2) {
        newErrors.firstName = 'First name must be at least 2 characters';
      }

      if (!formData.lastName.trim()) {
        newErrors.lastName = 'Last name is required';
      } else if (formData.lastName.length < 2) {
        newErrors.lastName = 'Last name must be at least 2 characters';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const endpoint = `/api/auth/${isLogin ? 'login' : 'register'}`;
      const payload = isLogin 
        ? {
            username_or_email: formData.username,
            password: formData.password
          }
        : {
            username: formData.username,
            email: formData.email,
            password: formData.password,
            first_name: formData.firstName,
            last_name: formData.lastName
          };

      console.log(`🔄 Attempting ${isLogin ? 'login' : 'registration'}...`);

      const response = await fetch(API_BASE_URL + endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        console.log('✅ Authentication successful');
        onAuthSuccess(data.user, data.token);
      } else {
        console.error('❌ Authentication failed:', data.error);
        setErrors({ general: data.error || 'Authentication failed' });
      }
    } catch (error) {
      console.error('❌ Network error:', error);
      const errorMessage = 'Network error. Please check your connection and try again.';
      setErrors({ general: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: ''
    });
    setErrors({});
  };

  return (
    <div className="auth-overlay">
      <div className="auth-container">
        <div className="auth-header">
          <button className="auth-close" onClick={onClose}>×</button>
          <div className="auth-logo">
            <div className="auth-logo-icon">📚</div>
            <h1 className="auth-title">Course Scheduler</h1>
          </div>
          <p className="auth-subtitle">
            {isLogin ? 'Welcome back! Sign in to access your saved schedules.' : 'Create your account to save and manage your course schedules.'}
          </p>
        </div>

        <div className="auth-tabs">
          <button 
            className={`auth-tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Sign In
          </button>
          <button 
            className={`auth-tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {errors.general && (
            <div className="auth-error general-error">
              {errors.general}
            </div>
          )}

          {!isLogin && (
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">First Name</label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  className={errors.firstName ? 'error' : ''}
                  placeholder="Enter your first name"
                />
                {errors.firstName && <span className="auth-error">{errors.firstName}</span>}
              </div>
              <div className="form-group">
                <label htmlFor="lastName">Last Name</label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  className={errors.lastName ? 'error' : ''}
                  placeholder="Enter your last name"
                />
                {errors.lastName && <span className="auth-error">{errors.lastName}</span>}
              </div>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">
              {isLogin ? 'Username or Email' : 'Username'}
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              className={errors.username ? 'error' : ''}
              placeholder={isLogin ? 'Enter username or email' : 'Choose a username'}
            />
            {errors.username && <span className="auth-error">{errors.username}</span>}
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={errors.email ? 'error' : ''}
                placeholder="Enter your email address"
              />
              {errors.email && <span className="auth-error">{errors.email}</span>}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-container">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={errors.password ? 'error' : ''}
                placeholder="Enter your password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            {errors.password && <span className="auth-error">{errors.password}</span>}
            {!isLogin && (
              <div className="password-requirements">
                <small>Password must be at least 8 characters with letters and numbers</small>
              </div>
            )}
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type={showPassword ? 'text' : 'password'}
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={errors.confirmPassword ? 'error' : ''}
                placeholder="Confirm your password"
              />
              {errors.confirmPassword && <span className="auth-error">{errors.confirmPassword}</span>}
            </div>
          )}

          <button 
            type="submit" 
            className="auth-submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="loading-spinner"></div>
                {isLogin ? 'Signing In...' : 'Creating Account...'}
              </>
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button 
              type="button" 
              className="auth-link" 
              onClick={toggleMode}
            >
              {isLogin ? 'Sign up here' : 'Sign in here'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginRegister;