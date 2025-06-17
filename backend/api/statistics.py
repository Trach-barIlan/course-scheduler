from flask import Blueprint, request, jsonify, session
from auth.supabase_client import SupabaseClient
import json
from datetime import datetime, timedelta

statistics_bp = Blueprint('statistics', __name__)

def get_supabase_client():
    """Get Supabase client instance"""
    try:
        return SupabaseClient()
    except ValueError as e:
        print(f"Supabase configuration error: {e}")
        return None

@statistics_bp.route('/user', methods=['GET'])
def get_user_statistics():
    """Get user's statistics for dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        # Get user statistics
        stats_result = supabase.supabase.table("user_statistics")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

        # Get saved schedules count
        schedules_result = supabase.supabase.table("saved_schedules")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()

        # Get recent generation logs for success rate calculation
        logs_result = supabase.supabase.table("schedule_generation_logs")\
            .select("success")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()

        # Calculate statistics
        if stats_result.data:
            user_stats = stats_result.data[0]
        else:
            # Create default statistics if none exist
            user_stats = {
                'schedules_created_total': 0,
                'schedules_created_this_week': 0,
                'total_courses_scheduled': 0,
                'average_schedule_generation_time': 0,
                'preferred_schedule_type': 'crammed',
                'constraints_used_count': 0
            }

        # Calculate success rate
        success_rate = 98  # Default
        if logs_result.data:
            successful_generations = sum(1 for log in logs_result.data if log['success'])
            total_generations = len(logs_result.data)
            if total_generations > 0:
                success_rate = round((successful_generations / total_generations) * 100)

        # Calculate efficiency (based on average generation time)
        efficiency = 85  # Default
        if user_stats['average_schedule_generation_time'] > 0:
            # Lower generation time = higher efficiency
            # Assume 1000ms is baseline (85%), scale from there
            baseline_time = 1000
            avg_time = user_stats['average_schedule_generation_time']
            if avg_time <= baseline_time:
                efficiency = min(95, 85 + (baseline_time - avg_time) / baseline_time * 10)
            else:
                efficiency = max(60, 85 - (avg_time - baseline_time) / baseline_time * 25)
            efficiency = round(efficiency)

        # Calculate hours saved (estimate: 30 minutes saved per schedule)
        hours_saved = user_stats['schedules_created_total'] * 0.5

        return jsonify({
            'statistics': {
                'schedules_created': user_stats['schedules_created_total'],
                'schedules_this_week': user_stats['schedules_created_this_week'],
                'saved_schedules_count': schedules_result.count or 0,
                'hours_saved': round(hours_saved, 1),
                'success_rate': success_rate,
                'efficiency': efficiency,
                'total_courses_scheduled': user_stats['total_courses_scheduled'],
                'preferred_schedule_type': user_stats['preferred_schedule_type'],
                'constraints_used_count': user_stats['constraints_used_count'],
                'average_generation_time': round(user_stats['average_schedule_generation_time'])
            }
        }), 200

    except Exception as e:
        print(f"Error fetching user statistics: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@statistics_bp.route('/log-generation', methods=['POST'])
def log_schedule_generation():
    """Log a schedule generation attempt"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.get_json()
        
        # Validate required fields
        courses_count = data.get('courses_count', 0)
        constraints_count = data.get('constraints_count', 0)
        generation_time_ms = data.get('generation_time_ms', 0)
        schedule_type = data.get('schedule_type', 'crammed')
        success = data.get('success', True)
        error_message = data.get('error_message')
        schedule_id = data.get('schedule_id')  # Optional, for saved schedules

        # Log the generation attempt
        log_data = {
            'user_id': user_id,
            'courses_count': courses_count,
            'constraints_count': constraints_count,
            'generation_time_ms': generation_time_ms,
            'schedule_type': schedule_type,
            'success': success,
            'error_message': error_message,
            'schedule_id': schedule_id
        }

        log_result = supabase.supabase.table("schedule_generation_logs")\
            .insert(log_data)\
            .execute()

        # Update user statistics using the database function
        if success:
            supabase.supabase.rpc('update_user_statistics', {
                'p_user_id': user_id,
                'p_courses_count': courses_count,
                'p_constraints_count': constraints_count,
                'p_generation_time_ms': generation_time_ms,
                'p_schedule_type': schedule_type,
                'p_success': success
            }).execute()

        return jsonify({
            'message': 'Generation logged successfully',
            'log_id': log_result.data[0]['id'] if log_result.data else None
        }), 201

    except Exception as e:
        print(f"Error logging schedule generation: {e}")
        return jsonify({'error': 'Failed to log generation'}), 500

@statistics_bp.route('/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get user's recent activity for dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        # Get recent schedule generations
        logs_result = supabase.supabase.table("schedule_generation_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        # Get recent saved schedules
        schedules_result = supabase.supabase.table("saved_schedules")\
            .select("schedule_name, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()

        # Format activity data
        activities = []

        # Add schedule generations
        for log in logs_result.data or []:
            created_at = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
            time_ago = format_time_ago(created_at)
            
            if log['success']:
                action = f"Generated schedule with {log['courses_count']} courses"
            else:
                action = f"Failed to generate schedule ({log['error_message'] or 'Unknown error'})"
            
            activities.append({
                'action': action,
                'time': time_ago,
                'type': 'generation',
                'success': log['success']
            })

        # Add saved schedules
        for schedule in schedules_result.data or []:
            created_at = datetime.fromisoformat(schedule['created_at'].replace('Z', '+00:00'))
            time_ago = format_time_ago(created_at)
            
            activities.append({
                'action': f"Saved '{schedule['schedule_name']}'",
                'time': time_ago,
                'type': 'save',
                'success': True
            })

        # Sort by time and limit to 10 most recent
        activities.sort(key=lambda x: x['time'], reverse=False)
        activities = activities[:10]

        return jsonify({
            'activities': activities
        }), 200

    except Exception as e:
        print(f"Error fetching recent activity: {e}")
        return jsonify({'error': 'Failed to fetch activity'}), 500

def format_time_ago(timestamp):
    """Format timestamp as 'X time ago'"""
    now = datetime.now(timestamp.tzinfo)
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

@statistics_bp.route('/debug', methods=['GET'])
def debug_statistics():
    """Debug endpoint to check statistics state"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    supabase = get_supabase_client()
    if not supabase:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        # Get all user statistics
        stats_result = supabase.supabase.table("user_statistics")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

        # Get recent logs
        logs_result = supabase.supabase.table("schedule_generation_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()

        return jsonify({
            'user_id': user_id,
            'statistics': stats_result.data,
            'recent_logs': logs_result.data
        }), 200

    except Exception as e:
        print(f"Error in debug statistics: {e}")
        return jsonify({'error': 'Debug failed'}), 500