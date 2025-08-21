import json
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: Missing Supabase credentials")
    exit(1)

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def load_original_data():
    """Load original courses data from JSON"""
    try:
        with open('courses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both direct array and wrapper object formats
            if isinstance(data, dict) and 'courses' in data:
                return data['courses']
            elif isinstance(data, list):
                return data
            else:
                print(f"⚠️  Unexpected JSON structure: {type(data)}")
                return []
    except Exception as e:
        print(f"❌ Error loading courses.json: {e}")
        return []

def verify_migration():
    """Verify that all data was migrated correctly"""
    print("🔍 Verifying migration results...")
    
    # Load original data
    original_courses = load_original_data()
    print(f"📄 Original JSON file contains: {len(original_courses)} courses")
    
    # Count original events and time slots
    original_events = 0
    original_time_slots = 0
    original_lecturers = set()
    
    for course in original_courses:
        for event in course.get('events', []):
            original_events += 1
            original_time_slots += len(event.get('timeSlots', []))
            for lecturer in event.get('lecturers', []):
                if lecturer.strip():
                    original_lecturers.add(lecturer.strip())
    
    print(f"📊 Original data statistics:")
    print(f"   - Courses: {len(original_courses)}")
    print(f"   - Course Events: {original_events}")
    print(f"   - Unique Lecturers: {len(original_lecturers)}")
    print(f"   - Time Slots: {original_time_slots}")
    
    # Check migrated data in Supabase
    print(f"\n🔍 Checking migrated data in Supabase...")
    
    try:
        # Count courses
        courses_result = supabase.table('courses').select('id', count='exact').execute()
        migrated_courses = courses_result.count
        
        # Count course events
        events_result = supabase.table('course_events').select('id', count='exact').execute()
        migrated_events = events_result.count
        
        # Count lecturers
        lecturers_result = supabase.table('lecturers').select('id', count='exact').execute()
        migrated_lecturers = lecturers_result.count
        
        # Count time slots
        slots_result = supabase.table('time_slots').select('id', count='exact').execute()
        migrated_slots = slots_result.count
        
        print(f"📈 Migrated data statistics:")
        print(f"   - Courses: {migrated_courses}")
        print(f"   - Course Events: {migrated_events}")
        print(f"   - Lecturers: {migrated_lecturers}")
        print(f"   - Time Slots: {migrated_slots}")
        
        # Compare counts
        print(f"\n📊 Migration comparison:")
        courses_match = migrated_courses == len(original_courses)
        events_match = migrated_events == original_events
        lecturers_match = migrated_lecturers == len(original_lecturers)
        slots_match = migrated_slots == original_time_slots
        
        print(f"   - Courses: {'✅' if courses_match else '❌'} ({migrated_courses}/{len(original_courses)})")
        print(f"   - Events: {'✅' if events_match else '❌'} ({migrated_events}/{original_events})")
        print(f"   - Lecturers: {'✅' if lecturers_match else '❌'} ({migrated_lecturers}/{len(original_lecturers)})")
        print(f"   - Time Slots: {'✅' if slots_match else '❌'} ({migrated_slots}/{original_time_slots})")
        
        all_match = courses_match and events_match and lecturers_match and slots_match
        
        if all_match:
            print(f"\n🎉 Perfect migration! All data counts match exactly.")
        else:
            print(f"\n⚠️  Some counts don't match. This could be due to:")
            print(f"   - Duplicate lecturers being merged")
            print(f"   - Invalid/empty time slots being filtered")
            print(f"   - Data cleaning during migration")
        
        # Sample some data to verify structure
        print(f"\n📋 Sample migrated data:")
        
        # Sample course
        sample_course = supabase.table('courses').select('*').limit(1).execute()
        if sample_course.data:
            course = sample_course.data[0]
            print(f"   Sample Course: {course.get('name', 'N/A')} (ID: {course.get('id', 'N/A')})")
        
        # Sample lecturer
        sample_lecturer = supabase.table('lecturers').select('*').limit(1).execute()
        if sample_lecturer.data:
            lecturer = sample_lecturer.data[0]
            print(f"   Sample Lecturer: {lecturer.get('name', 'N/A')} (ID: {lecturer.get('id', 'N/A')})")
        
        # Sample time slot with related data
        sample_slot = supabase.table('time_slots').select('''
            *, 
            course_events(course_id, courses(name)),
            days_of_week(name)
        ''').limit(1).execute()
        if sample_slot.data:
            slot = sample_slot.data[0]
            course_name = slot.get('course_events', {}).get('courses', {}).get('name', 'N/A')
            day_name = slot.get('days_of_week', {}).get('name', 'N/A')
            print(f"   Sample Time Slot: {course_name} on {day_name} ({slot.get('start_time', 'N/A')}-{slot.get('end_time', 'N/A')})")
        
        return all_match
        
    except Exception as e:
        print(f"❌ Error checking Supabase data: {e}")
        return False

def check_database_structure():
    """Check if all required tables exist and have data"""
    print(f"\n🏗️  Checking database structure...")
    
    required_tables = [
        'universities', 'departments', 'courses', 'course_events', 
        'lecturers', 'time_slots', 'course_categories', 'semesters', 'days_of_week'
    ]
    
    for table in required_tables:
        try:
            result = supabase.table(table).select('*', count='exact').limit(1).execute()
            count = result.count
            has_data = len(result.data) > 0
            print(f"   {table}: {'✅' if has_data else '⚠️'} ({count} records)")
        except Exception as e:
            print(f"   {table}: ❌ Error accessing table: {e}")

if __name__ == "__main__":
    print("🔍 Migration Verification Report")
    print("=" * 50)
    
    check_database_structure()
    migration_success = verify_migration()
    
    print("\n" + "=" * 50)
    if migration_success:
        print("🎉 Migration verification completed successfully!")
        print("✅ Your course data has been successfully migrated to Supabase.")
        print("\n💡 Next steps:")
        print("   1. Update your API endpoints to use Supabase instead of JSON")
        print("   2. Test the schedule viewer with the new database backend")
        print("   3. Consider adding more universities and departments")
    else:
        print("⚠️  Migration verification found some discrepancies.")
        print("   The core data is likely migrated, but some counts don't match exactly.")
        print("   This is often normal due to data cleaning and deduplication.")
