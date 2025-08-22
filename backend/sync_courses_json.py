#!/usr/bin/env python3
"""
Database to JSON Sync Script

This script synchronizes the courses.json file with the latest data from the Supabase database.
It can be run manually or scheduled as a cron job for automatic updates.

Usage:
    python sync_courses_json.py
    
Scheduling (example cron entry for every 6 hours):
    0 */6 * * * cd /path/to/backend && python sync_courses_json.py >> /var/log/course-sync.log 2>&1
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from api.supabase_courses import get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/course-sync.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

def sync_courses_to_json():
    """
    Sync courses from Supabase database to JSON file
    Returns True if successful, False otherwise
    """
    try:
        logger.info("Starting courses synchronization from database to JSON...")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Fetch all active courses with full details
        logger.info("Fetching courses from Supabase...")
        result = supabase.table('courses').select('''
            id, name, english_name, description, credits, level,
            events:course_events(
                id, group_number, max_students, enrolled_students, notes,
                category:course_categories(name),
                location:locations(full_name),
                lecturers:course_event_lecturers(
                    lecturer:lecturers(name)
                ),
                time_slots:time_slots(
                    start_time, end_time, specific_date, is_cancelled,
                    day:days_of_week(name_english),
                    semester:semesters(code, name, academic_year)
                )
            )
        ''').eq('is_active', True).execute()
        
        courses_data = result.data
        logger.info(f"Fetched {len(courses_data)} courses from database")
        
        # Transform to courses.json format
        logger.info("Transforming data to JSON format...")
        courses_json = {'courses': []}
        
        for course in courses_data:
            course_entry = {
                'id': course['id'],
                'name': course['name'],
                'english_name': course.get('english_name'),
                'description': course.get('description'),
                'credits': course.get('credits'),
                'level': course.get('level'),
                'events': []
            }
            
            # Process events
            for event in course.get('events', []):
                # Extract lecturers
                lecturers = []
                for lec_assoc in event.get('lecturers', []):
                    lecturers.append(lec_assoc['lecturer']['name'])
                
                event_entry = {
                    'id': f"{course['id']}-{event['id']}",
                    'group_number': event.get('group_number'),
                    'category': event.get('category', {}).get('name', ''),
                    'lecturers': lecturers,
                    'location': event.get('location', {}).get('full_name', '') if event.get('location') else '',
                    'max_students': event.get('max_students'),
                    'enrolled_students': event.get('enrolled_students'),
                    'notes': event.get('notes'),
                    'timeSlots': []
                }
                
                # Process time slots
                for slot in event.get('time_slots', []):
                    if slot.get('is_cancelled', False):
                        continue  # Skip cancelled slots
                    
                    slot_entry = {
                        'day': slot.get('day', {}).get('name_english', ''),
                        'from': slot.get('start_time', ''),
                        'to': slot.get('end_time', ''),
                        'semester': slot.get('semester', {}).get('code', ''),
                        'specific_date': slot.get('specific_date')
                    }
                    event_entry['timeSlots'].append(slot_entry)
                
                # Only include events that have time slots
                if event_entry['timeSlots']:
                    course_entry['events'].append(event_entry)
            
            # Only include courses that have events
            if course_entry['events']:
                courses_json['courses'].append(course_entry)
        
        # Write to JSON file
        courses_path = os.path.join(backend_dir, 'integrations', 'courses.json')
        backup_path = f"{courses_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup of existing file
        if os.path.exists(courses_path):
            logger.info(f"Creating backup: {backup_path}")
            with open(courses_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        
        # Write new JSON file
        logger.info(f"Writing updated courses.json with {len(courses_json['courses'])} courses...")
        with open(courses_path, 'w', encoding='utf-8') as f:
            json.dump(courses_json, f, ensure_ascii=False, indent=2)
        
        # Verify the written file
        with open(courses_path, 'r', encoding='utf-8') as f:
            verification = json.load(f)
            
        logger.info(f"✅ Successfully synchronized {len(verification['courses'])} courses to JSON")
        logger.info(f"📄 File size: {os.path.getsize(courses_path) / 1024:.1f} KB")
        
        # Clean up old backups (keep only last 5)
        backup_pattern = f"{courses_path}.backup."
        backup_files = [f for f in os.listdir(os.path.dirname(courses_path)) if f.startswith(os.path.basename(backup_pattern))]
        backup_files.sort(reverse=True)
        
        for old_backup in backup_files[5:]:  # Keep only 5 most recent
            old_backup_path = os.path.join(os.path.dirname(courses_path), old_backup)
            os.remove(old_backup_path)
            logger.info(f"🗑️  Removed old backup: {old_backup}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error synchronizing courses: {e}")
        logger.error(f"Traceback: {str(e.__class__.__name__)}: {str(e)}")
        return False

def get_sync_statistics():
    """Get statistics about the current JSON file"""
    try:
        courses_path = os.path.join(backend_dir, 'integrations', 'courses.json')
        
        if not os.path.exists(courses_path):
            return {"error": "courses.json not found"}
        
        # Get file stats
        stat = os.stat(courses_path)
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        file_size_kb = stat.st_size / 1024
        
        # Load and count courses
        with open(courses_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        courses = data.get('courses', [])
        total_events = sum(len(course.get('events', [])) for course in courses)
        total_time_slots = sum(
            len(event.get('timeSlots', [])) 
            for course in courses 
            for event in course.get('events', [])
        )
        
        # Semester distribution
        semesters = {}
        for course in courses:
            for event in course.get('events', []):
                for slot in event.get('timeSlots', []):
                    semester = slot.get('semester', 'Unknown')
                    semesters[semester] = semesters.get(semester, 0) + 1
        
        return {
            "file_path": courses_path,
            "last_modified": modified_time.isoformat(),
            "age_hours": (datetime.now() - modified_time).total_seconds() / 3600,
            "file_size_kb": file_size_kb,
            "courses_count": len(courses),
            "events_count": total_events,
            "time_slots_count": total_time_slots,
            "semester_distribution": semesters
        }
        
    except Exception as e:
        logger.error(f"Error getting sync statistics: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🔄 Course Scheduler - Database to JSON Sync")
    print("=" * 50)
    
    # Check if we should just show stats
    if len(sys.argv) > 1 and sys.argv[1] in ['--stats', '-s']:
        stats = get_sync_statistics()
        print("📊 Current JSON File Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        sys.exit(0)
    
    # Show current stats
    print("\n📊 Before sync:")
    stats = get_sync_statistics()
    if 'error' not in stats:
        print(f"   Last modified: {stats['last_modified']}")
        print(f"   Age: {stats['age_hours']:.1f} hours")
        print(f"   Courses: {stats['courses_count']}")
        print(f"   File size: {stats['file_size_kb']:.1f} KB")
    else:
        print(f"   {stats['error']}")
    
    # Perform sync
    print("\n🔄 Starting synchronization...")
    success = sync_courses_to_json()
    
    # Show results
    print("\n📊 After sync:")
    stats = get_sync_statistics()
    if 'error' not in stats:
        print(f"   Courses: {stats['courses_count']}")
        print(f"   Events: {stats['events_count']}")
        print(f"   Time slots: {stats['time_slots_count']}")
        print(f"   File size: {stats['file_size_kb']:.1f} KB")
        print(f"   Semester distribution: {stats['semester_distribution']}")
    
    if success:
        print("\n✅ Synchronization completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Synchronization failed!")
        sys.exit(1)
