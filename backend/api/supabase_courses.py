"""
Supabase-based Courses API - Updated to use the new database schema
This replaces the JSON file-based approach with scalable database queries
"""

from flask import Blueprint, request, jsonify
import os
import logging
from auth.routes import token_required
from supabase import create_client, Client
from .courses import load_courses_data

logger = logging.getLogger(__name__)

# Create Blueprint
supabase_courses_bp = Blueprint('supabase_courses', __name__)

# Initialize Supabase client
def get_supabase_client():
    """Get Supabase client instance"""
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError("Missing Supabase credentials")
    
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@supabase_courses_bp.route('/courses/test-supabase', methods=['GET'])
def test_supabase_connection():
    """Test endpoint to verify Supabase connection - NO AUTH REQUIRED"""
    try:
        supabase = get_supabase_client()
        
        # Simple query to test connection
        result = supabase.table('courses').select('id, name').limit(3).execute()
        
        return jsonify({
            'success': True,
            'message': 'Supabase connection working!',
            'sample_courses': result.data,
            'total_found': len(result.data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Supabase connection failed: {str(e)}'
        }), 500

@supabase_courses_bp.route('/courses/search', methods=['GET'])
@token_required
def search_courses():
    """
    Search courses with autocomplete support using Supabase
    Query parameters:
    - q: Search query (course name, ID, lecturer)
    - limit: Maximum number of results (default: 20, max: 100)
    - category: Filter by event category (הרצאה, סדנה, etc.)
    - lecturer: Filter by lecturer name
    - day: Filter by day of week
    - semester: Filter by semester (A, B)
    - department: Filter by department code
    """
    try:
        supabase = get_supabase_client()
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)
        category = request.args.get('category', '').strip()
        lecturer = request.args.get('lecturer', '').strip()
        day = request.args.get('day', '').strip()
        semester = request.args.get('semester', '').strip()
        department = request.args.get('department', '').strip()
        
        # Build base query with comprehensive joins
        base_query = '''
            id, name, english_name, description, credits, level, language,
            department:departments(id, name, code),
            university:universities(name, code),
            events:course_events(
                id, group_number, max_students, enrolled_students, notes,
                category:course_categories(id, name, description),
                location:locations(full_name, building_name, room_number),
                lecturers:course_event_lecturers(
                    role, is_primary,
                    lecturer:lecturers(id, name, title, email)
                ),
                time_slots:time_slots(
                    start_time, end_time, specific_date,
                    semester:semesters(id, name, code, academic_year),
                    day:days_of_week(id, name_hebrew, name_english, day_number)
                )
            )
        '''
        
        query_builder = (
            supabase
            .table('courses')
            .select(base_query)
            .eq('is_active', True)
            .limit(limit)
        )
        
        # Apply text search filter
        if query:
            # Search in course name, English name, or course ID
            search_condition = f'name.ilike.%{query}%,english_name.ilike.%{query}%,id.ilike.%{query}%'
            query_builder = query_builder.or_(search_condition)
        
        # Apply department filter
        if department:
            query_builder = query_builder.eq('departments.code', department)
        
        # Execute base query
        result = query_builder.execute()
        courses = result.data
        
        # Apply complex filters that require Python processing
        filtered_courses = []
        
        for course in courses:
            course_matches = True
            filtered_events = []
            
            for event in course.get('events', []):
                event_matches = True
                
                # Category filter
                if category and event.get('category', {}).get('name', '').lower() != category.lower():
                    event_matches = False
                
                # Lecturer filter
                if lecturer:
                    event_lecturers = [
                        lec['lecturer']['name'] 
                        for lec in event.get('lecturers', [])
                    ]
                    if not any(lecturer.lower() in lec_name.lower() for lec_name in event_lecturers):
                        event_matches = False
                
                # Day and semester filters
                if day or semester:
                    matching_slots = []
                    for slot in event.get('time_slots', []):
                        slot_matches = True
                        
                        if day and slot.get('day', {}).get('name_hebrew', '').lower() != day.lower():
                            slot_matches = False
                        
                        if semester and slot.get('semester', {}).get('code', '').upper() != semester.upper():
                            slot_matches = False
                        
                        if slot_matches:
                            matching_slots.append(slot)
                    
                    if (day or semester) and not matching_slots:
                        event_matches = False
                    else:
                        # Update event with filtered time slots
                        event = {**event, 'time_slots': matching_slots}
                
                if event_matches:
                    filtered_events.append(event)
            
            # Only include course if it has matching events
            if filtered_events or not (category or lecturer or day or semester):
                course_copy = {**course, 'events': filtered_events}
                filtered_courses.append(course_copy)
        
        # Format results for frontend
        results = []
        for course in filtered_courses:
            # Extract summary information
            lecturers = set()
            categories = set()
            days = set()
            semesters = set()
            locations = set()
            
            for event in course.get('events', []):
                # Lecturers
                for lec_assoc in event.get('lecturers', []):
                    lecturers.add(lec_assoc['lecturer']['name'])
                
                # Categories
                if event.get('category'):
                    categories.add(event['category']['name'])
                
                # Locations
                if event.get('location'):
                    locations.add(event['location']['full_name'])
                
                # Days and semesters from time slots
                for slot in event.get('time_slots', []):
                    if slot.get('day'):
                        days.add(slot['day']['name_hebrew'])
                    if slot.get('semester'):
                        semesters.add(slot['semester']['code'])
            
            results.append({
                'id': course['id'],
                'name': course['name'],
                'english_name': course.get('english_name'),
                'description': course.get('description'),
                'credits': course.get('credits'),
                'level': course.get('level'),
                'department': course.get('department', {}),
                'events_count': len(course.get('events', [])),
                'summary': {
                    'lecturers': list(lecturers),
                    'categories': list(categories),
                    'days': list(days),
                    'semesters': list(semesters),
                    'locations': list(locations)
                },
                'events': course.get('events', [])  # Full event data
            })
        
        return jsonify({
            'success': True,
            'courses': results,
            'total_results': len(results),
            'query': query,
            'filters': {
                'category': category,
                'lecturer': lecturer,
                'day': day,
                'semester': semester,
                'department': department
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching courses: {e}")
        return jsonify({
            'success': False,
            'courses': [],
            'total_results': 0,
            'error': str(e),
            'query': request.args.get('q', '')
        }), 500

@supabase_courses_bp.route('/courses/autocomplete', methods=['GET'])
@token_required
def autocomplete_courses():
    """
    Autocomplete endpoint for course names and IDs using Supabase
    """
    try:
        supabase = get_supabase_client()
        
        query = request.args.get('q', '').strip()
        semester = request.args.get('semester', '').strip()
        limit = min(int(request.args.get('limit', 10)), 20)
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            }), 200
        
        # Search in courses
        search_condition = f'name.ilike.%{query}%,english_name.ilike.%{query}%,id.ilike.%{query}%'
        
        query_builder = (
            supabase
            .table('courses')
            .select('''
                id, name, english_name,
                events:course_events(
                    lecturers:course_event_lecturers(
                        lecturer:lecturers(name)
                    ),
                    time_slots:time_slots(
                        semester:semesters(code)
                    )
                )
            ''')
            .or_(search_condition)
            .eq('is_active', True)
            .limit(limit * 2)  # Get more to filter by semester
        )
        
        result = query_builder.execute()
        courses = result.data
        
        suggestions = []
        
        for course in courses:
            # Filter by semester if specified
            if semester:  # Re-enabled semester filtering
                has_semester = False
                for event in course.get('events', []):
                    for slot in event.get('time_slots', []):
                        if slot.get('semester', {}).get('code') == semester:
                            has_semester = True
                            break
                    if has_semester:
                        break
                
                if not has_semester:
                    continue
            
            # Extract lecturers
            lecturers = set()
            for event in course.get('events', []):
                for lec_assoc in event.get('lecturers', []):
                    lecturers.add(lec_assoc['lecturer']['name'])
            
            suggestions.append({
                'id': course['id'],
                'name': course['name'],
                'english_name': course.get('english_name'),
                'display': f"{course['id']} - {course['name']}",
                'lecturers': list(lecturers)[:3]  # Limit for display
            })
            
            if len(suggestions) >= limit:
                break
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'query': query
        }), 200
        
    except Exception as e:
        logger.error(f"Error in autocomplete: {e}")
        return jsonify({
            'success': False,
            'suggestions': [],
            'error': str(e)
        }), 500

