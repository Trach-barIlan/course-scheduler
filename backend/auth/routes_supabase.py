from flask import Blueprint, request, jsonify, session
from .supabase_client import SupabaseClient
import re

auth_bp = Blueprint('auth', __name__)

def get_supabase_client():
    """Get Supabase client instance"""
    try:
        return SupabaseClient()
    except ValueError as e:
        print(f"Supabase configuration error: {e}")
        return None

def validate_email(email):
    """Validate email format - more comprehensive validation"""
    # More strict email validation
    pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    
    # Additional checks
    if not re.match(pattern, email):
        return False
    
    # Check for common issues
    if email.count('@') != 1:
        return False
    
    local, domain = email.split('@')
    
    # Local part checks
    if len(local) == 0 or len(local) > 64:
        return False
    
    # Domain part checks
    if len(domain) == 0 or len(domain) > 255:
        return False
    
    # Domain must have at least one dot
    if '.' not in domain:
        return False
    
    # Domain parts shouldn't be empty
    domain_parts = domain.split('.')
    if any(len(part) == 0 for part in domain_parts):
        return False
    
    return True

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
    session.permanent = True
    session['user_id'] = user_data['id']
    session['username'] = user_data.get('username', '')
    session['email'] = user_data.get('email', '')
    session['first_name'] = user_data.get('first_name', '')
    session['last_name'] = user_data.get('last_name', '')
    session['authenticated'] = True
    
    print(f"✅ Session set successfully:")
    print(f"   User ID: {session.get('user_id')}")
    print(f"   Username: {session.get('username')}")
    print(f"   Email: {session.get('email')}")
    print(f"   Session ID: {session.get('_id', 'No session ID')}")
    print(f"   Full session: {dict(session)}")

@auth_bp.route('/register', methods=['POST'])
def register():
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        print(f"Registration attempt with data: {data}")
        
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
        
        print(f"Processed data - Username: {username}, Email: {email}")
        
        # Additional validations (username, email, password)
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
            
        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_message}), 400
        
        # Create user
        user_metadata = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        
        print(f"Attempting to create user with email: {email}")
        user = supabase.create_user(email, password, user_metadata)
        
        if user:
            # Set session data
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['authenticated'] = True
            
            print(f"✅ User registered successfully: {user['id']}")
            
            return jsonify({
                'message': 'Registration successful',
                'user': user
            }), 201
        else:
            print("❌ User creation failed - no user returned")
            return jsonify({'error': 'Registration failed. Email may already be in use or invalid.'}), 400
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        print(f"Error type: {type(e)}")
        
        # More specific error messages
        error_str = str(e).lower()
        if "email" in error_str and ("invalid" in error_str or "format" in error_str):
            return jsonify({'error': 'Please enter a valid email address'}), 400
        elif "already" in error_str or "exists" in error_str:
            return jsonify({'error': 'An account with this email already exists'}), 400
        elif "username" in error_str:
            return jsonify({'error': 'Username already taken'}), 400
        else:
            return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        
        username_or_email = str(data.get('username_or_email', '')).strip()
        password = str(data.get('password', ''))
        
        if not username_or_email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # For Supabase, we need to use email for authentication
        # If username is provided, we need to look up the email first
        email = username_or_email.lower()
        if not validate_email(username_or_email):
            # It's a username, look up the email
            try:
                profile = supabase.supabase.table("user_profiles").select("email").eq("username", username_or_email).execute()
                if profile.data:
                    email = profile.data[0]['email']
                else:
                    return jsonify({'error': 'Invalid username or password'}), 401
            except:
                return jsonify({'error': 'Invalid username or password'}), 401
        
        user = supabase.authenticate_user(email, password)
        
        if user:
            # Set session with comprehensive user data
            set_user_session(user)
            
            print(f"✅ session id set to: {session.get('user_id', 'No session ID')}")
            
            return jsonify({
                'message': 'Login successful',
                'user': user
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    print(f"🔓 Logout request - current session: {dict(session)}")
    
    supabase = get_supabase_client()
    if supabase:
        supabase.logout_user()
    
    session.clear()
    print("✅ Session cleared after logout")
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    print(f"🔍 Auth check - current session: {dict(session)}")
    print(f"Session ID: {session.get('user_id', 'No session ID')}")
    print(f"Session permanent: {session.permanent}")
    
    user_id = session.get('user_id')
    authenticated = session.get('authenticated', False)
    
    if not user_id or not authenticated:
        print(f"❌ Authentication failed - user_id: {user_id}, authenticated: {authenticated}")
        return jsonify({'error': 'Not authenticated'}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500
    
    user = supabase.get_user_by_id(user_id)
    if user:
        print(f"✅ User found: {user.get('username', 'Unknown')}")
        return jsonify({'user': user}), 200
    else:
        print("❌ User not found in database, clearing session")
        session.clear()
        return jsonify({'error': 'User not found'}), 404

@auth_bp.route('/refresh-session', methods=['POST'])
def refresh_session():
    """Refresh session to extend expiry and verify authentication"""
    print(f"🔄 Session refresh request - current session: {dict(session)}")
    
    user_id = session.get('user_id')
    authenticated = session.get('authenticated', False)
    
    if not user_id or not authenticated:
        print(f"❌ Session refresh failed - user_id: {user_id}, authenticated: {authenticated}")
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Verify user still exists in database
    supabase = get_supabase_client()
    if supabase:
        user = supabase.get_user_by_id(user_id)
        if not user:
            print("❌ User no longer exists, clearing session")
            session.clear()
            return jsonify({'error': 'User not found'}), 401
    
    # Refresh session by making it permanent again and updating data
    session.permanent = True
    session['last_refresh'] = str(datetime.now())
    
    print(f"✅ Session refreshed successfully for user: {user_id}")
    
    return jsonify({
        'message': 'Session refreshed',
        'user_id': user_id,
        'authenticated': True
    }), 200

@auth_bp.route('/debug', methods=['GET'])
def debug_session():
    """Debug endpoint to check session state"""
    return jsonify({
        'session_data': dict(session),
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'authenticated': session.get('authenticated', False),
        'has_session': bool(session),
        'session_id': session.get('_id', 'No session ID'),
        'session_permanent': session.permanent
    }), 200

@auth_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get basic stats for the app"""
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Get user count from Supabase
        result = supabase.supabase.table("user_profiles").select("id", count="exact").execute()
        user_count = result.count if result.count else 0
        
        return jsonify({
            'total_users': user_count,
            'app_name': 'Course Scheduler'
        }), 200
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500