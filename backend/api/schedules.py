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
    print(f"Save schedule request received")
    print(f"Session data: {dict(session)}")
    
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")
    
    if not user_id:
        print("No user_id in session - authentication required")
        return jsonify({'error': 'Authentication required. Please sign in again.'}), 401

    supabase = get_supabase_client()
    if not supabase:
        print("Failed to get Supabase client")
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
        if 'description' in data:
            schedule_data['description'] = data['description']
        if 'isPublic' in data:
            schedule_data['is_public'] = data['isPublic']

        print(f"Attempting to save schedule data: {schedule_data}")

        # Save to database
        result = supabase.supabase.table("saved_schedules").insert(schedule_data).execute()
        print(f"Database insert result: {result}")
        
        if result.data:
            saved_schedule = result.data[0]
            print(f"Schedule saved successfully: {saved_schedule}")
            return jsonify({
                'message': 'Schedule saved successfully',
                'schedule': saved_schedule
            }), 201
        else:
            print("No data returned from database insert")
            return jsonify({'error': 'Failed to save schedule'}), 500

    except Exception as e:
        print(f"Error saving schedule: {e}")
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
        'has_session': bool(session)
    }), 200