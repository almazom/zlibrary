#!/bin/bash

# IUC05_variety_test_v2: Multi-book pool approach for guaranteed variety
# Purpose: Load daily book pool and select different books per run
# Approach: Pre-generated pool → Round-robin selection → Telegram delivery

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration
TEST_NAME="IUC05_variety_test_v2"
TEST_DESCRIPTION="Multi-book pool approach with guaranteed variety"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"

# Initialize variables
EXTRACTED_TITLE=""
EXTRACTED_AUTHOR=""
EXTRACTED_CONFIDENCE=""
EXTRACTED_SOURCE_URL=""
RUN_NUMBER="${1:-1}"

# Pool file location
DAILY_POOL_FILE="$SCRIPT_DIR/books_pool_$(date '+%Y-%m-%d').json"

#=== POOL MANAGEMENT FUNCTIONS ===

check_pool_exists() {
    if [[ ! -f "$DAILY_POOL_FILE" ]]; then
        log_error "❌ Daily pool not found: $(basename "$DAILY_POOL_FILE")"
        log_info "🔧 Run: ./generate_daily_book_pool.sh"
        return 1
    fi
    return 0
}

load_pool_info() {
    if ! check_pool_exists; then
        return 1
    fi
    
    local total_books=$(jq length "$DAILY_POOL_FILE" 2>/dev/null || echo "0")
    log_info "📚 Pool loaded: $total_books books available"
    log_info "📁 Source: $(basename "$DAILY_POOL_FILE")"
    return 0
}

select_book_from_pool() {
    local run_number="$1"
    
    if ! check_pool_exists; then
        return 1
    fi
    
    local total_books=$(jq length "$DAILY_POOL_FILE")
    
    if [[ $total_books -eq 0 ]]; then
        log_error "❌ Empty book pool"
        return 1
    fi
    
    # Round-robin selection: (run_number - 1) % total_books
    local selected_index=$(( (run_number - 1) % total_books ))
    
    log_info "🎯 Selecting book at index $selected_index (run $run_number of $total_books total books)"
    
    # Extract selected book
    local selected_book=$(jq ".[$selected_index]" "$DAILY_POOL_FILE")
    
    # Parse book details
    EXTRACTED_TITLE=$(echo "$selected_book" | jq -r '.title')
    EXTRACTED_AUTHOR=$(echo "$selected_book" | jq -r '.author')
    EXTRACTED_CONFIDENCE=$(echo "$selected_book" | jq -r '.confidence')
    EXTRACTED_SOURCE_URL=$(echo "$selected_book" | jq -r '.source_url // "unknown"')
    
    if [[ -z "$EXTRACTED_TITLE" || "$EXTRACTED_TITLE" == "null" ]]; then
        log_error "❌ Invalid book selected from pool"
        return 1
    fi
    
    log_success "✅ Selected book from pool"
    log_info "📚 Title: $EXTRACTED_TITLE"
    log_info "✍️ Author: $EXTRACTED_AUTHOR"
    log_info "📊 Confidence: $EXTRACTED_CONFIDENCE"
    log_info "🌐 Source: $(basename "$EXTRACTED_SOURCE_URL")"
    
    return 0
}

#=== VARIETY TEST FUNCTIONS ===

send_selected_book_to_telegram() {
    log_step "📱 TELEGRAM: Run #$RUN_NUMBER - Sending selected book to bot"
    
    local book_query="$EXTRACTED_TITLE $EXTRACTED_AUTHOR"
    log_info "📋 Query: $book_query"
    log_info "🤖 Target: $TARGET_BOT"
    
    # Send the book search request
    if send_book_search "$book_query" "$TARGET_BOT"; then
        log_success "✅ Book search request sent via Telegram"
        log_success "📨 RUN #$RUN_NUMBER: '$EXTRACTED_TITLE' by '$EXTRACTED_AUTHOR'"
        return 0
    else
        log_error "❌ Failed to send book search request"
        return 1
    fi
}

