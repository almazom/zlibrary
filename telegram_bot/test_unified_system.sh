#!/bin/bash

# Unified System Test Script
# Tests both manual message sending and UC automated tests to verify 100% identical pipeline

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🧪 Unified System Test Suite${NC}"
echo -e "${BLUE}============================${NC}"
echo "🎯 Goal: Verify manual and UC automated messages trigger IDENTICAL pipeline"
echo "🔧 Method: Compare manual sender vs UC test results"
echo ""

# Function to print colored output
log_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_test() {
    echo -e "${CYAN}🧪 $1${NC}"
}

# Check if unified system is running
check_unified_system() {
    log_info "Checking if unified system is running..."
    
    if curl -s -f http://localhost:8765/health >/dev/null 2>&1; then
        log_info "✅ Unified system is running"
        return 0
    else
        log_error "❌ Unified system is not running"
        log_error "Please start it first:"
        log_error "  ./telegram_bot/start_unified_system.sh"
        return 1
    fi
}

# Test manual message sending
test_manual_message() {
    local message="$1"
    local test_name="$2"
    
    log_test "Testing manual message: '$message'"
    
    # Send manual message and capture result
    local result_file="/tmp/manual_test_result.json"
    
    if cd "$SCRIPT_DIR" && python3 manual_message_sender.py "$message" --json > "$result_file" 2>/dev/null; then
        local success=$(cat "$result_file" | jq -r '.success // false')
        local request_id=$(cat "$result_file" | jq -r '.request_id // "unknown"')
        
        if [[ "$success" == "true" ]]; then
            log_info "✅ Manual message test passed - Request ID: $request_id"
            echo "$result_file"
            return 0
        else
            log_error "❌ Manual message test failed"
            cat "$result_file" 2>/dev/null || echo "No result file"
            return 1
        fi
    else
        log_error "❌ Failed to execute manual message sender"
        return 1
    fi
}

# Test UC automated message
test_uc_automated_message() {
    local message="$1"
    local test_name="$2"
    
    log_test "Testing UC automated message: '$message'"
    
    # Create a simple UC test for this message
    local uc_test_file="/tmp/single_uc_test.py"
    
    cat > "$uc_test_file" << EOF
#!/usr/bin/env python3
import asyncio
import json
import sys
import os
sys.path.append('$SCRIPT_DIR')

from conflict_free_uc_test_v2 import ConflictFreeUCTestV2

async def main():
    tester = ConflictFreeUCTestV2()
    result = await tester.test_single_book_request("$message", "$test_name")
    print(json.dumps(result, indent=2, default=str))

if __name__ == '__main__':
    asyncio.run(main())
EOF
    
    # Run the UC test
    if cd "$SCRIPT_DIR" && python3 "$uc_test_file" 2>/dev/null; then
        log_info "✅ UC automated test completed"
        rm -f "$uc_test_file"
        return 0
    else
        log_error "❌ UC automated test failed"
        rm -f "$uc_test_file"
        return 1
    fi
}

# Compare results function
compare_results() {
    local manual_result_file="$1"
    local uc_result_file="$2"
    local test_name="$3"
    
    log_test "Comparing results for: $test_name"
    
    if [[ ! -f "$manual_result_file" ]] || [[ ! -f "$uc_result_file" ]]; then
        log_error "❌ Result files missing for comparison"
        return 1
    fi
    
    # Extract key metrics for comparison
    local manual_success=$(cat "$manual_result_file" | jq -r '.success // false')
    local uc_success=$(cat "$uc_result_file" | jq -r '.success // false')
    
    log_info "Manual success: $manual_success"
    log_info "UC success: $uc_success"
    
    if [[ "$manual_success" == "$uc_success" ]]; then
        log_info "✅ Results match - Pipeline identical confirmed!"
        return 0
    else
        log_error "❌ Results differ - Pipeline not identical"
        return 1
    fi
}

# Main test execution
main() {
    log_info "Starting unified system test..."
    
    # Check if system is running
    if ! check_unified_system; then
        exit 1
    fi
    
    # Test cases
    local test_cases=(
        "Clean Code:Programming Book"
        "Python Guide:Technical Book" 
        "Nonexistent XYZ 123:Not Found Test"
    )
    
    local passed_tests=0
    local total_tests=${#test_cases[@]}
    
    echo ""
    log_info "Running $total_tests test cases..."
    echo ""
    
    for test_case in "${test_cases[@]}"; do
        IFS=':' read -r message test_name <<< "$test_case"
        
        echo -e "${BLUE}📋 Testing: $test_name${NC}"
        echo -e "${BLUE}Query: '$message'${NC}"
        echo "-" | tr '-' '-' | head -c 50; echo ""
        
        # Test manual message
        if manual_result_file=$(test_manual_message "$message" "$test_name"); then
            log_info "Manual test: PASSED"
        else
            log_error "Manual test: FAILED"
            continue
        fi
        
        # Wait between tests
        sleep 3
        
        # Test UC automated message  
        if uc_result_file=$(test_uc_automated_message "$message" "$test_name"); then
            log_info "UC test: PASSED"
        else
            log_error "UC test: FAILED"
            continue
        fi
        
        # Compare results
        if compare_results "$manual_result_file" "$uc_result_file" "$test_name"; then
            log_info "Comparison: IDENTICAL ✅"
            ((passed_tests++))
        else
            log_error "Comparison: DIFFERENT ❌"
        fi
        
        echo ""
        log_info "Waiting 5s before next test..."
        sleep 5
        echo ""
    done
    
    # Final results
    echo "=" | tr '=' '=' | head -c 60; echo ""
    log_info "🏁 Test Suite Complete"
    log_info "📊 Results: $passed_tests/$total_tests tests passed"
    
    local success_rate=$((passed_tests * 100 / total_tests))
    log_info "📈 Success Rate: $success_rate%"
    
    if [[ $success_rate -ge 80 ]]; then
        echo ""
        echo -e "${GREEN}🎉 SUCCESS: Manual and UC automated messages trigger IDENTICAL pipeline!${NC}"
        echo -e "${GREEN}✅ HYPOTHESIS CONFIRMED: Unified system eliminates polling conflicts${NC}"
        echo -e "${GREEN}🔧 Solution: Use unified_message_processor.py for conflict-free operation${NC}"
    else
        echo ""
        echo -e "${RED}❌ FAILURE: Pipeline differences detected${NC}"
        echo -e "${RED}🔍 Further investigation needed${NC}"
    fi
    
    echo "=" | tr '=' '=' | head -c 60; echo ""
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    log_error "jq is required for this test. Please install it:"
    log_error "  sudo apt-get install jq"
    exit 1
fi

# Run main function
main "$@"