@supabase_courses_bp.route('/courses/course/<course_id>', methods=['GET'])
@token_required
def get_course_details(course_id):
    """Get detailed information for a specific course from local JSON (always)."""
    try:
        semester = request.args.get('semester', '').strip()

        courses_data = load_courses_data()
        all_courses = courses_data.get('courses', [])

        # Find course by ID
        course = next((c for c in all_courses if c.get('id') == course_id), None)

        if not course:
            return jsonify({
                'success': False,
                'course': None,
                'error': 'Course not found',
                'course_id': course_id
            }), 404

        # Filter events by semester if specified
        filtered_events = course.get('events', [])
        if semester:
            tmp = []
            for event in course.get('events', []):
                filtered_time_slots = [
                    slot for slot in event.get('timeSlots', [])
                    if slot.get('semester') == semester
                ]
                if filtered_time_slots:
                    tmp.append({**event, 'timeSlots': filtered_time_slots})
            filtered_events = tmp

        # Build summary fields
        lecturers = set()
        categories = set()
        days = set()
        semesters = set()
        locations = set()

        for event in filtered_events:
            for lec in event.get('lecturers', []) or []:
                lecturers.add(lec)
            if event.get('category'):
                categories.add(event.get('category'))
            if event.get('location'):
                locations.add(event.get('location'))
            for slot in event.get('timeSlots', []) or []:
                if slot.get('day'):
                    days.add(slot['day'])
                if slot.get('semester'):
                    semesters.add(slot['semester'])

        enhanced_course = {
            **course,
            'events': filtered_events,
            'summary': {
                'lecturers': list(lecturers),
                'categories': list(categories),
                'days': list(days),
                'semesters': list(semesters),
                'locations': list(filter(None, locations)),
                'events_count': len(filtered_events)
            }
        }

        return jsonify({
            'success': True,
            'course': enhanced_course,
            'course_id': course_id,
            'source': 'json'
        }), 200

    except Exception as e:
        logger.error(f"Error getting course details for {course_id}: {e}")
        return jsonify({
            'success': False,
            'course': None,
            'error': str(e),
            'course_id': course_id
        }), 500

