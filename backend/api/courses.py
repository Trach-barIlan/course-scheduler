from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime, timedelta
from auth.routes import get_current_user, get_auth_manager
from logger import logger

courses_router = APIRouter(prefix="/api/courses", tags=["courses"])

# Cache for courses data
_courses_cache = None
_cache_last_updated = None
_cache_ttl = timedelta(hours=6)

def load_courses_data():
    """Load courses data from JSON file with caching"""
    global _courses_cache, _cache_last_updated
    
    if (_courses_cache is not None and 
        _cache_last_updated is not None and 
        datetime.now() - _cache_last_updated < _cache_ttl):
        return _courses_cache
    
    try:
        courses_path = os.path.join(os.path.dirname(__file__), '..', 'integrations', 'courses.json')
        with open(courses_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        _courses_cache = data
        _cache_last_updated = datetime.now()
        return _courses_cache
    except Exception as e:
        logger.error("load_courses_failed", error=str(e))
        return {'courses': []}

def get_autocomplete_data():
    """Build optimized autocomplete structure from cache"""
    cache = load_courses_data()
    all_courses = cache.get('courses', [])
    
    autocomplete_data = {}
    for course in all_courses:
        course_id = course.get('id', '')
        course_name = course.get('name', '')
        
        semesters = set()
        lecturers = set()
        for event in course.get('events', []):
            for lecturer in event.get('lecturers', []):
                lecturers.add(lecturer)
            for time_slot in event.get('timeSlots', []):
                semester = time_slot.get('semester', '')
                if semester:
                    semesters.add(semester)
        
        autocomplete_data[course_id] = {
            'id': course_id,
            'name': course_name,
            'semesters': list(semesters),
            'lecturers': list(lecturers)[:3],
            'search_text': f"{course_id} {course_name}".lower(),
            'display': f"{course_id} - {course_name}"
        }
    return autocomplete_data

@courses_router.get("/fast-autocomplete")
async def fast_autocomplete(
    q: str = "", 
    semester: Optional[str] = None, 
    limit: int = 8
):
    """Ultra-fast JSON-based autocomplete."""
    query = q.strip().lower()
    if len(query) < 3:
        return {"success": True, "suggestions": [], "query_too_short": True}
    
    data = get_autocomplete_data()
    matches = []
    
    for course_id, course in data.items():
        if query in course['search_text']:
            if semester and semester not in course['semesters']:
                continue
            matches.append({
                'id': course['id'],
                'name': course['name'],
                'display': course['display'],
                'lecturers': course['lecturers']
            })
            if len(matches) >= limit:
                break
    
    matches.sort(key=lambda x: (0 if query in x['name'].lower() else 1, x['id']))
    
    return {
        "success": True, 
        "suggestions": matches[:limit],
        "query": q
    }

@courses_router.get("/course/{course_id}")
@courses_router.get("/fast-course/{course_id}")
async def get_course_details(course_id: str, semester: Optional[str] = None):
    """Get full course details from JSON."""
    try:
        cache = load_courses_data()
        all_courses = cache.get('courses', [])

        course = next((c for c in all_courses if str(c.get('id')) == str(course_id)), None)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Create a copy
        course_copy = json.loads(json.dumps(course))

        if semester:
            filtered_events = []
            for event in course_copy.get('events', []):
                slots = [s for s in event.get('timeSlots', []) if s.get('semester') == semester]
                if slots:
                    event['timeSlots'] = slots
                    filtered_events.append(event)
            course_copy['events'] = filtered_events

        # Build summary for frontend
        lecturers = set()
        categories = set()
        days = set()
        semesters = set()
        
        for event in course_copy.get('events', []):
            lecturers.update(event.get('lecturers', []) or [])
            if event.get('category'): categories.add(event['category'])
            for slot in event.get('timeSlots', []) or []:
                if slot.get('day'): days.add(slot['day'])
                if slot.get('semester'): semesters.add(slot['semester'])

        course_copy['summary'] = {
            'lecturers': list(lecturers),
            'categories': list(categories),
            'days': list(days),
            'semesters': list(semesters),
            'events_count': len(course_copy.get('events', []))
        }

        return {"success": True, "course": course_copy}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("course_details_failed", course_id=course_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@courses_router.get("/search")
async def search_courses(
    q: str = "", 
    limit: int = 20, 
    semester: Optional[str] = None,
    user: Dict = Depends(get_current_user)
):
    cache = load_courses_data()
    all_courses = cache.get('courses', [])
    query = q.strip().lower()
    
    results = []
    for course in all_courses:
        if not query or query in course['name'].lower() or query in str(course['id']):
            if semester:
                if not any(any(s.get('semester') == semester for s in e.get('timeSlots', [])) for e in course.get('events', [])):
                    continue
            results.append(course)
            if len(results) >= limit:
                break
                
    return {"success": True, "courses": results}

@courses_router.post("/conflicts")
async def check_conflicts(data: Dict[str, Any], user: Dict = Depends(get_current_user)):
    # Placeholder for conflict logic
    return {"success": True, "conflicts": []}

@courses_router.get("/filters")
async def get_filters(user: Dict = Depends(get_current_user)):
    # Placeholder for filters
    return {"success": True, "filters": {}}
