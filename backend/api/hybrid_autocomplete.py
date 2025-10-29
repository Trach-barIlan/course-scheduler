"""
Hybrid Autocomplete API - Fast JSON-based autocomplete with database fallback
This provides lightning-fast autocomplete using JSON files while maintaining 
real-time course details from the database.

Strategy:
1. Autocomplete: Use JSON file for instant results
2. Course Details: Fetch from database for real-time data
3. Sync: Periodic JSON updates from database
"""

from flask import Blueprint, request, jsonify
import json
import os
import logging
from datetime import datetime, timedelta
from auth.routes import token_required

logger = logging.getLogger(__name__)

hybrid_autocomplete_bp = Blueprint('hybrid_autocomplete', __name__)

# Cache for autocomplete data
_autocomplete_cache = None
_cache_last_updated = None
_cache_ttl = timedelta(hours=6)  # Refresh every 6 hours

def load_autocomplete_cache():
    """Load optimized autocomplete data from JSON with caching"""
    global _autocomplete_cache, _cache_last_updated
    
    # Check if cache is still valid
    if (_autocomplete_cache is not None and 
        _cache_last_updated is not None and 
        datetime.now() - _cache_last_updated < _cache_ttl):
        return _autocomplete_cache
    
    try:
        # Load from courses.json
        courses_path = os.path.join(os.path.dirname(__file__), '..', 'integrations', 'courses.json')
        with open(courses_path, 'r', encoding='utf-8') as f:
            courses_data = json.load(f)
        
        # Build optimized autocomplete structure
        autocomplete_data = {}
        
        for course in courses_data.get('courses', []):
            course_id = course.get('id', '')
            course_name = course.get('name', '')
            
            # Extract semesters and lecturers
            semesters = set()
            lecturers = set()
            
            for event in course.get('events', []):
                # Get lecturers
                for lecturer in event.get('lecturers', []):
                    lecturers.add(lecturer)
                
                # Get semesters from time slots
                for time_slot in event.get('timeSlots', []):
                    semester = time_slot.get('semester', '')
                    if semester:
                        semesters.add(semester)
            
            # Create autocomplete entry
            autocomplete_entry = {
                'id': course_id,
                'name': course_name,
                'semesters': list(semesters),
                'lecturers': list(lecturers)[:3],  # Limit for performance
                'search_text': f"{course_id} {course_name}".lower(),
                'display': f"{course_id} - {course_name}"
            }
            
            # Index by course ID for fast lookup
            autocomplete_data[course_id] = autocomplete_entry
        
        _autocomplete_cache = autocomplete_data
        _cache_last_updated = datetime.now()
        
        logger.info(f"Built autocomplete cache with {len(autocomplete_data)} courses")
        return _autocomplete_cache
        
    except Exception as e:
        logger.error(f"Error loading autocomplete cache: {e}")
        if _autocomplete_cache is None:
            _autocomplete_cache = {}
        return _autocomplete_cache

