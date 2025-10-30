"""
General Courses API - for the courses.json file
This handles the large collection of Hebrew courses
"""

from flask import Blueprint, request, jsonify
import json
import os
import logging
from auth.routes import token_required

logger = logging.getLogger(__name__)

courses_bp = Blueprint('courses', __name__)

# Cache for courses data
_courses_cache = None

def load_courses_data():
    """Load courses data from JSON file with caching"""
    global _courses_cache
    
    if _courses_cache is None:
        try:
            courses_path = os.path.join(os.path.dirname(__file__), '..', 'integrations', 'courses.json')
            with open(courses_path, 'r', encoding='utf-8') as f:
                _courses_cache = json.load(f)
            logger.info(f"Loaded {len(_courses_cache.get('courses', []))} courses from courses.json")
        except Exception as e:
            logger.error(f"Error loading courses data: {e}")
            _courses_cache = {'courses': []}
    
    return _courses_cache

@courses_bp.route('/courses/search', methods=['GET'])
@token_required
def search_courses():
    """
    Search courses with autocomplete support
    Query parameters:
    - q: Search query (course name, ID, lecturer)
    - limit: Maximum number of results (default: 20, max: 100)
    - category: Filter by event category (הרצאה, סדנה, etc.)
    - lecturer: Filter by lecturer name
    - day: Filter by day of week
    - semester: Filter by semester (A, B)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)
        category = request.args.get('category', '').strip()
        lecturer = request.args.get('lecturer', '').strip()
        day = request.args.get('day', '').strip()
        semester = request.args.get('semester', '').strip()
        
        courses_data = load_courses_data()
        all_courses = courses_data.get('courses', [])
        
        # Filter courses
        filtered_courses = []
        
        for course in all_courses:
            # Text search in course name or ID
            if query:
                if (query.lower() not in course['name'].lower() and 
                    query not in course['id']):
                    continue
            
            # Filter by category, lecturer, day, semester
            course_matches = False
            filtered_events = []
            
            for event in course.get('events', []):
                event_matches = True
                
                # Category filter
                if category and category.lower() not in event.get('category', '').lower():
                    event_matches = False
                
                # Lecturer filter  
                if lecturer and not any(lecturer.lower() in lec.lower() 
                                      for lec in event.get('lecturers', [])):
                    event_matches = False
                
                # Day and semester filters (check timeSlots)
                if (day or semester) and event.get('timeSlots'):
                    slot_matches = False
                    for slot in event['timeSlots']:
                        if day and day.lower() != slot.get('day', '').lower():
                            continue
                        if semester and semester.upper() != slot.get('semester', '').upper():
                            continue
                        slot_matches = True
                        break
                    if not slot_matches:
                        event_matches = False
                
                if event_matches:
                    filtered_events.append(event)
                    course_matches = True
            
            if course_matches:
                # Create a filtered version of the course
                filtered_course = course.copy()
                if category or lecturer or day or semester:
                    filtered_course['events'] = filtered_events
                filtered_courses.append(filtered_course)
                
                if len(filtered_courses) >= limit:
                    break
        
        # Format results for frontend
        results = []
        for course in filtered_courses:
            # Create summary info
            lecturers = set()
            categories = set()
            days = set()
            semesters = set()
            
            for event in course.get('events', []):
                lecturers.update(event.get('lecturers', []))
                categories.add(event.get('category', ''))
                for slot in event.get('timeSlots', []):
                    days.add(slot.get('day', ''))
                    semesters.add(slot.get('semester', ''))
            
            results.append({
                'id': course['id'],
                'name': course['name'],
                'events_count': len(course.get('events', [])),
                'lecturers': list(lecturers),
                'categories': list(categories),
                'days': list(days),
                'semesters': list(semesters),
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
                'semester': semester
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

@courses_bp.route('/courses/autocomplete', methods=['GET'])
@token_required  
def autocomplete_courses():
    """
    Autocomplete endpoint for course names and IDs
    Returns quick suggestions for search as user types
    """
    try:
        query = request.args.get('q', '').strip()
        semester = request.args.get('semester', '').strip()
        limit = min(int(request.args.get('limit', 10)), 20)
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            }), 200
        
        courses_data = load_courses_data()
        all_courses = courses_data.get('courses', [])
        
        suggestions = []
        query_lower = query.lower()
        
        for course in all_courses:
            # Match by course name or ID
            if (query_lower in course['name'].lower() or 
                query in course['id']):
                
                # Filter by semester if specified
                if semester:
                    has_semester = False
                    for event in course.get('events', []):
                        for time_slot in event.get('timeSlots', []):
                            if time_slot.get('semester') == semester:
                                has_semester = True
                                break
                        if has_semester:
                            break
                    
                    # Skip this course if it doesn't have the requested semester
                    if not has_semester:
                        continue
                
                # Get lecturers for display
                lecturers = set()
                for event in course.get('events', []):
                    lecturers.update(event.get('lecturers', []))
                
                suggestions.append({
                    'id': course['id'],
                    'name': course['name'],
                    'display': f"{course['id']} - {course['name']}",
                    'lecturers': list(lecturers)[:3]  # Limit to 3 lecturers for display
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

@courses_bp.route('/courses/course/<course_id>', methods=['GET'])
def get_course_details(course_id):
    """Get detailed information for a specific course"""
    try:
        semester = request.args.get('semester', '').strip()
        courses_data = load_courses_data()
        all_courses = courses_data.get('courses', [])
        
        # Find course by ID
        course = next((c for c in all_courses if c['id'] == course_id), None)
        
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
            filtered_events = []
            for event in course.get('events', []):
                # Filter time slots by semester
                filtered_time_slots = [
                    slot for slot in event.get('timeSlots', []) 
                    if slot.get('semester') == semester
                ]
                
                # Only include event if it has time slots for the requested semester
                if filtered_time_slots:
                    filtered_event = {
                        **event,
                        'timeSlots': filtered_time_slots
                    }
                    filtered_events.append(filtered_event)
        
        # Create filtered course
        filtered_course = {
            **course,
            'events': filtered_events
        }
        
        # Enhance course data with summary
        lecturers = set()
        categories = set()
        days = set()
        semesters = set()
        locations = set()
        
        for event in filtered_events:
            lecturers.update(event.get('lecturers', []))
            categories.add(event.get('category', ''))
            if event.get('location'):
                locations.add(event['location'])
            
            for slot in event.get('timeSlots', []):
                days.add(slot.get('day', ''))
                semesters.add(slot.get('semester', ''))
        
        enhanced_course = {
            **filtered_course,
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
            'course_id': course_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting course details for {course_id}: {e}")
        return jsonify({
            'success': False,
            'course': None,
            'error': str(e),
            'course_id': course_id
        }), 500

@courses_bp.route('/courses/filters', methods=['GET'])
@token_required
def get_filter_options():
    """Get available filter options (lecturers, categories, days, semesters)"""
    try:
        courses_data = load_courses_data()
        all_courses = courses_data.get('courses', [])
        
        lecturers = set()
        categories = set()
        days = set()
        semesters = set()
        
        for course in all_courses:
            for event in course.get('events', []):
                lecturers.update(event.get('lecturers', []))
                categories.add(event.get('category', ''))
                
                for slot in event.get('timeSlots', []):
                    days.add(slot.get('day', ''))
                    semesters.add(slot.get('semester', ''))
        
        return jsonify({
            'success': True,
            'filters': {
                'lecturers': sorted(list(filter(None, lecturers))),
                'categories': sorted(list(filter(None, categories))),
                'days': sorted(list(filter(None, days))),
                'semesters': sorted(list(filter(None, semesters)))
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        return jsonify({
            'success': False,
            'filters': {},
            'error': str(e)
        }), 500

@courses_bp.route('/courses/stats', methods=['GET'])
@token_required
def get_courses_stats():
    """Get statistics about the courses database"""
    try:
        courses_data = load_courses_data()
        all_courses = courses_data.get('courses', [])
        
        total_events = sum(len(course.get('events', [])) for course in all_courses)
        
        # Category distribution
        category_counts = {}
        lecturer_counts = {}
        
        for course in all_courses:
            for event in course.get('events', []):
                category = event.get('category', 'Unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
                
                for lecturer in event.get('lecturers', []):
                    lecturer_counts[lecturer] = lecturer_counts.get(lecturer, 0) + 1
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_courses': len(all_courses),
                'total_events': total_events,
                'categories': category_counts,
                'top_lecturers': dict(sorted(lecturer_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:10])
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting course statistics: {e}")
        return jsonify({
            'success': False,
            'statistics': {},
            'error': str(e)
        }), 500
