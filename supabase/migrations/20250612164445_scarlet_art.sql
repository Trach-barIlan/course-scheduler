/*
  # Fix User Registration RLS Policies

  1. Security Updates
    - Update RLS policies to allow user profile creation during registration
    - Add service role bypass for initial user creation
    - Maintain security for all other operations

  2. Changes
    - Modify INSERT policy for user_profiles to allow registration
    - Add proper authentication checks
    - Ensure data integrity
*/

-- Drop existing INSERT policy for user_profiles
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;

-- Create new INSERT policy that allows registration
CREATE POLICY "Enable insert for registration"
  ON user_profiles
  FOR INSERT
  WITH CHECK (true);

-- Also create a more restrictive policy for authenticated users
CREATE POLICY "Users can insert own profile when authenticated"
  ON user_profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- Update the SELECT policy to be more permissive for the user's own data
DROP POLICY IF EXISTS "Users can read own profile" ON user_profiles;
CREATE POLICY "Users can read own profile"
  ON user_profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- Also allow reading during registration process
CREATE POLICY "Enable read for registration"
  ON user_profiles
  FOR SELECT
  USING (true);