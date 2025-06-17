from flask import Blueprint, request, jsonify, session
from auth.supabase_client import SupabaseClient
import json
from datetime import datetime

schedules_bp = Blueprint('schedules', __name__)

def get_supabase_client():
    """Get Supabase client instance"""
    try:
        return SupabaseClient()
    except ValueError as e:
        print(f"Supabase configuration error: {e}")
        return None

@schedules_bp.route('/save', methods=['POST'])
def save_schedule():
    """Save a schedule to the database"""
    print(f"=== SAVE SCHEDULE REQUEST ===")
    print(f"Session data: {dict(session)}")
    print(f"Session ID: {session.get('_id', 'No session ID')}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"Request cookies: {request.cookies}")
    
    # Enhanced authentication check
    user_id = session.get('user_id')
    authenticated = session.get('authenticated', False)
    
    print(f"User ID from session: {user_id}")
    print(f"Authenticated flag: {authenticated}")
    
    if not user_id or not authenticated:
        print("❌ No user_id or not authenticated - checking if session needs refresh")
        
        # Try to refresh/verify the session
        supabase = get_supabase_client()
        if supabase:
            try:
                # Check if we can get current user from Supabase
                current_user = supabase.get_current_user()
                if current_user:
                    print(f"✅ Found current user in Supabase: {current_user['id']}")
                    # Update session with current user data
                    session.permanent = True
                    session['user_id'] = current_user['id']
                    session['username'] = current_user.get('username', '')
                    session['email'] = current_user.get('email', '')
                    session['first_name'] = current_user.get('first_name', '')
                    session['last_name'] = current_user.get('last_name', '')
                    session['authenticated'] = True
                    user_id = current_user['id']
                    print(f"✅ Session refreshed with user ID: {user_id}")
                else:
                    print("❌ No current user found in Supabase")
                    return jsonify({'error': 'Authentication required. Please sign in again.'}), 401
            except Exception as e:
                print(f"❌ Error checking current user: {e}")
                return jsonify({'error': 'Authentication required. Please sign in again.'}), 401
        else:
            print("❌ Failed to get Supabase client")
            return jsonify({'error': 'Authentication required. Please sign in again.'}), 401

    supabase = get_supabase_client()
    if not supabase:
        print("❌ Failed to get Supabase client")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        print(f"Request data: {data}")
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Schedule name is required'}), 400
        if not data.get('schedule'):
            return jsonify({'error': 'Schedule data is required'}), 400

        # Prepare schedule data
        schedule_data = {
            'user_id': user_id,
            'schedule_name': data['name'].strip(),
            'schedule_data': data['schedule'],
            'constraints_data': data.get('constraints', [])
        }
        
        # Add optional fields if they exist in the database schema
        if 'description' in data and data['description']:
            schedule_data['description'] = data['description']
        if 'isPublic' in data:
            schedule_data['is_public'] = data['isPublic']

        print(f"✅ Attempting to save schedule data: {schedule_data}")

        # Save to database using service role for reliable access
        result = supabase.service_supabase.table("saved_schedules").insert(schedule_data).execute()
        print(f"Database insert result: {result}")
        
        if result.data:
            saved_schedule = result.data[0]
            print(f"✅ Schedule saved successfully: {saved_schedule}")
            
            # Log the save activity
            try:
                log_data = {
                    'user_id': user_id,
                    'schedule_id': saved_schedule['id'],
                    'courses_count': len(data['schedule']) if isinstance(data['schedule'], list) else 0,
                    'constraints_count': len(data.get('constraints', [])),
                    'generation_time_ms': 0,  # This is a save operation, not generation
                    'schedule_type': 'saved',
                    'success': True,
                    'error_message': None
                }
                
                supabase.service_supabase.table("schedule_generation_logs").insert(log_data).execute()
                print(f"✅ Save activity logged")
            except Exception as log_error:
                print(f"⚠️ Failed to log save activity: {log_error}")
                # Don't fail the save if logging fails
            
            return jsonify({
                'message': 'Schedule saved successfully',
                'schedule': saved_schedule
            }), 201
        else:
            print("❌ No data returned from database insert")
            return jsonify({'error': 'Failed to save schedule'}), 500

    except Exception as e:
        print(f"❌ Error saving schedule: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to save schedule: {str(e)}'}), 500

@schedules_bp.route('/list', methods=['GET'])
def list_schedules():
    """Get user's saved schedules"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        result = supabase.supabase.table("saved_schedules")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()

        return jsonify({
            'schedules': result.data or []
        }), 200

    except Exception as e:
        print(f"Error fetching schedules: {e}")
        return jsonify({'error': 'Failed to fetch schedules'}), 500

@schedules_bp.route('/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    """Get a specific schedule"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        result = supabase.supabase.table("saved_schedules")\
            .select("*")\
            .eq("id", schedule_id)\
            .eq("user_id", user_id)\
            .execute()

        if result.data:
            return jsonify({
                'schedule': result.data[0]
            }), 200
        else:
            return jsonify({'error': 'Schedule not found'}), 404

    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return jsonify({'error': 'Failed to fetch schedule'}), 500

@schedules_bp.route('/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update a schedule"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        
        # Prepare update data
        update_data = {}
        if 'name' in data:
            update_data['schedule_name'] = data['name'].strip()
        if 'schedule' in data:
            update_data['schedule_data'] = data['schedule']
        if 'constraints' in data:
            update_data['constraints_data'] = data['constraints']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'isPublic' in data:
            update_data['is_public'] = data['isPublic']

        # Update in database
        result = supabase.supabase.table("saved_schedules")\
            .update(update_data)\
            .eq("id", schedule_id)\
            .eq("user_id", user_id)\
            .execute()

        if result.data:
            return jsonify({
                'message': 'Schedule updated successfully',
                'schedule': result.data[0]
            }), 200
        else:
            return jsonify({'error': 'Schedule not found or update failed'}), 404

    except Exception as e:
        print(f"Error updating schedule: {e}")
        return jsonify({'error': 'Failed to update schedule'}), 500

@schedules_bp.route('/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a schedule"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        result = supabase.supabase.table("saved_schedules")\
            .delete()\
            .eq("id", schedule_id)\
            .eq("user_id", user_id)\
            .execute()

        return jsonify({
            'message': 'Schedule deleted successfully'
        }), 200

    except Exception as e:
        print(f"Error deleting schedule: {e}")
        return jsonify({'error': 'Failed to delete schedule'}), 500

@schedules_bp.route('/debug', methods=['GET'])
def debug_session():
    """Debug endpoint to check session state"""
    return jsonify({
        'session_data': dict(session),
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'authenticated': session.get('authenticated', False),
        'has_session': bool(session),
        'session_id': session.get('_id', 'No session ID')
    }), 200