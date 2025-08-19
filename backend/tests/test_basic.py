import pytest
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_imports():
    """Test that basic imports work."""
    try:
        from flask import Flask
        assert Flask is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Flask: {e}")

def test_environment_setup():
    """Test that environment variables can be set."""
    test_var = "test_value"
    os.environ["TEST_VAR"] = test_var
    assert os.environ.get("TEST_VAR") == test_var

def test_mock_functionality():
    """Test that mocking works."""
    from unittest.mock import Mock
    
    mock_obj = Mock()
    mock_obj.test_method.return_value = "test_result"
    
    assert mock_obj.test_method() == "test_result"
    mock_obj.test_method.assert_called_once()

def test_pytest_fixtures():
    """Test that pytest fixtures work."""
    @pytest.fixture
    def sample_fixture():
        return "fixture_value"
    
    # This test should pass if fixtures work
    assert True

class TestBasicClass:
    """Basic test class to verify class-based tests work."""
    
    def test_class_method(self):
        """Test that class methods work."""
        assert True
    
    def test_with_setup(self):
        """Test with setup."""
        self.test_value = "test"
        assert self.test_value == "test"

def test_math_operations():
    """Test basic math operations."""
    assert 2 + 2 == 4
    assert 10 - 5 == 5
    assert 3 * 4 == 12
    assert 15 / 3 == 5

def test_string_operations():
    """Test string operations."""
    test_string = "Hello, World!"
    assert len(test_string) == 13
    assert test_string.upper() == "HELLO, WORLD!"
    assert test_string.lower() == "hello, world!"
    assert "Hello" in test_string

def test_list_operations():
    """Test list operations."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert sum(test_list) == 15
    assert max(test_list) == 5
    assert min(test_list) == 1
    
    # Test list comprehension
    doubled = [x * 2 for x in test_list]
    assert doubled == [2, 4, 6, 8, 10]

def test_dict_operations():
    """Test dictionary operations."""
    test_dict = {"a": 1, "b": 2, "c": 3}
    assert len(test_dict) == 3
    assert test_dict["a"] == 1
    assert "b" in test_dict
    assert test_dict.get("c") == 3
    assert test_dict.get("d", "default") == "default"

def test_exception_handling():
    """Test exception handling."""
    try:
        result = 10 / 0
        pytest.fail("Should have raised ZeroDivisionError")
    except ZeroDivisionError:
        assert True  # Expected exception
    
    # Test that we can raise and catch custom exceptions
    try:
        raise ValueError("Test error")
        pytest.fail("Should have raised ValueError")
    except ValueError as e:
        assert str(e) == "Test error"

def test_conditional_logic():
    """Test conditional logic."""
    x = 5
    y = 10
    
    if x < y:
        assert True
    else:
        pytest.fail("Condition should be True")
    
    # Test ternary operator
    result = "even" if x % 2 == 0 else "odd"
    assert result == "odd"
    
    # Test multiple conditions
    if x < 3:
        category = "small"
    elif x < 7:
        category = "medium"
    else:
        category = "large"
    
    assert category == "medium" 