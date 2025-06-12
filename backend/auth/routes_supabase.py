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
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        
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
        user_metadata = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        
        user = supabase.create_user(email, password, user_metadata)
        
        if user:
            # Set session
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            return jsonify({
                'message': 'User registered successfully',
                'user': user
            }), 201
        else:
            return jsonify({'error': 'Registration failed. Email may already be in use.'}), 400
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # For Supabase, we need to use email for authentication
        # If username is provided, we need to look up the email first
        email = username_or_email
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
            # Set session
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            return jsonify({
                'message': 'Login successful',
                'user': user
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    supabase = get_supabase_client()
    if supabase:
        supabase.logout_user()
    
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500
    
    user = supabase.get_user_by_id(user_id)
    if user:
        return jsonify({'user': user}), 200
    else:
        session.clear()
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