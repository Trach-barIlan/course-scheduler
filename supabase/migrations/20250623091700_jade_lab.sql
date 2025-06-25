/*
  # Add UID function for custom authentication

  1. Functions
    - Create `uid()` function that returns current user ID from session
    - This replaces Supabase's built-in `auth.uid()` function

  2. Security
    - Function is marked as SECURITY DEFINER to run with elevated privileges
    - Returns the user_id from the current session context
*/

-- Create a function to get the current user ID from session
-- This replaces auth.uid() for custom authentication
CREATE OR REPLACE FUNCTION public.uid()
RETURNS uuid
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT COALESCE(
    current_setting('app.current_user_id', true)::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid
  );
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.uid() TO authenticated;
GRANT EXECUTE ON FUNCTION public.uid() TO anon;

-- Create a function to set the current user ID in session
CREATE OR REPLACE FUNCTION public.set_current_user_id(user_id uuid)
RETURNS void
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT set_config('app.current_user_id', user_id::text, false);
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION public.set_current_user_id(uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION public.set_current_user_id(uuid) TO service_role;