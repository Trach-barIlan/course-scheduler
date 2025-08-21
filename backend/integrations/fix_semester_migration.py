#!/usr/bin/env python3
"""
Fix migration script to add missing Semester B data
This will add only the missing Semester B time slots without duplicating existing data
"""

import json
import asyncio
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: Missing Supabase credentials")
    exit(1)

# Connect with service role key
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

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
    semester_text = semester_text.strip().upper()
    
    # Direct mappings for English codes
    if semester_text == 'A':
        return 'A'
    elif semester_text == 'B':
        return 'B'
    elif semester_text in ['SUMMER', 'קיץ']:
        return 'SUMMER'
    
    # Hebrew character mappings  
    if 'א' in semester_text:
        return 'A'
    elif 'ב' in semester_text:
        return 'B'
    elif 'קיץ' in semester_text:
        return 'SUMMER'
    
    return 'A'  # Default

def load_courses_data():
    """Load courses data from JSON"""
    try:
        with open('courses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('courses', [])
    except Exception as e:
        print(f"❌ Error loading courses.json: {e}")
        return []

def fix_semester_migration():
    """Add missing Semester B time slots"""
    print("🔧 Starting Semester B migration fix...")
    
    # Load reference data
    courses_data = load_courses_data()
    print(f"📄 Loaded {len(courses_data)} courses from JSON")
    
    # Get existing semester and day mappings
    try:
        semesters_result = supabase.table('semesters').select('*').execute()
        semester_code_to_id = {sem['code']: sem['id'] for sem in semesters_result.data}
        print(f"📅 Loaded {len(semester_code_to_id)} semesters")
        
        days_result = supabase.table('days_of_week').select('*').execute()
        day_name_to_id = {day['name_english']: day['id'] for day in days_result.data}
        print(f"📆 Loaded {len(day_name_to_id)} days")
        
    except Exception as e:
        print(f"❌ Error loading reference data: {e}")
        return
    
    # Find existing time slots to avoid duplicates
    print("🔍 Checking existing time slots...")
    existing_slots = set()
    try:
        existing_result = supabase.table('time_slots').select('course_event_id, semester_id, day_of_week_id, start_time, end_time').execute()
        for slot in existing_result.data:
            slot_key = (slot['course_event_id'], slot['semester_id'], slot['day_of_week_id'], slot['start_time'], slot['end_time'])
            existing_slots.add(slot_key)
        print(f"📊 Found {len(existing_slots)} existing time slots")
    except Exception as e:
        print(f"❌ Error loading existing slots: {e}")
        return
    
    # Process only Semester B time slots
    new_slots_to_insert = []
    batch_size = 100
    processed_slots = 0
    skipped_slots = 0
    semester_b_count = 0
    
    for course in courses_data:
        for event in course.get('events', []):
            for time_slot in event.get('timeSlots', []):
                semester_code = map_semester_code(time_slot.get('semester', 'A'))
                
                # Only process Semester B slots
                if semester_code != 'B':
                    continue
                
                semester_b_count += 1
                
                # Map day name
                day_english = map_day_to_english(time_slot.get('day', ''))
                day_id = day_name_to_id.get(day_english)
                semester_id = semester_code_to_id.get(semester_code)
                
                if day_id and semester_id:
                    # Create unique key to check for duplicates
                    slot_key = (event['id'], semester_id, day_id, time_slot.get('from', ''), time_slot.get('to', ''))
                    
                    if slot_key in existing_slots:
                        skipped_slots += 1
                        continue
                    
                    time_slot_data = {
                        'course_event_id': event['id'],
                        'semester_id': semester_id,
                        'day_of_week_id': day_id,
                        'start_time': time_slot.get('from', ''),
                        'end_time': time_slot.get('to', ''),
                        'is_cancelled': False,
                        'additional_properties': {}
                    }
                    new_slots_to_insert.append(time_slot_data)
                    processed_slots += 1
                else:
                    print(f"⚠️ Missing mapping for day '{time_slot.get('day')}' or semester '{semester_code}'")
    
    print(f"\n📊 Analysis Results:")
    print(f"   - Semester B slots in JSON: {semester_b_count}")
    print(f"   - New slots to insert: {len(new_slots_to_insert)}")
    print(f"   - Skipped (already exist): {skipped_slots}")
    
    if not new_slots_to_insert:
        print("✅ All Semester B slots already exist in database!")
        return
    
    # Insert new time slots in batches
    print(f"\n🔄 Inserting {len(new_slots_to_insert)} new Semester B time slots...")
    
    for i in range(0, len(new_slots_to_insert), batch_size):
        batch = new_slots_to_insert[i:i+batch_size]
        try:
            result = supabase.table('time_slots').insert(batch).execute()
            batch_num = i//batch_size + 1
            total_batches = (len(new_slots_to_insert) + batch_size - 1) // batch_size
            print(f"   ✅ Inserted batch {batch_num}/{total_batches} ({len(batch)} slots)")
        except Exception as e:
            print(f"   ❌ Error inserting batch {batch_num}: {e}")
    
    print(f"\n🎉 Semester B migration fix completed!")
    print(f"✅ Added {len(new_slots_to_insert)} new time slots for Semester B")
    
    # Verify the fix
    print(f"\n🔍 Verifying fix...")
    try:
        # Count slots by semester
        all_slots = supabase.table('time_slots').select('semester:semesters(code)').limit(2000).execute()
        semester_counts = {}
        for slot in all_slots.data:
            code = slot['semester']['code']
            semester_counts[code] = semester_counts.get(code, 0) + 1
        
        print(f"📊 Updated semester distribution:")
        for code, count in sorted(semester_counts.items()):
            print(f"   - Semester {code}: {count} time slots")
            
        total_result = supabase.table('time_slots').select('id', count='exact').execute()
        print(f"   - Total time slots: {total_result.count}")
        
    except Exception as e:
        print(f"⚠️ Error verifying fix: {e}")

if __name__ == "__main__":
    fix_semester_migration()
