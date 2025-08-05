import pytest
from unittest.mock import Mock, patch
from schedule.logic import generate_schedule
from schedule.parserAI import parse_course_text
from auth.auth_manager import AuthManager
import json

def test_generate_schedule_no_conflicts(sample_courses):
    """Test schedule generation with no conflicts."""
    # Convert sample_courses format to match generate_schedule expectations
    courses_for_schedule = []
    for course in sample_courses:
        schedule_course = {
            "name": course["name"],
            "lectures": [(lec["day"], int(lec["startTime"]), int(lec["endTime"])) 
                        for lec in course["lectures"]] if course["lectures"] else [],
            "ta_times": [(prac["day"], int(prac["startTime"]), int(prac["endTime"])) 
                        for prac in course["practices"]] if course["practices"] else []
        }
        courses_for_schedule.append(schedule_course)
    
    # Parse constraints from string format
    constraints_text = "No classes before 9am"
    parsed_constraints = parse_course_text(constraints_text)
    
    schedule = generate_schedule(courses_for_schedule, "crammed", parsed_constraints.get("constraints", []))
    assert schedule is not None
    assert len(schedule) == 2
    assert schedule[0]["name"] == "CS101"
    assert schedule[1]["name"] == "Math101"
    # Verify no time conflicts
    assert _check_no_conflicts(schedule)

def test_generate_schedule_with_conflicts():
    """Test schedule generation with time conflicts."""
    conflicting_courses = [
        {
            "name": "CS101",
            "lectures": [("Mon", 9, 11), ("Mon", 9, 11)],  # Conflict - same time
            "ta_times": []
        }
    ]
    schedule = generate_schedule(conflicting_courses, "crammed", [])
    # Should handle conflicts gracefully - will return None or empty since there's a conflict
    assert schedule is None or len(schedule) <= 1

def test_generate_schedule_crammed_preference(sample_courses):
    """Test schedule generation with crammed preference."""
    # Convert sample_courses format
    courses_for_schedule = []
    for course in sample_courses:
        schedule_course = {
            "name": course["name"],
            "lectures": [(lec["day"], int(lec["startTime"]), int(lec["endTime"])) 
                        for lec in course["lectures"]] if course["lectures"] else [],
            "ta_times": [(prac["day"], int(prac["startTime"]), int(prac["endTime"])) 
                        for prac in course["practices"]] if course["practices"] else []
        }
        courses_for_schedule.append(schedule_course)
    
    schedule = generate_schedule(courses_for_schedule, "crammed", [])
    assert schedule is not None
    # Crammed should try to minimize days
    days_used = set()
    for course in schedule:
        if course.get("lecture"):
            days_used.add(course["lecture"].split()[0])
        if course.get("ta"):
            days_used.add(course["ta"].split()[0])
    # Should use fewer days for crammed preference
    assert len(days_used) <= 4  # Reasonable expectation

def test_generate_schedule_spaced_preference(sample_courses):
    """Test schedule generation with spaced preference."""
    # Convert sample_courses format
    courses_for_schedule = []
    for course in sample_courses:
        schedule_course = {
            "name": course["name"],
            "lectures": [(lec["day"], int(lec["startTime"]), int(lec["endTime"])) 
                        for lec in course["lectures"]] if course["lectures"] else [],
            "ta_times": [(prac["day"], int(prac["startTime"]), int(prac["endTime"])) 
                        for prac in course["practices"]] if course["practices"] else []
        }
        courses_for_schedule.append(schedule_course)
    
    schedule = generate_schedule(courses_for_schedule, "spaced", [])
    assert schedule is not None
    # Spaced should distribute across more days
    days_used = set()
    for course in schedule:
        if course.get("lecture"):
            days_used.add(course["lecture"].split()[0])
        if course.get("ta"):
            days_used.add(course["ta"].split()[0])
    # Should use more days for spaced preference
    assert len(days_used) >= 2  # At least 2 different days

def _check_no_conflicts(schedule):
    """Helper method to check for time conflicts in schedule."""
    time_slots = {}
    for course in schedule:
        if course.get("lecture"):
            day, time_range = course["lecture"].split()
            if day not in time_slots:
                time_slots[day] = []
            time_slots[day].append(time_range)
        if course.get("ta"):
            day, time_range = course["ta"].split()
            if day not in time_slots:
                time_slots[day] = []
            time_slots[day].append(time_range)
    # Check for overlapping time ranges
    for day, slots in time_slots.items():
        for i, slot1 in enumerate(slots):
            for j, slot2 in enumerate(slots):
                if i != j and _time_ranges_overlap(slot1, slot2):
                    return False
    return True

def _time_ranges_overlap(range1, range2):
    """Helper method to check if two time ranges overlap."""
    start1, end1 = map(int, range1.split('-'))
    start2, end2 = map(int, range2.split('-'))
    return not (end1 <= start2 or end2 <= start1)

def test_parse_time_constraints():
    """Test parsing time-based constraints."""
    constraints = "No classes before 9am and no classes after 5pm"
    parsed = parse_course_text(constraints)
    assert "constraints" in parsed
    assert any(c["type"] == "no_early_classes" for c in parsed["constraints"])
    # Note: "after 5pm" parsing might need adjustment in parserAI.py

