-- Enhanced Courses Database Schema with Room for Expansion

-- 1. Universities table (for future multi-university support)
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL, -- e.g., 'BIU', 'TAU', 'HUJI'
    website_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 2. Departments table (expandable for all departments)
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    university_id INTEGER NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    code TEXT NOT NULL, -- Department code from university system
    description TEXT,
    website_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(university_id, code)
);

-- 3. Course categories/types (expandable)
CREATE TABLE course_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- e.g., 'הרצאה', 'סדנה', 'תרגיל', 'סמינריון'
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 4. Semesters table (for better semester management)
CREATE TABLE semesters (
    id SERIAL PRIMARY KEY,
    university_id INTEGER NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- e.g., 'סמסטר א׳', 'סמסטר ב׳', 'קיץ'
    code TEXT NOT NULL, -- e.g., 'A', 'B', 'SUMMER'
    academic_year TEXT NOT NULL, -- e.g., '2024-2025'
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(university_id, code, academic_year)
);

-- 5. Enhanced Courses table with extensible fields
CREATE TABLE courses (
    id TEXT PRIMARY KEY, -- Course ID from university system
    university_id INTEGER NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    english_name TEXT, -- For international students
    description TEXT,
    credits INTEGER, -- Number of credits
    prerequisites TEXT[], -- Array of prerequisite course IDs
    level TEXT, -- e.g., 'undergraduate', 'graduate', 'phd'
    language TEXT DEFAULT 'hebrew', -- Course language
    syllabus_url TEXT,
    is_active BOOLEAN DEFAULT true,
    academic_year TEXT, -- e.g., '2024-2025'
    
    -- Extensible JSON field for future course properties
    additional_properties JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 6. Lecturers/Instructors table (enhanced)
CREATE TABLE lecturers (
    id SERIAL PRIMARY KEY,
    university_id INTEGER NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    office_location TEXT,
    department_id INTEGER REFERENCES departments(id),
    title TEXT, -- e.g., 'ד"ר', 'פרופ׳', 'מר', 'גב׳'
    bio TEXT,
    website_url TEXT,
    
    -- Extensible JSON field for future lecturer properties
    additional_properties JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    UNIQUE(university_id, name, email)
);

-- 7. Locations/Rooms table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    university_id INTEGER NOT NULL REFERENCES universities(id) ON DELETE CASCADE,
    building_name TEXT,
    room_number TEXT,
    full_name TEXT NOT NULL, -- Complete location description
    capacity INTEGER,
    equipment TEXT[], -- Array of available equipment
    accessibility_features TEXT[],
    
    -- Extensible JSON field for future location properties
    additional_properties JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(university_id, full_name)
);

