/*
  # Fix Registration RLS Policies

  1. Security Updates
    - Update RLS policies to allow proper user registration
    - Ensure authenticated users can create their own profiles
    - Maintain security for all operations

  2. Changes
    - Drop conflicting policies
    - Create comprehensive policies for registration flow
    - Ensure proper authentication context
*/

-- Drop all existing policies to start fresh
DROP POLICY IF EXISTS "Users can manage own profile" ON user_profiles;
DROP POLICY IF EXISTS "Service role can insert profiles" ON user_profiles;
DROP POLICY IF EXISTS "Users can read own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile when authenticated" ON user_profiles;
DROP POLICY IF EXISTS "Enable insert for registration" ON user_profiles;
DROP POLICY IF EXISTS "Enable read for registration" ON user_profiles;

-- Create comprehensive policies for user_profiles

-- 1. Allow authenticated users to read their own profile
CREATE POLICY "Users can read own profile"
  ON user_profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- 2. Allow authenticated users to insert their own profile (for registration)
CREATE POLICY "Users can insert own profile"
  ON user_profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- 3. Allow authenticated users to update their own profile
CREATE POLICY "Users can update own profile"
  ON user_profiles
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- 4. Allow authenticated users to delete their own profile
CREATE POLICY "Users can delete own profile"
  ON user_profiles
  FOR DELETE
  TO authenticated
  USING (auth.uid() = id);

-- 5. Allow service role to manage profiles (for admin operations)
CREATE POLICY "Service role can manage all profiles"
  ON user_profiles
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Ensure RLS is enabled
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Verify the foreign key constraint is correct
DO $$
BEGIN
  -- Ensure we have the correct foreign key to auth.users
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_auth_users_fkey' 
    AND table_name = 'user_profiles'
  ) THEN
    -- Drop any existing foreign key constraints
    ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_id_fkey;
    
    -- Add the correct foreign key constraint
    ALTER TABLE user_profiles 
    ADD CONSTRAINT user_profiles_auth_users_fkey 
    FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;
    
    RAISE NOTICE 'Added correct foreign key constraint to auth.users';
  END IF;
END $$;

-- Clean up any orphaned records
DELETE FROM user_profiles 
WHERE id NOT IN (SELECT id FROM auth.users);

-- Ensure proper indexes exist
CREATE INDEX IF NOT EXISTS idx_user_profiles_id ON user_profiles(id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);

-- Ensure unique constraints exist
DO $$
BEGIN
  -- Username unique constraint
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_username_key' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_username_key UNIQUE (username);
  END IF;
  
  -- Email unique constraint  
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_email_unique' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_email_unique UNIQUE (email);
  END IF;
END $$;