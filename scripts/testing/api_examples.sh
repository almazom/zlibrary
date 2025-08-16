#!/bin/bash

# =============================================================================
# Z-Library API Usage Examples - JSON Interface
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_SCRIPT="$SCRIPT_DIR/zlib_book_search.sh"

# Colors for non-JSON output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_section() { echo -e "${CYAN}🔷 $*${NC}"; }
print_success() { echo -e "${GREEN}✅ $*${NC}"; }
print_error() { echo -e "${RED}❌ $*${NC}"; }

echo -e "${WHITE}Z-Library API Examples - JSON Interface${NC}"
echo "========================================"
echo

# Example 1: Basic JSON Search
print_section "Example 1: Basic JSON Search"
echo "Command: $API_SCRIPT --json \"python programming\""
echo "Response:"
$API_SCRIPT --json "python programming" 2>/dev/null | jq '.' || print_error "Search failed - check credentials in .env file"
echo

# Example 2: Search with filters (JSON)
print_section "Example 2: Search with Filters (JSON)"
echo "Command: $API_SCRIPT --json -f pdf -l english -c 3 \"machine learning\""
echo "Response:"
$API_SCRIPT --json -f pdf -l english -c 3 "machine learning" 2>/dev/null | jq '.' || print_error "Filtered search failed"
echo

# Example 3: Check limits (JSON)
print_section "Example 3: Check Download Limits (JSON)"
echo "Command: $API_SCRIPT --json --limits"
echo "Response:"
$API_SCRIPT --json --limits 2>/dev/null | jq '.' || print_error "Limits check failed"
echo

# Example 4: Error handling (JSON)
print_section "Example 4: Error Handling (JSON)"
echo "Command: $API_SCRIPT --json \"\" (empty query)"
echo "Response:"
$API_SCRIPT --json "" 2>/dev/null | jq '.' || echo '{"status": "error", "message": "Empty query provided"}'
echo

# Example 5: Download attempt (JSON)
print_section "Example 5: Download Attempt (JSON)"
echo "Command: $API_SCRIPT --json --download -f epub \"test book\""
echo "Response:"
$API_SCRIPT --json --download -f epub -o "/tmp/zlib_test" "test book" 2>/dev/null | jq '.' || print_error "Download failed"
echo

# Example 6: Integration example
print_section "Example 6: Integration Script Example"
cat << 'EOF'
#!/bin/bash
# Integration example - using the API from another script

search_books() {
    local query="$1"
    local format="${2:-pdf}"
    
    # Call Z-Library API and parse JSON
    local result=$(./zlib_book_search.sh --json -f "$format" "$query" 2>/dev/null)
    local status=$(echo "$result" | jq -r '.status')
    
    if [[ "$status" == "success" ]]; then
        echo "Found books:"
        echo "$result" | jq -r '.results[] | "- \(.name) by \(.authors | join(", "))"'
    else
        echo "Search failed: $(echo "$result" | jq -r '.message')"
    fi
}

# Usage
search_books "python programming" "pdf"
EOF
echo

# Example 7: Python integration
print_section "Example 7: Python Integration Example"
cat << 'EOF'
#!/usr/bin/env python3
import subprocess
import json
import sys

def search_books(query, format_type="pdf", count=5):
    """Search books using Z-Library CLI API"""
    cmd = [
        "./zlib_book_search.sh", 
        "--json", 
        "-f", format_type,
        "-c", str(count),
        query
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        try:
            return json.loads(e.stdout)
        except:
            return {"status": "error", "message": str(e)}

def check_limits():
    """Check download limits"""
    cmd = ["./zlib_book_search.sh", "--json", "--limits"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        try:
            return json.loads(e.stdout)
        except:
            return {"status": "error", "message": str(e)}

# Usage example
if __name__ == "__main__":
    # Search for books
    books = search_books("data science", "pdf", 3)
    
    if books["status"] == "success":
        print(f"Found {books['total_results']} books:")
        for book in books["results"]:
            print(f"- {book['name']}")
    else:
        print(f"Error: {books['message']}")
    
    # Check limits
    limits = check_limits()
    if limits["status"] == "success":
        remaining = limits["limits"]["daily_remaining"]
        print(f"Downloads remaining: {remaining}")
    else:
        print(f"Cannot check limits: {limits['message']}")
EOF
echo

# Example 8: curl/HTTP API wrapper
print_section "Example 8: HTTP API Wrapper Example"
cat << 'EOF'
#!/bin/bash
# Simple HTTP API wrapper using netcat or socat

# Start a simple HTTP server that wraps the CLI tool
start_api_server() {
    local port="${1:-8080}"
    
    echo "Starting Z-Library API server on port $port..."
    
    while true; do
        # Simple HTTP response
        {
            echo "HTTP/1.1 200 OK"
            echo "Content-Type: application/json"
            echo "Access-Control-Allow-Origin: *"
            echo ""
            
            # Parse query from HTTP request
            read request
            query=$(echo "$request" | grep -o 'q=[^&]*' | cut -d'=' -f2 | sed 's/%20/ /g')
            
            if [[ -n "$query" ]]; then
                ./zlib_book_search.sh --json "$query" 2>/dev/null
            else
                echo '{"status": "error", "message": "No query provided"}'
            fi
        } | nc -l -p $port
    done
}

# Usage: start_api_server 8080
# Then: curl "http://localhost:8080/?q=python+programming"
EOF
echo

print_section "Testing Summary"
echo "To test all examples above:"
echo "1. Ensure credentials are set in .env file"
echo "2. Install dependencies: pip install aiohttp aiofiles"
echo "3. Run: chmod +x $API_SCRIPT"
echo "4. Test: $API_SCRIPT --json --limits"
echo

if [[ -f "$SCRIPT_DIR/../.env" ]]; then
    print_success "Found .env file"
else
    print_error "No .env file found - create from env.template"
fi

if command -v jq >/dev/null; then
    print_success "jq is available for JSON parsing"
else
    echo "💡 Install jq for better JSON parsing: apt install jq / brew install jq"
fi

echo
echo "🚀 Ready for API integration!"