@supabase_courses_bp.route('/courses/filters', methods=['GET'])
@token_required
def get_filter_options():
    """Get available filter options from Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Get lecturers
        lecturers_result = (
            supabase
            .table('lecturers')
            .select('name')
            .eq('is_active', True)
            .execute()
        )
        lecturers = [lec['name'] for lec in lecturers_result.data]
        
        # Get categories
        categories_result = (
            supabase
            .table('course_categories')
            .select('name')
            .execute()
        )
        categories = [cat['name'] for cat in categories_result.data]
        
        # Get days
        days_result = (
            supabase
            .table('days_of_week')
            .select('name_hebrew, name_english')
            .execute()
        )
        days = [day['name_hebrew'] for day in days_result.data]
        
        # Get semesters
        semesters_result = (
            supabase
            .table('semesters')
            .select('code, name')
            .execute()
        )
        semesters = [sem['code'] for sem in semesters_result.data]
        
        # Get departments
        departments_result = (
            supabase
            .table('departments')
            .select('code, name')
            .execute()
        )
        departments = [{'code': dept['code'], 'name': dept['name']} for dept in departments_result.data]
        
        return jsonify({
            'success': True,
            'filters': {
                'lecturers': sorted(lecturers),
                'categories': sorted(categories),
                'days': days,  # Keep original order
                'semesters': semesters,
                'departments': departments
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        return jsonify({
            'success': False,
            'filters': {},
            'error': str(e)
        }), 500

@supabase_courses_bp.route('/courses/stats', methods=['GET'])
@token_required
def get_courses_stats():
    """Get statistics about the courses database from Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Get basic counts
        courses_count = supabase.table('courses').select('id', count='exact').eq('is_active', True).execute()
        events_count = supabase.table('course_events').select('id', count='exact').eq('is_active', True).execute()
        lecturers_count = supabase.table('lecturers').select('id', count='exact').eq('is_active', True).execute()
        slots_count = supabase.table('time_slots').select('id', count='exact').eq('is_cancelled', False).execute()
        
        # Get courses by department
        dept_courses = (
            supabase
            .table('courses')
            .select('department:departments(name)')
            .eq('is_active', True)
            .execute()
        )
        
        dept_counts = {}
        for course in dept_courses.data:
            dept_name = course['department']['name']
            dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
        
        # Get courses by level
        level_courses = (
            supabase
            .table('courses')
            .select('level')
            .eq('is_active', True)
            .execute()
        )
        
        level_counts = {}
        for course in level_courses.data:
            level = course.get('level') or 'Unknown'
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Get top categories
        category_events = (
            supabase
            .table('course_events')
            .select('category:course_categories(name)')
            .eq('is_active', True)
            .execute()
        )
        
        category_counts = {}
        for event in category_events.data:
            cat_name = event['category']['name']
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_courses': courses_count.count,
                'total_events': events_count.count,
                'total_lecturers': lecturers_count.count,
                'total_time_slots': slots_count.count,
                'courses_by_department': dept_counts,
                'courses_by_level': level_counts,
                'events_by_category': category_counts
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting course statistics: {e}")
        return jsonify({
            'success': False,
            'statistics': {},
            'error': str(e)
        }), 500

