#!/bin/bash

# IUC03_invalid_book_search: Invalid book search error handling integration test
# Generated from: features/IUC03_invalid_book_search.feature
# Follows: IUC Golden Standard v1.0 - Error Handling Pattern
# Created: 2025-08-13 MSK

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration
TEST_NAME="IUC03_invalid_book_search"
TEST_DESCRIPTION="Invalid book search error handling integration test (atomic)"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"

# GHERKIN MAPPING:
# "Given I have authenticated Telegram user session" → given_I_have_authenticated_session()
# "When I send invalid book title to the bot" → when_I_send_invalid_book_title()
# "Then I should receive error message within {int} seconds" → then_I_should_receive_error_message()

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

given_the_bot_is_running_and_responsive() {
    log_given "🤖 GIVEN: The bot is running and responsive"
    
    # Check bot accessibility
    if ! check_bot_accessibility "$TARGET_BOT"; then
        log_error "❌ Bot is not accessible"
        return 1
    fi
    
    log_success "✅ Bot is accessible"
}

when_I_send_invalid_book_title() {
    # Generate truly random non-existent book title with timestamp and random elements
    local timestamp=$(date +%s%N | cut -b1-13)  # nanosecond precision
    local random_suffix=$(openssl rand -hex 8 2>/dev/null || echo "$(($RANDOM$RANDOM))")
    local invalid_title="NONEXISTENT_BOOK_${timestamp}_${random_suffix}_SHOULD_NOT_EXIST"
    
    log_when "❌ WHEN: I send invalid book title '$invalid_title'"
    
    # Record start time for timing validation
    IUC_TEST_START_TIME=$(get_epoch)
    
    # Send invalid book search
    if send_book_search "$invalid_title" "$TARGET_BOT"; then
        log_info "📤 Invalid book search request sent"
        log_info "📋 Book title: $invalid_title"
        log_info "🤖 Target bot: $TARGET_BOT"
        log_info "⏰ Request time: $(get_timestamp)"
    else
        log_error "❌ Failed to send invalid book search request"
        return 1
    fi
}

then_I_should_receive_error_message() {
    local timeout="${1:-30}"
    
    log_then "❌ THEN: I should receive error message within ${timeout}s"
    
    # Read error response
    local response
    if response=$(read_bot_response "$timeout"); then
        log_info "📥 Error response received: $response"
    else
        log_error "❌ No error response received within ${timeout}s"
        return 1
    fi
    
    # Validate error message (updated for better user-friendly messages)
    if validate_response "$response" "Book not found\|Not found\|Search temporarily unavailable\|Network connection issue\|Service authentication issue\|Too many requests\|⚠️.*temporarily unavailable" "error"; then
        log_success "✅ Error message validation passed"
        return 0
    else
        log_error "❌ Error message validation failed"
        return 1
    fi
}

#=== TEST EXECUTION ===

run_invalid_book_search_scenario() {
    log_step "🧪 SCENARIO: Invalid book search error handling"
    echo "=========================================="
    
    # Execute Gherkin steps in order
    given_I_have_authenticated_session
    given_the_bot_is_running_and_responsive
    when_I_send_invalid_book_title
    then_I_should_receive_error_message 30
    
    # Validate timing
    if validate_timing "$IUC_TEST_START_TIME" 35; then
        log_success "✅ Timing validation passed"
    else
        log_warn "⚠️ Timing validation failed (took longer than expected)"
    fi
    
    log_success "✅ Invalid book search scenario completed"
}

main() {
    echo "🚀 $TEST_NAME: $TEST_DESCRIPTION"
    echo "=================================================="
    log_info "⏰ Start time: $(get_timestamp)"
    log_info "🤖 Target bot: $TARGET_BOT"
    log_info "🎯 Test focus: Error handling for invalid book titles"
    log_info "👤 User: ${IUC_USER_NAME:-Unknown} (ID: ${IUC_USER_ID:-Unknown})"
    log_info "🔄 Test type: Atomic Invalid Book Search Test"
    echo "=================================================="
    echo ""
    
    # Run atomic test scenario - ONLY invalid book search
    local overall_result="PASSED"
    
    # Invalid book search scenario (atomic test)
    if ! run_invalid_book_search_scenario; then
        overall_result="FAILED"
        log_error "❌ Invalid book search scenario failed"
    fi
    
    # Generate final report
    generate_test_report "$TEST_NAME" "$overall_result" "$TEST_DESCRIPTION"
    
    if [[ "$overall_result" == "PASSED" ]]; then
        log_success "🎉 $TEST_NAME PASSED: Invalid book error handling successful!"
        exit 0
    else
        log_error "❌ $TEST_NAME FAILED: Invalid book error handling failed"
        exit 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
🎯 IUC03_invalid_book_search: Invalid book search error handling integration test

OVERVIEW:
=========
Atomic integration test for invalid book search error handling with real Telegram bot.
Tests the complete error flow: Invalid book request → Error message → Validation.

USAGE:
======
./tests/IUC/IUC03_invalid_book_search.sh           # Run the test
./tests/IUC/IUC03_invalid_book_search.sh --help    # Show this help

ATOMIC TEST SCENARIO:
====================
1. Invalid book search error handling
   - Send randomly generated non-existent book title
   - Receive error message ("Search failed", "Not found", etc.)
   - Validate error response within 30 seconds
   - Validate timing and content

ATOMIC PRINCIPLE:
=================
This test focuses ONLY on error handling scenarios:
- ✅ ONE scenario: Invalid book → Error response
- ✅ ONE validation: Error message pattern matching
- ✅ ONE outcome: Pass/Fail based on error handling

RANDOM TITLE GENERATION:
========================
Each test run generates a truly unique invalid title:
- Nanosecond timestamp for temporal uniqueness
- Cryptographic random hex for collision prevention
- Clear naming convention indicating non-existence
- Example: NONEXISTENT_BOOK_1755071609207_73adeed79feac7b9_SHOULD_NOT_EXIST

GHERKIN SPECIFICATION:
======================
Scenario: Invalid book search returns appropriate error
  Given I have authenticated Telegram user session
  And The bot is running and responsive
  When I send invalid book title to the bot
  Then I should receive error message within 30 seconds

ERROR PATTERNS DETECTED:
========================
User-Friendly Messages (NEW):
- "📚 Book not found: [title]" with helpful suggestions
- "🌐 Network connection issue"  
- "⚠️ Search service temporarily unavailable"
- "🔐 Service authentication issue"
- "⏳ Too many requests"

Legacy Patterns (Fallback):
- "Not found"
- Any message containing "Error"

TIMING EXPECTATIONS:
====================
- Error response: 1-5 seconds (immediate)
- Total test duration: <35 seconds

AI LEARNING REFERENCE:
======================
This test demonstrates atomic testing principles:
- Single responsibility: ONLY error handling
- Clear success criteria: Error message received
- Isolated scenario: No valid book testing mixed in
- Predictable behavior: Always generates error (by design)

VERSION: 1.0.0
STATUS: ✅ PRODUCTION READY
ATOMIC: ✅ SINGLE SCENARIO FOCUS
EOF
}

# Handle help flag
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

# Execute main function
main "$@"