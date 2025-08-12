#!/bin/bash

# Test script for URL extraction functionality
# Tests the integration of Claude-powered URL extraction with book search

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}URL Extraction Test Suite${NC}"
echo -e "${BLUE}================================${NC}\n"

# Test URLs
GOODREADS_URL="https://www.goodreads.com/book/show/6483624"
PODPISNIE_URL="https://www.podpisnie.ru/books/maniac/"
AMAZON_URL="https://www.amazon.com/dp/B08V1YY9CM"

# Function to run test
run_test() {
    local name="$1"
    local url="$2"
    local options="${3:-}"
    
    echo -e "${YELLOW}Test: $name${NC}"
    echo -e "URL: $url"
    echo -e "Options: $options"
    echo "---"
    
    # Run the search
    result=$(./scripts/book_search.sh $options "$url" 2>/dev/null || echo '{"status": "error"}')
    
    # Check status
    status=$(echo "$result" | jq -r '.status' 2>/dev/null || echo "parse_error")
    
    if [[ "$status" == "success" ]]; then
        echo -e "${GREEN}✓ SUCCESS${NC}"
        
        # Extract key information
        title=$(echo "$result" | jq -r '.result.book_info.title // "N/A"' 2>/dev/null)
        authors=$(echo "$result" | jq -r '.result.book_info.authors[0] // "N/A"' 2>/dev/null)
        confidence=$(echo "$result" | jq -r '.result.confidence.score // 0' 2>/dev/null)
        format=$(echo "$result" | jq -r '.result.format_downloaded // "N/A"' 2>/dev/null)
        
        echo "  Title: $title"
        echo "  Authors: $authors"
        echo "  Confidence: $confidence"
        echo "  Format: $format"
    else
        echo -e "${RED}✗ FAILED${NC}"
        error=$(echo "$result" | jq -r '.result.message // .result.error // "Unknown error"' 2>/dev/null)
        echo "  Error: $error"
    fi
    
    echo ""
}

# Test 1: Goodreads URL with Claude extraction
echo -e "${BLUE}1. Goodreads URL Tests${NC}\n"
run_test "Goodreads with Claude extraction" "$GOODREADS_URL" "--claude-extract"
run_test "Goodreads without Claude extraction" "$GOODREADS_URL" ""

# Test 2: Podpisnie URL
echo -e "${BLUE}2. Podpisnie URL Tests${NC}\n"
run_test "Podpisnie standard" "$PODPISNIE_URL" ""
run_test "Podpisnie with Claude" "$PODPISNIE_URL" "--claude-extract"

# Test 3: Direct text search for comparison
echo -e "${BLUE}3. Direct Text Search${NC}\n"
run_test "Direct search" "Музпросвет Андрей Горохов" ""

# Test 4: Test with download flag
echo -e "${BLUE}4. Download Test${NC}\n"
run_test "Goodreads with download" "$GOODREADS_URL" "--claude-extract --download"

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Tests demonstrate URL extraction capabilities:"
echo -e "• Claude extraction enhances URL parsing"
echo -e "• Fallback to pattern matching when Claude unavailable"
echo -e "• Integration with Z-Library search backend"