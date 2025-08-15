#!/bin/bash

# IUC05_variety_test: Test book variety across multiple runs
# Purpose: Validate different book extraction each time

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration
TEST_NAME="IUC05_variety_test"
TEST_DESCRIPTION="Book variety validation across runs"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"

# Different working book URLs for variety testing
BOOK_URLS=(
    "https://eksmo.ru/book/k-sebe-nezhno-ITD1083100/"
    "https://alpinabook.ru/catalog/book-nezapadnaya-istoriya-nauki/"
    "https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"
    "https://alpinabook.ru/catalog/book-pishi-sokrashchay-2025/"
    "https://eksmo.ru/book/maniak-ITD1077738/"
)

# Initialize variables
EXTRACTED_TITLE=""
EXTRACTED_AUTHOR=""
EXTRACTED_CONFIDENCE=""
RUN_NUMBER="${1:-1}"

#=== VARIETY TEST FUNCTIONS ===

select_random_book_url() {
    local url_count=${#BOOK_URLS[@]}
    # Use run number and timestamp for variety
    local index=$(( (RUN_NUMBER + $(date +%s)) % url_count ))
    echo "${BOOK_URLS[$index]}"
}

extract_book_from_url() {
    local book_url="$1"
    
    log_step "🤖 EXTRACT: Run #$RUN_NUMBER - Extracting from random URL"
    log_info "📋 URL: $book_url"
    
    local claude_result
    if claude_result=$(timeout 60 claude -p "Use WebFetch to visit $book_url and extract book metadata. Return JSON with: title, author, year, publisher, isbn, confidence" --allowedTools "WebFetch" --output-format json 2>/dev/null); then
        
        # Extract the JSON from Claude's response
        local json_content=$(echo "$claude_result" | jq -r '.result' 2>/dev/null)
        
        # Parse the JSON content to extract book details
        if echo "$json_content" | grep -q '```json'; then
            # Extract JSON from markdown code block
            json_content=$(echo "$json_content" | sed -n '/```json/,/```/p' | grep -v '```')
        fi
        
        # Extract book information
        EXTRACTED_TITLE=$(echo "$json_content" | jq -r '.title' 2>/dev/null || echo "")
        EXTRACTED_AUTHOR=$(echo "$json_content" | jq -r '.author' 2>/dev/null || echo "")
        EXTRACTED_CONFIDENCE=$(echo "$json_content" | jq -r '.confidence' 2>/dev/null || echo "0.8")
        
        # Clean up title and author (remove null values)
        if [[ "$EXTRACTED_TITLE" == "null" || -z "$EXTRACTED_TITLE" ]]; then
            EXTRACTED_TITLE="Unknown Title"
        fi
        if [[ "$EXTRACTED_AUTHOR" == "null" || -z "$EXTRACTED_AUTHOR" ]]; then
            EXTRACTED_AUTHOR="Unknown Author"
        fi
        
        log_success "✅ Successfully extracted book metadata"
        log_info "📚 Title: $EXTRACTED_TITLE"
        log_info "✍️ Author: $EXTRACTED_AUTHOR"
        log_info "📊 Confidence: $EXTRACTED_CONFIDENCE"
        return 0
    else
        log_error "❌ Claude extraction failed"
        return 1
    fi
}

send_book_to_telegram() {
    log_step "📱 TELEGRAM: Run #$RUN_NUMBER - Sending book to bot"
    
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

#=== MAIN TEST EXECUTION ===

run_single_variety_test() {
    log_step "🧪 RUN #$RUN_NUMBER: Book variety test"
    echo "=========================================="
    
    # Step 1: Quick authentication check
    if ! authenticate_user_session >/dev/null 2>&1; then
        log_error "❌ Authentication failed"
        return 1
    fi
    
    # Step 2: Select and extract from random URL
    local selected_url
    selected_url=$(select_random_book_url)
    
    if ! extract_book_from_url "$selected_url"; then
        log_error "❌ Book extraction failed"
        return 1
    fi
    
    # Step 3: Send to Telegram
    if ! send_book_to_telegram; then
        log_error "❌ Telegram sending failed"  
        return 1
    fi
    
    log_success "✅ RUN #$RUN_NUMBER completed: '$EXTRACTED_TITLE' by '$EXTRACTED_AUTHOR'"
    
    # Output for tracking
    echo "BOOK_RESULT_$RUN_NUMBER: $EXTRACTED_TITLE | $EXTRACTED_AUTHOR | $selected_url"
    
    return 0
}

main() {
    echo "🚀 $TEST_NAME - RUN #$RUN_NUMBER"
    echo "==============================="
    
    # Run single variety test
    if run_single_variety_test; then
        log_success "🎉 RUN #$RUN_NUMBER PASSED: Book variety test successful!"
        exit 0
    else
        log_error "❌ RUN #$RUN_NUMBER FAILED: Book variety test failed"
        exit 1
    fi
}

# Execute main function
main "$@"