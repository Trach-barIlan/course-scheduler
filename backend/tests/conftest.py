import pytest
import os
import sys
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as fastapi_app

@pytest.fixture
def app():
    """App fixture for FastAPI."""
    yield fastapi_app

@pytest.fixture
def client():
    """Test client for FastAPI."""
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture
def mock_auth_token():
    return "mock-auth-token-12345"

@pytest.fixture
def mock_user_data():
    return {
        "id": "test-user-id",
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_courses():
    return [
        {
            "id": "cs101",
            "name": "CS101",
            "lectures": ["Mon 9-11", "Wed 9-11"],
            "ta_times": ["Tue 14-16"]
        }
    ]

@pytest.fixture
def sample_constraints():
    return [{"type": "no_classes_before", "time": 9}]
