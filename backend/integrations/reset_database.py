#!/usr/bin/env python3
"""
Complete database reset - delete all course data and re-upload from JSON
This will ensure clean data without duplicates
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('/Users/yonitrach/Desktop/RandomProj/course-scheduler/backend/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def map_day_to_id(hebrew_day):
    """Map Hebrew day names to day IDs"""
    day_mapping = {
        'ראשון': 1,
        'שני': 2, 
        'שלישי': 3,
        'רביעי': 4,
        'חמישי': 5,
        'שישי': 6,
        'שבת': 7,
        'Sunday': 1,
        'Monday': 2,
        'Tuesday': 3,
        'Wednesday': 4,
        'Thursday': 5,
        'Friday': 6,
        'Saturday': 7
    }
    return day_mapping.get(hebrew_day, 3)  # Default to Tuesday

def map_semester_to_id(semester_code):
    """Map semester codes to IDs"""
    semester_mapping = {
        'A': 1,
        'B': 2,
        'SUMMER': 3,
        'קיץ': 3
    }
    return semester_mapping.get(semester_code, 1)  # Default to semester A

def map_category_to_id(category_name):
    """Map Hebrew category names to IDs"""
    category_mapping = {
        'הרצאה': 1,
        'תרגיל': 2,
        'מעבדה': 3,
        'סמינר': 4,
        'פרויקט': 5,
        'lecture': 1,
        'practice': 2,
        'lab': 3,
        'seminar': 4,
        'project': 5
    }
    return category_mapping.get(category_name, 1)  # Default to lecture

def reset_and_reload_courses():
    """Delete all course data and reload from JSON"""
    
    print("🗑️  COMPLETE DATABASE RESET AND RELOAD")
    print("=" * 50)
    print("⚠️  WARNING: This will delete ALL course data in the database!")
    print("⚠️  Make sure you have a backup if needed!")
    
    response = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Operation cancelled")
        return
    
    # Step 1: Load JSON data
    print("\n📄 Loading JSON data...")
    try:
        with open('courses.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        courses_list = json_data.get('courses', [])
        print(f"✅ Loaded {len(courses_list)} courses from JSON")
        
        # Count total events and time slots
        total_events = 0
        total_slots = 0
        for course in courses_list:
            course_events = course.get('events', [])
            total_events += len(course_events)
            for event in course_events:
                total_slots += len(event.get('timeSlots', []))
        
        print(f"📊 Total events to import: {total_events}")
        print(f"📊 Total time slots to import: {total_slots}")
        
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return
    
    # Step 2: Delete existing data
    print(f"\n🗑️  Deleting existing database data...")
    try:
        # Delete in correct order (foreign key constraints)
        print("   Deleting time_slots...")
        supabase.table('time_slots').delete().neq('id', 0).execute()
        
        print("   Deleting course_events...")
        supabase.table('course_events').delete().neq('id', '').execute()
        
        print("   Deleting courses...")
        supabase.table('courses').delete().neq('id', '').execute()
        
        print("✅ All course data deleted")
        
    except Exception as e:
        print(f"❌ Error deleting data: {e}")
        return
    
    # Step 3: Insert courses
    print(f"\n📥 Inserting courses...")
    courses_batch = []
    
    for course in courses_list:
        course_data = {
            'id': course['id'],
            'university_id': 1,  # Bar-Ilan
            'department_id': 376,  # Default department
            'name': course['name'],
            'english_name': None,
            'description': None,
            'credits': None,
            'prerequisites': None,
            'level': None,
            'language': 'hebrew',
            'syllabus_url': None,
            'is_active': True,
            'academic_year': '2024-2025',
            'additional_properties': {}
        }
        courses_batch.append(course_data)
    
    try:
        # Insert courses in batches
        batch_size = 100
        courses_inserted = 0
        
        for i in range(0, len(courses_batch), batch_size):
            batch = courses_batch[i:i + batch_size]
            supabase.table('courses').insert(batch).execute()
            courses_inserted += len(batch)
            print(f"   ✅ Inserted courses batch: {courses_inserted}/{len(courses_batch)}")
        
        print(f"✅ Inserted {courses_inserted} courses")
        
    except Exception as e:
        print(f"❌ Error inserting courses: {e}")
        return
    
    # Step 4: Insert course events
    print(f"\n📥 Inserting course events...")
    events_batch = []
    
    for course in courses_list:
        for event in course.get('events', []):
            event_data = {
                'id': event['id'],
                'course_id': course['id'],
                'category_id': map_category_to_id(event.get('category', 'הרצאה')),
                'group_number': '01',
                'max_students': None,
                'enrolled_students': 0,
                'location_id': None,
                'recurrence_pattern': None,
                'is_online': False,
                'meeting_link': None,
                'notes': None,
                'additional_properties': {},
                'is_active': True
            }
            events_batch.append(event_data)
    
    try:
        # Insert events in batches
        events_inserted = 0
        
        for i in range(0, len(events_batch), batch_size):
            batch = events_batch[i:i + batch_size]
            supabase.table('course_events').insert(batch).execute()
            events_inserted += len(batch)
            print(f"   ✅ Inserted events batch: {events_inserted}/{len(events_batch)}")
        
        print(f"✅ Inserted {events_inserted} course events")
        
    except Exception as e:
        print(f"❌ Error inserting events: {e}")
        return
    
    # Step 5: Insert time slots
    print(f"\n📥 Inserting time slots...")
    slots_batch = []
    
    for course in courses_list:
        for event in course.get('events', []):
            for time_slot in event.get('timeSlots', []):
                slot_data = {
                    'course_event_id': event['id'],
                    'semester_id': map_semester_to_id(time_slot.get('semester', 'A')),
                    'day_of_week_id': map_day_to_id(time_slot.get('day', 'Tuesday')),
                    'start_time': time_slot.get('from', '09:00:00'),
                    'end_time': time_slot.get('to', '12:00:00'),
                    'specific_date': None,
                    'is_cancelled': False,
                    'cancellation_reason': None,
                    'alternative_location_id': None,
                    'additional_properties': {}
                }
                slots_batch.append(slot_data)
    
    try:
        # Insert time slots in batches
        slots_inserted = 0
        
        for i in range(0, len(slots_batch), batch_size):
            batch = slots_batch[i:i + batch_size]
            supabase.table('time_slots').insert(batch).execute()
            slots_inserted += len(batch)
            print(f"   ✅ Inserted slots batch: {slots_inserted}/{len(slots_batch)}")
        
        print(f"✅ Inserted {slots_inserted} time slots")
        
    except Exception as e:
        print(f"❌ Error inserting time slots: {e}")
        return
    
    # Step 6: Verify the import
    print(f"\n🔍 Verifying import...")
    try:
        # Count what we imported
        courses_count = supabase.table('courses').select('id', count='exact').execute()
        events_count = supabase.table('course_events').select('id', count='exact').execute()
        slots_count = supabase.table('time_slots').select('id', count='exact').execute()
        
        print(f"📊 Database now contains:")
        print(f"   Courses: {courses_count.count}")
        print(f"   Events: {events_count.count}")
        print(f"   Time slots: {slots_count.count}")
        
        # Check course 893312 specifically
        course_893312_slots = supabase.table('time_slots').select('semester_id').eq('course_event_id', '893312-01-0').execute()
        if course_893312_slots.data:
            semester_counts = {}
            for slot in course_893312_slots.data:
                sem_id = slot['semester_id']
                sem_name = 'A' if sem_id == 1 else 'B' if sem_id == 2 else f'ID-{sem_id}'
                semester_counts[sem_name] = semester_counts.get(sem_name, 0) + 1
            
            print(f"✅ Course 893312 verification:")
            for sem, count in semester_counts.items():
                print(f"   Semester {sem}: {count} slots")
        
        print(f"\n🎉 DATABASE RESET AND RELOAD COMPLETED!")
        print(f"✅ All duplicates removed")
        print(f"✅ Clean data imported from JSON")
        print(f"✅ Semester filtering should now work correctly")
        
    except Exception as e:
        print(f"❌ Error verifying import: {e}")

if __name__ == "__main__":
    reset_and_reload_courses()
