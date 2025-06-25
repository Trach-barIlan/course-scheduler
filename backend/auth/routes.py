from flask import Blueprint, request, jsonify, g
from .auth_manager import AuthManager
import re
from datetime import datetime, timedelta
import traceback
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def get_auth_manager():
    """Get AuthManager instance"""
    try:
        return AuthManager()
    except ValueError as e:
        print(f"Auth configuration error: {e}")
        return None

def token_required(f):
    """Decorator to require valid token authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header is required'}), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header must be Bearer token'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            auth_manager = get_auth_manager()
            
            if not auth_manager:
                return jsonify({'error': 'Authentication service unavailable'}), 500
            
            user = auth_manager.validate_session(token)
            
            if not user:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Store user in Flask's g object for use in the route
            g.user = user
            
        except Exception as e:
            print(f"Token validation error: {e}")
            return jsonify({'error': 'Token validation failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        data = request.get_json()
        print(f"Registration attempt: {data.get('username')} / {data.get('email')}")
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field) or not str(data[field]).strip():
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        username = str(data['username']).strip()
        email = str(data['email']).strip().lower()
        password = str(data['password'])
        first_name = str(data['first_name']).strip()
        last_name = str(data['last_name']).strip()
        
        # Validate username
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate names
        if len(first_name) < 2:
            return jsonify({'error': 'First name must be at least 2 characters long'}), 400
        if len(last_name) < 2:
            return jsonify({'error': 'Last name must be at least 2 characters long'}), 400
        
        # Create user
        user = auth_manager.create_user(username, email, password, first_name, last_name)
        
        if user:
            # Create session
            user_agent = request.headers.get('User-Agent')
            ip_address = request.remote_addr
            token = auth_manager.create_session(user['id'], user_agent, ip_address)
            
            if token:
                print(f"✅ User registered and logged in: {user['username']}")
                
                return jsonify({
                    'message': 'Registration successful',
                    'user': user,
                    'token': token
                }), 201
            else:
                return jsonify({'error': 'Registration successful but failed to create session'}), 500
        else:
            return jsonify({'error': 'Registration failed'}), 400
        
    except ValueError as e:
        error_str = str(e).lower()
        if "email" in error_str and "exists" in error_str:
            return jsonify({'error': 'An account with this email already exists'}), 400
        elif "username" in error_str and "exists" in error_str:
            return jsonify({'error': 'Username already taken'}), 400
        else:
            return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"❌ Registration error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        data = request.get_json()
        
        username_or_email = str(data.get('username_or_email', '')).strip()
        password = str(data.get('password', ''))
        
        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400
        
        print(f"Login attempt: {username_or_email}")
        
        user = auth_manager.authenticate_user(username_or_email, password)
        
        if user:
            # Create session
            user_agent = request.headers.get('User-Agent')
            ip_address = request.remote_addr
            token = auth_manager.create_session(user['id'], user_agent, ip_address)
            
            if token:
                print(f"✅ User logged in successfully: {user['username']}")
                
                return jsonify({
                    'message': 'Login successful',
                    'user': user,
                    'token': token
                }), 200
            else:
                return jsonify({'error': 'Login successful but failed to create session'}), 500
        else:
            print(f"❌ Login failed for: {username_or_email}")
            return jsonify({'error': 'Invalid username/email or password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        auth_manager = get_auth_manager()
        
        if auth_manager:
            auth_manager.delete_session(token)
        
        print(f"✅ User {g.user.get('username')} logged out successfully")
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        print(f"❌ Logout error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    try:
        print(f"✅ User found: {g.user.get('username', 'Unknown')}")
        return jsonify({'user': g.user}), 200
            
    except Exception as e:
        print(f"❌ Unexpected error in get_current_user: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Authentication check failed',
            'details': str(e),
            'authenticated': False
        }), 500

@auth_bp.route('/refresh-session', methods=['POST'])
@token_required
def refresh_session():
    """Refresh session to extend expiry and verify authentication"""
    try:
        print(f"✅ Session refreshed successfully for user: {g.user.get('username')}")
        
        return jsonify({
            'message': 'Session refreshed',
            'user': g.user,
            'authenticated': True
        }), 200
            
    except Exception as e:
        print(f"❌ Unexpected error in refresh_session: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Session refresh failed',
            'details': str(e),
            'authenticated': False
        }), 500

@auth_bp.route('/debug', methods=['GET'])
@token_required
def debug_session():
    """Debug endpoint to check session state"""
    try:
        auth_header = request.headers.get('Authorization')
        
        return jsonify({
            'has_auth_header': bool(auth_header),
            'auth_header_format': auth_header.startswith('Bearer ') if auth_header else False,
            'user': g.user,
            'authenticated': True,
            'request_headers': dict(request.headers),
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr
        }), 200
        
    except Exception as e:
        print(f"❌ Unexpected error in debug_session: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Debug failed',
            'details': str(e),
            'has_auth_header': False,
            'authenticated': False
        }), 500

@auth_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get basic stats for the app"""
    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500
    
    try:
        result = auth_manager.service_supabase.table("user_profiles").select("id", count="exact").execute()
        user_count = result.count if result.count else 0
        
        return jsonify({
            'total_users': user_count,
            'app_name': 'Course Scheduler'
        }), 200
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500