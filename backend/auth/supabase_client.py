import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import re

class SupabaseClient:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(url, key)

    def validate_email_format(self, email: str) -> bool:
        """Validate email format using a more comprehensive regex"""
        pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(pattern, email) is not None

    def create_user(self, email: str, password: str, user_metadata: Dict[str, Any]) -> Optional[Dict]:
        """Create a new user with Supabase Auth"""
        try:
            # Validate email format before sending to Supabase
            if not self.validate_email_format(email):
                print(f"Invalid email format: {email}")
                return None

            # Clean and validate the email
            email = email.strip().lower()
            
            # Check if username already exists
            existing_user = self.supabase.table("user_profiles").select("username").eq("username", user_metadata.get("username")).execute()
            if existing_user.data:
                print(f"Username already exists: {user_metadata.get('username')}")
                return None

            print(f"Attempting to create user with email: {email}")
            
            # Create the auth user first
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata
                }
            })
            
            print(f"Supabase auth response: {response}")
            
            if response.user:
                # Sign in the user immediately to get proper authentication context
                sign_in_response = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if sign_in_response.user:
                    print(f"User signed in successfully: {sign_in_response.user.id}")
                    
                    # Now create the profile record with the authenticated user context
                    profile_data = {
                        "id": response.user.id,
                        "username": user_metadata.get("username"),
                        "first_name": user_metadata.get("first_name"),
                        "last_name": user_metadata.get("last_name"),
                        "email": email
                    }
                    
                    print(f"Creating profile with data: {profile_data}")
                    
                    # Use the authenticated session to create the profile
                    profile_response = self.supabase.table("user_profiles").insert(profile_data).execute()
                    print(f"Profile creation response: {profile_response}")
                    
                    return {
                        "id": response.user.id,
                        "email": response.user.email,
                        "username": user_metadata.get("username"),
                        "first_name": user_metadata.get("first_name"),
                        "last_name": user_metadata.get("last_name"),
                        "created_at": response.user.created_at
                    }
                else:
                    print("Failed to sign in after registration")
                    return None
            else:
                print("No user returned from Supabase")
                return None
            
        except Exception as e:
            print(f"Detailed error creating user: {e}")
            print(f"Error type: {type(e)}")
            
            # Check for specific Supabase errors
            error_message = str(e).lower()
            if "email" in error_message and "invalid" in error_message:
                print("Email validation failed at Supabase level")
            elif "already" in error_message or "exists" in error_message:
                print("User already exists")
            elif "policy" in error_message:
                print("Row Level Security policy violation")
            
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
            
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            profile = self.supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if profile.data:
                return profile.data[0]
            
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def logout_user(self) -> bool:
        """Logout current user"""
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            print(f"Error logging out: {e}")
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
            print(f"Error getting current user: {e}")
            return None