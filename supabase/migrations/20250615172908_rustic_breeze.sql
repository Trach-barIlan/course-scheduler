/*
  # Fix Foreign Key Constraint Issue

  1. Problem
    - user_profiles table has foreign key to non-existent users table
    - Should reference auth.users instead
    - Current constraint is causing registration failures

  2. Solution
    - Drop the problematic foreign key constraint
    - Add correct foreign key to auth.users
    - Ensure proper RLS policies
    - Fix any data inconsistencies

  3. Changes
    - Remove user_profiles_id_fkey constraint
    - Add proper foreign key to auth.users
    - Update policies if needed
*/

-- Drop the problematic foreign key constraint
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_id_fkey' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles DROP CONSTRAINT user_profiles_id_fkey;
    RAISE NOTICE 'Dropped problematic foreign key constraint user_profiles_id_fkey';
  END IF;
END $$;

-- Add the correct foreign key constraint to auth.users
DO $$
BEGIN
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

-- Ensure the table structure is correct
DO $$
BEGIN
  -- Make sure id column exists and is properly typed
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'user_profiles' 
    AND column_name = 'id' 
    AND data_type = 'uuid'
  ) THEN
    -- If id column doesn't exist or is wrong type, recreate it
    ALTER TABLE user_profiles DROP COLUMN IF EXISTS id;
    ALTER TABLE user_profiles ADD COLUMN id uuid PRIMARY KEY;
    RAISE NOTICE 'Fixed id column in user_profiles';
  END IF;
END $$;

-- Clean up any orphaned records (records without corresponding auth.users)
DELETE FROM user_profiles 
WHERE id NOT IN (SELECT id FROM auth.users);

-- Update RLS policies to ensure they work correctly
DROP POLICY IF EXISTS "Enable insert for registration" ON user_profiles;
DROP POLICY IF EXISTS "Enable read for registration" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile when authenticated" ON user_profiles;
DROP POLICY IF EXISTS "Users can read own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;

-- Create comprehensive RLS policies
CREATE POLICY "Users can manage own profile"
  ON user_profiles
  FOR ALL
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Allow service role to insert during registration
CREATE POLICY "Service role can insert profiles"
  ON user_profiles
  FOR INSERT
  TO service_role
  WITH CHECK (true);

-- Allow authenticated users to read their own profile
CREATE POLICY "Users can read own profile"
  ON user_profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- Ensure RLS is enabled
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Add helpful indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_user_profiles_id ON user_profiles(id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username_unique ON user_profiles(username);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email_unique ON user_profiles(email);

-- Ensure username and email are unique
DO $$
BEGIN
  -- Add unique constraint on username if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_username_unique' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_username_unique UNIQUE (username);
  END IF;
  
  -- Add unique constraint on email if it doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE constraint_name = 'user_profiles_email_unique' 
    AND table_name = 'user_profiles'
  ) THEN
    ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_email_unique UNIQUE (email);
  END IF;
END $$;