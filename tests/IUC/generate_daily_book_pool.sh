#!/bin/bash

# generate_daily_book_pool.sh: Extract multiple books from Russian bookstore category pages
# Purpose: Create daily pool of 40+ books for variety testing
# Created: 2025-08-13 - Multi-book extraction approach

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Configuration
BOOKS_PER_URL="8"           # Extract 8 books from each category URL
TIMEOUT="90"                # Timeout per Claude extraction 
MIN_CONFIDENCE="0.7"        # Minimum confidence for inclusion
DAILY_POOL_FILE="$SCRIPT_DIR/books_pool_$(date '+%Y-%m-%d').json"

# Russian bookstore category URLs - for multi-book extraction
CATEGORY_URLS=(
    "https://eksmo.ru/catalog/books/fiction/"                    # Fiction books
    "https://alpinabook.ru/catalog/business/"                   # Business books  
    "https://labirint.ru/books/detskaya-literatura/"            # Children's literature
    "https://book24.ru/catalog/bestsellers/"                   # Bestsellers
    "https://admarginem.ru/catalog/art/"                       # Art books
)

# Initialize variables
TOTAL_BOOKS_EXTRACTED=0
ALL_BOOKS="[]"

#=== UTILITY FUNCTIONS ===

log_pool_info() {
    log_info "📊 POOL STATUS: $*"
}

validate_book_metadata() {
    local book_json="$1"
    
    local title=$(echo "$book_json" | jq -r '.title // empty' 2>/dev/null)
    local author=$(echo "$book_json" | jq -r '.author // empty' 2>/dev/null)  
    local confidence=$(echo "$book_json" | jq -r '.confidence // 0' 2>/dev/null)
    
    # Validation checks
    if [[ -z "$title" || "$title" == "null" || "$title" == "Unknown Title" ]]; then
        return 1
    fi
    
    if [[ -z "$author" || "$author" == "null" || "$author" == "Unknown Author" ]]; then
        return 1
    fi
    
    # Confidence check (basic comparison)
    if [[ "${confidence%%.*}" -eq "0" && "${confidence#*.}" -lt "70" ]]; then
        return 1
    fi
    
    return 0
}

#=== MULTI-BOOK EXTRACTION FUNCTIONS ===

