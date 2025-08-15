#!/bin/bash

# test_single_category.sh: Test extraction from single category URL
# Purpose: Validate multi-book extraction approach with one bookstore

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test single category URL
TEST_URL="https://eksmo.ru/catalog/books/fiction/"
BOOKS_COUNT=5

echo "🧪 Testing single category extraction"
echo "====================================="
log_info "📋 URL: $TEST_URL"
log_info "🎯 Target: $BOOKS_COUNT books"
echo ""

# Test extraction
log_step "🤖 EXTRACT: Testing Claude multi-book extraction"

claude_prompt="Use WebFetch to visit $TEST_URL and extract exactly $BOOKS_COUNT DIFFERENT books from this page. Look for book titles and authors. Return JSON array format:
[
    {\"title\": \"Actual Book Title\", \"author\": \"Author Name\", \"confidence\": 0.9},
    {\"title\": \"Another Book Title\", \"author\": \"Author Name\", \"confidence\": 0.8}
]

Extract DIFFERENT books, not duplicates. Focus on variety. Set confidence to 0.9 for clear titles/authors, 0.7 for partial information."

log_info "📤 Sending request to Claude..."

if claude_result=$(timeout 60 claude -p "$claude_prompt" --allowedTools "WebFetch" --output-format json 2>/dev/null); then
    log_success "✅ Claude responded"
    
    # Extract and display the result
    json_content=$(echo "$claude_result" | jq -r '.result' 2>/dev/null || echo "$claude_result")
    
    # Handle markdown code blocks
    if echo "$json_content" | grep -q '```json'; then
        json_content=$(echo "$json_content" | sed -n '/```json/,/```/p' | grep -v '```')
    fi
    
    log_info "📥 Raw result:"
    echo "$json_content" | head -10
    echo ""
    
    # Validate JSON
    if echo "$json_content" | jq . >/dev/null 2>&1; then
        log_success "✅ Valid JSON received"
        
        # Check if array
        if echo "$json_content" | jq -e 'type == "array"' >/dev/null 2>&1; then
            book_count=$(echo "$json_content" | jq length)
            log_success "✅ Array with $book_count books"
            
            # Display extracted books
            log_info "📚 Extracted books:"
            echo "$json_content" | jq -r '.[] | "  - \"" + .title + "\" by " + .author + " (confidence: " + (.confidence | tostring) + ")"' 2>/dev/null || echo "Error parsing books"
        else
            log_warn "⚠️ Single object, not array"
            echo "$json_content" | jq .
        fi
    else
        log_error "❌ Invalid JSON"
        echo "Content: $json_content"
    fi
else
    log_error "❌ Claude extraction failed"
    exit 1
fi

log_success "🎉 Single category test completed"