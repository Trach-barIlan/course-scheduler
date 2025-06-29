from flask import Blueprint, request, jsonify, g
from auth.routes import token_required
from auth.auth_manager import AuthManager
import json
from datetime import datetime

schedules_bp = Blueprint('schedules', __name__)

def get_auth_manager():
    """Get AuthManager instance"""
    try:
        return AuthManager()
    except ValueError as e:
        print(f"Auth configuration error: {e}")
        return None

@schedules_bp.route('/save', methods=['POST'])
@token_required
def save_schedule():
    """Save a schedule to the database"""
    print(f"=== SAVE SCHEDULE REQUEST ===")
    print(f"User from g.user: {g.user}")
    
    user_id = g.user['id']
    
    print(f"User ID from g.user: {user_id}")

    auth_manager = get_auth_manager()
    if not auth_manager:
        print("❌ Failed to get AuthManager")
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data.get('name'):
            return jsonify({'error': 'Schedule name is required'}), 400
        if not data.get('schedule'):
            return jsonify({'error': 'Schedule data is required'}), 400

        # Get client with user context
        client = auth_manager.get_client_for_user(user_id)

        schedule_data = {
            'user_id': user_id,
            'schedule_name': data['name'].strip(),
            'schedule_data': data['schedule'],
            'constraints_data': data.get('constraints', [])
        }

        print(f"✅ Attempting to save schedule data: {schedule_data}")

        result = client.table("saved_schedules").insert(schedule_data).execute()
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
                    'generation_time_ms': 0,
                    'schedule_type': 'saved',
                    'success': True,
                    'error_message': None
                }
                
                client.table("schedule_generation_logs").insert(log_data).execute()
                print(f"✅ Save activity logged")
            except Exception as log_error:
                print(f"⚠️ Failed to log save activity: {log_error}")
            
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
@token_required
def list_schedules():
    """Get user's saved schedules"""
    user_id = g.user['id']

    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        client = auth_manager.get_client_for_user(user_id)
        
        result = client.table("saved_schedules")\
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
@token_required
def get_schedule(schedule_id):
    """Get a specific saved schedule"""
    user_id = g.user['id']
    
    print(f"🔍 Fetching schedule {schedule_id} for user {user_id}")
    
    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500
    
    try:
        client = auth_manager.get_client_for_user(user_id)
        
        result = client.table("saved_schedules")\
            .select("*")\
            .eq("id", schedule_id)\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        print(f"📊 Database result: {result}")
        
        if not result.data:
            print(f"❌ Schedule {schedule_id} not found for user {user_id}")
            return jsonify({'error': 'Schedule not found'}), 404
        
        schedule_data = result.data
        print(f"✅ Found schedule: {schedule_data['schedule_name']}")
        
        return jsonify({
            'schedule': {
                'id': schedule_data['id'],
                'schedule_name': schedule_data['schedule_name'],
                'created_at': schedule_data['created_at'],
                'schedule_data': schedule_data['schedule_data']
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching schedule: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch schedule'}), 500

@schedules_bp.route('/<schedule_id>', methods=['DELETE'])
@token_required
def delete_schedule(schedule_id):
    """Delete a schedule"""
    user_id = g.user['id']

    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        client = auth_manager.get_client_for_user(user_id)
        
        result = client.table("saved_schedules")\
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