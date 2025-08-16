#!/bin/bash

# Interactive URL to EPUB Testing Service
# Simple, user-focused interface for testing book URL extraction and download

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOK_SEARCH="$SCRIPT_DIR/book_search.sh"
RESULTS_FILE="$SCRIPT_DIR/../test_results/interactive_test_$(date +%Y%m%d_%H%M%S).json"

# Test counters
TOTAL_TESTS=0
SUCCESSFUL=0
FAILED=0

# Results array for final report
declare -a TEST_RESULTS

# Ensure results directory exists
mkdir -p "$(dirname "$RESULTS_FILE")"

# Function to process single URL
process_url() {
    local url="$1"
    local test_num="$2"
    
    echo -e "\n${BLUE}Processing [$test_num]:${NC} $url"
    echo "⏳ Extracting book information..."
    
    # Call book_search.sh
    local result
    result=$("$BOOK_SEARCH" "$url" 2>/dev/null || echo '{"status": "error", "result": {"message": "Script execution failed"}}')
    
    # Parse result
    local status
    local book_title
    local confidence
    local download_path
    
    status=$(echo "$result" | jq -r '.status // "error"')
    
    if [[ "$status" == "success" ]]; then
        book_title=$(echo "$result" | jq -r '.result.book_info.title // "Unknown"')
        confidence=$(echo "$result" | jq -r '.result.confidence.score // 0')
        download_path=$(echo "$result" | jq -r '.result.epub_download_url // "N/A"')
        
        # Check if confidence meets threshold (0.6)
        if (( $(echo "$confidence >= 0.6" | bc -l) )); then
            echo -e "${GREEN}✅ Downloaded:${NC} $book_title"
            echo -e "   Confidence: $confidence"
            if [[ -f "$download_path" ]]; then
                local size
                size=$(ls -lh "$download_path" 2>/dev/null | awk '{print $5}' || echo "N/A")
                echo -e "   File: $(basename "$download_path") ($size)"
            fi
            ((SUCCESSFUL++))
            TEST_RESULTS+=("{\"url\": \"$url\", \"book\": \"$book_title\", \"success\": true, \"confidence\": $confidence}")
        else
            echo -e "${YELLOW}⚠️  Low confidence:${NC} $confidence"
            echo -e "   Book: $book_title"
            echo -e "   Skipped download (confidence < 0.6)"
            ((FAILED++))
            TEST_RESULTS+=("{\"url\": \"$url\", \"book\": \"$book_title\", \"success\": false, \"confidence\": $confidence, \"reason\": \"Low confidence\"}")
        fi
    else
        local error_msg
        error_msg=$(echo "$result" | jq -r '.result.message // "Unknown error"')
        echo -e "${RED}❌ Failed:${NC} $error_msg"
        ((FAILED++))
        TEST_RESULTS+=("{\"url\": \"$url\", \"book\": null, \"success\": false, \"confidence\": 0, \"reason\": \"$error_msg\"}")
    fi
    
    ((TOTAL_TESTS++))
}

# Function to display results table
display_results_table() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                        TEST RESULTS TABLE                         ${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    
    printf "%-40s | %-30s | %-8s | %-10s\n" "URL" "Book" "Success" "Confidence"
    echo "--------------------------------------------------------------------------------"
    
    for result in "${TEST_RESULTS[@]}"; do
        local url
        local book
        local success
        local confidence
        
        url=$(echo "$result" | jq -r '.url' | cut -c1-40)
        book=$(echo "$result" | jq -r '.book // "N/A"' | cut -c1-30)
        success=$(echo "$result" | jq -r '.success')
        confidence=$(echo "$result" | jq -r '.confidence')
        
        if [[ "$success" == "true" ]]; then
            success_mark="${GREEN}✓${NC}"
        else
            success_mark="${RED}✗${NC}"
        fi
        
        printf "%-40s | %-30s | %-8b | %-10s\n" "$url" "$book" "$success_mark" "$confidence"
    done
    
    echo "--------------------------------------------------------------------------------"
    echo -e "${BLUE}Summary:${NC} Total: $TOTAL_TESTS | Success: $SUCCESSFUL | Failed: $FAILED"
    
    # Calculate success rate
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        local success_rate
        success_rate=$(echo "scale=1; $SUCCESSFUL * 100 / $TOTAL_TESTS" | bc)
        echo -e "${BLUE}Success Rate:${NC} ${success_rate}%"
        
        if (( $(echo "$success_rate >= 80" | bc -l) )); then
            echo -e "${GREEN}✅ Target achieved (≥80%)${NC}"
        else
            echo -e "${YELLOW}⚠️  Below target (<80%)${NC}"
        fi
    fi
}

# Main interactive loop
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}         Interactive URL to EPUB Testing Service                  ${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "This service will:"
    echo "• Accept book URLs one at a time"
    echo "• Extract book information from the URL"
    echo "• Download EPUB if confidence ≥ 0.6"
    echo "• Generate test report after completion"
    echo ""
    echo -e "${YELLOW}Enter 'done' when finished testing${NC}"
    echo ""
    
    local test_count=1
    
    while true; do
        echo -n "Enter URL (or 'done'): "
        read -r url
        
        # Check for exit
        if [[ "$url" == "done" ]] || [[ -z "$url" ]]; then
            break
        fi
        
        # Process the URL
        process_url "$url" "$test_count"
        ((test_count++))
        
        echo ""
    done
    
    # Display final results
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        display_results_table
        
        # Save results to JSON file
        echo -e "\n${BLUE}Saving results to:${NC} $RESULTS_FILE"
        {
            echo "{"
            echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
            echo "  \"total_tests\": $TOTAL_TESTS,"
            echo "  \"successful\": $SUCCESSFUL,"
            echo "  \"failed\": $FAILED,"
            echo "  \"success_rate\": $(echo "scale=2; $SUCCESSFUL * 100 / $TOTAL_TESTS" | bc),"
            echo "  \"results\": ["
            for i in "${!TEST_RESULTS[@]}"; do
                echo -n "    ${TEST_RESULTS[$i]}"
                if [[ $i -lt $((${#TEST_RESULTS[@]} - 1)) ]]; then
                    echo ","
                else
                    echo ""
                fi
            done
            echo "  ]"
            echo "}"
        } > "$RESULTS_FILE"
        
        echo -e "${GREEN}✅ Test session complete!${NC}"
    else
        echo -e "\n${YELLOW}No tests performed${NC}"
    fi
}

# Run main function
main