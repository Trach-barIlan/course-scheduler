from flask import Blueprint, request, jsonify, session
from .auth_manager import AuthManager
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def get_auth_manager():
    """Get AuthManager instance"""
    try:
        return AuthManager()
    except ValueError as e:
        print(f"Auth configuration error: {e}")
        return None

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

def set_user_session(user_data):
    """Set user session with all required data"""
    print(f"🔧 Setting session for user: {user_data.get('username')}")
    
    session.permanent = True
    session['user_id'] = str(user_data['id'])
    session['username'] = user_data.get('username', '')
    session['email'] = user_data.get('email', '')
    session['first_name'] = user_data.get('first_name', '')
    session['last_name'] = user_data.get('last_name', '')
    session['authenticated'] = True
    session['login_time'] = datetime.now().isoformat()
    session.modified = True
    # Log the session cookie value if available
    cookie_name = session._get_cookie_name() if hasattr(session, '_get_cookie_name') else 'session'
    cookie_value = request.cookies.get(cookie_name)
    print(f"   Session cookie ({cookie_name}): {cookie_value}")
    print(f"✅ Session set for user: {user_data.get('username')}")
    print(f"   Session ID: {session.get('user_id')}")

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
            set_user_session(user)
            print(f"✅ User registered and logged in: {user['username']}")
            
            return jsonify({
                'message': 'Registration successful',
                'user': user
            }), 201
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
            set_user_session(user)
            print(f"✅ User logged in successfully: {user['username']}")
            
            return jsonify({
                'message': 'Login successful',
                'user': user
            }), 200
        else:
            print(f"❌ Login failed for: {username_or_email}")
            return jsonify({'error': 'Invalid username/email or password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    print(f"🔓 Logout request - current session: {dict(session)}")
    session.clear()
    session.modified = True
    print("✅ Session cleared after logout")
    
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    print(f"🔍 Auth check - current session: {dict(session)}")
    
    user_id = session.get('user_id')
    authenticated = session.get('authenticated', False)
    
    print(f"   user_id: {user_id} (type: {type(user_id)})")
    print(f"   authenticated: {authenticated} (type: {type(authenticated)})")
    
    if not user_id or not authenticated:
        print(f"❌ Authentication failed - user_id: {user_id}, authenticated: {authenticated}")
        return jsonify({'error': 'Not authenticated'}), 401
    
    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500
    
    user = auth_manager.get_user_by_id(user_id)
    if user:
        print(f"✅ User found: {user.get('username', 'Unknown')}")
        return jsonify({'user': user}), 200
    else:
        print("❌ User not found in database, clearing session")
        session.clear()
        session.modified = True
        return jsonify({'error': 'User not found'}), 404

@auth_bp.route('/refresh-session', methods=['POST'])
def refresh_session():
    """Refresh session to extend expiry and verify authentication"""
    print(f"🔄 Session refresh request - current session: {dict(session)}")
    
    user_id = session.get('user_id')
    
    if not user_id:
        print(f"❌ Session refresh failed - no user_id")
        return jsonify({'error': 'Not authenticated'}), 401
    
    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500
    
    user = auth_manager.get_user_by_id(user_id)
    if user:
        # Just update the login time, don't reset the entire session
        session['login_time'] = datetime.now().isoformat()
        session.modified = True
        
        print(f"✅ Session refreshed successfully for user: {user.get('username')}")
        
        return jsonify({
            'message': 'Session refreshed',
            'user': user,
            'authenticated': True
        }), 200
    else:
        print("❌ User no longer exists, clearing session")
        session.clear()
        session.modified = True
        return jsonify({'error': 'User not found'}), 401

@auth_bp.route('/debug', methods=['GET'])
def debug_session():
    """Debug endpoint to check session state"""
    session_data = dict(session)
    print(f"🔍 Debug session data: {session_data}")
    
    return jsonify({
        'session_data': session_data,
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'authenticated': session.get('authenticated', False),
        'has_session': bool(session),
        'session_permanent': session.permanent,
        'login_time': session.get('login_time'),
        'session_keys': list(session.keys()),
        'request_cookies': dict(request.cookies),
        'session_modified': getattr(session, 'modified', 'unknown')
    }), 200

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