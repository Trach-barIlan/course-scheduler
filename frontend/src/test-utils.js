import React from 'react';
import { render } from '@testing-library/react';

// Mock react-router-dom for testing
const MockBrowserRouter = ({ children }) => (
  <div data-testid="mock-router">{children}</div>
);

// Use mock router for now to avoid module resolution issues
const BrowserRouter = MockBrowserRouter;

// Custom render function that includes providers
const AllTheProviders = ({ children }) => {
  return (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  );
};

const customRender = (ui, options) =>
  render(ui, { wrapper: AllTheProviders, ...options });

// Mock data for testing
export const mockUser = {
  id: 'test-user-id',
  username: 'testuser',
  email: 'test@example.com',
  created_at: '2024-01-01T00:00:00Z'
};

export const mockAuthToken = 'mock-auth-token-12345';

export const mockCourses = [
  {
    name: 'CS101',
    hasLecture: true,
    hasPractice: true,
    lectures: [
      { day: 'Mon', startTime: '9', endTime: '11' },
      { day: 'Wed', startTime: '9', endTime: '11' }
    ],
    practices: [
      { day: 'Tue', startTime: '14', endTime: '16' }
    ]
  },
  {
    name: 'Math101',
    hasLecture: true,
    hasPractice: false,
    lectures: [
      { day: 'Tue', startTime: '10', endTime: '12' },
      { day: 'Thu', startTime: '10', endTime: '12' }
    ],
    practices: []
  }
];

export const mockSchedule = [
  {
    name: 'CS101',
    lecture: 'Mon 9-11',
    ta: 'Tue 14-16'
  },
  {
    name: 'Math101',
    lecture: 'Tue 10-12',
    ta: null
  }
];

export const mockStatistics = {
  schedules_created: 5,
  schedules_this_week: 2,
  saved_schedules_count: 3,
  hours_saved: 12,
  success_rate: 98,
  efficiency: 85,
  total_courses_scheduled: 15,
  preferred_schedule_type: 'crammed',
  constraints_used_count: 8,
  average_generation_time: 3.2
};

// Mock fetch responses
export const mockFetchResponse = (data, status = 200) => {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data))
  });
};

export const mockFetchError = (error, status = 500) => {
  return Promise.resolve({
    ok: false,
    status,
    json: () => Promise.resolve({ error }),
    text: () => Promise.resolve(JSON.stringify({ error }))
  });
};

// Custom matchers
export const expectElementToBeInDocument = (element) => {
  expect(element).toBeInTheDocument();
};

export const expectElementToHaveText = (element, text) => {
  expect(element).toHaveTextContent(text);
};

export const expectElementToHaveClass = (element, className) => {
  expect(element).toHaveClass(className);
};

export const expectElementToBeDisabled = (element) => {
  expect(element).toBeDisabled();
};

export const expectElementToBeEnabled = (element) => {
  expect(element).not.toBeDisabled();
};

// Wait for async operations
export const waitForElementToBeRemoved = async (element) => {
  await new Promise(resolve => setTimeout(resolve, 0));
  expect(element).not.toBeInTheDocument();
};

// Mock console methods
export const mockConsole = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn()
};

// Setup console mocks
export const setupConsoleMocks = () => {
  jest.spyOn(console, 'log').mockImplementation(mockConsole.log);
  jest.spyOn(console, 'error').mockImplementation(mockConsole.error);
  jest.spyOn(console, 'warn').mockImplementation(mockConsole.warn);
  jest.spyOn(console, 'info').mockImplementation(mockConsole.info);
};

// Cleanup console mocks
export const cleanupConsoleMocks = () => {
  jest.restoreAllMocks();
};

// Export everything
export * from '@testing-library/react';
export { customRender as render };

// Export empty object to prevent Jest from treating this as a test suite
export default {}; 