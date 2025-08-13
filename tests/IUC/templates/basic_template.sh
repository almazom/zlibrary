#!/bin/bash

# [TEST_NAME]: [TEST_DESCRIPTION]
# Generated from: features/[TEST_NAME].feature
# Follows: IUC Golden Standard v1.0
# Created: $(date '+%Y-%m-%d %H:%M:%S MSK')

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration
TEST_NAME="[TEST_NAME]"
TEST_DESCRIPTION="[TEST_DESCRIPTION]"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"
EXPECTED_RESPONSE="[EXPECTED_RESPONSE]"

# GHERKIN MAPPING:
# "Given I have authenticated Telegram user session" → given_I_have_authenticated_session()
# "When I [ACTION]" → when_I_[ACTION]()
# "Then I should [EXPECTATION]" → then_I_should_[EXPECTATION]()

#=== GHERKIN STEP IMPLEMENTATIONS ===

given_I_have_authenticated_session() {
    log_given "🔐 GIVEN: I have authenticated Telegram user session"
    
    if ! authenticate_user_session; then
        log_error "❌ Authentication failed - cannot proceed"
        exit 1
    fi
    
    if ! verify_test_environment; then
        log_error "❌ Environment verification failed"
        exit 1
    fi
}

when_I_[ACTION]() {
    # Replace [ACTION] with specific action, e.g., send_start_command
    local action_param="${1:-}"
    
    log_when "📤 WHEN: I [ACTION] $action_param"
    
    # Record start time for timing validation
    IUC_TEST_START_TIME=$(get_epoch)
    
    # Implement specific action here
    # Example: send_start_command "$TARGET_BOT"
    # Example: send_book_search "$action_param" "$TARGET_BOT"
    
    log_info "Action completed at $(get_timestamp)"
}

then_I_should_[EXPECTATION]() {
    local expected="${1:-$EXPECTED_RESPONSE}"
    local timeout="${2:-10}"
    
    log_then "✅ THEN: I should [EXPECTATION]"
    
    # Read bot response
    local response
    if response=$(read_bot_response "$timeout"); then
        log_success "✅ Response received"
    else
        log_error "❌ Failed to read response"
        return 1
    fi
    
    # Validate response
    if validate_response "$response" "$expected" "auto"; then
        log_success "✅ Validation passed"
        return 0
    else
        log_error "❌ Validation failed"
        return 1
    fi
}

#=== TEST EXECUTION ===

run_test_scenario() {
    local scenario_name="$1"
    
    log_step "🧪 SCENARIO: $scenario_name"
    echo "=========================================="
    
    # Execute Gherkin steps in order
    given_I_have_authenticated_session
    
    # Add specific When/Then steps based on scenario
    # Example:
    # when_I_send_start_command
    # then_I_should_receive_welcome_message
    
    log_success "✅ Scenario '$scenario_name' completed"
}

main() {
    echo "🚀 $TEST_NAME: $TEST_DESCRIPTION"
    echo "=================================================="
    log_info "⏰ Start time: $(get_timestamp)"
    log_info "🤖 Target bot: $TARGET_BOT"
    log_info "👤 User: ${IUC_USER_NAME:-Unknown} (ID: ${IUC_USER_ID:-Unknown})"
    log_info "🔄 Test type: Integration with feedback loop"
    echo "=================================================="
    echo ""
    
    # Run test scenarios
    local overall_result="PASSED"
    
    if ! run_test_scenario "Successful [SCENARIO_NAME]"; then
        overall_result="FAILED"
    fi
    
    # Generate final report
    generate_test_report "$TEST_NAME" "$overall_result" "$TEST_DESCRIPTION"
    
    if [[ "$overall_result" == "PASSED" ]]; then
        log_success "🎉 $TEST_NAME PASSED: All scenarios successful!"
        exit 0
    else
        log_error "❌ $TEST_NAME FAILED: Some scenarios failed"
        exit 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
🎯 [TEST_NAME]: [TEST_DESCRIPTION]

OVERVIEW:
=========
[TEST_OVERVIEW_DESCRIPTION]

USAGE:
======
./tests/IUC/[TEST_NAME].sh                # Run the test
./tests/IUC/[TEST_NAME].sh --help         # Show this help

SCENARIOS:
==========
1. Successful [SCENARIO_NAME]
   - [SCENARIO_DESCRIPTION]
   
2. [ERROR_SCENARIO_NAME]
   - [ERROR_SCENARIO_DESCRIPTION]

GHERKIN SPECIFICATION:
======================
See: features/[TEST_NAME].feature

AI LEARNING REFERENCE:
======================
This test follows IUC Golden Standard patterns:
- Authentication via authenticate_user_session()
- Message sending via send_*() functions
- Response reading via read_bot_response()
- Validation via validate_response()
- Rich UI with emoji feedback

VERSION: 1.0.0
STATUS: ✅ PRODUCTION READY
EOF
}

# Handle help flag
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

# Execute main function
main "$@"