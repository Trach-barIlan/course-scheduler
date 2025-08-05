import pytest
import os
import sys
from unittest.mock import Mock, patch
import tempfile

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app
from auth.database import UserDatabase

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the Flask app."""
    return app.test_cli_runner()

@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('auth.database.UserDatabase') as mock:
        mock_db = Mock()
        mock.return_value = mock_db
        yield mock_db

@pytest.fixture
def mock_auth_token():
    """Mock authentication token for testing."""
    return "mock-auth-token-12345"

@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "id": "test-user-id",
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_courses():
    """Sample course data for testing."""
    return [
        {
            "name": "CS101",
            "hasLecture": True,
            "hasPractice": True,
            "lectures": [
                {"day": "Mon", "startTime": "9", "endTime": "11"},
                {"day": "Wed", "startTime": "9", "endTime": "11"}
            ],
            "practices": [
                {"day": "Tue", "startTime": "14", "endTime": "16"}
            ]
        },
        {
            "name": "Math101",
            "hasLecture": True,
            "hasPractice": False,
            "lectures": [
                {"day": "Tue", "startTime": "10", "endTime": "12"},
                {"day": "Thu", "startTime": "10", "endTime": "12"}
            ],
            "practices": []
        }
    ]

@pytest.fixture
def sample_constraints():
    """Sample constraints for testing."""
    return "No classes before 9am and no Friday classes"

@pytest.fixture
def sample_schedule():
    """Sample generated schedule for testing."""
    return [
        {
            "name": "CS101",
            "lecture": "Mon 9-11",
            "ta": "Tue 14-16"
        },
        {
            "name": "Math101",
            "lecture": "Tue 10-12",
            "ta": None
        }
    ] 