@hybrid_autocomplete_bp.route('/courses/fast-autocomplete', methods=['GET'])
def fast_autocomplete():
    """
    Ultra-fast autocomplete using JSON-based lookup
    Returns results in <10ms instead of 100-500ms database queries
    """
    try:
        query = request.args.get('q', '').strip().lower()
        semester = request.args.get('semester', '').strip()
        limit = min(int(request.args.get('limit', 8)), 15)
        
        # Minimum query length for performance
        if len(query) < 3:
            return jsonify({
                'success': True,
                'suggestions': [],
                'source': 'json_cache',
                'query_too_short': True
            }), 200
        
        # Load autocomplete cache
        autocomplete_data = load_autocomplete_cache()
        
        # Fast in-memory search
        matches = []
        
        for course_id, course_data in autocomplete_data.items():
            # Quick text matching
            if query in course_data['search_text']:
                # Semester filtering
                if semester and semester not in course_data['semesters']:
                    continue
                
                matches.append({
                    'id': course_data['id'],
                    'name': course_data['name'],
                    'display': course_data['display'],
                    'lecturers': course_data['lecturers']
                })
                
                # Early exit for performance
                if len(matches) >= limit:
                    break
        
        # Sort by relevance (exact matches first, then by course ID)
        matches.sort(key=lambda x: (
            0 if query in x['name'].lower() else 1,  # Exact name matches first
            x['id']  # Then by course ID
        ))
        
        return jsonify({
            'success': True,
            'suggestions': matches[:limit],
            'source': 'json_cache',
            'query': request.args.get('q', ''),
            'cache_age_hours': (datetime.now() - _cache_last_updated).total_seconds() / 3600 if _cache_last_updated else 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error in fast autocomplete: {e}")
        return jsonify({
            'success': False,
            'suggestions': [],
            'error': str(e),
            'source': 'json_cache'
        }), 500

@hybrid_autocomplete_bp.route('/courses/refresh-cache', methods=['POST'])
@token_required
def refresh_autocomplete_cache():
    """
    Manually refresh the autocomplete cache
    Can be called after database updates
    """
    try:
        global _autocomplete_cache, _cache_last_updated
        
        # Force cache refresh
        _autocomplete_cache = None
        _cache_last_updated = None
        
        # Rebuild cache
        cache_data = load_autocomplete_cache()
        
        return jsonify({
            'success': True,
            'message': 'Autocomplete cache refreshed',
            'courses_count': len(cache_data),
            'refreshed_at': _cache_last_updated.isoformat() if _cache_last_updated else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@hybrid_autocomplete_bp.route('/courses/cache-status', methods=['GET'])
@token_required
def get_cache_status():
    """Get information about the autocomplete cache"""
    try:
        cache_data = load_autocomplete_cache()
        
        return jsonify({
            'success': True,
            'status': {
                'courses_count': len(cache_data),
                'last_updated': _cache_last_updated.isoformat() if _cache_last_updated else None,
                'age_hours': (datetime.now() - _cache_last_updated).total_seconds() / 3600 if _cache_last_updated else None,
                'ttl_hours': _cache_ttl.total_seconds() / 3600,
                'next_refresh': (_cache_last_updated + _cache_ttl).isoformat() if _cache_last_updated else 'immediate'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting cache status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hybrid_autocomplete_bp.route('/courses/fast-course/<course_id>', methods=['GET'])
def fast_course_details(course_id):
    """
    Return full course details (events + timeSlots) from the JSON cache without requiring auth.
    This is read-only and intended for unauthenticated UIs to populate times quickly.
    """
    try:
        semester = request.args.get('semester', '').strip()

        # Load courses.json directly (keeps this endpoint independent of DB)
        courses_path = os.path.join(os.path.dirname(__file__), '..', 'integrations', 'courses.json')
        with open(courses_path, 'r', encoding='utf-8') as f:
            courses_data = json.load(f)

        all_courses = courses_data.get('courses', [])
        course = next((c for c in all_courses if c.get('id') == course_id), None)

        if not course:
            return jsonify({'success': False, 'course': None, 'error': 'Course not found', 'course_id': course_id}), 404

        # Optionally filter timeSlots by semester
        filtered_events = course.get('events', [])
        if semester:
            new_events = []
            for event in course.get('events', []):
                filtered_time_slots = [slot for slot in event.get('timeSlots', []) if slot.get('semester') == semester]
                if filtered_time_slots:
                    ev = { **event, 'timeSlots': filtered_time_slots }
                    new_events.append(ev)
            filtered_events = new_events

        filtered_course = { **course, 'events': filtered_events }

        return jsonify({ 'success': True, 'course': filtered_course, 'course_id': course_id }), 200
    except Exception as e:
        logger.error(f"Error in fast_course_details for {course_id}: {e}")
        return jsonify({ 'success': False, 'course': None, 'error': str(e), 'course_id': course_id }), 500

# Background sync service (could be implemented separately)
def sync_json_from_database():
    """
    Sync the JSON file from the database
    This would be called by a scheduled job (cron, celery, etc.)
    """
    try:
        from .supabase_courses import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Get all courses from database
        result = supabase.table('courses').select('''
            id, name, english_name,
            events:course_events(
                id, category:course_categories(name),
                lecturers:course_event_lecturers(
                    lecturer:lecturers(name)
                ),
                time_slots:time_slots(
                    start_time, end_time,
                    day:days_of_week(name_english),
                    semester:semesters(code)
                )
            )
        ''').eq('is_active', True).execute()
        
        # Transform to courses.json format
        courses_json = {'courses': []}
        
        for course in result.data:
            course_entry = {
                'id': course['id'],
                'name': course['name'],
                'events': []
            }
            
            for event in course.get('events', []):
                event_entry = {
                    'id': f"{course['id']}-{event['id']}",
                    'category': event.get('category', {}).get('name', ''),
                    'lecturers': [lec['lecturer']['name'] for lec in event.get('lecturers', [])],
                    'timeSlots': []
                }
                
                for slot in event.get('time_slots', []):
                    slot_entry = {
                        'day': slot.get('day', {}).get('name_english', ''),
                        'from': slot.get('start_time', ''),
                        'to': slot.get('end_time', ''),
                        'semester': slot.get('semester', {}).get('code', '')
                    }
                    event_entry['timeSlots'].append(slot_entry)
                
                course_entry['events'].append(event_entry)
            
            courses_json['courses'].append(course_entry)
        
        # Write to JSON file
        courses_path = os.path.join(os.path.dirname(__file__), '..', 'integrations', 'courses.json')
        with open(courses_path, 'w', encoding='utf-8') as f:
            json.dump(courses_json, f, ensure_ascii=False, indent=2)
        
        # Refresh cache
        global _autocomplete_cache, _cache_last_updated
        _autocomplete_cache = None
        _cache_last_updated = None
        load_autocomplete_cache()
        
        logger.info(f"Successfully synced {len(courses_json['courses'])} courses from database to JSON")
        return True
        
    except Exception as e:
        logger.error(f"Error syncing JSON from database: {e}")
        return False
