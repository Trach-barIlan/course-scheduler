#!/usr/bin/env python3
"""
Test runner script for Schedgic backend tests.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all backend tests with coverage."""
    print("🧪 Running Schedgic Backend Tests...")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--verbose",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode

def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"🧪 Running specific test: {test_file}")
    print("=" * 50)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    cmd = [sys.executable, "-m", "pytest", f"tests/{test_file}", "--verbose"]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Test passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test failed with exit code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        exit_code = run_specific_test(test_file)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code) 