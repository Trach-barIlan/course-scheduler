import os
from supabase import create_client, Client
from typing import Optional, Dict, Any

class SupabaseClient:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(url, key)

    def create_user(self, email: str, password: str, user_metadata: Dict[str, Any]) -> Optional[Dict]:
        """Create a new user with Supabase Auth"""
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata
                }
            })
            
            if response.user:
                # Also create a profile record in our custom table
                profile_data = {
                    "id": response.user.id,
                    "username": user_metadata.get("username"),
                    "first_name": user_metadata.get("first_name"),
                    "last_name": user_metadata.get("last_name"),
                    "email": email
                }
                
                self.supabase.table("user_profiles").insert(profile_data).execute()
                
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "username": user_metadata.get("username"),
                    "first_name": user_metadata.get("first_name"),
                    "last_name": user_metadata.get("last_name"),
                    "created_at": response.user.created_at
                }
            
            return None
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        try:
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