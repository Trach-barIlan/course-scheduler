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
        
        # Use service role client for all operations since we're managing auth ourselves
        self.supabase: Client = create_client(url, service_key)
        self.service_supabase: Client = create_client(url, service_key)
        print("✅ AuthManager initialized successfully with token-based auth")

    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)

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
        """Create a new user in user_profiles table"""
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
                
                # Initialize user statistics
                try:
                    stats_data = {
                        "user_id": user['id']
                    }
                    self.service_supabase.table("user_statistics").insert(stats_data).execute()
                except Exception as stats_error:
                    print(f"⚠️ Failed to create user statistics: {stats_error}")
                
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

    def login(self, username_or_email, password):
        user = self.authenticate_user(username_or_email, password)
        if user:
            return {"success": True, "user": user}
        else:
            return {"success": False, "error": "Invalid credentials"}

    def create_session(self, user_id: str, user_agent: str = None, ip_address: str = None) -> Optional[str]:
        """Create a new session for the user"""
        try:
            token = self.generate_session_token()
            expires_at = datetime.now() + timedelta(days=7)  # 7 day expiry
            
            # Call the database function to create session
            result = self.service_supabase.rpc('create_user_session', {
                'p_user_id': user_id,
                'p_token': token,
                'p_expires_at': expires_at.isoformat(),
                'p_user_agent': user_agent,
                'p_ip_address': ip_address
            }).execute()
            
            if result.data:
                print(f"✅ Session created for user: {user_id}")
                return token
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return None

    def validate_session(self, token: str) -> Optional[Dict]:
        """Validate a session token and return user data"""
        try:
            result = self.service_supabase.rpc('validate_session', {
                'p_token': token
            }).execute()
            
            if result.data and len(result.data) > 0:
                session_data = result.data[0]
                if session_data.get('is_valid'):
                    return {
                        'id': session_data['user_id'],
                        'username': session_data['username'],
                        'email': session_data['email'],
                        'first_name': session_data['first_name'],
                        'last_name': session_data['last_name']
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error validating session: {e}")
            return None

    def delete_session(self, token: str) -> bool:
        """Delete a session (logout)"""
        try:
            result = self.service_supabase.table("user_sessions").delete().eq("token", token).execute()
            return True
        except Exception as e:
            print(f"❌ Error deleting session: {e}")
            return False

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

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            self.service_supabase.rpc('cleanup_expired_sessions').execute()
        except Exception as e:
            print(f"❌ Error cleaning up sessions: {e}")

    def get_client_for_user(self, user_id: str) -> Client:
        """Get a Supabase client with user context set"""
        # Set user context for RLS
        try:
            self.service_supabase.rpc('set_current_user_id', {'user_id': user_id}).execute()
        except Exception as e:
            print(f"⚠️ Failed to set user context: {e}")
        return self.service_supabase

    def validate_token(self, token):
        user = self.get_user_by_id(token)
        if user:
            return {"success": True, "user": user}
        else:
            return {"success": False, "error": "Invalid token"}