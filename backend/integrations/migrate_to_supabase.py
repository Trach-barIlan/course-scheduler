import json
import asyncio
from supabase import create_client, Client
import os
from typing import Dict, List, Optional

# Try to load .env file from parent directory (backend folder)
try:
    from dotenv import load_dotenv
    # Load .env from parent directory
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")  # Service role key bypasses RLS

# Validate credentials
if not SUPABASE_URL or SUPABASE_URL == "your-supabase-url":
    print("❌ Error: SUPABASE_URL not set in environment variables")
    print("Please check your .env file in the backend directory")
    exit(1)

# For migration, prefer service key which bypasses RLS
SUPABASE_KEY = SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY

if not SUPABASE_KEY or SUPABASE_KEY == "your-supabase-anon-key":
    print("❌ Error: Neither SUPABASE_SERVICE_KEY nor SUPABASE_ANON_KEY set in environment variables") 
    print("Please check your .env file in the backend directory")
    print("For migration, SUPABASE_SERVICE_KEY is recommended to bypass Row Level Security")
    exit(1)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    key_type = "service role" if SUPABASE_SERVICE_KEY else "anon"
    print(f"✅ Successfully connected to Supabase using {key_type} key")
    
    if not SUPABASE_SERVICE_KEY:
        print("⚠️  Using anon key - may encounter Row Level Security restrictions")
        print("   Consider adding SUPABASE_SERVICE_KEY to your .env file for migrations")
    
except Exception as e:
    print(f"❌ Error connecting to Supabase: {e}")
    print("Please check your credentials in the .env file")
    exit(1)

def map_day_to_english(hebrew_day: str) -> str:
    """Map Hebrew day names to English"""
    day_mapping = {
        'ראשון': 'Sunday',
        'שני': 'Monday', 
        'שלישי': 'Tuesday',
        'רביעי': 'Wednesday',
        'חמישי': 'Thursday',
        'שישי': 'Friday',
        'שבת': 'Saturday'
    }
    return day_mapping.get(hebrew_day, hebrew_day)

def map_semester_code(semester_text: str) -> str:
    """Map semester text to code"""
    if 'א' in semester_text:
        return 'A'
    elif 'ב' in semester_text:
        return 'B'
    elif 'קיץ' in semester_text or 'summer' in semester_text.lower():
        return 'SUMMER'
    return 'A'  # Default

async def get_or_create_department(course_id: str, university_id: int) -> int:
    """Determine department from course ID and create if needed"""
    
    # Extract department code from course ID (first 2-3 digits typically)
    dept_code = course_id[:2] if len(course_id) >= 2 else "00"
    
    # Department name mapping based on common patterns
    dept_mapping = {
        "01": {"name": "מקרא", "description": "חוג למקרא"},
        "02": {"name": "תלמוד", "description": "חוג לתלמוד"}, 
        "03": {"name": "מחשבת ישראל", "description": "חוג למחשבת ישראל"},
        "04": {"name": "תולדות ישראל", "description": "חוג לתולדות ישראל"},
        "89": {"name": "מדעי המחשב", "description": "החוג למדעי המחשב"},
        "891": {"name": "מתמטיקה", "description": "החוג למתמטיקה"},
        "892": {"name": "סטטיסטיקה", "description": "החוג לסטטיסטיקה"},
        "893": {"name": "מדעי המחשב מתקדם", "description": "חוג מדעי המחשב - תארים מתקדמים"},
        "894": {"name": "בינה מלאכותית", "description": "חוג לבינה מלאכותית"},
        "895": {"name": "הנדסת תוכנה", "description": "חוג להנדסת תוכנה"},
        "896": {"name": "גרפיקה וחזון מחשב", "description": "חוג לגרפיקה ממוחשבת וחזון מחשב"}
    }
    
    # Try exact match first, then fallback to first 2 digits
    dept_info = dept_mapping.get(dept_code)
    if not dept_info and len(dept_code) > 2:
        dept_info = dept_mapping.get(dept_code[:2])
    
    if not dept_info:
        dept_info = {"name": f"חוג {dept_code}", "description": f"חוג עם קוד {dept_code}"}
    
    # Check if department exists
    existing_dept = supabase.table('departments').select('id').eq('university_id', university_id).eq('code', dept_code).execute()
    
    if existing_dept.data:
        return existing_dept.data[0]['id']
    
    # Create new department
    new_dept = supabase.table('departments').insert({
        'university_id': university_id,
        'code': dept_code,
        'name': dept_info['name'],
        'description': dept_info['description']
    }).execute()
    
    return new_dept.data[0]['id']

