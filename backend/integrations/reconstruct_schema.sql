-- Schedgic Database Schema Reconstruction (Complete)
-- This script recreates the table structure and functions for the course scheduler backend.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Reference Tables
CREATE TABLE IF NOT EXISTS universities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    location TEXT,
    website_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(university_id, code)
);

CREATE TABLE IF NOT EXISTS semesters (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    year TEXT NOT NULL,
    name TEXT NOT NULL, -- e.g., 'Semester A', 'Semester B', 'Summer'
    code TEXT NOT NULL, -- e.g., 'A', 'B', 'SUMMER'
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(university_id, year, code)
);

CREATE TABLE IF NOT EXISTS days_of_week (
    id SERIAL PRIMARY KEY,
    name_hebrew TEXT NOT NULL,
    name_english TEXT NOT NULL,
    day_number INTEGER NOT NULL -- 1 for Sunday, 7 for Saturday
);

CREATE TABLE IF NOT EXISTS course_categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL -- e.g., 'הרצאה', 'תרגיל', 'מעבדה'
);

-- 2. Auth & User Tables
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_statistics (
    user_id UUID PRIMARY KEY REFERENCES user_profiles(id) ON DELETE CASCADE,
    schedules_created_total INTEGER DEFAULT 0,
    schedules_created_this_week INTEGER DEFAULT 0,
    schedules_created_this_month INTEGER DEFAULT 0,
    total_courses_scheduled INTEGER DEFAULT 0,
    average_schedule_generation_time NUMERIC DEFAULT 0,
    preferred_schedule_type TEXT DEFAULT 'crammed',
    constraints_used_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS saved_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    schedule_name TEXT NOT NULL,
    schedule_data JSONB NOT NULL,
    constraints_data JSONB,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Core Course Tables
CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY, -- Using course code as ID (e.g., '89110')
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    english_name TEXT,
    description TEXT,
    credits NUMERIC,
    prerequisites TEXT,
    level TEXT,
    language TEXT DEFAULT 'hebrew',
    syllabus_url TEXT,
    academic_year TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    additional_properties JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lecturers (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    title TEXT,
    email TEXT,
    website_url TEXT,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(university_id, name, email)
);

CREATE TABLE IF NOT EXISTS course_events (
    id TEXT PRIMARY KEY, -- e.g., '89110-01-0'
    course_id TEXT REFERENCES courses(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES course_categories(id) ON DELETE SET NULL,
    group_number TEXT, -- e.g., '01'
    max_students INTEGER,
    enrolled_students INTEGER DEFAULT 0,
    location_id INTEGER, 
    recurrence_pattern TEXT,
    is_online BOOLEAN DEFAULT FALSE,
    meeting_link TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    additional_properties JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS course_event_lecturers (
    id SERIAL PRIMARY KEY,
    course_event_id TEXT REFERENCES course_events(id) ON DELETE CASCADE,
    lecturer_id INTEGER REFERENCES lecturers(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'instructor',
    is_primary BOOLEAN DEFAULT TRUE,
    UNIQUE(course_event_id, lecturer_id)
);

CREATE TABLE IF NOT EXISTS time_slots (
    id SERIAL PRIMARY KEY,
    course_event_id TEXT REFERENCES course_events(id) ON DELETE CASCADE,
    semester_id INTEGER REFERENCES semesters(id) ON DELETE CASCADE,
    day_of_week_id INTEGER REFERENCES days_of_week(id) ON DELETE SET NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    specific_date DATE,
    is_cancelled BOOLEAN DEFAULT FALSE,
    cancellation_reason TEXT,
    alternative_location_id INTEGER,
    additional_properties JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Logs
CREATE TABLE IF NOT EXISTS schedule_generation_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    courses_count INTEGER,
    constraints_count INTEGER,
    generation_time_ms INTEGER,
    schedule_type TEXT,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. RPC Functions

-- Function to create a user session
CREATE OR REPLACE FUNCTION create_user_session(
    p_user_id UUID,
    p_token TEXT,
    p_expires_at TIMESTAMP WITH TIME ZONE,
    p_user_agent TEXT DEFAULT NULL,
    p_ip_address TEXT DEFAULT NULL
) RETURNS JSONB AS $$
DECLARE
    v_session_id UUID;
BEGIN
    INSERT INTO user_sessions (user_id, token, expires_at, user_agent, ip_address)
    VALUES (p_user_id, p_token, p_expires_at, p_user_agent, p_ip_address)
    RETURNING id INTO v_session_id;
    
    RETURN jsonb_build_object('session_id', v_session_id, 'status', 'created');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate a session
CREATE OR REPLACE FUNCTION validate_session(p_token TEXT)
RETURNS TABLE (
    is_valid BOOLEAN,
    user_id UUID,
    username TEXT,
    email TEXT,
    first_name TEXT,
    last_name TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (s.expires_at > CURRENT_TIMESTAMP AND s.is_active = TRUE) as is_valid,
        u.id as user_id,
        u.username,
        u.email,
        u.first_name,
        u.last_name
    FROM user_sessions s
    JOIN user_profiles u ON s.user_id = u.id
    WHERE s.token = p_token;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions() RETURNS VOID AS $$
BEGIN
    UPDATE user_sessions SET is_active = FALSE WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update user statistics
CREATE OR REPLACE FUNCTION update_user_statistics(
    p_user_id UUID,
    p_courses_count INTEGER,
    p_constraints_count INTEGER,
    p_generation_time_ms INTEGER,
    p_schedule_type TEXT,
    p_success BOOLEAN
) RETURNS VOID AS $$
BEGIN
    INSERT INTO user_statistics (user_id, schedules_created_total, total_courses_scheduled, constraints_used_count, preferred_schedule_type)
    VALUES (p_user_id, 1, p_courses_count, p_constraints_count, p_schedule_type)
    ON CONFLICT (user_id) DO UPDATE SET
        schedules_created_total = user_statistics.schedules_created_total + 1,
        total_courses_scheduled = user_statistics.total_courses_scheduled + p_courses_count,
        constraints_used_count = user_statistics.constraints_used_count + p_constraints_count,
        preferred_schedule_type = p_schedule_type,
        average_schedule_generation_time = (user_statistics.average_schedule_generation_time * user_statistics.schedules_created_total + p_generation_time_ms) / (user_statistics.schedules_created_total + 1),
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Dummy function for set_current_user_id (often used for RLS)
CREATE OR REPLACE FUNCTION set_current_user_id(user_id TEXT) RETURNS TEXT AS $$
BEGIN
  RETURN user_id;
END;
$$ LANGUAGE plpgsql;

-- Exec function (if needed by some older scripts)
CREATE OR REPLACE FUNCTION exec(sql TEXT) RETURNS VOID AS $$
BEGIN
    EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- 6. Seed Data
INSERT INTO universities (name, code) VALUES ('Bar-Ilan University', 'BIU') ON CONFLICT DO NOTHING;

INSERT INTO days_of_week (name_hebrew, name_english, day_number) VALUES
('ראשון', 'Sunday', 1),
('שני', 'Monday', 2),
('שלישי', 'Tuesday', 3),
('רביעי', 'Wednesday', 4),
('חמישי', 'Thursday', 5),
('שישי', 'Friday', 6),
('שבת', 'Saturday', 7)
ON CONFLICT DO NOTHING;

INSERT INTO course_categories (name) VALUES
('הרצאה'),
('תרגיל'),
('מעבדה'),
('סמינר'),
('פרויקט')
ON CONFLICT DO NOTHING;

-- Initial Semesters for 2024-2025
INSERT INTO semesters (university_id, year, name, code) VALUES
(1, '2024-2025', 'Semester A', 'A'),
(1, '2024-2025', 'Semester B', 'B'),
(1, '2024-2025', 'Summer', 'SUMMER')
ON CONFLICT DO NOTHING;
