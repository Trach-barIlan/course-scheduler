-- Create courses table in Supabase
CREATE TABLE courses (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create course events table
CREATE TABLE course_events (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    location TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create lecturers table
CREATE TABLE lecturers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create course event lecturers junction table
CREATE TABLE course_event_lecturers (
    course_event_id TEXT NOT NULL REFERENCES course_events(id) ON DELETE CASCADE,
    lecturer_id INTEGER NOT NULL REFERENCES lecturers(id) ON DELETE CASCADE,
    PRIMARY KEY (course_event_id, lecturer_id)
);

-- Create time slots table
CREATE TABLE time_slots (
    id SERIAL PRIMARY KEY,
    course_event_id TEXT NOT NULL REFERENCES course_events(id) ON DELETE CASCADE,
    day TEXT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    semester TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX idx_courses_name ON courses USING gin(to_tsvector('hebrew', name));
CREATE INDEX idx_course_events_course_id ON course_events(course_id);
CREATE INDEX idx_course_events_category ON course_events(category);
CREATE INDEX idx_time_slots_course_event_id ON time_slots(course_event_id);
CREATE INDEX idx_time_slots_day_time ON time_slots(day, start_time, end_time);
CREATE INDEX idx_lecturers_name ON lecturers USING gin(to_tsvector('hebrew', name));

-- Enable Row Level Security (optional but recommended)
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE lecturers ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_event_lecturers ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_slots ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (adjust as needed)
CREATE POLICY "Allow public read access on courses" ON courses FOR SELECT USING (true);
CREATE POLICY "Allow public read access on course_events" ON course_events FOR SELECT USING (true);
CREATE POLICY "Allow public read access on lecturers" ON lecturers FOR SELECT USING (true);
CREATE POLICY "Allow public read access on course_event_lecturers" ON course_event_lecturers FOR SELECT USING (true);
CREATE POLICY "Allow public read access on time_slots" ON time_slots FOR SELECT USING (true);