async def migrate_courses_to_supabase():
    """Migrate courses data from JSON to enhanced Supabase schema"""
    
    print("Starting enhanced migration to Supabase...")
    
    # Read the JSON file
    try:
        with open('courses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: courses.json file not found!")
        return
    
    courses_data = data.get('courses', [])
    print(f"Found {len(courses_data)} courses to migrate")
    
    # Get university ID (should be 1 for Bar-Ilan)
    university_result = supabase.table('universities').select('id').eq('code', 'BIU').execute()
    if not university_result.data:
        print("Error: Bar-Ilan University not found in database!")
        return
    
    university_id = university_result.data[0]['id']
    print(f"Using university ID: {university_id}")
    
    # Get category mappings
    categories_result = supabase.table('course_categories').select('id, name').execute()
    category_name_to_id = {cat['name']: cat['id'] for cat in categories_result.data}
    
    # Get semester mappings  
    semesters_result = supabase.table('semesters').select('id, code').eq('university_id', university_id).execute()
    semester_code_to_id = {sem['code']: sem['id'] for sem in semesters_result.data}
    
    # Get day mappings
    days_result = supabase.table('days_of_week').select('id, name_english').execute()
    day_name_to_id = {day['name_english']: day['id'] for day in days_result.data}
    
    # Process lecturers first
    print("Processing lecturers...")
    lecturers_set = set()
    for course in courses_data:
        for event in course['events']:
            for lecturer in event.get('lecturers', []):
                if lecturer.strip():
                    lecturers_set.add(lecturer.strip())
    
    print(f"Found {len(lecturers_set)} unique lecturers")
    
    # Insert lecturers in batches
    lecturers_data = []
    for lecturer_name in lecturers_set:
        # Extract title if present
        title = ""
        name = lecturer_name
        if lecturer_name.startswith(('ד"ר', 'פרופ׳', 'מר', 'גב׳')):
            parts = lecturer_name.split(' ', 1)
            if len(parts) > 1:
                title = parts[0]
                name = parts[1]
        
        lecturers_data.append({
            'university_id': university_id,
            'name': lecturer_name,  # Keep full name for uniqueness
            'title': title
        })
    
    batch_size = 100
    for i in range(0, len(lecturers_data), batch_size):
        batch = lecturers_data[i:i+batch_size]
        try:
            result = supabase.table('lecturers').upsert(batch, on_conflict='university_id,name,email').execute()
            print(f"Processed lecturers batch {i//batch_size + 1}/{(len(lecturers_data) + batch_size - 1)//batch_size}")
        except Exception as e:
            print(f"Error processing lecturers batch {i//batch_size + 1}: {e}")
    
    # Get lecturer ID mappings
    lecturers_result = supabase.table('lecturers').select('id, name').eq('university_id', university_id).execute()
    lecturer_name_to_id = {lecturer['name']: lecturer['id'] for lecturer in lecturers_result.data}
    
    # Process courses and their components
    print("Processing courses...")
    
    courses_to_insert = []
    events_to_insert = []
    event_lecturers_to_insert = []
    time_slots_to_insert = []
    
    processed_courses = 0
    
    for course in courses_data:
        try:
            # Get or create department
            department_id = await get_or_create_department(course['id'], university_id)
            
            # Prepare course data
            course_data = {
                'id': course['id'],
                'university_id': university_id,
                'department_id': department_id,
                'name': course['name'],
                'academic_year': '2024-2025',  # Current academic year
                'is_active': True,
                'additional_properties': {}
            }
            courses_to_insert.append(course_data)
            
            # Process events for this course
            for event in course.get('events', []):
                # Get category ID
                category_name = event.get('category', 'הרצאה')
                category_id = category_name_to_id.get(category_name)
                if not category_id:
                    # Default to first category if not found
                    category_id = list(category_name_to_id.values())[0]
                
                # Extract group number from event ID if present
                group_number = None
                if '-' in event['id']:
                    parts = event['id'].split('-')
                    if len(parts) >= 2:
                        group_number = parts[1]
                
                event_data = {
                    'id': event['id'],
                    'course_id': course['id'],
                    'category_id': category_id,
                    'group_number': group_number,
                    'is_active': True,
                    'additional_properties': {}
                }
                events_to_insert.append(event_data)
                
                # Process lecturer associations
                for lecturer_name in event.get('lecturers', []):
                    if lecturer_name.strip() and lecturer_name.strip() in lecturer_name_to_id:
                        event_lecturer_data = {
                            'course_event_id': event['id'],
                            'lecturer_id': lecturer_name_to_id[lecturer_name.strip()],
                            'role': 'instructor',
                            'is_primary': True
                        }
                        event_lecturers_to_insert.append(event_lecturer_data)
                
                # Process time slots
                for time_slot in event.get('timeSlots', []):
                    # Map day name
                    day_english = map_day_to_english(time_slot.get('day', ''))
                    day_id = day_name_to_id.get(day_english)
                    
                    # Map semester
                    semester_code = map_semester_code(time_slot.get('semester', 'A'))
                    semester_id = semester_code_to_id.get(semester_code)
                    
                    if day_id and semester_id:
                        time_slot_data = {
                            'course_event_id': event['id'],
                            'semester_id': semester_id,
                            'day_of_week_id': day_id,
                            'start_time': time_slot.get('from', ''),
                            'end_time': time_slot.get('to', ''),
                            'is_cancelled': False,
                            'additional_properties': {}
                        }
                        time_slots_to_insert.append(time_slot_data)
            
            processed_courses += 1
            if processed_courses % 100 == 0:
                print(f"Processed {processed_courses}/{len(courses_data)} courses...")
                
        except Exception as e:
            print(f"Error processing course {course.get('id', 'unknown')}: {e}")
    
    print(f"Prepared {len(courses_to_insert)} courses, {len(events_to_insert)} events, {len(time_slots_to_insert)} time slots")
    
    # Insert all data in batches
    print("Inserting courses...")
    for i in range(0, len(courses_to_insert), batch_size):
        batch = courses_to_insert[i:i+batch_size]
        try:
            result = supabase.table('courses').upsert(batch, on_conflict='id').execute()
            print(f"Inserted courses batch {i//batch_size + 1}/{(len(courses_to_insert) + batch_size - 1)//batch_size}")
        except Exception as e:
            print(f"Error inserting courses batch {i//batch_size + 1}: {e}")
    
    print("Inserting course events...")
    for i in range(0, len(events_to_insert), batch_size):
        batch = events_to_insert[i:i+batch_size]
        try:
            result = supabase.table('course_events').upsert(batch, on_conflict='id').execute()
            print(f"Inserted events batch {i//batch_size + 1}/{(len(events_to_insert) + batch_size - 1)//batch_size}")
        except Exception as e:
            print(f"Error inserting events batch {i//batch_size + 1}: {e}")
    
    print("Inserting event-lecturer associations...")
    for i in range(0, len(event_lecturers_to_insert), batch_size):
        batch = event_lecturers_to_insert[i:i+batch_size]
        try:
            result = supabase.table('course_event_lecturers').upsert(batch).execute()
            print(f"Inserted event-lecturers batch {i//batch_size + 1}/{(len(event_lecturers_to_insert) + batch_size - 1)//batch_size}")
        except Exception as e:
            print(f"Error inserting event-lecturers batch {i//batch_size + 1}: {e}")
    
    print("Inserting time slots...")
    for i in range(0, len(time_slots_to_insert), batch_size):
        batch = time_slots_to_insert[i:i+batch_size]
        try:
            result = supabase.table('time_slots').insert(batch).execute()
            print(f"Inserted time slots batch {i//batch_size + 1}/{(len(time_slots_to_insert) + batch_size - 1)//batch_size}")
        except Exception as e:
            print(f"Error inserting time slots batch {i//batch_size + 1}: {e}")
    
    print("\n🎉 Enhanced migration completed successfully!")
    print(f"✅ Migrated {len(courses_to_insert)} courses")
    print(f"✅ Migrated {len(events_to_insert)} course events") 
    print(f"✅ Migrated {len(lecturers_data)} lecturers")
    print(f"✅ Migrated {len(time_slots_to_insert)} time slots")

if __name__ == "__main__":
    asyncio.run(migrate_courses_to_supabase())
