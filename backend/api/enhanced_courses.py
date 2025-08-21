"""
Enhanced Courses API with Supabase Database
Supports the new normalized schema with room for expansion
"""

from supabase import create_client, Client
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, time
import json

class CoursesAPI:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    async def search_courses(
        self, 
        query: Optional[str] = None,
        department_id: Optional[int] = None,
        category_id: Optional[int] = None,
        level: Optional[str] = None,
        has_time_slots: bool = True,
        academic_year: str = "2024-2025",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Advanced course search with multiple filters
        """
        
        # Base query with joins
        query_builder = (
            self.supabase
            .table('courses')
            .select('''
                id, name, english_name, description, credits, level, language,
                university:universities(name, code),
                department:departments(name, code, description),
                events:course_events(
                    id, group_number, max_students, enrolled_students, is_online, notes,
                    category:course_categories(name, description),
                    location:locations(full_name, building_name, room_number, capacity),
                    lecturers:course_event_lecturers(
                        role, is_primary,
                        lecturer:lecturers(name, title, email, office_location)
                    ),
                    time_slots:time_slots(
                        start_time, end_time, specific_date, is_cancelled,
                        semester:semesters(name, code, academic_year),
                        day:days_of_week(name_hebrew, name_english, day_number)
                    )
                )
            ''')
            .eq('is_active', True)
            .eq('academic_year', academic_year)
        )
        
        # Apply filters
        if department_id:
            query_builder = query_builder.eq('department_id', department_id)
        
        if level:
            query_builder = query_builder.eq('level', level)
        
        # Text search (supports both Hebrew and English)
        if query:
            query_builder = query_builder.or_(
                f'name.ilike.%{query}%,english_name.ilike.%{query}%'
            )
        
        # Pagination
        query_builder = query_builder.range(offset, offset + limit - 1)
        
        try:
            result = query_builder.execute()
            
            courses = result.data
            
            # Filter courses with time slots if requested
            if has_time_slots:
                courses = [
                    course for course in courses
                    if any(
                        event.get('time_slots', []) 
                        for event in course.get('events', [])
                    )
                ]
            
            # Filter by category if specified
            if category_id:
                courses = [
                    course for course in courses
                    if any(
                        event.get('category', {}).get('id') == category_id
                        for event in course.get('events', [])
                    )
                ]
            
            return {
                "courses": courses,
                "total": len(courses),
                "offset": offset,
                "limit": limit
            }
            
        except Exception as e:
            raise Exception(f"Error searching courses: {str(e)}")
    
    async def get_course_by_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed course information by ID
        """
        try:
            result = (
                self.supabase
                .table('courses')
                .select('''
                    *, 
                    university:universities(*),
                    department:departments(*),
                    events:course_events(
                        *,
                        category:course_categories(*),
                        location:locations(*),
                        lecturers:course_event_lecturers(
                            *,
                            lecturer:lecturers(*)
                        ),
                        time_slots:time_slots(
                            *,
                            semester:semesters(*),
                            day:days_of_week(*)
                        )
                    ),
                    materials:course_materials(*),
                    prerequisites:course_prerequisites(
                        *,
                        prerequisite:courses!course_prerequisites_prerequisite_course_id_fkey(id, name)
                    )
                ''')
                .eq('id', course_id)
                .eq('is_active', True)
                .execute()
            )
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            raise Exception(f"Error getting course {course_id}: {str(e)}")
    
    async def get_departments(self, university_code: str = "BIU") -> List[Dict[str, Any]]:
        """
        Get all departments for a university
        """
        try:
            result = (
                self.supabase
                .table('departments')
                .select('*, university:universities(name, code)')
                .eq('universities.code', university_code)
                .execute()
            )
            
            return result.data
            
        except Exception as e:
            raise Exception(f"Error getting departments: {str(e)}")
    
    async def get_lecturers(
        self, 
        department_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get lecturers with optional filters
        """
        try:
            query_builder = (
                self.supabase
                .table('lecturers')
                .select('*, department:departments(name)')
                .eq('is_active', True)
            )
            
            if department_id:
                query_builder = query_builder.eq('department_id', department_id)
            
            if search:
                query_builder = query_builder.ilike('name', f'%{search}%')
            
            result = query_builder.execute()
            return result.data
            
        except Exception as e:
            raise Exception(f"Error getting lecturers: {str(e)}")
    
    async def get_schedule_conflicts(
        self, 
        course_event_ids: List[str],
        semester_code: str = "A"
    ) -> List[Dict[str, Any]]:
        """
        Check for time conflicts between selected course events
        """
        try:
            # Get time slots for the selected events
            result = (
                self.supabase
                .table('time_slots')
                .select('''
                    *,
                    course_event:course_events(
                        id, course_id,
                        course:courses(name)
                    ),
                    day:days_of_week(name_english, day_number),
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
            for i, slot1 in enumerate(time_slots):
                for slot2 in time_slots[i+1:]:
                    # Same day check
                    if slot1['day']['day_number'] == slot2['day']['day_number']:
                        # Time overlap check
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
                                'day': slot1['day']['name_english'],
                                'time1': f"{slot1['start_time']}-{slot1['end_time']}",
                                'time2': f"{slot2['start_time']}-{slot2['end_time']}"
                            })
            
            return conflicts
            
        except Exception as e:
            raise Exception(f"Error checking conflicts: {str(e)}")
    
    async def get_course_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the course database
        """
        try:
            # Get counts for various entities
            stats = {}
            
            # Course counts
            courses_result = self.supabase.table('courses').select('id', count='exact').eq('is_active', True).execute()
            stats['total_courses'] = courses_result.count
            
            # Department counts
            dept_result = self.supabase.table('departments').select('id', count='exact').execute()
            stats['total_departments'] = dept_result.count
            
            # Lecturer counts
            lecturer_result = self.supabase.table('lecturers').select('id', count='exact').eq('is_active', True).execute()
            stats['total_lecturers'] = lecturer_result.count
            
            # Course events counts
            events_result = self.supabase.table('course_events').select('id', count='exact').eq('is_active', True).execute()
            stats['total_course_events'] = events_result.count
            
            # Time slots counts
            slots_result = self.supabase.table('time_slots').select('id', count='exact').eq('is_cancelled', False).execute()
            stats['total_time_slots'] = slots_result.count
            
            # Courses by department
            dept_courses = (
                self.supabase
                .table('courses')
                .select('department:departments(name), id')
                .eq('is_active', True)
                .execute()
            )
            
            dept_counts = {}
            for course in dept_courses.data:
                dept_name = course['department']['name']
                dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
            
            stats['courses_by_department'] = dept_counts
            
            # Courses by level
            level_result = (
                self.supabase
                .table('courses')
                .select('level')
                .eq('is_active', True)
                .execute()
            )
            
            level_counts = {}
            for course in level_result.data:
                level = course.get('level') or 'Unknown'
                level_counts[level] = level_counts.get(level, 0) + 1
            
            stats['courses_by_level'] = level_counts
            
            return stats
            
        except Exception as e:
            raise Exception(f"Error getting statistics: {str(e)}")
    
    async def add_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new course to the database
        """
        try:
            result = (
                self.supabase
                .table('courses')
                .insert(course_data)
                .execute()
            )
            
            return result.data[0]
            
        except Exception as e:
            raise Exception(f"Error adding course: {str(e)}")
    
    async def update_course(self, course_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update course information
        """
        try:
            result = (
                self.supabase
                .table('courses')
                .update(updates)
                .eq('id', course_id)
                .execute()
            )
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            raise Exception(f"Error updating course {course_id}: {str(e)}")


# Usage example and helper functions
async def migrate_and_test():
    """
    Example usage of the enhanced API
    """
    api = CoursesAPI()
    
    # Search for computer science courses
    cs_courses = await api.search_courses(
        query="מדעי המחשב",
        has_time_slots=True,
        limit=10
    )
    
    print(f"Found {cs_courses['total']} CS courses")
    
    # Get course details
    if cs_courses['courses']:
        first_course = cs_courses['courses'][0]
        course_details = await api.get_course_by_id(first_course['id'])
        print(f"Course details: {course_details['name']}")
    
    # Get statistics
    stats = await api.get_course_statistics()
    print(f"Database statistics: {stats}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_and_test())