-- 8. Enhanced Course Events table
CREATE TABLE course_events (
    id TEXT PRIMARY KEY, -- Event ID from university system
    course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES course_categories(id),
    group_number TEXT, -- Group/section number
    max_students INTEGER,
    enrolled_students INTEGER DEFAULT 0,
    location_id INTEGER REFERENCES locations(id),
    
    -- Meeting pattern (for recurring events)
    recurrence_pattern TEXT, -- e.g., 'weekly', 'biweekly'
    
    -- Special properties
    is_online BOOLEAN DEFAULT false,
    meeting_link TEXT, -- For online classes
    notes TEXT,
    
    -- Extensible JSON field for future event properties
    additional_properties JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 9. Course Event Lecturers (many-to-many with roles)
CREATE TABLE course_event_lecturers (
    course_event_id TEXT NOT NULL REFERENCES course_events(id) ON DELETE CASCADE,
    lecturer_id INTEGER NOT NULL REFERENCES lecturers(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'instructor', -- e.g., 'instructor', 'assistant', 'guest'
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    PRIMARY KEY (course_event_id, lecturer_id)
);

-- 10. Days of week reference table
CREATE TABLE days_of_week (
    id SERIAL PRIMARY KEY,
    name_hebrew TEXT NOT NULL UNIQUE,
    name_english TEXT NOT NULL UNIQUE,
    name_short TEXT NOT NULL UNIQUE, -- e.g., 'SUN', 'MON'
    day_number INTEGER NOT NULL UNIQUE -- 1=Sunday, 2=Monday, etc.
);

-- Insert standard days of week
INSERT INTO days_of_week (name_hebrew, name_english, name_short, day_number) VALUES
('ראשון', 'Sunday', 'SUN', 1),
('שני', 'Monday', 'MON', 2),
('שלישי', 'Tuesday', 'TUE', 3),
('רביעי', 'Wednesday', 'WED', 4),
('חמישי', 'Thursday', 'THU', 5),
('שישי', 'Friday', 'FRI', 6),
('שבת', 'Saturday', 'SAT', 7);

-- 11. Enhanced Time Slots table
CREATE TABLE time_slots (
    id SERIAL PRIMARY KEY,
    course_event_id TEXT NOT NULL REFERENCES course_events(id) ON DELETE CASCADE,
    semester_id INTEGER NOT NULL REFERENCES semesters(id),
    day_of_week_id INTEGER NOT NULL REFERENCES days_of_week(id),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    
    -- Specific dates (for non-recurring events)
    specific_date DATE,
    
    -- Exceptions and modifications
    is_cancelled BOOLEAN DEFAULT false,
    cancellation_reason TEXT,
    alternative_location_id INTEGER REFERENCES locations(id),
    
    -- Extensible JSON field for future time slot properties
    additional_properties JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 12. Course Materials table (for future expansion)
CREATE TABLE course_materials (
    id SERIAL PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    type TEXT NOT NULL, -- e.g., 'textbook', 'article', 'video', 'website'
    url TEXT,
    isbn TEXT,
    author TEXT,
    is_required BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 13. Course Prerequisites (separate table for complex relationships)
CREATE TABLE course_prerequisites (
    course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    prerequisite_course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    is_required BOOLEAN DEFAULT true,
    alternative_group INTEGER, -- For "Course A OR Course B" scenarios
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    PRIMARY KEY (course_id, prerequisite_course_id)
);

-- Performance Indexes
CREATE INDEX idx_courses_university_department ON courses(university_id, department_id);
CREATE INDEX idx_courses_name_search ON courses USING gin(to_tsvector('simple', name));
CREATE INDEX idx_courses_english_name_search ON courses USING gin(to_tsvector('english', english_name));
CREATE INDEX idx_courses_active_year ON courses(is_active, academic_year);
CREATE INDEX idx_courses_level ON courses(level);

CREATE INDEX idx_lecturers_university ON lecturers(university_id);
CREATE INDEX idx_lecturers_name_search ON lecturers USING gin(to_tsvector('simple', name));
CREATE INDEX idx_lecturers_active ON lecturers(is_active);

CREATE INDEX idx_course_events_course_id ON course_events(course_id);
CREATE INDEX idx_course_events_active ON course_events(is_active);
CREATE INDEX idx_course_events_category ON course_events(category_id);

CREATE INDEX idx_time_slots_event_semester ON time_slots(course_event_id, semester_id);
CREATE INDEX idx_time_slots_day_time ON time_slots(day_of_week_id, start_time, end_time);
CREATE INDEX idx_time_slots_active ON time_slots(is_cancelled);

CREATE INDEX idx_locations_university ON locations(university_id);
CREATE INDEX idx_departments_university ON departments(university_id);

-- Full-text search indexes for multiple languages
CREATE INDEX idx_courses_multilingual_search ON courses USING gin(
    (to_tsvector('simple', coalesce(name, '')) || to_tsvector('english', coalesce(english_name, '')))
);

-- JSONB indexes for extensible fields (for future use)
CREATE INDEX idx_courses_additional_properties ON courses USING gin(additional_properties);
CREATE INDEX idx_lecturers_additional_properties ON lecturers USING gin(additional_properties);
CREATE INDEX idx_course_events_additional_properties ON course_events USING gin(additional_properties);

-- Enable Row Level Security
ALTER TABLE universities ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE lecturers ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_slots ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_materials ENABLE ROW LEVEL SECURITY;

-- Public read access policies (adjust based on your needs)
CREATE POLICY "Allow public read access on universities" ON universities FOR SELECT USING (true);
CREATE POLICY "Allow public read access on departments" ON departments FOR SELECT USING (true);
CREATE POLICY "Allow public read access on courses" ON courses FOR SELECT USING (is_active = true);
CREATE POLICY "Allow public read access on course_events" ON course_events FOR SELECT USING (is_active = true);
CREATE POLICY "Allow public read access on lecturers" ON lecturers FOR SELECT USING (is_active = true);
CREATE POLICY "Allow public read access on locations" ON locations FOR SELECT USING (is_active = true);
CREATE POLICY "Allow public read access on time_slots" ON time_slots FOR SELECT USING (is_cancelled = false);
CREATE POLICY "Allow public read access on course_categories" ON course_categories FOR SELECT USING (true);
CREATE POLICY "Allow public read access on semesters" ON semesters FOR SELECT USING (true);
CREATE POLICY "Allow public read access on days_of_week" ON days_of_week FOR SELECT USING (true);
CREATE POLICY "Allow public read access on course_materials" ON course_materials FOR SELECT USING (true);
CREATE POLICY "Allow public read access on course_prerequisites" ON course_prerequisites FOR SELECT USING (true);
CREATE POLICY "Allow public read access on course_event_lecturers" ON course_event_lecturers FOR SELECT USING (true);

-- Insert initial data for Bar-Ilan University
INSERT INTO universities (name, code, website_url) VALUES 
('אוניברסיטת בר-אילן', 'BIU', 'https://www.biu.ac.il');

-- Insert common course categories
INSERT INTO course_categories (name, description) VALUES
('הרצאה', 'שיעור אקדמי רגיל'),
('תרגיל', 'שיעור תרגול והדגמה'),
('סדנה', 'שיעור מעשי ואינטראקטיבי'),
('סמינריון', 'קורס מחקר ודיון'),
('מעבדה', 'שיעור מעשי במעבדה'),
('הדרכה', 'הדרכה אישית או קבוצתית'),
('פרויקט', 'עבודת פרויקט מודרכת');

-- Insert current academic year semesters for Bar-Ilan
INSERT INTO semesters (university_id, name, code, academic_year, is_active) VALUES
(1, 'סמסטר א׳', 'A', '2024-2025', true),
(1, 'סמסטר ב׳', 'B', '2024-2025', true),
(1, 'סמסטר קיץ', 'SUMMER', '2024-2025', true);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_universities_updated_at BEFORE UPDATE ON universities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lecturers_updated_at BEFORE UPDATE ON lecturers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_course_events_updated_at BEFORE UPDATE ON course_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_time_slots_updated_at BEFORE UPDATE ON time_slots FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
