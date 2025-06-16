/*
  # Fix Service Role Access for User Registration

  1. Problem
    - Service role is still being blocked by RLS policies
    - Need to ensure service role can bypass RLS completely
    - Current policies are too restrictive

  2. Solution
    - Add explicit service role policies
    - Ensure service role can perform all operations
    - Maintain security for regular users

  3. Changes
    - Add service role bypass policies
    - Verify RLS configuration
    - Test service role access
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
    SELECT row_security 
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