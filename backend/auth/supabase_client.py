import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import re

class SupabaseClient:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        if not service_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required for user registration")
        
        self.supabase: Client = create_client(url, key)
        
        # Create a service role client for admin operations
        self.service_supabase: Client = create_client(url, service_key)
        print(f"✅ Service role client created successfully")

    def validate_email_format(self, email: str) -> bool:
        """Validate email format using a comprehensive regex"""
        pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(pattern, email) is not None

    def create_user(self, email: str, password: str, user_metadata: Dict[str, Any]) -> Optional[Dict]:
        """Create a new user with Supabase Auth"""
        try:
            # Validate email format before sending to Supabase
            if not self.validate_email_format(email):
                print(f"❌ Invalid email format: {email}")
                return None

            # Clean and validate the email
            email = email.strip().lower()
            
            # Check if username already exists using service role
            existing_user = self.service_supabase.table("user_profiles").select("username").eq("username", user_metadata.get("username")).execute()
            if existing_user.data:
                print(f"❌ Username already exists: {user_metadata.get('username')}")
                return None

            print(f"🔄 Attempting to create user with email: {email}")
            
            # Step 1: Create the auth user with auto-confirm enabled
            auth_response = self.service_supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": user_metadata
            })
            
            print(f"✅ Supabase auth response: user={auth_response.user.id if auth_response.user else 'None'}")
            
            if not auth_response.user:
                print("❌ No user returned from Supabase auth")
                return None

            user_id = auth_response.user.id
            print(f"✅ Auth user created with ID: {user_id}")
            
            # Step 2: Wait a moment for the trigger to create the profile
            import time
            time.sleep(2)
            
            # Step 3: Check if profile was created by trigger
            profile_check = self.service_supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if profile_check.data:
                print("✅ User profile created automatically by trigger")
                profile_data = profile_check.data[0]
            else:
                print("⚠️ Profile not created by trigger, creating manually...")
                
                # Step 4: Create the profile manually using the service role client
                profile_data = {
                    "id": user_id,
                    "username": user_metadata.get("username"),
                    "first_name": user_metadata.get("first_name"),
                    "last_name": user_metadata.get("last_name"),
                    "email": email
                }
                
                print(f"🔄 Creating profile manually...")
                print(f"Profile data: {profile_data}")
                
                # Use the service role client to bypass RLS policies
                profile_response = self.service_supabase.table("user_profiles").insert(profile_data).execute()
                print(f"✅ Manual profile creation response: {profile_response}")
                
                if not profile_response.data:
                    print("❌ Failed to create user profile manually")
                    # Don't return None here - the auth user was created successfully
                    # We'll return the user data anyway and let them try to log in
                    print("⚠️ Continuing with auth user data only")
                
                profile_data = profile_response.data[0] if profile_response.data else {
                    "username": user_metadata.get("username"),
                    "first_name": user_metadata.get("first_name"),
                    "last_name": user_metadata.get("last_name"),
                    "email": email
                }
            
            return {
                "id": user_id,
                "email": email,
                "username": user_metadata.get("username"),
                "first_name": user_metadata.get("first_name"),
                "last_name": user_metadata.get("last_name"),
                "created_at": auth_response.user.created_at
            }
                        
        except Exception as e:
            print(f"❌ Detailed error creating user: {e}")
            print(f"Error type: {type(e)}")
            
            # Check for specific Supabase errors
            error_message = str(e).lower()
            if "email" in error_message and "invalid" in error_message:
                print("❌ Email validation failed at Supabase level")
            elif "already" in error_message or "exists" in error_message:
                print("❌ User already exists")
            elif "policy" in error_message or "row-level security" in error_message:
                print("❌ Row Level Security policy violation")
            elif "foreign key" in error_message:
                print("❌ Foreign key constraint violation")
            elif "credentials" in error_message:
                print("❌ Authentication credentials issue")
            
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        try:
            email = email.strip().lower()
            
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Get additional profile data
                profile = self.supabase.table("user_profiles").select("*").eq("id", response.user.id).execute()
                
                if profile.data:
                    profile_data = profile.data[0]
                    return {
                        "id": response.user.id,
                        "email": response.user.email,
                        "username": profile_data.get("username"),
                        "first_name": profile_data.get("first_name"),
                        "last_name": profile_data.get("last_name"),
                        "created_at": response.user.created_at,
                        "last_login": response.user.last_sign_in_at
                    }
                else:
                    print(f"❌ No profile found for user {response.user.id}")
                    
                    # Try to create a missing profile for this orphaned user
                    print("🔄 Attempting to create missing profile...")
                    try:
                        # Get user metadata from auth user
                        auth_user = self.service_supabase.auth.admin.get_user_by_id(response.user.id)
                        if auth_user.user:
                            metadata = auth_user.user.user_metadata or {}
                            
                            profile_data = {
                                "id": response.user.id,
                                "username": metadata.get("username", response.user.email.split('@')[0]),
                                "first_name": metadata.get("first_name", "User"),
                                "last_name": metadata.get("last_name", "Profile"),
                                "email": response.user.email
                            }
                            
                            # Create the missing profile
                            create_result = self.service_supabase.table("user_profiles").insert(profile_data).execute()
                            
                            if create_result.data:
                                print("✅ Successfully created missing profile")
                                profile_data = create_result.data[0]
                                return {
                                    "id": response.user.id,
                                    "email": response.user.email,
                                    "username": profile_data.get("username"),
                                    "first_name": profile_data.get("first_name"),
                                    "last_name": profile_data.get("last_name"),
                                    "created_at": response.user.created_at,
                                    "last_login": response.user.last_sign_in_at
                                }
                            else:
                                print("❌ Failed to create missing profile")
                    except Exception as profile_error:
                        print(f"❌ Error creating missing profile: {profile_error}")
                    
                    return None
            
            return None
            
        except Exception as e:
            print(f"❌ Error authenticating user: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            profile = self.supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if profile.data:
                return profile.data[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None

    def logout_user(self) -> bool:
        """Logout current user"""
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            print(f"❌ Error logging out: {e}")
            return False

    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user"""
        try:
            user = self.supabase.auth.get_user()
            if user and user.user:
                profile = self.supabase.table("user_profiles").select("*").eq("id", user.user.id).execute()
                
                if profile.data:
                    profile_data = profile.data[0]
                    return {
                        "id": user.user.id,
                        "email": user.user.email,
                        "username": profile_data.get("username"),
                        "first_name": profile_data.get("first_name"),
                        "last_name": profile_data.get("last_name"),
                        "created_at": user.user.created_at,
                        "last_login": user.user.last_sign_in_at
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting current user: {e}")
            return None