extract_multiple_books_from_url() {
    local category_url="$1"
    local count="$2"
    
    log_step "🤖 EXTRACT: Getting $count books from category page"
    log_info "📋 URL: $category_url"
    
    local claude_prompt="Use WebFetch to visit $category_url and extract exactly $count DIFFERENT books from this page. Look for book titles and authors. Return JSON array format:
[
    {\"title\": \"Actual Book Title\", \"author\": \"Author Name\", \"confidence\": 0.9},
    {\"title\": \"Another Book Title\", \"author\": \"Author Name\", \"confidence\": 0.8}
]

Extract DIFFERENT books, not duplicates. Focus on variety. Set confidence to 0.9 for clear titles/authors, 0.7 for partial information."
    
    local claude_result
    if claude_result=$(timeout "$TIMEOUT" claude -p "$claude_prompt" --allowedTools "WebFetch" --output-format json 2>/dev/null); then
        
        # Extract JSON from Claude response
        local json_content=$(echo "$claude_result" | jq -r '.result' 2>/dev/null || echo "$claude_result")
        
        # Handle markdown code blocks
        if echo "$json_content" | grep -q '```json'; then
            json_content=$(echo "$json_content" | sed -n '/```json/,/```/p' | grep -v '```' | jq -c '.')
        fi
        
        # Validate JSON array
        if echo "$json_content" | jq . >/dev/null 2>&1; then
            # Check if it's an array
            if echo "$json_content" | jq -e 'type == "array"' >/dev/null 2>&1; then
                echo "$json_content"
                return 0
            else
                # Single object, wrap in array
                echo "[$json_content]"
                return 0
            fi
        else
            log_error "❌ Invalid JSON from Claude"
            return 1
        fi
    else
        log_error "❌ Claude extraction failed for $category_url"
        return 1
    fi
}

process_extracted_books() {
    local books_array="$1"
    local url="$2"
    local valid_books=0
    
    log_info "🔍 Processing extracted books from $(basename "$url")"
    
    # Process each book in the array
    local book_count=$(echo "$books_array" | jq length)
    for ((i=0; i<book_count; i++)); do
        local book=$(echo "$books_array" | jq ".[$i]")
        
        if validate_book_metadata "$book"; then
            # Add URL source to book metadata
            book=$(echo "$book" | jq --arg url "$url" '. + {source_url: $url}')
            
            # Add to global pool
            ALL_BOOKS=$(echo "$ALL_BOOKS" | jq ". += [$book]")
            ((valid_books++))
            ((TOTAL_BOOKS_EXTRACTED++))
            
            local title=$(echo "$book" | jq -r '.title')
            local author=$(echo "$book" | jq -r '.author')
            log_success "✅ Added: '$title' by '$author'"
        else
            log_warn "⚠️ Skipped invalid book metadata"
        fi
    done
    
    log_pool_info "Processed $valid_books valid books from $(basename "$url")"
    return 0
}

#=== MAIN POOL GENERATION ===

generate_daily_book_pool() {
    log_step "📚 GENERATE: Daily book pool creation"
    echo "================================================="
    log_info "🎯 Target: $((${#CATEGORY_URLS[@]} * BOOKS_PER_URL)) books from ${#CATEGORY_URLS[@]} category URLs"
    log_info "📁 Output: $(basename "$DAILY_POOL_FILE")"
    log_info "⏰ Start time: $(get_timestamp)"
    echo ""
    
    # Process each category URL
    local url_index=1
    for category_url in "${CATEGORY_URLS[@]}"; do
        log_step "🌐 PROCESSING URL $url_index/${#CATEGORY_URLS[@]}: $(basename "$category_url")"
        
        local books_from_url
        if books_from_url=$(extract_multiple_books_from_url "$category_url" "$BOOKS_PER_URL"); then
            if process_extracted_books "$books_from_url" "$category_url"; then
                log_success "✅ Successfully processed URL $url_index"
            else
                log_error "❌ Failed to process books from URL $url_index"
            fi
        else
            log_error "❌ Failed to extract books from URL $url_index"
            log_info "🔄 Continuing with remaining URLs..."
        fi
        
        echo "" # Spacing between URLs
        ((url_index++))
    done
    
    # Save the book pool
    echo "$ALL_BOOKS" | jq '.' > "$DAILY_POOL_FILE"
    
    # Generate summary
    log_step "📊 POOL GENERATION SUMMARY"
    echo "=================================="
    log_success "✅ Pool generated: $(basename "$DAILY_POOL_FILE")"
    log_info "📚 Total books: $TOTAL_BOOKS_EXTRACTED"
    log_info "📁 File size: $(wc -c < "$DAILY_POOL_FILE") bytes"
    log_info "⏰ Generation time: $(get_timestamp)"
    
    if [[ $TOTAL_BOOKS_EXTRACTED -ge 20 ]]; then
        log_success "🎉 SUCCESS: Pool contains $TOTAL_BOOKS_EXTRACTED books (sufficient for variety testing)"
        return 0
    else
        log_error "❌ WARNING: Only $TOTAL_BOOKS_EXTRACTED books extracted (may not provide sufficient variety)"
        return 1
    fi
}

#=== POOL VALIDATION ===

validate_pool_quality() {
    log_step "🔍 VALIDATE: Book pool quality"
    
    if [[ ! -f "$DAILY_POOL_FILE" ]]; then
        log_error "❌ Pool file not found: $DAILY_POOL_FILE"
        return 1
    fi
    
    local total_books=$(jq length "$DAILY_POOL_FILE")
    local unique_titles=$(jq -r '.[].title' "$DAILY_POOL_FILE" | sort | uniq | wc -l)
    local high_confidence=$(jq '[.[] | select(.confidence >= 0.8)] | length' "$DAILY_POOL_FILE")
    
    log_info "📊 Total books: $total_books"
    log_info "📊 Unique titles: $unique_titles"
    log_info "📊 High confidence (≥0.8): $high_confidence"
    
    # Show sample books
    log_info "📖 Sample books from pool:"
    jq -r '.[:3] | .[] | "  - \"" + .title + "\" by " + .author + " (confidence: " + (.confidence | tostring) + ")"' "$DAILY_POOL_FILE"
    
    if [[ $unique_titles -ge 15 ]]; then
        log_success "✅ Pool quality: EXCELLENT ($unique_titles unique titles)"
        return 0
    elif [[ $unique_titles -ge 10 ]]; then
        log_success "✅ Pool quality: GOOD ($unique_titles unique titles)"
        return 0
    else
        log_warn "⚠️ Pool quality: LIMITED ($unique_titles unique titles - may have variety issues)"
        return 1
    fi
}

#=== MAIN EXECUTION ===

main() {
    echo "🚀 Daily Book Pool Generation"
    echo "============================="
    log_info "📅 Date: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    log_info "🎯 Purpose: Generate variety pool for IUC05 testing"
    echo ""
    
    # Check if pool already exists for today
    if [[ -f "$DAILY_POOL_FILE" ]]; then
        log_info "📁 Pool already exists: $(basename "$DAILY_POOL_FILE")"
        log_info "🔄 Regenerating fresh pool..."
        rm "$DAILY_POOL_FILE"
    fi
    
    # Generate the pool
    if generate_daily_book_pool; then
        echo ""
        if validate_pool_quality; then
            log_success "🎉 POOL GENERATION COMPLETED SUCCESSFULLY!"
            log_info "📋 Usage: ./IUC05_variety_test_v2.sh <run_number>"
            exit 0
        else
            log_warn "⚠️ Pool generated but with quality concerns"
            exit 0
        fi
    else
        log_error "❌ POOL GENERATION FAILED"
        exit 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
📚 Daily Book Pool Generation Script

OVERVIEW:
=========
Extracts multiple books from Russian bookstore category pages to create a daily pool
for variety testing. Generates 40+ unique books from 5 different bookstore categories.

USAGE:
======
./generate_daily_book_pool.sh                # Generate fresh daily pool
./generate_daily_book_pool.sh --help         # Show this help

OUTPUT:
=======
- books_pool_YYYY-MM-DD.json                 # Daily book pool file
- Contains 30-50 books with title, author, confidence, source_url

BOOKSTORE CATEGORIES:
=====================
- eksmo.ru/catalog/books/fiction/            # Fiction
- alpinabook.ru/catalog/business/            # Business  
- labirint.ru/books/detskaya-literatura/     # Children's
- book24.ru/catalog/bestsellers/             # Bestsellers
- admarginem.ru/catalog/art/                 # Art

QUALITY REQUIREMENTS:
=====================
- Minimum 0.7 confidence per book
- No "Unknown Title/Author" entries
- Unique titles preferred
- Valid JSON format

NEXT STEPS:
===========
After pool generation, use with:
./IUC05_variety_test_v2.sh 1   # Test run 1
./IUC05_variety_test_v2.sh 2   # Test run 2
...

VERSION: 2.0.0 - Multi-book extraction approach
STATUS: 🚀 READY FOR PRODUCTION
EOF
}

# Handle help flag
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

# Execute main function
main "$@"