from flask import Blueprint, request, jsonify, session
from auth.auth_manager import AuthManager
import json
from datetime import datetime, timedelta

statistics_bp = Blueprint('statistics', __name__)

def get_auth_manager():
    """Get AuthManager instance"""
    try:
        return AuthManager()
    except ValueError as e:
        print(f"Auth configuration error: {e}")
        return None

@statistics_bp.route('/user', methods=['GET'])
def get_user_statistics():
    """Get user's statistics for dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        # Get user statistics
        stats_result = auth_manager.service_supabase.table("user_statistics")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

        # Get saved schedules count
        schedules_result = auth_manager.service_supabase.table("saved_schedules")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()

        # Get recent generation logs for success rate calculation
        logs_result = auth_manager.service_supabase.table("schedule_generation_logs")\
            .select("success")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()

        # Calculate statistics
        if stats_result.data:
            user_stats = stats_result.data[0]
        else:
            user_stats = {
                'schedules_created_total': 0,
                'schedules_created_this_week': 0,
                'total_courses_scheduled': 0,
                'average_schedule_generation_time': 0,
                'preferred_schedule_type': 'crammed',
                'constraints_used_count': 0
            }

        # Calculate success rate
        success_rate = 98
        if logs_result.data:
            successful_generations = sum(1 for log in logs_result.data if log['success'])
            total_generations = len(logs_result.data)
            if total_generations > 0:
                success_rate = round((successful_generations / total_generations) * 100)

        # Calculate efficiency
        efficiency = 85
        if user_stats['average_schedule_generation_time'] > 0:
            baseline_time = 1000
            avg_time = user_stats['average_schedule_generation_time']
            if avg_time <= baseline_time:
                efficiency = min(95, 85 + (baseline_time - avg_time) / baseline_time * 10)
            else:
                efficiency = max(60, 85 - (avg_time - baseline_time) / baseline_time * 25)
            efficiency = round(efficiency)

        # Calculate hours saved
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

@statistics_bp.route('/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get user's recent activity for dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        # Get recent schedule generations
        logs_result = auth_manager.service_supabase.table("schedule_generation_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        # Get recent saved schedules
        schedules_result = auth_manager.service_supabase.table("saved_schedules")\
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