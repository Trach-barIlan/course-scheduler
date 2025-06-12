import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/auth"

def test_registration():
    """Test user registration"""
    print("🧪 Testing User Registration...")
    
    test_user = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_user)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return test_user
        else:
            print("❌ Registration failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def test_login(user_data):
    """Test user login"""
    if not user_data:
        return None
        
    print("\n🧪 Testing User Login...")
    
    login_data = {
        "username_or_email": user_data["username"],
        "password": user_data["password"]
    }
    
    try:
        session = requests.Session()
        response = session.post(f"{BASE_URL}/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return session
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_profile(session):
    """Test getting user profile"""
    if not session:
        return
        
    print("\n🧪 Testing User Profile...")
    
    try:
        response = session.get(f"{BASE_URL}/me")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Profile fetch successful!")
        else:
            print("❌ Profile fetch failed!")
            
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")

def test_logout(session):
    """Test user logout"""
    if not session:
        return
        
    print("\n🧪 Testing User Logout...")
    
    try:
        response = session.post(f"{BASE_URL}/logout")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Logout successful!")
        else:
            print("❌ Logout failed!")
            
    except Exception as e:
        print(f"❌ Error during logout: {e}")

def run_full_test():
    """Run complete authentication test suite"""
    print("🚀 Starting Authentication Test Suite")
    print("=" * 50)
    
    # Test registration
    user_data = test_registration()
    
    # Test login
    session = test_login(user_data)
    
    # Test profile
    test_profile(session)
    
    # Test logout
    test_logout(session)
    
    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete!")

if __name__ == "__main__":
    print("Make sure your Flask server is running on http://127.0.0.1:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    run_full_test()