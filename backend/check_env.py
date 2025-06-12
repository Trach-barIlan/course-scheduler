import os
from dotenv import load_dotenv

def check_environment():
    """Check if environment variables are properly set"""
    print("🔍 Checking Environment Configuration...")
    print("=" * 50)
    
    # Load .env file
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Show partial value for security
            if 'KEY' in var:
                display_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    print("-" * 50)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\n📝 To fix this:")
        print("1. Create a .env file in the backend folder")
        print("2. Add the following variables:")
        print("   SUPABASE_URL=your_supabase_project_url")
        print("   SUPABASE_ANON_KEY=your_supabase_anon_key")
        print("   SECRET_KEY=your_secret_key_here")
        print("\n🔗 Get your Supabase credentials from:")
        print("   Supabase Dashboard → Settings → API")
        return False
    else:
        print("✅ All environment variables are set!")
        return True

def test_supabase_connection():
    """Test connection to Supabase"""
    print("\n🔗 Testing Supabase Connection...")
    print("=" * 50)
    
    try:
        from auth.supabase_client import SupabaseClient
        client = SupabaseClient()
        
        # Try a simple query
        result = client.supabase.table("user_profiles").select("id", count="exact").execute()
        print("✅ Successfully connected to Supabase!")
        print(f"📊 Current user count: {result.count}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("\n🔧 Possible issues:")
        print("1. Check your SUPABASE_URL and SUPABASE_ANON_KEY")
        print("2. Make sure your Supabase project is active")
        print("3. Verify the database migration was run successfully")
        return False

if __name__ == "__main__":
    env_ok = check_environment()
    if env_ok:
        test_supabase_connection()