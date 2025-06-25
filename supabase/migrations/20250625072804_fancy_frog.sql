/*
  # Token-Based Authentication System

  1. New Tables
    - `user_sessions`
      - `id` (uuid, primary key)
      - `user_id` (uuid, foreign key to user_profiles)
      - `token` (text, unique)
      - `expires_at` (timestamp)
      - `created_at` (timestamp)
      - `last_used_at` (timestamp)
      - `user_agent` (text, optional)
      - `ip_address` (text, optional)

  2. Security
    - Enable RLS on user_sessions table
    - Add policies for users to manage their own sessions
    - Add cleanup function for expired sessions

  3. Indexes
    - Add indexes for token lookups and cleanup
*/

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  token text UNIQUE NOT NULL,
  expires_at timestamptz NOT NULL,
  created_at timestamptz DEFAULT now(),
  last_used_at timestamptz DEFAULT now(),
  user_agent text,
  ip_address text
);

-- Enable RLS
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- RLS Policies
CREATE POLICY "Users can read own sessions"
  ON user_sessions
  FOR SELECT
  TO authenticated
  USING (user_id = public.uid());

CREATE POLICY "Users can delete own sessions"
  ON user_sessions
  FOR DELETE
  TO authenticated
  USING (user_id = public.uid());

-- Service role has full access
CREATE POLICY "Service role full access to sessions"
  ON user_sessions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Function to cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  DELETE FROM user_sessions 
  WHERE expires_at < now();
  
  RAISE NOTICE 'Cleaned up expired sessions';
END;
$$;

-- Function to create a new session
CREATE OR REPLACE FUNCTION create_user_session(
  p_user_id uuid,
  p_token text,
  p_expires_at timestamptz,
  p_user_agent text DEFAULT NULL,
  p_ip_address text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  session_id uuid;
BEGIN
  -- Clean up any existing sessions for this user (optional - for single session per user)
  -- DELETE FROM user_sessions WHERE user_id = p_user_id;
  
  -- Insert new session
  INSERT INTO user_sessions (
    user_id,
    token,
    expires_at,
    user_agent,
    ip_address
  ) VALUES (
    p_user_id,
    p_token,
    p_expires_at,
    p_user_agent,
    p_ip_address
  ) RETURNING id INTO session_id;
  
  RETURN session_id;
END;
$$;

-- Function to validate and refresh a session
CREATE OR REPLACE FUNCTION validate_session(p_token text)
RETURNS TABLE(
  user_id uuid,
  username text,
  email text,
  first_name text,
  last_name text,
  session_id uuid,
  is_valid boolean
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Update last_used_at and return user info if session is valid
  RETURN QUERY
  UPDATE user_sessions 
  SET last_used_at = now()
  FROM user_profiles
  WHERE user_sessions.token = p_token
    AND user_sessions.expires_at > now()
    AND user_sessions.user_id = user_profiles.id
  RETURNING 
    user_profiles.id,
    user_profiles.username,
    user_profiles.email,
    user_profiles.first_name,
    user_profiles.last_name,
    user_sessions.id,
    true;
END;
$$;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION cleanup_expired_sessions() TO service_role;
GRANT EXECUTE ON FUNCTION create_user_session(uuid, text, timestamptz, text, text) TO service_role;
GRANT EXECUTE ON FUNCTION validate_session(text) TO service_role;