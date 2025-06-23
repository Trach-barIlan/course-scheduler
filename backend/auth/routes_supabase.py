from flask import Blueprint, request, jsonify, session
from .supabase_client import SupabaseClient
import re
from datetime import datetime

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
        
        # Validate username
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400
        
        # Validate email with enhanced validation
        if not validate_email(email):
            print(f"Email validation failed for: {email}")
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate names
        if len(first_name) < 1:
            return jsonify({'error': 'First name is required'}), 400
        if len(last_name) < 1:
            return jsonify({'error': 'Last name is required'}), 400
        
        # Create user
        user_metadata = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        
        print(f"Attempting to create user with email: {email}")
        user = supabase.create_user(email, password, user_metadata)
        
        if user:
            # Set session with explicit session management
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['login_time'] = datetime.utcnow().isoformat()
            session.modified = True  # Force session save
            
            print(f"User created successfully: {user['id']}")
            print(f"Session set: user_id={session.get('user_id')}, username={session.get('username')}")
            
            response = jsonify({
                'message': 'User registered successfully',
                'user': user
            })
            response.status_code = 201
            
            # Ensure session cookie is set properly
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        else:
            print("User creation failed - no user returned")
            return jsonify({'error': 'Registration failed. Email may already be in use or invalid.'}), 400
        
    except Exception as e:
        print(f"Registration error: {e}")
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
        print(f"Login attempt with data: {data}")
        
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
        
        print(f"Attempting login with email: {email}")
        user = supabase.authenticate_user(email, password)
        
        if user:
            # Clear any existing session data first
            session.clear()
            
            # Set session with explicit session management
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['login_time'] = datetime.utcnow().isoformat()
            session.modified = True  # Force session save
            
            print(f"Login successful for user: {user['id']}")
            print(f"Session set: user_id={session.get('user_id')}, username={session.get('username')}")
            print(f"Session permanent: {session.permanent}")
            print(f"Session modified: {session.modified}")
            
            response = jsonify({
                'message': 'Login successful',
                'user': user
            })
            response.status_code = 200
            
            # Ensure session cookie is set properly
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    print(f"Logout request - current session: user_id={session.get('user_id')}")
    
    supabase = get_supabase_client()
    if supabase:
        supabase.logout_user()
    
    session.clear()
    session.modified = True  # Force session save
    
    print("Session cleared")
    
    response = jsonify({'message': 'Logged out successfully'})
    response.status_code = 200
    
    # Clear any cached responses
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    print(f"Auth check - session user_id: {user_id}")
    print(f"Full session: {dict(session)}")
    print(f"Session permanent: {session.permanent}")
    print(f"Session new: {session.new}")
    
    if not user_id:
        print("No user_id in session")
        return jsonify({'error': 'Not authenticated'}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500
    
    user = supabase.get_user_by_id(user_id)
    if user:
        print(f"User found: {user}")
        response = jsonify({'user': user})
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        print("User not found in database")
        session.clear()
        session.modified = True
        return jsonify({'error': 'User not found'}), 404

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