@supabase_courses_bp.route('/courses/conflicts', methods=['POST'])
@token_required
def check_schedule_conflicts():
    """Check for time conflicts between selected course events"""
    try:
        supabase = get_supabase_client()
        
        data = request.get_json()
        course_event_ids = data.get('course_event_ids', [])
        semester_code = data.get('semester', 'A')
        
        if not course_event_ids:
            return jsonify({
                'success': True,
                'conflicts': []
            }), 200
        
        # Get time slots for selected events
        result = (
            supabase
            .table('time_slots')
            .select('''
                *,
                course_event:course_events(
                    id, course_id,
                    course:courses(name)
                ),
                day:days_of_week(name_english, name_hebrew, day_number),
                semester:semesters(code)
            ''')
            .in_('course_event_id', course_event_ids)
            .eq('semester.code', semester_code)
            .eq('is_cancelled', False)
            .execute()
        )
        
        time_slots = result.data
        conflicts = []
        
        # Check for conflicts
        from datetime import datetime
        
        for i, slot1 in enumerate(time_slots):
            for slot2 in time_slots[i+1:]:
                # Same day check
                if slot1['day']['day_number'] == slot2['day']['day_number']:
                    # Parse times
                    start1 = datetime.strptime(slot1['start_time'], '%H:%M').time()
                    end1 = datetime.strptime(slot1['end_time'], '%H:%M').time()
                    start2 = datetime.strptime(slot2['start_time'], '%H:%M').time()
                    end2 = datetime.strptime(slot2['end_time'], '%H:%M').time()
                    
                    # Check if times overlap
                    if not (end1 <= start2 or end2 <= start1):
                        conflicts.append({
                            'course1': {
                                'id': slot1['course_event']['course_id'],
                                'name': slot1['course_event']['course']['name'],
                                'event_id': slot1['course_event']['id']
                            },
                            'course2': {
                                'id': slot2['course_event']['course_id'],
                                'name': slot2['course_event']['course']['name'],
                                'event_id': slot2['course_event']['id']
                            },
                            'day': slot1['day']['name_hebrew'],
                            'time1': f"{slot1['start_time']}-{slot1['end_time']}",
                            'time2': f"{slot2['start_time']}-{slot2['end_time']}"
                        })
        
        return jsonify({
            'success': True,
            'conflicts': conflicts,
            'semester': semester_code
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking conflicts: {e}")
        return jsonify({
            'success': False,
            'conflicts': [],
            'error': str(e)
        }), 500
