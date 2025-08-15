#!/bin/bash

# IUC05_libru_extraction: Fast lib.ru book extraction and high-confidence search
# Architecture: Simplified single-path extraction using lib.ru engine only
# Created: 2025-08-14 23:11:00 MSK

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration - SIMPLIFIED
TEST_NAME="IUC05_libru_extraction"
TEST_DESCRIPTION="Fast lib.ru book extraction and high-confidence search (simplified)"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"
MIN_CONFIDENCE="0.8"  # 80%+ confidence requirement
EXTRACTION_TIMEOUT="10"  # Max 10 seconds for extraction
MAX_RETRY_ATTEMPTS="2"   # Single retry only

# lib.ru configuration
LIBRU_CATEGORIES="RUFANT,INOFANT"  # Skip RAZNOE as it can be empty
MAX_BOOKS="1"  # We only need one book for the test

# Global variables
EXTRACTED_TITLE=""
EXTRACTED_AUTHOR=""
EXTRACTED_CONFIDENCE=""
EXTRACTION_TIME=""

#=== CORE FUNCTIONS ===

extract_book_from_libru() {
    log_info "⚡ Running lib.ru extraction engine..."
    
    local engine_path="$SCRIPT_DIR/../../scripts/lib_ru_extractor_engine.py"
    local extraction_start=$(date +%s.%3N)
    
    # Run extraction with timeout and capture only JSON output
    local extraction_result
    if extraction_result=$(timeout $EXTRACTION_TIMEOUT python3 "$engine_path" --format json --category RUFANT 2>/dev/null | tail -n +10); then
        local extraction_end=$(date +%s.%3N)
        EXTRACTION_TIME=$(echo "$extraction_end - $extraction_start" | bc -l)
        echo "$extraction_result"
        return 0
    else
        log_warn "⚠️ lib.ru extraction failed or timed out"
        return 1
    fi
}

validate_extraction_result() {
    local json_result="$1"
    
    # Check if we got valid JSON
    if ! echo "$json_result" | jq . >/dev/null 2>&1; then
        log_error "❌ Invalid JSON response"
        return 1
    fi
    
    # Check success status
    local success=$(echo "$json_result" | jq -r '.success')
    if [[ "$success" != "true" ]]; then
        local error=$(echo "$json_result" | jq -r '.error // "Unknown error"')
        log_error "❌ Extraction failed: $error"
        return 1
    fi
    
    # Extract book data
    EXTRACTED_TITLE=$(echo "$json_result" | jq -r '.book.title')
    EXTRACTED_AUTHOR=$(echo "$json_result" | jq -r '.book.author')
    EXTRACTED_CONFIDENCE=$(echo "$json_result" | jq -r '.book.confidence')
    
    # Validate required fields
    if [[ -z "$EXTRACTED_TITLE" || "$EXTRACTED_TITLE" == "null" ]]; then
        log_error "❌ Missing or invalid title"
        return 1
    fi
    
    if [[ -z "$EXTRACTED_AUTHOR" || "$EXTRACTED_AUTHOR" == "null" ]]; then
        log_error "❌ Missing or invalid author"
        return 1
    fi
    
    # Validate confidence
    if command -v bc >/dev/null 2>&1; then
        if (( $(echo "$EXTRACTED_CONFIDENCE < $MIN_CONFIDENCE" | bc -l) )); then
            log_error "❌ Low confidence: $EXTRACTED_CONFIDENCE (required: $MIN_CONFIDENCE)"
            return 1
        fi
    fi
    
    log_success "✅ Book extracted: '$EXTRACTED_TITLE' by $EXTRACTED_AUTHOR"
    log_info "🎯 Confidence: $EXTRACTED_CONFIDENCE"
    log_info "⚡ Time: ${EXTRACTION_TIME}s"
    
    return 0
}

#=== GHERKIN STEP IMPLEMENTATIONS ===

given_I_have_authenticated_session() {
    log_given "🔐 GIVEN: I have authenticated Telegram user session"
    
    if ! authenticate_user_session; then
        log_error "❌ User session not authenticated"
        return 1
    fi
    
    log_success "✅ Authentication successful"
}

