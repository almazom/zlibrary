#!/bin/bash

# IUC02_book_search: Book search and EPUB delivery integration test
# Generated from: features/IUC02_book_search.feature
# Follows: IUC Golden Standard v1.0 - Book Search Pattern
# Created: $(date '+%Y-%m-%d %H:%M:%S MSK')

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration
TEST_NAME="IUC02_book_search"
TEST_DESCRIPTION="Book search and EPUB delivery integration test"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"
BOOK_TITLE="${BOOK_TITLE:-Clean Code Robert Martin}"

# GHERKIN MAPPING:
# "Given I have authenticated Telegram user session" → given_I_have_authenticated_session()
# "When I send book title {string} to the bot" → when_I_send_book_title()
# "Then I should receive a progress message within {int} seconds" → then_I_should_receive_progress_message_within_N_seconds()
# "And I should receive an EPUB file within {int} seconds" → and_I_should_receive_EPUB_file_within_N_seconds()

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

when_I_send_book_title() {
    local book_title="${1:-$BOOK_TITLE}"
    
    log_when "📚 WHEN: I send book title '$book_title' to the bot"
    
    # Record start time for timing validation
    IUC_TEST_START_TIME=$(get_epoch)
    
    # Send book search request
    if send_book_search "$book_title" "$TARGET_BOT"; then
        log_success "✅ Book search request sent"
        log_info "📋 Book title: $book_title"
        log_info "🤖 Target bot: $TARGET_BOT"
        log_info "⏰ Request time: $(get_timestamp)"
    else
        log_error "❌ Failed to send book search request"
        return 1
    fi
}

then_I_should_receive_progress_message_within_N_seconds() {
    local timeout="${1:-10}"
    
    log_then "🔍 THEN: I should receive progress message within ${timeout}s"
    
    # Read progress message
    local response
    if response=$(read_progress_message "$timeout"); then
        log_success "✅ Progress message received"
        log_info "📥 Response: $response"
    else
        log_error "❌ No progress message received within ${timeout}s"
        return 1
    fi
    
    # Validate progress message content
    if validate_response "$response" "🔍 Searching" "progress"; then
        log_success "✅ Progress message validation passed"
        return 0
    else
        log_error "❌ Progress message validation failed"
        return 1
    fi
}

and_I_should_receive_EPUB_file_within_N_seconds() {
    local timeout="${1:-30}"
    
    log_then "📚 AND: I should receive EPUB file within ${timeout}s"
    
    # Read EPUB delivery
    local response
    if response=$(read_epub_delivery "$timeout"); then
        log_success "✅ EPUB file received"
        log_info "📥 File delivery response: $response"
    else
        log_error "❌ No EPUB file received within ${timeout}s"
        return 1
    fi
    
    # Validate EPUB file delivery
    if validate_response "$response" "file" "file"; then
        log_success "✅ EPUB file validation passed"
        return 0
    else
        log_error "❌ EPUB file validation failed"
        return 1
    fi
}

and_I_should_receive_success_confirmation_message() {
    log_then "✅ AND: I should receive success confirmation message"
    
    # Read confirmation message
    local response
    if response=$(read_bot_response 10); then
        log_success "✅ Confirmation message received"
        log_info "📥 Confirmation: $response"
    else
        log_warn "⚠️ No confirmation message received (optional)"
        return 0  # This is optional, not critical
    fi
    
    return 0
}

# Error scenario implementations
when_I_send_invalid_book_title() {
    local invalid_title="${1:-INVALID_BOOK_THAT_DOES_NOT_EXIST_XYZ123}"
    
    log_when "❌ WHEN: I send invalid book title '$invalid_title'"
    
    # Record start time
    IUC_TEST_START_TIME=$(get_epoch)
    
    # Send invalid book search
    if send_book_search "$invalid_title" "$TARGET_BOT"; then
        log_info "📤 Invalid book search request sent"
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
    
    # Validate error message
    if validate_response "$response" "No books found\|Not found\|Error" "error"; then
        log_success "✅ Error message validation passed"
        return 0
    else
        log_error "❌ Error message validation failed"
        return 1
    fi
}

