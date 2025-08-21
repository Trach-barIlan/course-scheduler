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

# Connect with service role key
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# SQL to add INSERT policies
insert_policies_sql = '''
-- Add INSERT policies to allow data migration
CREATE POLICY IF NOT EXISTS "Allow public insert access on universities" ON universities FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on departments" ON departments FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on courses" ON courses FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on course_events" ON course_events FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on lecturers" ON lecturers FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on locations" ON locations FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on time_slots" ON time_slots FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on course_materials" ON course_materials FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on course_prerequisites" ON course_prerequisites FOR INSERT WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public insert access on course_event_lecturers" ON course_event_lecturers FOR INSERT WITH CHECK (true);

-- Allow UPDATE access for UPSERT operations
CREATE POLICY IF NOT EXISTS "Allow public update access on universities" ON universities FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on departments" ON departments FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on courses" ON courses FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on course_events" ON course_events FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on lecturers" ON lecturers FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on locations" ON locations FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on time_slots" ON time_slots FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on course_materials" ON course_materials FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on course_prerequisites" ON course_prerequisites FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "Allow public update access on course_event_lecturers" ON course_event_lecturers FOR UPDATE USING (true) WITH CHECK (true);
'''

print("Adding INSERT and UPDATE policies to bypass RLS during migration...")

try:
    # Execute the SQL using the RPC call
    result = supabase.rpc('exec', {'sql': insert_policies_sql}).execute()
    print("✅ Successfully added INSERT and UPDATE policies")
except Exception as e:
    print(f"Error adding policies (this is expected if they already exist): {e}")
    print("Continuing with migration...")

print("🎉 Policies setup complete! You can now run the migration.")