when_I_extract_book_using_libru_engine() {
    log_when "⚡ WHEN: I extract book using lib.ru engine"
    
    local attempt=1
    local extraction_result=""
    
    while [[ $attempt -le $MAX_RETRY_ATTEMPTS ]]; do
        log_info "🔄 Extraction attempt $attempt/$MAX_RETRY_ATTEMPTS"
        
        if extraction_result=$(extract_book_from_libru); then
            if validate_extraction_result "$extraction_result"; then
                log_success "✅ Extraction successful on attempt $attempt"
                return 0
            else
                log_warn "⚠️ Validation failed on attempt $attempt"
            fi
        else
            log_warn "⚠️ Engine failed on attempt $attempt"
        fi
        
        if [[ $attempt -lt $MAX_RETRY_ATTEMPTS ]]; then
            log_info "⏳ Retrying in 2 seconds..."
            sleep 2
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_error "❌ Extraction failed after $MAX_RETRY_ATTEMPTS attempts"
    return 1
}

then_extraction_should_complete_within_timeout() {
    log_then "⏱️ THEN: Extraction should complete within ${EXTRACTION_TIMEOUT}s"
    
    if command -v bc >/dev/null 2>&1; then
        if (( $(echo "$EXTRACTION_TIME > $EXTRACTION_TIMEOUT" | bc -l) )); then
            log_error "❌ Extraction took ${EXTRACTION_TIME}s (max: ${EXTRACTION_TIMEOUT}s)"
            return 1
        fi
    fi
    
    log_success "✅ Extraction completed in ${EXTRACTION_TIME}s"
    return 0
}

when_I_search_for_extracted_book() {
    log_when "🔍 WHEN: I search for the extracted book"
    
    # Prepare book query
    local book_query="$EXTRACTED_TITLE $EXTRACTED_AUTHOR"
    
    # Send book search request
    if send_book_search "$book_query" "$TARGET_BOT"; then
        log_success "✅ Book search request sent"
        log_info "📋 Query: $book_query"
        log_info "🤖 Bot: $TARGET_BOT"
    else
        log_error "❌ Failed to send book search request"
        return 1
    fi
}

then_I_should_receive_progress_message() {
    log_then "📨 THEN: I should receive progress message"
    
    local response
    if response=$(read_progress_message 10); then
        log_success "✅ Progress message received"
        log_info "📥 Response: $response"
        
        # Validate progress message
        if validate_response "$response" "🔍 Searching" "progress"; then
            log_success "✅ Progress message validation passed"
            return 0
        fi
    fi
    
    log_error "❌ No valid progress message received"
    return 1
}

then_I_should_receive_epub_delivery() {
    log_then "📚 THEN: I should receive EPUB delivery"
    
    local response
    if response=$(read_epub_delivery 30); then
        log_success "✅ EPUB delivery received"
        log_info "📁 Response: $response"
        
        # Validate EPUB response
        if validate_response "$response" "📎" "epub"; then
            log_success "✅ EPUB validation passed"
            return 0
        fi
    fi
    
    log_error "❌ No valid EPUB delivery received"
    return 1
}

#=== TEST SCENARIO ===

run_simplified_libru_extraction_scenario() {
    log_step "🧪 SCENARIO: Fast lib.ru extraction and EPUB delivery"
    echo "=========================================="
    
    # Execute simplified test flow
    given_I_have_authenticated_session
    when_I_extract_book_using_libru_engine
    then_extraction_should_complete_within_timeout
    when_I_search_for_extracted_book
    then_I_should_receive_progress_message
    then_I_should_receive_epub_delivery
    
    # Success summary
    log_success "✅ Simplified lib.ru extraction test completed successfully"
    log_info "📖 Book: '$EXTRACTED_TITLE' by $EXTRACTED_AUTHOR"
    log_info "⚡ Extraction time: ${EXTRACTION_TIME}s"
    log_info "🎯 Confidence: $EXTRACTED_CONFIDENCE"
}

#=== MAIN EXECUTION ===

main() {
    log_step "🚀 $TEST_NAME: $TEST_DESCRIPTION"
    echo "=================================================="
    log_info "⏰ Start time: $(get_timestamp)"
    log_info "🤖 Target bot: $TARGET_BOT"
    log_info "📊 Min confidence: $MIN_CONFIDENCE"
    log_info "⏱️ Max extraction time: ${EXTRACTION_TIMEOUT}s"
    echo "=================================================="
    
    # Initialize test environment
    if ! verify_test_environment; then
        log_error "❌ Test environment verification failed"
        exit 1
    fi
    
    # Run the simplified scenario
    if run_simplified_libru_extraction_scenario; then
        log_success "✅ Test completed successfully"
        exit 0
    else
        log_error "❌ Test failed"
        exit 1
    fi
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi