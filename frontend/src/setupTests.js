// Setup jest-dom matchers (v5 syntax)
import '@testing-library/jest-dom/extend-expect';

// Mock environment variables
process.env.REACT_APP_API_BASE_URL = 'http://localhost:5001';

// Mock localStorage  
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock fetch globally
global.fetch = jest.fn();

// Console suppression for test output cleanliness
const originalConsole = {
  log: console.log,
  warn: console.warn,
  error: console.error
};

console.log = (...args) => {
  const message = String(args[0] || '');
  // Suppress test-related log messages
  if (message.includes('📋 Step') || 
      message.includes('Save response status') ||
      message.includes('🔍 Checking authentication') ||
      message.includes('❌ No auth token') ||
      message.includes('✅ Auth token') ||
      message.includes('📊 Loading') ||
      message.includes('💾 Saving')) {
    return;
  }
  originalConsole.log.apply(console, args);
};

console.warn = (...args) => {
  const message = String(args[0] || '');
  if (message.includes('outdated JSX transform') ||
      message.includes('React Router Future Flag Warning')) {
    return;
  }
  originalConsole.warn.apply(console, args);
};

console.error = (...args) => {
  const message = String(args[0] || '');
  if (message.includes('❌ Error saving') ||
      message.includes('Network error') ||
      message.includes('not wrapped in act')) {
    return;
  }
  originalConsole.error.apply(console, args);
};