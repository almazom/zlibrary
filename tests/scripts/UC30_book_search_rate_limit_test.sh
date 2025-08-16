#!/bin/bash

# =============================================================================
# UC30: Book Search Rate Limiting and Error Handling Test
# Tests the fixed book search system with proper rate limit detection
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_NAME="UC30_book_search_rate_limit_test"
TIMESTAMP=$(TZ=Europe/Moscow date '+%Y%m%d_%H%M%S')
LOG_FILE="/tmp/${TEST_NAME}_${TIMESTAMP}.log"

# Test queries
TEST_QUERIES=(
    "Clean Code Robert Martin"
    "Python Programming"
    "Atomic Habits"
)

echo -e "${CYAN}🔍 Starting $TEST_NAME${NC}"
echo -e "${BLUE}📝 Log file: $LOG_FILE${NC}"
echo

# Function to test book search functionality
test_book_search() {
    local query="$1"
    local test_num="$2"
    
    echo -e "${YELLOW}📖 Test $test_num: Testing search for '$query'${NC}"
    
    # Run book search with debug
    local result
    result=$(cd "$PROJECT_ROOT" && DEBUG=true ./scripts/book_search.sh "$query" 2>&1)
    
    # Log the full result
    echo "=== Test $test_num: $query ===" >> "$LOG_FILE"
    echo "$result" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Parse JSON response
    local json_part
    json_part=$(echo "$result" | grep '^{' | head -1)
    
    if [[ -n "$json_part" ]]; then
        local status
        status=$(echo "$json_part" | jq -r '.status // "unknown"')
        
        case "$status" in
            "success")
                echo -e "  ${GREEN}✅ SUCCESS: Book found and available${NC}"
                local title
                title=$(echo "$json_part" | jq -r '.result.book_info.title // "Unknown"')
                echo -e "  📚 Title: $title"
                
                local download_available
                download_available=$(echo "$json_part" | jq -r '.result.download_info.available // false')
                if [[ "$download_available" == "true" ]]; then
                    echo -e "  ${GREEN}📥 Download: Available${NC}"
                else
                    echo -e "  ${YELLOW}📥 Download: Not available (quality/confidence filters)${NC}"
                fi
                return 0
                ;;
            "error")
                local error_code
                local error_message
                error_code=$(echo "$json_part" | jq -r '.result.error // "unknown"')
                error_message=$(echo "$json_part" | jq -r '.result.message // "Unknown error"')
                
                if [[ "$error_code" == "search_failed" ]] && [[ "$error_message" == *"No working accounts found"* ]]; then
                    # Check if rate limiting was detected
                    if echo "$result" | grep -q "is rate limited"; then
                        echo -e "  ${YELLOW}⏳ EXPECTED: All accounts are rate limited${NC}"
                        echo -e "  ${BLUE}ℹ️  Rate limiting properly detected and handled${NC}"
                        return 0
                    else
                        echo -e "  ${RED}❌ ERROR: No working accounts (unexpected)${NC}"
                        echo -e "  🔍 Error: $error_message"
                        return 1
                    fi
                else
                    echo -e "  ${RED}❌ ERROR: $error_code${NC}"
                    echo -e "  🔍 Message: $error_message"
                    return 1
                fi
                ;;
            "not_found")
                echo -e "  ${YELLOW}📭 NOT FOUND: No books matching search criteria${NC}"
                return 0
                ;;
            *)
                echo -e "  ${RED}❌ UNKNOWN STATUS: $status${NC}"
                return 1
                ;;
        esac
    else
        echo -e "  ${RED}❌ INVALID RESPONSE: No JSON found${NC}"
        echo -e "  🔍 Raw output: ${result:0:100}..."
        return 1
    fi
}

# Function to test account configuration
test_account_config() {
    echo -e "${YELLOW}🔧 Testing account configuration loading${NC}"
    
    # Test account loading
    local account_test
    account_test=$(cd "$PROJECT_ROOT" && python3 -c "
import json, sys
from pathlib import Path
sys.path.insert(0, './scripts')

# Import the loading function
from book_search_engine import load_accounts_config

accounts = load_accounts_config()
print(f'Loaded {len(accounts)} active accounts')
for i, (email, password) in enumerate(accounts):
    print(f'  {i+1}. {email}')
")
    
    echo "$account_test"
    echo "=== Account Configuration Test ===" >> "$LOG_FILE"
    echo "$account_test" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    if echo "$account_test" | grep -q "Loaded [1-9]"; then
        echo -e "  ${GREEN}✅ Account configuration loading works${NC}"
        return 0
    else
        echo -e "  ${RED}❌ No active accounts found in configuration${NC}"
        return 1
    fi
}

# Function to test error handling
test_error_handling() {
    echo -e "${YELLOW}🧪 Testing error handling with invalid input${NC}"
    
    # Test with empty query
    local empty_result
    empty_result=$(cd "$PROJECT_ROOT" && ./scripts/book_search.sh "" 2>&1 || true)
    
    echo "=== Error Handling Test ===" >> "$LOG_FILE"
    echo "$empty_result" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    if echo "$empty_result" | grep -q '"status": "error"'; then
        echo -e "  ${GREEN}✅ Empty query properly handled${NC}"
        return 0
    else
        echo -e "  ${RED}❌ Empty query not properly handled${NC}"
        return 1
    fi
}

# Main test execution
main() {
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    echo -e "${CYAN}🚀 Starting Book Search System Tests${NC}"
    echo "Timestamp: $(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')"
    echo
    
    # Test 1: Account configuration
    echo -e "${BLUE}=== Test 1: Account Configuration ===${NC}"
    ((total_tests++))
    if test_account_config; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    echo
    
    # Test 2: Error handling
    echo -e "${BLUE}=== Test 2: Error Handling ===${NC}"
    ((total_tests++))
    if test_error_handling; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    echo
    
    # Test 3-5: Book search functionality
    for i in "${!TEST_QUERIES[@]}"; do
        local test_num=$((i + 3))
        echo -e "${BLUE}=== Test $test_num: Book Search Functionality ===${NC}"
        ((total_tests++))
        if test_book_search "${TEST_QUERIES[$i]}" "$test_num"; then
            ((passed_tests++))
        else
            ((failed_tests++))
        fi
        echo
        
        # Add delay between requests to avoid additional rate limiting
        if [[ $i -lt $((${#TEST_QUERIES[@]} - 1)) ]]; then
            echo -e "${CYAN}⏳ Waiting 2 seconds between requests...${NC}"
            sleep 2
        fi
    done
    
    # Summary
    echo -e "${CYAN}📊 Test Results Summary${NC}"
    echo -e "Total Tests: $total_tests"
    echo -e "Passed: ${GREEN}$passed_tests${NC}"
    echo -e "Failed: ${RED}$failed_tests${NC}"
    echo -e "Success Rate: $(( passed_tests * 100 / total_tests ))%"
    echo
    
    if [[ $failed_tests -eq 0 ]]; then
        echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
        echo -e "${BLUE}✨ Book search system is working correctly with proper rate limit handling${NC}"
    else
        echo -e "${YELLOW}⚠️  Some tests failed. Check log file: $LOG_FILE${NC}"
    fi
    
    # Final summary in log
    echo "=== FINAL SUMMARY ===" >> "$LOG_FILE"
    echo "Total: $total_tests, Passed: $passed_tests, Failed: $failed_tests" >> "$LOG_FILE"
    echo "Timestamp: $(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')" >> "$LOG_FILE"
    
    return $failed_tests
}

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ Error: jq is required but not installed${NC}"
    exit 1
fi

# Run main test
main "$@"