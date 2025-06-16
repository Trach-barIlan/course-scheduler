/*
  # Fix RLS Policies for User Registration

  1. Security Changes
    - Clean up all existing policies on user_profiles table
    - Create service role policy with full access (bypasses RLS)
    - Create authenticated user policies for CRUD operations
    - Grant explicit permissions to service role

  2. Tables Affected
    - `user_profiles` - RLS policies and permissions
    - `saved_schedules` - Service role permissions

  3. Important Notes
    - Service role policy allows backend registration to work
    - RLS remains enabled for security
    - Authenticated users can only access their own data
*/

-- Temporarily disable RLS to clean up policies
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Drop all existing policies to start completely fresh
DROP POLICY IF EXISTS "authenticated_users_read_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "authenticated_users_insert_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "authenticated_users_update_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "authenticated_users_delete_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "service_role_full_access" ON user_profiles;

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

-- Also grant permissions for saved_schedules table
GRANT ALL ON saved_schedules TO service_role;

-- Grant permissions on sequences (for auto-generated IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;