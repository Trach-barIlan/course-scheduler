from flask import Blueprint, request, jsonify, g
from auth.routes import token_required
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
@token_required
def get_user_statistics():
    """Get user's statistics for dashboard"""
    user_id = g.user['id']

    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        client = auth_manager.get_client_for_user(user_id)
        
        # Get user statistics
        stats_result = client.table("user_statistics")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

        # Get saved schedules count
        schedules_result = client.table("saved_schedules")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()

        # Get recent generation logs for success rate calculation
        logs_result = client.table("schedule_generation_logs")\
            .select("success, generation_time_ms, courses_count, constraints_count")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()

        # Calculate statistics
        if stats_result.data:
            user_stats = stats_result.data[0]
        else:
            # Initialize user statistics if they don't exist
            user_stats = {
                'schedules_created_total': 0,
                'schedules_created_this_week': 0,
                'schedules_created_this_month': 0,
                'total_courses_scheduled': 0,
                'average_schedule_generation_time': 0,
                'preferred_schedule_type': 'crammed',
                'constraints_used_count': 0
            }
            
            # Create initial statistics record
            try:
                client.table("user_statistics").insert({
                    'user_id': user_id,
                    **user_stats
                }).execute()
            except Exception as e:
                print(f"Failed to create initial statistics: {e}")

        # Calculate success rate from recent logs
        success_rate = 98  # Default
        if logs_result.data and len(logs_result.data) > 0:
            successful_generations = sum(1 for log in logs_result.data if log.get('success', True))
            total_generations = len(logs_result.data)
            if total_generations > 0:
                success_rate = round((successful_generations / total_generations) * 100)

        # Calculate efficiency based on generation time
        efficiency = 85  # Default
        if logs_result.data and len(logs_result.data) > 0:
            avg_time = sum(log.get('generation_time_ms', 1000) for log in logs_result.data) / len(logs_result.data)
            baseline_time = 1000  # 1 second baseline
            if avg_time <= baseline_time:
                efficiency = min(95, 85 + (baseline_time - avg_time) / baseline_time * 10)
            else:
                efficiency = max(60, 85 - (avg_time - baseline_time) / baseline_time * 25)
            efficiency = round(efficiency)

        # Calculate hours saved (estimate 30 minutes saved per schedule)
        hours_saved = user_stats.get('schedules_created_total', 0) * 0.5

        # Get actual saved schedules count
        saved_schedules_count = schedules_result.count if schedules_result.count is not None else 0

        return jsonify({
            'statistics': {
                'schedules_created': user_stats.get('schedules_created_total', 0),
                'schedules_this_week': user_stats.get('schedules_created_this_week', 0),
                'schedules_created_this_month': user_stats.get('schedules_created_this_month', 0),
                'saved_schedules_count': saved_schedules_count,
                'hours_saved': round(hours_saved, 1),
                'success_rate': success_rate,
                'efficiency': efficiency,
                'total_courses_scheduled': user_stats.get('total_courses_scheduled', 0),
                'preferred_schedule_type': user_stats.get('preferred_schedule_type', 'crammed'),
                'constraints_used_count': user_stats.get('constraints_used_count', 0),
                'average_generation_time': round(user_stats.get('average_schedule_generation_time', 0))
            }
        }), 200

    except Exception as e:
        print(f"Error fetching user statistics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@statistics_bp.route('/recent-activity', methods=['GET'])
@token_required
def get_recent_activity():
    """Get user's recent activity for dashboard"""
    user_id = g.user['id']

    auth_manager = get_auth_manager()
    if not auth_manager:
        return jsonify({'error': 'Authentication service unavailable'}), 500

    try:
        client = auth_manager.get_client_for_user(user_id)
        
        # Get recent schedule generations
        logs_result = client.table("schedule_generation_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        # Get recent saved schedules
        schedules_result = client.table("saved_schedules")\
            .select("schedule_name, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()

        # Format activity data
        activities = []

        # Add schedule generations
        for log in logs_result.data or []:
            try:
                created_at = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                time_ago = format_time_ago(created_at)
                
                if log.get('success', True):
                    action = f"Generated schedule with {log.get('courses_count', 0)} courses"
                else:
                    error_msg = log.get('error_message', 'Unknown error')
                    action = f"Failed to generate schedule ({error_msg})"
                
                activities.append({
                    'action': action,
                    'time': time_ago,
                    'type': 'generation',
                    'success': log.get('success', True),
                    'timestamp': created_at
                })
            except Exception as e:
                print(f"Error processing log entry: {e}")
                continue

        # Add saved schedules
        for schedule in schedules_result.data or []:
            try:
                created_at = datetime.fromisoformat(schedule['created_at'].replace('Z', '+00:00'))
                time_ago = format_time_ago(created_at)
                
                activities.append({
                    'action': f"Saved '{schedule['schedule_name']}'",
                    'time': time_ago,
                    'type': 'save',
                    'success': True,
                    'timestamp': created_at
                })
            except Exception as e:
                print(f"Error processing schedule entry: {e}")
                continue

        # Sort by timestamp (most recent first) and limit to 10
        activities.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        activities = activities[:10]

        # Remove timestamp from response (used only for sorting)
        for activity in activities:
            activity.pop('timestamp', None)

        return jsonify({
            'activities': activities
        }), 200

    except Exception as e:
        print(f"Error fetching recent activity: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch activity'}), 500

def format_time_ago(timestamp):
    """Format timestamp as 'X time ago'"""
    try:
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
    except Exception as e:
        print(f"Error formatting time: {e}")
        return "Recently"