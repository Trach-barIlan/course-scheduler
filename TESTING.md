# 🧪 Testing Guide for Schedgic

This document provides comprehensive information about the testing setup for the Schedgic course scheduling application.

## 📋 Table of Contents

- [Overview](#overview)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Best Practices](#best-practices)

## 🎯 Overview

Schedgic uses a comprehensive testing strategy with:
- **Backend**: pytest with Flask testing utilities
- **Frontend**: Jest with React Testing Library
- **Coverage**: Minimum 80% coverage requirement
- **CI/CD**: Automated testing in deployment pipeline

## 🔧 Backend Testing

### Test Structure
```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures and configuration
│   ├── test_auth.py         # Authentication tests
│   ├── test_schedule.py     # Scheduling logic tests
│   └── test_ai_model.py     # AI model tests
├── pytest.ini              # Pytest configuration
└── run_tests.py            # Test runner script
```

### Test Categories

#### 1. Authentication Tests (`test_auth.py`)
- User registration and login
- Token validation
- Session management
- API endpoint testing

#### 2. Schedule Logic Tests (`test_schedule.py`)
- Course parsing and validation
- Schedule generation algorithms
- Constraint processing
- Conflict detection

#### 3. AI Model Tests (`test_ai_model.py`)
- Natural language constraint parsing
- NER model functionality
- Pattern matching
- Integration testing

### Running Backend Tests

```bash
# Run all tests
cd backend
python run_tests.py

# Run specific test file
python run_tests.py test_auth.py

# Run with pytest directly
pytest tests/ --verbose --cov=. --cov-report=html

# Run tests in watch mode
pytest tests/ --watch
```

## ⚛️ Frontend Testing

### Test Structure
```
frontend/src/
├── __tests__/
│   ├── setupTests.js        # Global test setup
│   ├── test-utils.js        # Test utilities and mocks
│   ├── SaveScheduleModal.test.js
│   └── Dashboard.test.js
└── components/
    └── [component files]
```

### Test Categories

#### 1. Component Tests
- Rendering and display
- User interactions
- State management
- Props validation

#### 2. Integration Tests
- API integration
- Data flow
- Error handling
- Loading states

#### 3. Accessibility Tests
- ARIA labels
- Keyboard navigation
- Screen reader compatibility

### Running Frontend Tests

```bash
# Run tests in watch mode
cd frontend
npm test

# Run tests with coverage
npm run test:coverage

# Run tests for CI/CD
npm run test:ci

# Run tests in debug mode
npm run test:debug
```

## 🚀 Running Tests

### Quick Start

```bash
# Backend tests
cd backend
python run_tests.py

# Frontend tests
cd frontend
npm run test:coverage
```

### Full Test Suite

```bash
# Run all tests with coverage
./scripts/run_all_tests.sh
```

### Individual Component Testing

```bash
# Test specific backend module
cd backend
pytest tests/test_auth.py -v

# Test specific frontend component
cd frontend
npm test -- --testNamePattern="SaveScheduleModal"
```

## 📊 Test Coverage

### Coverage Requirements
- **Minimum**: 80% overall coverage
- **Critical paths**: 90% coverage
- **New features**: 85% coverage

### Coverage Reports

#### Backend Coverage
```bash
cd backend
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

#### Frontend Coverage
```bash
cd frontend
npm run test:coverage
# Coverage report in terminal and coverage/lcov-report/
```

### Coverage Areas

#### Backend Coverage
- Authentication system: 95%
- Schedule generation: 90%
- AI model: 85%
- API endpoints: 90%

#### Frontend Coverage
- Components: 85%
- User interactions: 90%
- API integration: 85%
- Error handling: 90%

## ✍️ Writing Tests

### Backend Test Guidelines

#### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestComponentName:
    """Test cases for ComponentName."""
    
    def test_specific_functionality(self, mock_dependency):
        """Test description."""
        # Arrange
        expected = "expected result"
        
        # Act
        result = function_under_test()
        
        # Assert
        assert result == expected
```

#### Fixtures
```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "key": "value",
        "list": [1, 2, 3]
    }

@pytest.fixture
def mock_api():
    """Mock external API calls."""
    with patch('module.api_call') as mock:
        mock.return_value = {"success": True}
        yield mock
```

### Frontend Test Guidelines

#### Test Structure
```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '../__tests__/test-utils';
import ComponentName from '../components/ComponentName';

describe('ComponentName', () => {
  const defaultProps = {
    // Component props
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders correctly', () => {
      render(<ComponentName {...defaultProps} />);
      expect(screen.getByText('Expected text')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    test('handles user input', async () => {
      render(<ComponentName {...defaultProps} />);
      
      const input = screen.getByLabelText('Input label');
      fireEvent.change(input, { target: { value: 'test value' } });
      
      await waitFor(() => {
        expect(input.value).toBe('test value');
      });
    });
  });
});
```

#### Mocking
```javascript
// Mock API calls
global.fetch = jest.fn();

// Mock successful response
global.fetch.mockResolvedValue({
  ok: true,
  json: () => Promise.resolve({ data: 'test' })
});

// Mock error response
global.fetch.mockRejectedValue(new Error('Network error'));
```

## 🎯 Best Practices

### General Testing Principles

1. **AAA Pattern**: Arrange, Act, Assert
2. **Test Isolation**: Each test should be independent
3. **Descriptive Names**: Test names should describe the scenario
4. **Single Responsibility**: Each test should test one thing
5. **Fast Execution**: Tests should run quickly

### Backend Testing Best Practices

1. **Mock External Dependencies**: Use mocks for database, APIs, etc.
2. **Test Edge Cases**: Include error conditions and boundary values
3. **Use Fixtures**: Reuse common test data
4. **Test API Endpoints**: Verify request/response handling
5. **Validate Data**: Test data validation and sanitization

### Frontend Testing Best Practices

1. **Test User Behavior**: Focus on user interactions, not implementation
2. **Accessibility Testing**: Include ARIA and keyboard navigation tests
3. **Mock External APIs**: Don't make real API calls in tests
4. **Test Error States**: Verify error handling and user feedback
5. **Component Isolation**: Test components in isolation

### Test Data Management

```python
# Backend: Use factories for test data
from factory import Factory, Faker

class UserFactory(Factory):
    class Meta:
        model = User
    
    username = Faker('user_name')
    email = Faker('email')
```

```javascript
// Frontend: Use mock data utilities
export const mockUser = {
  id: 'test-user-id',
  username: 'testuser',
  email: 'test@example.com'
};
```

## 🔍 Debugging Tests

### Backend Debugging

```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test with debugger
pytest tests/test_auth.py::TestAuthManager::test_login_success -s

# Run with coverage and show missing lines
pytest --cov=. --cov-report=term-missing
```

### Frontend Debugging

```bash
# Run tests in debug mode
npm run test:debug

# Run specific test file
npm test -- --testPathPattern="SaveScheduleModal"

# Run with verbose output
npm test -- --verbose
```

## 🚨 Common Issues

### Backend Issues

1. **Import Errors**: Ensure proper path setup in `conftest.py`
2. **Mock Issues**: Verify mock setup and cleanup
3. **Database Issues**: Use test database or mocks
4. **Environment Variables**: Set test environment variables

### Frontend Issues

1. **Component Not Found**: Check import paths and component exports
2. **Mock Not Working**: Verify mock setup and timing
3. **Async Issues**: Use `waitFor` for async operations
4. **CSS Issues**: Mock CSS imports in tests

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python run_tests.py

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 16
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm run test:ci
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)

---

**Happy Testing! 🧪✨** 