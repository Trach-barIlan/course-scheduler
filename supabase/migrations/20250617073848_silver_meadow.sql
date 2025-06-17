/*
  # Add User Statistics Tracking

  1. New Tables
    - `user_statistics`
      - `user_id` (uuid, foreign key to user_profiles)
      - `schedules_created_total` (integer)
      - `schedules_created_this_week` (integer)
      - `schedules_created_this_month` (integer)
      - `last_schedule_generated` (timestamp)
      - `total_courses_scheduled` (integer)
      - `average_schedule_generation_time` (float)
      - `preferred_schedule_type` (text)
      - `constraints_used_count` (integer)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

    - `schedule_generation_logs`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key)
      - `schedule_id` (uuid, foreign key to saved_schedules, nullable)
      - `courses_count` (integer)
      - `constraints_count` (integer)
      - `generation_time_ms` (integer)
      - `schedule_type` (text - crammed/spaced)
      - `success` (boolean)
      - `error_message` (text, nullable)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on both tables
    - Add policies for users to read/write their own data

  3. Functions
    - Function to update user statistics
    - Function to calculate weekly/monthly stats
*/

-- Create user_statistics table
CREATE TABLE IF NOT EXISTS user_statistics (
  user_id uuid PRIMARY KEY REFERENCES user_profiles(id) ON DELETE CASCADE,
  schedules_created_total integer DEFAULT 0,
  schedules_created_this_week integer DEFAULT 0,
  schedules_created_this_month integer DEFAULT 0,
  last_schedule_generated timestamptz,
  total_courses_scheduled integer DEFAULT 0,
  average_schedule_generation_time float DEFAULT 0,
  preferred_schedule_type text DEFAULT 'crammed',
  constraints_used_count integer DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create schedule_generation_logs table
CREATE TABLE IF NOT EXISTS schedule_generation_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  schedule_id uuid REFERENCES saved_schedules(id) ON DELETE SET NULL,
  courses_count integer NOT NULL DEFAULT 0,
  constraints_count integer DEFAULT 0,
  generation_time_ms integer DEFAULT 0,
  schedule_type text DEFAULT 'crammed',
  success boolean DEFAULT true,
  error_message text,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE user_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedule_generation_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_statistics
CREATE POLICY "Users can read own statistics"
  ON user_statistics
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own statistics"
  ON user_statistics
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own statistics"
  ON user_statistics
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for schedule_generation_logs
CREATE POLICY "Users can read own generation logs"
  ON schedule_generation_logs
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own generation logs"
  ON schedule_generation_logs
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Service role policies for backend operations
CREATE POLICY "Service role full access to user_statistics"
  ON user_statistics
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role full access to schedule_generation_logs"
  ON schedule_generation_logs
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Function to update user statistics
CREATE OR REPLACE FUNCTION update_user_statistics(
  p_user_id uuid,
  p_courses_count integer DEFAULT 0,
  p_constraints_count integer DEFAULT 0,
  p_generation_time_ms integer DEFAULT 0,
  p_schedule_type text DEFAULT 'crammed',
  p_success boolean DEFAULT true
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  current_week_start date;
  current_month_start date;
BEGIN
  -- Calculate week and month boundaries
  current_week_start := date_trunc('week', now())::date;
  current_month_start := date_trunc('month', now())::date;
  
  -- Insert or update user statistics
  INSERT INTO user_statistics (
    user_id,
    schedules_created_total,
    schedules_created_this_week,
    schedules_created_this_month,
    last_schedule_generated,
    total_courses_scheduled,
    constraints_used_count,
    preferred_schedule_type,
    updated_at
  )
  VALUES (
    p_user_id,
    1,
    1,
    1,
    now(),
    p_courses_count,
    p_constraints_count,
    p_schedule_type,
    now()
  )
  ON CONFLICT (user_id) DO UPDATE SET
    schedules_created_total = user_statistics.schedules_created_total + 1,
    schedules_created_this_week = CASE 
      WHEN user_statistics.updated_at::date >= current_week_start 
      THEN user_statistics.schedules_created_this_week + 1
      ELSE 1
    END,
    schedules_created_this_month = CASE 
      WHEN user_statistics.updated_at::date >= current_month_start 
      THEN user_statistics.schedules_created_this_month + 1
      ELSE 1
    END,
    last_schedule_generated = now(),
    total_courses_scheduled = user_statistics.total_courses_scheduled + p_courses_count,
    constraints_used_count = user_statistics.constraints_used_count + p_constraints_count,
    preferred_schedule_type = p_schedule_type,
    average_schedule_generation_time = CASE 
      WHEN user_statistics.schedules_created_total = 0 THEN p_generation_time_ms::float
      ELSE (user_statistics.average_schedule_generation_time * user_statistics.schedules_created_total + p_generation_time_ms) / (user_statistics.schedules_created_total + 1)
    END,
    updated_at = now();
END;
$$;

-- Function to reset weekly/monthly counters (to be called by a cron job)
CREATE OR REPLACE FUNCTION reset_periodic_statistics()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  current_week_start date;
  current_month_start date;
BEGIN
  current_week_start := date_trunc('week', now())::date;
  current_month_start := date_trunc('month', now())::date;
  
  -- Reset weekly counters for users who haven't generated schedules this week
  UPDATE user_statistics 
  SET schedules_created_this_week = 0
  WHERE updated_at::date < current_week_start;
  
  -- Reset monthly counters for users who haven't generated schedules this month
  UPDATE user_statistics 
  SET schedules_created_this_month = 0
  WHERE updated_at::date < current_month_start;
END;
$$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_statistics_user_id ON user_statistics(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_generation_logs_user_id ON schedule_generation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_generation_logs_created_at ON schedule_generation_logs(created_at);

-- Create updated_at trigger for user_statistics
CREATE OR REPLACE FUNCTION update_user_statistics_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_statistics_updated_at
  BEFORE UPDATE ON user_statistics
  FOR EACH ROW
  EXECUTE FUNCTION update_user_statistics_updated_at();