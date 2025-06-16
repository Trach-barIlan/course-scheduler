/*
  # Fix Orphaned Users and Add Cleanup

  1. Problem Resolution
    - Find users in auth.users without corresponding user_profiles
    - Create missing profiles for orphaned users
    - Add trigger to prevent future orphaned users

  2. Cleanup Mechanism
    - Function to automatically create profiles when auth users are created
    - Trigger to ensure profile creation happens automatically

  3. Data Integrity
    - Ensure all existing auth users have profiles
    - Prevent future orphaned user situations
*/

-- First, let's create a function to safely create missing profiles
CREATE OR REPLACE FUNCTION create_missing_user_profiles()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    auth_user RECORD;
    profile_exists BOOLEAN;
BEGIN
    -- Loop through all auth users
    FOR auth_user IN 
        SELECT id, email, raw_user_meta_data, created_at
        FROM auth.users
    LOOP
        -- Check if profile exists
        SELECT EXISTS(
            SELECT 1 FROM user_profiles WHERE id = auth_user.id
        ) INTO profile_exists;
        
        -- If no profile exists, create one
        IF NOT profile_exists THEN
            INSERT INTO user_profiles (
                id,
                username,
                first_name,
                last_name,
                email,
                created_at
            ) VALUES (
                auth_user.id,
                COALESCE(
                    auth_user.raw_user_meta_data->>'username',
                    split_part(auth_user.email, '@', 1)
                ),
                COALESCE(
                    auth_user.raw_user_meta_data->>'first_name',
                    'User'
                ),
                COALESCE(
                    auth_user.raw_user_meta_data->>'last_name',
                    'Profile'
                ),
                auth_user.email,
                auth_user.created_at
            );
            
            RAISE NOTICE 'Created missing profile for user: %', auth_user.email;
        END IF;
    END LOOP;
END;
$$;

-- Run the function to fix existing orphaned users
SELECT create_missing_user_profiles();

-- Create a trigger function to automatically create profiles for new auth users
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Insert a new profile for the new auth user
    INSERT INTO user_profiles (
        id,
        username,
        first_name,
        last_name,
        email,
        created_at
    ) VALUES (
        NEW.id,
        COALESCE(
            NEW.raw_user_meta_data->>'username',
            split_part(NEW.email, '@', 1)
        ),
        COALESCE(
            NEW.raw_user_meta_data->>'first_name',
            'User'
        ),
        COALESCE(
            NEW.raw_user_meta_data->>'last_name',
            'Profile'
        ),
        NEW.email,
        NEW.created_at
    );
    
    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- Log the error but don't fail the auth user creation
        RAISE WARNING 'Failed to create user profile for %: %', NEW.email, SQLERRM;
        RETURN NEW;
END;
$$;

-- Drop the trigger if it exists and create a new one
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();

-- Grant necessary permissions for the trigger function
GRANT USAGE ON SCHEMA auth TO postgres;
GRANT SELECT ON auth.users TO postgres;

-- Also ensure service role can execute these functions
GRANT EXECUTE ON FUNCTION create_missing_user_profiles() TO service_role;
GRANT EXECUTE ON FUNCTION handle_new_user() TO service_role;

-- Verify the fix worked
DO $$
DECLARE
    auth_count INTEGER;
    profile_count INTEGER;
    orphaned_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO auth_count FROM auth.users;
    SELECT COUNT(*) INTO profile_count FROM user_profiles;
    
    orphaned_count := auth_count - profile_count;
    
    RAISE NOTICE 'Auth users: %, User profiles: %, Orphaned users: %', 
        auth_count, profile_count, orphaned_count;
        
    IF orphaned_count = 0 THEN
        RAISE NOTICE 'SUCCESS: All auth users now have profiles!';
    ELSE
        RAISE WARNING 'WARNING: Still have % orphaned users', orphaned_count;
    END IF;
END;
$$;