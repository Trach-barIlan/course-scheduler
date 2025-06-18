import os
import hashlib
import secrets
from datetime import datetime, timedelta
from supabase import create_client, Client
from typing import Optional, Dict, Any

class AuthManager:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key or not service_key:
            raise ValueError("Missing required Supabase environment variables")
        
        self.supabase: Client = create_client(url, key)
        self.service_supabase: Client = create_client(url, service_key)
        print("✅ AuthManager initialized successfully")

    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return salt + password_hash.hex()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if len(hashed) < 32:
            return False
        salt = hashed[:32]
        stored_hash = hashed[32:]
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return password_hash.hex() == stored_hash

    def create_user(self, username: str, email: str, password: str, first_name: str, last_name: str) -> Optional[Dict]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing = self.service_supabase.table("user_profiles").select("id").eq("email", email).execute()
            if existing.data:
                raise ValueError("Email already exists")
            
            existing = self.service_supabase.table("user_profiles").select("id").eq("username", username).execute()
            if existing.data:
                raise ValueError("Username already exists")

            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user profile
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "first_name": first_name,
                "last_name": last_name
            }
            
            result = self.service_supabase.table("user_profiles").insert(user_data).execute()
            
            if result.data:
                user = result.data[0]
                # Remove password hash from response
                user.pop('password_hash', None)
                return user
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            raise e

    def authenticate_user(self, username_or_email: str, password: str) -> Optional[Dict]:
        """Authenticate user with username/email and password"""
        try:
            # Try to find user by email first, then username
            user_result = self.service_supabase.table("user_profiles").select("*").eq("email", username_or_email).execute()
            
            if not user_result.data:
                user_result = self.service_supabase.table("user_profiles").select("*").eq("username", username_or_email).execute()
            
            if not user_result.data:
                return None
            
            user = user_result.data[0]
            
            # Verify password
            if self.verify_password(password, user['password_hash']):
                # Update last login
                self.service_supabase.table("user_profiles").update({
                    "last_login": datetime.now().isoformat()
                }).eq("id", user['id']).execute()
                
                # Remove password hash from response
                user.pop('password_hash', None)
                return user
            
            return None
            
        except Exception as e:
            print(f"❌ Error authenticating user: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            result = self.service_supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if result.data:
                user = result.data[0]
                user.pop('password_hash', None)
                return user
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None