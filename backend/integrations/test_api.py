#!/usr/bin/env python3
"""
Test script to verify the new Supabase courses API is working
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

BASE_URL = "http://localhost:5000/api"

def get_auth_token():
    """Get authentication token for testing"""
    # You'll need to replace this with actual login credentials
    login_data = {
        "email": "test@example.com", 
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get('token')
        else:
            print(f"Failed to get auth token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def test_autocomplete(token=None, query="מדע"):
    """Test the autocomplete endpoint"""
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(
            f"{BASE_URL}/courses/autocomplete",
            params={'q': query, 'limit': 5},
            headers=headers
        )
        
        print(f"Autocomplete Test (query='{query}'):")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        print("-" * 50)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing autocomplete: {e}")
        return False

def test_search(token=None, query="מדע"):
    """Test the search endpoint"""
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(
            f"{BASE_URL}/courses/search",
            params={'q': query, 'limit': 3},
            headers=headers
        )
        
        print(f"Search Test (query='{query}'):")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Total Results: {data.get('total_results')}")
            
            courses = data.get('courses', [])
            print(f"Sample courses:")
            for i, course in enumerate(courses[:2]):
                print(f"  {i+1}. {course.get('id')} - {course.get('name')}")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
        print("-" * 50)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing search: {e}")
        return False

def test_filters(token=None):
    """Test the filters endpoint"""
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(f"{BASE_URL}/courses/filters", headers=headers)
        
        print("Filters Test:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            filters = data.get('filters', {})
            print(f"Available filters:")
            print(f"  - Departments: {len(filters.get('departments', []))}")
            print(f"  - Categories: {len(filters.get('categories', []))}")
            print(f"  - Lecturers: {len(filters.get('lecturers', []))}")
            print(f"  - Semesters: {filters.get('semesters', [])}")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
        print("-" * 50)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing filters: {e}")
        return False

def test_without_auth():
    """Test endpoints without authentication to see error messages"""
    print("Testing without authentication...")
    
    try:
        response = requests.get(f"{BASE_URL}/courses/autocomplete?q=test")
        print(f"Autocomplete without auth: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

if __name__ == "__main__":
    print("🧪 Testing Supabase Courses API")
    print("=" * 50)
    
    # Test without auth first
    test_without_auth()
    
    # Try to get auth token
    token = get_auth_token()
    
    if not token:
        print("⚠️ No auth token available - testing with public access")
        print("Note: Some endpoints may require authentication")
        token = None
    else:
        print("✅ Got auth token for testing")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_autocomplete(token):
        tests_passed += 1
    
    if test_search(token):
        tests_passed += 1
    
    if test_filters(token):
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