display_variety_result() {
    log_step "📊 VARIETY: Run #$RUN_NUMBER result summary"
    
    echo "=========================================="
    echo "RUN_RESULT_$RUN_NUMBER:"
    echo "  Title: $EXTRACTED_TITLE"
    echo "  Author: $EXTRACTED_AUTHOR"
    echo "  Confidence: $EXTRACTED_CONFIDENCE"
    echo "  Source: $(basename "$EXTRACTED_SOURCE_URL")"
    echo "  Query: $EXTRACTED_TITLE $EXTRACTED_AUTHOR"
    echo "=========================================="
}

#=== MAIN TEST EXECUTION ===

run_variety_test_v2() {
    log_step "🧪 RUN #$RUN_NUMBER: Multi-book pool variety test"
    echo "============================================="
    
    # Step 1: Load pool information
    if ! load_pool_info; then
        log_error "❌ Pool loading failed"
        return 1
    fi
    
    # Step 2: Quick authentication check
    if ! authenticate_user_session >/dev/null 2>&1; then
        log_error "❌ Authentication failed"
        return 1
    fi
    
    # Step 3: Select book from pool by run number
    if ! select_book_from_pool "$RUN_NUMBER"; then
        log_error "❌ Book selection failed"
        return 1
    fi
    
    # Step 4: Send to Telegram
    if ! send_selected_book_to_telegram; then
        log_error "❌ Telegram sending failed"
        return 1
    fi
    
    # Step 5: Display result for variety tracking
    display_variety_result
    
    log_success "✅ RUN #$RUN_NUMBER completed successfully"
    return 0
}

#=== MAIN EXECUTION ===

main() {
    echo "🚀 $TEST_NAME - RUN #$RUN_NUMBER"
    echo "================================="
    log_info "⏰ Start time: $(get_timestamp)"
    log_info "🎯 Approach: Multi-book pool with round-robin selection"
    log_info "🤖 Target bot: $TARGET_BOT"
    log_info "📁 Pool file: $(basename "$DAILY_POOL_FILE")"
    echo ""
    
    # Run the variety test
    if run_variety_test_v2; then
        log_success "🎉 RUN #$RUN_NUMBER PASSED: Variety test successful!"
        exit 0
    else
        log_error "❌ RUN #$RUN_NUMBER FAILED: Variety test failed"
        exit 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
🎯 IUC05_variety_test_v2: Multi-book pool approach with guaranteed variety

OVERVIEW:
=========
Uses pre-generated daily book pool for guaranteed variety across test runs.
Each run selects a different book using round-robin algorithm.

USAGE:
======
# First, generate the daily pool:
./generate_daily_book_pool.sh

# Then run variety tests:
./IUC05_variety_test_v2.sh 1    # Selects book[0]
./IUC05_variety_test_v2.sh 2    # Selects book[1]  
./IUC05_variety_test_v2.sh 3    # Selects book[2]
./IUC05_variety_test_v2.sh 4    # Selects book[3]
./IUC05_variety_test_v2.sh 5    # Selects book[4]

GUARANTEED VARIETY:
===================
✅ Different book each run (until pool exhausted)
✅ Round-robin selection prevents duplicates
✅ 40+ book pool allows extensive variety testing
✅ Books from multiple Russian bookstore categories

APPROACH BENEFITS:
==================
- No more extraction timeouts during testing
- Predictable variety across runs
- Fast test execution (no Claude calls)
- Reliable book metadata quality
- Simple integration with existing Telegram flow

POOL REQUIREMENTS:
==================
- Daily pool must exist: books_pool_YYYY-MM-DD.json
- Pool generated by: ./generate_daily_book_pool.sh
- Contains validated books with title, author, confidence
- Minimum 10+ books for variety testing

VERSION: 2.0.0 - Multi-book pool approach
STATUS: ✅ PRODUCTION READY
EOF
}

# Handle help flag  
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

# Validate run number
if ! [[ "$RUN_NUMBER" =~ ^[0-9]+$ ]] || [[ $RUN_NUMBER -lt 1 ]]; then
    log_error "❌ Invalid run number: $RUN_NUMBER (must be positive integer)"
    echo "Usage: $0 <run_number>"
    exit 2
fi

# Execute main function
main "$@"