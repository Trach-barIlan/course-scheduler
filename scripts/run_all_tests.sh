#!/bin/bash

# 🧪 Schedgic Test Runner
# Runs all tests for both backend and frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run backend tests
run_backend_tests() {
    print_status "Running backend tests..."
    
    if [ ! -d "backend" ]; then
        print_error "Backend directory not found!"
        return 1
    fi
    
    cd backend
    
    # Check if Python is available
    if ! command_exists python3; then
        print_error "Python 3 is not installed!"
        return 1
    fi
    
    # Check if requirements are installed
    if [ ! -d "venv" ] && [ ! -f "requirements.txt" ]; then
        print_warning "Virtual environment not found. Installing dependencies..."
        pip install -r requirements.txt
    fi
    
    # Run tests
    if python3 run_tests.py; then
        print_success "Backend tests passed!"
        cd ..
        return 0
    else
        print_error "Backend tests failed!"
        cd ..
        return 1
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running frontend tests..."
    
    if [ ! -d "frontend" ]; then
        print_error "Frontend directory not found!"
        return 1
    fi
    
    cd frontend
    
    # Check if Node.js is available
    if ! command_exists node; then
        print_error "Node.js is not installed!"
        return 1
    fi
    
    # Check if npm is available
    if ! command_exists npm; then
        print_error "npm is not installed!"
        return 1
    fi
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_warning "Installing frontend dependencies..."
        npm install
    fi
    
    # Run tests with coverage
    if npm run test:coverage; then
        print_success "Frontend tests passed!"
        cd ..
        return 0
    else
        print_error "Frontend tests failed!"
        cd ..
        return 1
    fi
}

# Function to generate test report
generate_report() {
    print_status "Generating test report..."
    
    echo "## 🧪 Schedgic Test Report" > test_report.md
    echo "Generated on: $(date)" >> test_report.md
    echo "" >> test_report.md
    
    # Backend coverage info
    if [ -f "backend/htmlcov/index.html" ]; then
        echo "### Backend Coverage" >> test_report.md
        echo "- Coverage report: backend/htmlcov/index.html" >> test_report.md
        echo "" >> test_report.md
    fi
    
    # Frontend coverage info
    if [ -d "frontend/coverage" ]; then
        echo "### Frontend Coverage" >> test_report.md
        echo "- Coverage report: frontend/coverage/lcov-report/index.html" >> test_report.md
        echo "" >> test_report.md
    fi
    
    print_success "Test report generated: test_report.md"
}

# Main execution
main() {
    echo "🧪 Schedgic Test Suite"
    echo "======================"
    echo ""
    
    # Store original directory
    ORIGINAL_DIR=$(pwd)
    
    # Track test results
    BACKEND_PASSED=false
    FRONTEND_PASSED=false
    
    # Run backend tests
    if run_backend_tests; then
        BACKEND_PASSED=true
    fi
    
    # Run frontend tests
    if run_frontend_tests; then
        FRONTEND_PASSED=true
    fi
    
    # Generate report
    cd "$ORIGINAL_DIR"
    generate_report
    
    # Summary
    echo ""
    echo "📊 Test Summary"
    echo "==============="
    
    if [ "$BACKEND_PASSED" = true ]; then
        print_success "Backend: PASSED"
    else
        print_error "Backend: FAILED"
    fi
    
    if [ "$FRONTEND_PASSED" = true ]; then
        print_success "Frontend: PASSED"
    else
        print_error "Frontend: FAILED"
    fi
    
    echo ""
    
    # Overall result
    if [ "$BACKEND_PASSED" = true ] && [ "$FRONTEND_PASSED" = true ]; then
        print_success "🎉 All tests passed!"
        exit 0
    else
        print_error "❌ Some tests failed!"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --backend-only)
        print_status "Running backend tests only..."
        run_backend_tests
        ;;
    --frontend-only)
        print_status "Running frontend tests only..."
        run_frontend_tests
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  --backend-only    Run only backend tests"
        echo "  --frontend-only   Run only frontend tests"
        echo "  --help, -h        Show this help message"
        echo ""
        echo "Default: Run all tests"
        exit 0
        ;;
    *)
        main
        ;;
esac 