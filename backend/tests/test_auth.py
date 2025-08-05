import pytest
import json
from unittest.mock import Mock, patch
from auth.auth_manager import AuthManager
from auth.models import User

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_ANON_KEY': 'test-anon-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    }):
        yield

class TestAuthManager:
    """Test cases for the AuthManager class."""
    
    def test_create_user_success(self, mock_database):
        """Test successful user creation."""
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = [{
            "id": "test-user-id",
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }]
        
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
            mock_create_client.return_value = mock_supabase
            
            auth_manager = AuthManager()
            result = auth_manager.create_user("testuser", "test@example.com", "password123", "Test", "User")
            
            assert result["id"] == "test-user-id"
            assert result["username"] == "testuser"
            assert result["email"] == "test@example.com"
    
    def test_create_user_duplicate_email(self, mock_database):
        """Test user creation with duplicate email."""
        # Mock database error response
        mock_database.create_user.side_effect = ValueError("Email already exists")
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
            mock_supabase.table.return_value.insert.return_value.execute.side_effect = ValueError("Email already exists")
            mock_create_client.return_value = mock_supabase
            auth_manager = AuthManager()
            try:
                auth_manager.create_user("testuser", "test@example.com", "password123", "Test", "User")
            except Exception as e:
                assert "already exists" in str(e).lower()
    
    def test_login_success(self, mock_database):
        """Test successful user login."""
        # Mock database response
        mock_user = Mock(
            id="test-user-id",
            username="testuser",
            email="test@example.com"
        )
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            mock_create_client.return_value = mock_supabase
            auth_manager = AuthManager()
            # Patch authenticate_user to return mock_user
            auth_manager.authenticate_user = Mock(return_value={
                "id": "test-user-id",
                "username": "testuser",
                "email": "test@example.com"
            })
            result = auth_manager.login("test@example.com", "password123")
            assert result["success"] is True
            assert result["user"]["id"] == "test-user-id"

    def test_login_invalid_credentials(self, mock_database):
        """Test login with invalid credentials."""
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            mock_create_client.return_value = mock_supabase
            auth_manager = AuthManager()
            # Patch authenticate_user to return None
            auth_manager.authenticate_user = Mock(return_value=None)
            result = auth_manager.login("test@example.com", "wrongpassword")
            assert result["success"] is False
            assert "invalid" in result["error"].lower()

    def test_validate_token_success(self, mock_database):
        """Test successful token validation."""
        mock_user = Mock(
            id="test-user-id",
            username="testuser",
            email="test@example.com"
        )
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            mock_create_client.return_value = mock_supabase
            auth_manager = AuthManager()
            # Patch get_user_by_id to return mock_user
            auth_manager.get_user_by_id = Mock(return_value={
                "id": "test-user-id",
                "username": "testuser",
                "email": "test@example.com"
            })
            result = auth_manager.validate_token("valid-token")
            assert result["success"] is True
            assert result["user"]["id"] == "test-user-id"

    def test_validate_token_invalid(self, mock_database):
        """Test invalid token validation."""
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            mock_create_client.return_value = mock_supabase
            auth_manager = AuthManager()
            # Patch get_user_by_id to return None
            auth_manager.get_user_by_id = Mock(return_value=None)
            result = auth_manager.validate_token("invalid-token")
            assert result["success"] is False
            assert "invalid" in result["error"].lower()

class TestAuthRoutes:
    """Test cases for authentication API routes."""
    
    def test_register_success(self, client, mock_database):
        """Test successful user registration via API."""
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            # Mock existing user checks to return empty (no existing users)
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
            # Mock successful user creation
            mock_result = Mock()
            mock_result.data = [{
                "id": "test-user-id",
                "username": "testuser",
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            }]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
            mock_create_client.return_value = mock_supabase
            
            response = client.post('/api/auth/register', json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "first_name": "Test",
                "last_name": "User"
            })
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["message"] == "Registration successful"
            assert "token" in data
            assert data["user"]["username"] == "testuser"
            assert data["user"]["email"] == "test@example.com"
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            mock_create_client.return_value = mock_supabase
            
            response = client.post('/api/auth/register', json={
                "username": "testuser"
                # Missing email and password
            })
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            assert "required" in data["error"].lower() or "missing" in data["error"].lower()
    
    def test_login_success(self, client, mock_database):
        """Test successful user login via API."""
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            # Mock user lookup for authentication
            mock_user_result = Mock()
            mock_user_result.data = [{
                "id": "test-user-id",
                "username": "testuser",
                "email": "test@example.com",
                "password_hash": "mocked_hash"  # This should match whatever hash is expected
            }]
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_result
            # Mock password verification and user update
            mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
            # Mock session creation RPC call
            mock_session_result = Mock()
            mock_session_result.data = True
            mock_supabase.rpc.return_value.execute.return_value = mock_session_result
            mock_create_client.return_value = mock_supabase
            
            # Mock password verification and session token generation
            with patch.object(AuthManager, 'verify_password', return_value=True), \
                 patch.object(AuthManager, 'generate_session_token', return_value='mocked_token'):
                response = client.post('/api/auth/login', json={
                    "username_or_email": "test@example.com",
                    "password": "password123"
                })
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert "token" in data
                assert "user" in data
                assert data["user"]["username"] == "testuser"
    
    def test_me_endpoint_success(self, client, mock_database, mock_user_data):
        """Test successful user info retrieval."""
        # Mock successful token validation
        mock_user = Mock(**mock_user_data)
        mock_database.get_user_by_id.return_value = mock_user
        
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            # Mock the validate_session RPC call
            mock_validate_result = Mock()
            mock_validate_result.data = [{
                'is_valid': True,
                'user_id': 'test-user-id',
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }]
            mock_supabase.rpc.return_value.execute.return_value = mock_validate_result
            mock_create_client.return_value = mock_supabase
            
            response = client.get('/api/auth/me', headers={
                'Authorization': 'Bearer valid-token'
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "user" in data
            assert data["user"]["username"] == "testuser"
    
    def test_me_endpoint_no_token(self, client):
        """Test user info retrieval without token."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert "token" in data["error"].lower() or "authorization" in data["error"].lower()
    
    def test_logout_success(self, client, mock_database):
        """Test successful user logout."""
        # Mock successful logout
        mock_database.update_last_login.return_value = None
        
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            # Mock the validate_session RPC call for token validation
            mock_validate_result = Mock()
            mock_validate_result.data = [{
                'is_valid': True,
                'user_id': 'test-user-id',
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }]
            # Mock delete session call
            mock_delete_result = Mock()
            mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete_result
            mock_supabase.rpc.return_value.execute.return_value = mock_validate_result
            mock_create_client.return_value = mock_supabase
            
            response = client.post('/api/auth/logout', headers={
                'Authorization': 'Bearer valid-token'
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "message" in data or "success" in str(data).lower()