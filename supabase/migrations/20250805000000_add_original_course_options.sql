-- Add original_course_options column to saved_schedules table
-- This will store the original course data with all alternative time slots
-- so users can modify schedules after saving them

ALTER TABLE saved_schedules 
ADD COLUMN original_course_options JSONB DEFAULT '[]'::jsonb;

-- Add comment to explain the purpose of this column
COMMENT ON COLUMN saved_schedules.original_course_options IS 'Original course data with all available time slots for schedule modification';
