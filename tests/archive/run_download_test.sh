#!/bin/bash

# 🧪 Z-Library EPUB Download Test Runner
# =====================================

set -e  # Exit on error

echo "🚀 Z-Library EPUB Download Test Runner"
echo "======================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔷${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "Not in zlibrary project root directory!"
    exit 1
fi

print_status "Checking project structure..."

# Create tests directory if it doesn't exist
if [[ ! -d "tests" ]]; then
    print_status "Creating tests directory..."
    mkdir -p tests
fi

# Create downloads directory if it doesn't exist
if [[ ! -d "downloads" ]]; then
    print_status "Creating downloads directory..."
    mkdir -p downloads
fi

# Check if virtual environment exists
if [[ ! -d ".venv" ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."
pip install -e .

# Additional dependencies for testing
print_status "Installing testing dependencies..."
pip install aiohttp python-dotenv

print_success "Environment setup complete!"

# Check for .env file and credentials
if [[ ! -f ".env" ]]; then
    print_warning ".env file not found!"
    echo
    echo "📝 To set up credentials securely:"
    echo "1. Copy the template: cp env.template .env"
    echo "2. Edit .env with your Z-Library credentials"
    echo "3. The .env file will be ignored by git for security"
    echo
    
    if [[ -f "env.template" ]]; then
        read -p "📋 Copy env.template to .env now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp env.template .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your credentials before running the test again"
            echo
            echo "Required credentials:"
            echo "  ZLOGIN=your-email@example.com"
            echo "  ZPASSW=your-password"
            echo
            exit 1
        fi
    fi
elif [[ -z "$ZLOGIN" ]] || [[ -z "$ZPASSW" ]]; then
    print_warning "Z-Library credentials not set in .env file"
    print_warning "Please edit .env file with your credentials:"
    echo "  ZLOGIN=your-email@example.com"
    echo "  ZPASSW=your-password"
    echo
fi

# Run the test
print_status "Running Z-Library EPUB download test..."
echo

cd tests
python test_real_download.py

# Check test result
TEST_RESULT=$?

echo
if [[ $TEST_RESULT -eq 0 ]]; then
    print_success "Test completed successfully!"
    
    # Check if any EPUB files were downloaded
    if [[ -d "../downloads" ]] && [[ $(ls -1 ../downloads/*.epub 2>/dev/null | wc -l) -gt 0 ]]; then
        print_success "EPUB files downloaded:"
        ls -la ../downloads/*.epub
    fi
else
    print_error "Test failed with exit code: $TEST_RESULT"
fi

# Deactivate virtual environment
deactivate

echo
print_status "Test runner completed."
exit $TEST_RESULT 