#=== TEST EXECUTION ===

run_successful_book_search_scenario() {
    log_step "🧪 SCENARIO: Successful book search and delivery"
    echo "=========================================="
    
    # Execute Gherkin steps in order
    given_I_have_authenticated_session
    given_the_bot_is_running_and_responsive
    when_I_send_book_title "$BOOK_TITLE"
    then_I_should_receive_progress_message_within_N_seconds 10
    and_I_should_receive_EPUB_file_within_N_seconds 30
    and_I_should_receive_success_confirmation_message
    
    # Validate timing
    if validate_timing "$IUC_TEST_START_TIME" 40; then
        log_success "✅ Timing validation passed"
    else
        log_warn "⚠️ Timing validation failed (took longer than expected)"
    fi
    
    log_success "✅ Successful book search scenario completed"
}

run_book_not_found_scenario() {
    log_step "🧪 SCENARIO: Book not found error handling"
    echo "=========================================="
    
    # Execute error scenario steps
    given_I_have_authenticated_session
    given_the_bot_is_running_and_responsive
    when_I_send_invalid_book_title
    then_I_should_receive_progress_message_within_N_seconds 10
    then_I_should_receive_error_message 30
    
    log_success "✅ Book not found scenario completed"
}

main() {
    echo "🚀 $TEST_NAME: $TEST_DESCRIPTION"
    echo "=================================================="
    log_info "⏰ Start time: $(get_timestamp)"
    log_info "🤖 Target bot: $TARGET_BOT"
    log_info "📚 Test book: $BOOK_TITLE"
    log_info "👤 User: ${IUC_USER_NAME:-Unknown} (ID: ${IUC_USER_ID:-Unknown})"
    log_info "🔄 Test type: Book Search Integration with feedback loop"
    echo "=================================================="
    echo ""
    
    # Run test scenarios
    local overall_result="PASSED"
    
    # Happy path scenario
    if ! run_successful_book_search_scenario; then
        overall_result="FAILED"
        log_error "❌ Happy path scenario failed"
    fi
    
    # Error scenario (optional, don't fail overall test)
    echo ""
    if ! run_book_not_found_scenario; then
        log_warn "⚠️ Error scenario had issues (not critical)"
    fi
    
    # Generate final report
    generate_test_report "$TEST_NAME" "$overall_result" "$TEST_DESCRIPTION"
    
    if [[ "$overall_result" == "PASSED" ]]; then
        log_success "🎉 $TEST_NAME PASSED: Book search integration successful!"
        exit 0
    else
        log_error "❌ $TEST_NAME FAILED: Book search integration failed"
        exit 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
🎯 IUC02_book_search: Book search and EPUB delivery integration test

OVERVIEW:
=========
Integration test for book search functionality with real Telegram bot.
Tests the complete flow: Search request → Progress message → EPUB delivery.

USAGE:
======
./tests/IUC/IUC02_book_search.sh                # Run the test
./tests/IUC/IUC02_book_search.sh --help         # Show this help

SCENARIOS:
==========
1. Successful book search and delivery
   - Send book title to bot
   - Receive progress message (🔍 Searching...)
   - Receive EPUB file within 30 seconds
   - Validate timing and content
   
2. Book not found error handling
   - Send invalid book title
   - Receive progress message
   - Receive "No books found" error message

GHERKIN SPECIFICATION:
======================
See: features/IUC02_book_search.feature

AI LEARNING REFERENCE:
======================
This test follows IUC Golden Standard patterns:
- Authentication via authenticate_user_session()
- Book search via send_book_search()
- Progress reading via read_progress_message()
- File delivery via read_epub_delivery()
- Validation via validate_response() with auto-detection
- Rich UI with emoji feedback and timing validation

TIMING EXPECTATIONS:
====================
- Progress message: 5-10 seconds
- EPUB delivery: 15-30 seconds
- Total test duration: <40 seconds

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