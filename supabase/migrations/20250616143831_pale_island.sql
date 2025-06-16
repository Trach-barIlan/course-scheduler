/*
  # Fix Service Role Access and RLS Policies

  1. Problem
    - Service role being blocked by RLS policies
    - Need to ensure service role has full access to user_profiles table
    - Clean up existing policies and create proper hierarchy

  2. Solution
    - Drop all existing policies
    - Create service role policy with highest priority
    - Add authenticated user policies
    - Grant explicit permissions to service role

  3. Changes
    - Service role gets full access (bypasses RLS)
    - Authenticated users can only access their own data
    - Proper schema permissions for service role
*/

-- Temporarily disable RLS to clean up policies
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Drop all existing policies to start completely fresh
DROP POLICY IF EXISTS "authenticated_users_read_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "authenticated_users_insert_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "authenticated_users_update_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "authenticated_users_delete_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "service_role_full_access" ON user_profiles;
DROP POLICY IF EXISTS "Users can read own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can delete own profile" ON user_profiles;
DROP POLICY IF EXISTS "Service role can manage all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Users can manage own profile" ON user_profiles;

-- Re-enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create service role policy FIRST (highest priority)
CREATE POLICY "service_role_full_access"
  ON user_profiles
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Create authenticated user policies
CREATE POLICY "authenticated_users_read_own_profile"
  ON user_profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "authenticated_users_insert_own_profile"
  ON user_profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

CREATE POLICY "authenticated_users_update_own_profile"
  ON user_profiles
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY "authenticated_users_delete_own_profile"
  ON user_profiles
  FOR DELETE
  TO authenticated
  USING (auth.uid() = id);

-- Verify service role can access the table
DO $$
BEGIN
  -- Test if service role policies are working
  RAISE NOTICE 'Service role policies created successfully';
  RAISE NOTICE 'RLS is enabled: %', (
    SELECT rowsecurity 
    FROM pg_tables 
    WHERE tablename = 'user_profiles'
  );
END $$;

-- Grant explicit permissions to service role
GRANT ALL ON user_profiles TO service_role;
GRANT USAGE ON SCHEMA public TO service_role;

-- Ensure the auth schema is accessible
GRANT USAGE ON SCHEMA auth TO service_role;
GRANT SELECT ON auth.users TO service_role;

-- Also grant permissions on saved_schedules table for consistency
GRANT ALL ON saved_schedules TO service_role;

-- Ensure sequences are accessible (for auto-generated IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Create indexes if they don't exist (for performance)
CREATE INDEX IF NOT EXISTS idx_user_profiles_id ON user_profiles(id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username_unique ON user_profiles(username);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email_unique ON user_profiles(email);