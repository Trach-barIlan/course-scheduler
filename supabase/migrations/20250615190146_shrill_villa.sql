/*
  # Fix Registration RLS Policies - Final Fix

  1. Problem
    - RLS policies are blocking profile creation during registration
    - Authentication context not properly established during profile insert
    - Need to allow profile creation for newly registered users

  2. Solution
    - Create specific policy for registration flow
    - Allow authenticated users to insert their own profiles
    - Ensure proper authentication context handling
    - Maintain security for all other operations

  3. Changes
    - Drop conflicting policies
    - Create registration-friendly policies
    - Ensure proper foreign key constraints
    - Add comprehensive logging
*/

-- Drop all existing policies to start completely fresh
DROP POLICY IF EXISTS "Users can read own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can delete own profile" ON user_profiles;
DROP POLICY IF EXISTS "Service role can manage all profiles" ON user_profiles;
DROP POLICY IF EXISTS "Users can manage own profile" ON user_profiles;
DROP POLICY IF EXISTS "Enable insert for registration" ON user_profiles;
DROP POLICY IF EXISTS "Enable read for registration" ON user_profiles;

-- Ensure RLS is enabled
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create comprehensive policies that work with the registration flow

-- 1. Allow authenticated users to read their own profile
CREATE POLICY "authenticated_users_read_own_profile"
  ON user_profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- 2. Allow authenticated users to insert their own profile (critical for registration)
CREATE POLICY "authenticated_users_insert_own_profile"
  ON user_profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- 3. Allow authenticated users to update their own profile
CREATE POLICY "authenticated_users_update_own_profile"
  ON user_profiles
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- 4. Allow authenticated users to delete their own profile
CREATE POLICY "authenticated_users_delete_own_profile"
  ON user_profiles
  FOR DELETE
  TO authenticated
  USING (auth.uid() = id);

-- 5. Allow service role full access (for admin operations and cleanup)
CREATE POLICY "service_role_full_access"
  ON user_profiles
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Ensure the foreign key constraint is correct
DO $$
BEGIN
  -- Drop any problematic foreign key constraints
  IF EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_id_fkey' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles DROP CONSTRAINT user_profiles_id_fkey;
    RAISE NOTICE 'Dropped old foreign key constraint';
  END IF;

  -- Add the correct foreign key constraint to auth.users
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_auth_users_fkey' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles 
    ADD CONSTRAINT user_profiles_auth_users_fkey 
    FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;
    RAISE NOTICE 'Added correct foreign key constraint to auth.users';
  END IF;
END $$;

-- Clean up any orphaned records
DELETE FROM user_profiles 
WHERE id NOT IN (SELECT id FROM auth.users);

-- Ensure proper indexes exist for performance
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
    RAISE NOTICE 'Added username unique constraint';
  END IF;
  
  -- Email unique constraint  
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_email_key' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_email_key UNIQUE (email);
    RAISE NOTICE 'Added email unique constraint';
  END IF;
END $$;

-- Verify the table structure
DO $$
BEGIN
  -- Ensure all required columns exist with correct types
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'user_profiles' 
    AND column_name = 'id' 
    AND data_type = 'uuid'
  ) THEN
    RAISE EXCEPTION 'user_profiles.id column missing or wrong type';
  END IF;
  
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'user_profiles' 
    AND column_name = 'username' 
    AND data_type = 'text'
  ) THEN
    RAISE EXCEPTION 'user_profiles.username column missing or wrong type';
  END IF;
  
  RAISE NOTICE 'Table structure verified successfully';
END $$;