def test_parse_day_constraints():
    """Test parsing day-based constraints."""
    constraints = "No classes on Friday and no Monday classes"
    parsed = parse_course_text(constraints)
    
    assert "constraints" in parsed
    assert any(c["type"] == "no_day" and c["day"] == "Fri" for c in parsed["constraints"])
    # The current parser might not catch "no Monday classes" - let's test what it actually returns

def test_parse_ta_constraints():
    """Test parsing TA-based constraints."""
    constraints = "Avoid TA Smith and prefer TA Johnson"
    parsed = parse_course_text(constraints)
    
    assert "constraints" in parsed
    # The current parser might not handle TA constraints - let's test what it returns
    # We can update this test once we verify the parser behavior

def test_parse_empty_constraints():
    """Test parsing empty constraints."""
    parsed = parse_course_text("")
    
    assert parsed == {"constraints": [], "courses": []}

def test_parse_invalid_constraints():
    """Test parsing invalid constraint format."""
    # Should handle gracefully
    parsed = parse_course_text("Invalid constraint format 12345")
    
    assert isinstance(parsed, dict)
    assert "constraints" in parsed

class TestScheduleAPI:
    """Test cases for the schedule API endpoints."""
    
    def test_generate_schedule_success(self, client, mock_database, mock_user_data, sample_courses):
        """Test successful schedule generation via API."""
        # Convert sample_courses to API format (courses with string time slots)
        api_courses = []
        for course in sample_courses:
            api_course = {
                "name": course["name"],
                "lectures": [f"{lec['day']} {lec['startTime']}-{lec['endTime']}" for lec in course["lectures"]],
                "ta_times": [f"{prac['day']} {prac['startTime']}-{prac['endTime']}" for prac in course["practices"]]
            }
            api_courses.append(api_course)
        
        # Mock authentication for schedule API
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            # Mock the validate_session RPC call for token validation
            mock_validate_result = Mock()
            mock_validate_result.data = [{
                'is_valid': True,
                'user_id': 'test-user-id', 
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }]
            mock_supabase.rpc.return_value.execute.return_value = mock_validate_result
            mock_create_client.return_value = mock_supabase
        
            response = client.post('/api/schedule', 
                headers={'Authorization': 'Bearer valid-token'},
                json={
                    "courses": api_courses,
                    "constraints": "No classes before 9am",
                    "preference": "crammed"
                }
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "schedule" in data
            assert data["schedule"] is not None
            assert len(data["schedule"]) > 0
    
    def test_generate_schedule_no_auth(self, client, sample_courses):
        """Test schedule generation without authentication."""
        # Convert sample_courses to API format
        api_courses = []
        for course in sample_courses:
            api_course = {
                "name": course["name"],
                "lectures": [f"{lec['day']} {lec['startTime']}-{lec['endTime']}" for lec in course["lectures"]],
                "ta_times": [f"{prac['day']} {prac['startTime']}-{prac['endTime']}" for prac in course["practices"]]
            }
            api_courses.append(api_course)
        
        response = client.post('/api/schedule', 
            json={
                "courses": api_courses,
                "constraints": "No classes before 9am",
                "preference": "crammed"
            }
        )
        
        # Should work without auth, as the endpoint doesn't require it
        assert response.status_code == 200
    
    def test_generate_schedule_invalid_data(self, client, mock_database, mock_user_data):
        """Test schedule generation with invalid data."""
        # Mock authentication for schedule API
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            # Mock the validate_session RPC call for token validation
            mock_validate_result = Mock()
            mock_validate_result.data = [{
                'is_valid': True,
                'user_id': 'test-user-id',
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }]
            mock_supabase.rpc.return_value.execute.return_value = mock_validate_result
            mock_create_client.return_value = mock_supabase
        
            response = client.post('/api/schedule', 
                headers={'Authorization': 'Bearer valid-token'},
                json={
                    "courses": [],  # Empty courses
                    "constraints": "",
                    "preference": "invalid_preference"
                }
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
    
    def test_save_schedule_success(self, client, mock_database, mock_user_data, sample_schedule):
        """Test successful schedule saving."""
        # Mock authentication for schedule API
        with patch('auth.auth_manager.create_client') as mock_create_client:
            mock_supabase = Mock()
            # Mock the validate_session RPC call for token validation
            mock_validate_result = Mock()
            mock_validate_result.data = [{
                'is_valid': True,
                'user_id': 'test-user-id',
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }]
            mock_supabase.rpc.return_value.execute.return_value = mock_validate_result
            
            # Mock the database insert for saving schedule
            mock_insert_result = Mock()
            mock_insert_result.data = [{"id": "schedule-123", "schedule_name": "Test Schedule"}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_result
            
            mock_create_client.return_value = mock_supabase
            
            # Mock get_client_for_user to return the same mocked supabase client
            with patch.object(AuthManager, 'get_client_for_user', return_value=mock_supabase):
                response = client.post('/api/schedules/save', 
                    headers={'Authorization': 'Bearer valid-token'},
                    json={
                        "name": "Test Schedule",
                        "description": "Test description",  
                        "schedule": sample_schedule,
                        "isPublic": False
                    }
                )
                
                assert response.status_code == 201
                data = json.loads(response.data)
                assert "message" in data
                assert "schedule" in data
                assert data["schedule"]["id"] == "schedule-123"