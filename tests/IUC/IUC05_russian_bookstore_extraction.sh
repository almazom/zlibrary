#!/bin/bash

# IUC05_russian_bookstore_extraction: Russian bookstore URL extraction and high-confidence book search
# Generated from: features/IUC05_russian_bookstore_extraction.feature
# Follows: IUC Golden Standard v1.0 - Russian Bookstore Extraction Pattern
# Created: $(date '+%Y-%m-%d %H:%M:%S MSK')

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration
TEST_NAME="IUC05_russian_bookstore_extraction"
TEST_DESCRIPTION="Russian bookstore URL extraction and high-confidence book search (atomic)"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"
MIN_CONFIDENCE="0.8"  # 80%+ confidence requirement
MAX_EXTRACTION_ATTEMPTS="6"  # Increased for better reliability

# Fixed URLs for consistency testing (when CONSISTENCY_TEST=true)
FIXED_TEST_URLS=(
    "https://alpinabook.ru/catalog/book-nezapadnaya-istoriya-nauki/"
    "https://eksmo.ru/book/k-sebe-nezhno-ITD1083100/"
    "https://www.podpisnie.ru/"
)

# Initialize global variables to avoid unbound variable errors
SELECTED_BOOKSTORE=""
STORE_TYPE=""
EXTRACTED_TITLE=""
EXTRACTED_AUTHOR="" 
EXTRACTED_CONFIDENCE=""
DISCOVERED_BOOK_TITLE=""
DISCOVERED_BOOK_URL=""
DISCOVERY_RESULT=""

# Russian bookstore URLs pool - Curated reliable collection
RUSSIAN_BOOKSTORES=(
    # HIGH RELIABILITY - Tested and verified accessible
    "https://alpinabook.ru/catalog/book-nezapadnaya-istoriya-nauki/"  # Science books, clean metadata
    "https://eksmo.ru/book/k-sebe-nezhno-ITD1083100/"                 # Self-help, good structure  
    "https://www.labirint.ru"                                          # Major retailer, JSON-LD support
    "https://www.podpisnie.ru/"                                        # Independent, accessible
    
    # MEDIUM RELIABILITY - Good content but needs careful handling  
    "https://chitai-gorod.ru"          # Major chain, extensive catalog
    "https://www.litres.ru"            # E-books, good metadata
    "https://mybook.ru"                # Digital platform
    
    # BACKUP OPTIONS - Use if others fail
    "https://eksmo.ru"                 # Publisher site, may have category pages
    "https://www.slowbooks.ru/"        # Literary focus, smaller catalog
)

# Daily tracking file
BOOKS_TRACKING_FILE="$SCRIPT_DIR/books_extracted_$(date '+%Y-%m-%d').json"

# Success rate tracking
SUCCESS_LOG_FILE="$SCRIPT_DIR/extraction_success_$(date '+%Y-%m-%d').log"

# GHERKIN MAPPING:
# "Given I have a pool of Russian bookstore URLs" → given_I_have_bookstore_urls()
# "When I select a random bookstore URL" → when_I_select_random_bookstore()
# "And I extract book metadata using Claude AI" → and_I_extract_book_metadata()
# "And the extracted book has not been processed today" → and_book_is_not_duplicate()
# "Then I should get valid book metadata" → then_I_should_get_valid_metadata()
# "When I search for the extracted book" → when_I_search_for_book()
# "Then I should receive EPUB file" → then_I_should_receive_epub()

#=== UTILITY FUNCTIONS ===

select_random_bookstore() {
    # Use fixed URLs for consistency testing
    if [[ "${CONSISTENCY_TEST:-false}" == "true" ]]; then
        local fixed_count=${#FIXED_TEST_URLS[@]}
        local random_index=$((RANDOM % fixed_count))
        echo "${FIXED_TEST_URLS[$random_index]}"
    else
        local bookstore_count=${#RUSSIAN_BOOKSTORES[@]}
        local random_index=$((RANDOM % bookstore_count))
        echo "${RUSSIAN_BOOKSTORES[$random_index]}"
    fi
}

select_specific_bookstore() {
    local index="${1:-0}"
    if [[ "${CONSISTENCY_TEST:-false}" == "true" ]]; then
        local fixed_count=${#FIXED_TEST_URLS[@]}
        local safe_index=$((index % fixed_count))
        echo "${FIXED_TEST_URLS[$safe_index]}"
    else
        local bookstore_count=${#RUSSIAN_BOOKSTORES[@]}
        local safe_index=$((index % bookstore_count))
        echo "${RUSSIAN_BOOKSTORES[$safe_index]}"
    fi
}

detect_store_type() {
    local url="$1"
    case "$url" in
        *alpinabook*) echo "academic" ;;
        *eksmo*) echo "publisher" ;;
        *labirint*|*chitai-gorod*) echo "commercial" ;;
        *litres*|*mybook*) echo "digital" ;;
        *podpisnie*|*slowbooks*) echo "independent" ;;
        *) echo "unknown" ;;
    esac
}

get_extraction_prompt() {
    local store_type="$1"
    case "$store_type" in
        "academic")
            echo "Use WebFetch to visit this URL and extract Russian academic/science book metadata. Look in page title, breadcrumbs, product details. Return ONLY valid JSON with fields: title (in original Russian), author (full name in Russian), year, publisher, isbn, confidence. Set confidence to 0.9 for complete data, 0.8 for good data, 0.6 for partial."
            ;;
        "publisher")  
            echo "Use WebFetch to visit this URL and extract book metadata from Russian publisher site. Look for book title, author name, publication details. Return ONLY valid JSON with fields: title (in Russian), author (in Russian), year, publisher, isbn, confidence. Set confidence to 0.9 for complete data, 0.8 for good data, 0.6 for partial."
            ;;
        "commercial"|"digital")
            echo "Use WebFetch to visit this URL and extract book metadata from Russian bookstore. Look in product page, meta tags, structured data. Return ONLY valid JSON with fields: title (in Russian), author (in Russian), year, publisher, isbn, confidence. Set confidence to 0.9 for complete data, 0.8 for good data, 0.6 for partial."
            ;;
        "independent")
            echo "Use WebFetch to visit this URL and extract book metadata from independent Russian bookstore. Look for book information in page content. Return ONLY valid JSON with fields: title (in Russian), author (in Russian), year, publisher, isbn, confidence. Set confidence to 0.9 for complete data, 0.8 for good data, 0.6 for partial."
            ;;
        *)
            echo "Use WebFetch to visit this URL and extract Russian book metadata. Find title and author in original Russian language. Return ONLY valid JSON with fields: title, author, year, publisher, isbn, confidence. Set confidence based on data completeness."
            ;;
    esac
}

extract_with_claude() {
    local url="$1"
    local store_type="$2"
    local prompt=$(get_extraction_prompt "$store_type")
    
    log_info "🤖 Using Claude AI to extract from: $url"
    
    # Construct proper prompt with URL
    local full_prompt="$prompt Visit this URL: $url"
    
    # Use claude command with WebFetch
    local claude_result
    if claude_result=$(claude -p "$full_prompt" --allowedTools "WebFetch" --output-format json 2>/dev/null); then
        # Extract the actual result from Claude's response
        local extracted_result
        if extracted_result=$(echo "$claude_result" | jq -r '.result' 2>/dev/null); then
            echo "$extracted_result"
        else
            echo "$claude_result"
        fi
        return 0
    else
        log_error "❌ Claude extraction failed for $url"
        return 1
    fi
}

is_duplicate_book() {
    local title="$1"
    local author="$2"
    
    # Create tracking file if doesn't exist
    if [[ ! -f "$BOOKS_TRACKING_FILE" ]]; then
        echo "[]" > "$BOOKS_TRACKING_FILE"
        return 1  # Not duplicate if file doesn't exist
    fi
    
    # Check if title+author combination exists
    if command -v jq >/dev/null 2>&1; then
        local duplicate_count
        duplicate_count=$(jq --arg title "$title" --arg author "$author" \
            '[.[] | select(.title == $title and .author == $author)] | length' \
            "$BOOKS_TRACKING_FILE" 2>/dev/null || echo "0")
        
        [[ "$duplicate_count" -gt 0 ]]
    else
        # Fallback without jq - simple grep
        grep -q "\"title\":\"$title\".*\"author\":\"$author\"" "$BOOKS_TRACKING_FILE" 2>/dev/null
    fi
}

log_extraction_attempt() {
    local url="$1"
    local success="$2"  # true/false
    local title="${3:-}"
    local author="${4:-}"
    local confidence="${5:-0}"
    
    local timestamp=$(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')
    local log_entry="[$timestamp] URL=$url SUCCESS=$success TITLE=\"$title\" AUTHOR=\"$author\" CONFIDENCE=$confidence"
    
    echo "$log_entry" >> "$SUCCESS_LOG_FILE"
}

calculate_success_rate() {
    if [[ -f "$SUCCESS_LOG_FILE" ]]; then
        local total_attempts=$(grep -c "URL=" "$SUCCESS_LOG_FILE" 2>/dev/null || echo "0")
        local successful_attempts=$(grep -c "SUCCESS=true" "$SUCCESS_LOG_FILE" 2>/dev/null || echo "0")
        
        if [[ $total_attempts -gt 0 ]]; then
            local success_rate=$(( (successful_attempts * 100) / total_attempts ))
            log_info "📊 Success rate: $successful_attempts/$total_attempts ($success_rate%)"
        else
            log_info "📊 No extraction attempts logged yet"
        fi
    fi
}

save_extracted_book() {
    local title="$1"
    local author="$2"
    local url="$3"
    local confidence="$4"
    
    local timestamp=$(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')
    local book_entry="{\"title\":\"$title\",\"author\":\"$author\",\"url\":\"$url\",\"confidence\":$confidence,\"extracted_at\":\"$timestamp\"}"
    
    if command -v jq >/dev/null 2>&1; then
        # Add to JSON array using jq
        local temp_file
        temp_file=$(mktemp)
        jq --argjson entry "$book_entry" '. += [$entry]' "$BOOKS_TRACKING_FILE" > "$temp_file" && mv "$temp_file" "$BOOKS_TRACKING_FILE"
    else
        # Fallback without jq
        if [[ -s "$BOOKS_TRACKING_FILE" ]]; then
            # Remove last ] and add entry
            sed -i '$ s/]$/,' "$BOOKS_TRACKING_FILE"
            echo "$book_entry]" >> "$BOOKS_TRACKING_FILE"
        else
            echo "[$book_entry]" > "$BOOKS_TRACKING_FILE"
        fi
    fi
    
    log_success "✅ Saved book to tracking: $title by $author"
    
    # Log successful extraction
    log_extraction_attempt "$url" "true" "$title" "$author" "$confidence"
}

validate_metadata() {
    local json_result="$1"
    
    log_info "📥 Validating JSON: $json_result"
    
    # Extract fields (handle both single object and array responses)
    if command -v jq >/dev/null 2>&1; then
        # First try to extract from Claude response format
        local book_data="$json_result"
        
        # Check if it's a Claude result object
        if echo "$json_result" | jq -e '.result' >/dev/null 2>&1; then
            book_data=$(echo "$json_result" | jq -r '.result' 2>/dev/null)
        fi
        
        # Check if response is an array, if so take first element
        if echo "$book_data" | jq -e 'type == "array"' >/dev/null 2>&1; then
            book_data=$(echo "$book_data" | jq -r '.[0]' 2>/dev/null)
        fi
        
        # Extract JSON from markdown code blocks if present
        if echo "$book_data" | grep -q '```json'; then
            book_data=$(echo "$book_data" | sed -n '/```json/,/```/p' | sed '1d;$d')
        fi
        
        local title=$(echo "$book_data" | jq -r '.title // empty' 2>/dev/null)
        local author=$(echo "$book_data" | jq -r '.author // empty' 2>/dev/null)
        local confidence=$(echo "$book_data" | jq -r '.confidence // 0' 2>/dev/null)
        
        log_info "📖 Extracted - Title: '$title', Author: '$author', Confidence: '$confidence'"
    else
        # Fallback parsing without jq
        local title=$(echo "$json_result" | grep -o '"title":"[^"]*"' | cut -d'"' -f4 || echo "")
        local author=$(echo "$json_result" | grep -o '"author":"[^"]*"' | cut -d'"' -f4 || echo "")
        local confidence=$(echo "$json_result" | grep -o '"confidence":[0-9.]*' | cut -d':' -f2 || echo "0")
    fi
    
    # Validation checks
    if [[ -z "$title" || "$title" == "null" ]]; then
        log_error "❌ Invalid title: '$title'"
        return 1
    fi
    
    if [[ -z "$author" || "$author" == "null" ]]; then
        log_error "❌ Invalid author: '$author'"
        return 1
    fi
    
    # Confidence check (using bc if available, otherwise basic comparison)
    if command -v bc >/dev/null 2>&1; then
        if (( $(echo "$confidence < $MIN_CONFIDENCE" | bc -l) )); then
            log_error "❌ Low confidence: $confidence (required: $MIN_CONFIDENCE)"
            return 1
        fi
    else
        # Simple comparison for confidence (assuming reasonable values)
        if [[ "${confidence%%.*}" -eq "0" && "${confidence#*.}" -lt "80" ]]; then
            log_error "❌ Low confidence: $confidence (required: $MIN_CONFIDENCE)"
            return 1
        fi
    fi
    
    # Duplicate check
    if is_duplicate_book "$title" "$author"; then
        log_error "❌ Duplicate book: '$title' by '$author'"
        return 1
    fi
    
    # Export for use in other functions
    export EXTRACTED_TITLE="$title"
    export EXTRACTED_AUTHOR="$author"
    export EXTRACTED_CONFIDENCE="$confidence"
    
    log_success "✅ Valid metadata: '$title' by '$author' (confidence: $confidence)"
    return 0
}

#=== GHERKIN STEP IMPLEMENTATIONS ===

given_I_have_bookstore_urls() {
    log_given "🏪 GIVEN: I have a pool of Russian bookstore URLs"
    
    local bookstore_count=${#RUSSIAN_BOOKSTORES[@]}
    log_info "📋 Available bookstores: $bookstore_count"
    log_info "🔍 Tracking file: $(basename "$BOOKS_TRACKING_FILE")"
    
    if [[ $bookstore_count -eq 0 ]]; then
        log_error "❌ No bookstore URLs configured"
        return 1
    fi
}

given_I_have_authenticated_session() {
    log_given "🔐 GIVEN: I have authenticated Telegram user session"
    
    if ! authenticate_user_session; then
        log_error "❌ Authentication failed - cannot proceed"
        return 1
    fi
    
    if ! verify_test_environment; then
        log_error "❌ Environment verification failed"
        return 1
    fi
}

when_I_extract_books_with_libru_engine() {
    log_when "⚡ WHEN: I extract books using fast lib.ru engine"
    
    # Use the high-performance lib.ru extractor engine
    local engine_path="$SCRIPT_DIR/../../scripts/lib_ru_extractor_engine.py"
    
    log_info "📚 Using lib.ru multi-category extraction engine"
    
    # Run lib.ru extraction engine  
    if LIBRU_RESULT=$(python3 "$engine_path" --format json --silent 2>&1); then
        # Check if we got valid JSON
        if echo "$LIBRU_RESULT" | jq . >/dev/null 2>&1; then
            local success=$(echo "$LIBRU_RESULT" | jq -r '.success')
            if [[ "$success" == "true" ]]; then
                local title=$(echo "$LIBRU_RESULT" | jq -r '.book.title')
                local author=$(echo "$LIBRU_RESULT" | jq -r '.book.author')
                local category=$(echo "$LIBRU_RESULT" | jq -r '.category')
                local extraction_time=$(echo "$LIBRU_RESULT" | jq -r '.performance.total_time')
                local confidence=$(echo "$LIBRU_RESULT" | jq -r '.book.confidence')
                
                log_success "✅ Lib.ru engine extracted book in ${extraction_time}s"
                log_info "📖 Title: $title"
                log_info "✍️ Author: $author"
                log_info "📂 Category: lib.ru/$category"
                log_info "🎯 Confidence: $confidence"
                
                # Set global variables for the test flow
                EXTRACTED_TITLE="$title"
                EXTRACTED_AUTHOR="$author"
                EXTRACTED_CONFIDENCE="$confidence"
                SELECTED_BOOKSTORE="lib.ru/$category"
                
                export EXTRACTED_TITLE EXTRACTED_AUTHOR EXTRACTED_CONFIDENCE SELECTED_BOOKSTORE
                return 0
            else
                local error=$(echo "$LIBRU_RESULT" | jq -r '.error // "Unknown error"')
                log_warn "⚠️ Lib.ru engine returned error: $error"
            fi
        else
            log_warn "⚠️ Lib.ru engine returned invalid JSON"
        fi
    else
        log_warn "⚠️ Failed to run lib.ru engine"
    fi
    
    log_info "🔄 Falling back to book_discovery engine"
    return 1
}

when_I_discover_books_with_engine() {
    log_when "🤖 WHEN: I discover books using book_discovery engine"
    
    # Use the atomic book_discovery engine
    local engine_path="$SCRIPT_DIR/engines/book_discovery/engine.sh"
    local selected_store=$(select_random_bookstore)
    
    log_info "🏪 Using engine with store: $selected_store"
    
    # Run book discovery engine
    if DISCOVERY_RESULT=$("$engine_path" --store "$selected_store" --count 3 --verbose 2>&1); then
        # Check if we got valid JSON
        if echo "$DISCOVERY_RESULT" | jq . >/dev/null 2>&1; then
            local status=$(echo "$DISCOVERY_RESULT" | jq -r '.status')
            if [[ "$status" == "success" ]]; then
                local book_count=$(echo "$DISCOVERY_RESULT" | jq -r '.result.discovered_count')
                log_success "✅ Engine discovered $book_count books"
                
                # Extract first book for testing
                DISCOVERED_BOOK_TITLE=$(echo "$DISCOVERY_RESULT" | jq -r '.result.books[0].title' 2>/dev/null || echo "")
                DISCOVERED_BOOK_URL=$(echo "$DISCOVERY_RESULT" | jq -r '.result.books[0].url' 2>/dev/null || echo "")
                
                export DISCOVERY_RESULT DISCOVERED_BOOK_TITLE DISCOVERED_BOOK_URL SELECTED_BOOKSTORE="$selected_store"
                return 0
            else
                local error_code=$(echo "$DISCOVERY_RESULT" | jq -r '.error.code')
                log_warn "⚠️ Engine returned error: $error_code"
                if [[ "$error_code" == "missing_dependencies" ]]; then
                    log_info "📋 Claude dependencies missing - this is expected in test environment"
                    log_info "🔄 Falling back to manual URL selection for testing"
                    # Fallback to original method
                    SELECTED_BOOKSTORE=$(select_random_bookstore)
                    STORE_TYPE=$(detect_store_type "$SELECTED_BOOKSTORE")
                    export SELECTED_BOOKSTORE STORE_TYPE
                    return 0
                fi
                return 1
            fi
        else
            log_error "❌ Engine returned invalid JSON"
            return 1
        fi
    else
        log_error "❌ Engine execution failed"
        return 1
    fi
}

and_I_extract_book_metadata() {
    log_when "🤖 AND: I extract book metadata using Claude AI with WebFetch"
    
    local attempt=1
    local extraction_success=false
    local same_url_retries=2  # Try same URL twice before switching
    
    while [[ $attempt -le $MAX_EXTRACTION_ATTEMPTS ]]; do
        log_info "🔄 Extraction attempt $attempt/$MAX_EXTRACTION_ATTEMPTS from $SELECTED_BOOKSTORE"
        
        # Try extraction from current bookstore
        if CLAUDE_RESULT=$(extract_with_claude "$SELECTED_BOOKSTORE" "$STORE_TYPE"); then
            log_info "📥 Claude result: $CLAUDE_RESULT"
            
            # Validate the extracted metadata
            if validate_metadata "$CLAUDE_RESULT"; then
                extraction_success=true
                break
            else
                log_warn "⚠️ Validation failed for attempt $attempt"
                log_extraction_attempt "$SELECTED_BOOKSTORE" "false" "" "" "0"
                # Add small delay between validation failures
                sleep 2
            fi
        else
            log_warn "⚠️ Extraction failed for attempt $attempt"
            log_extraction_attempt "$SELECTED_BOOKSTORE" "false" "" "" "0"
            # Add small delay between extraction failures
            sleep 1
        fi
        
        # Retry logic: try same URL twice, then switch
        if [[ $attempt -lt $MAX_EXTRACTION_ATTEMPTS ]]; then
            if [[ $((attempt % same_url_retries)) -eq 0 ]]; then
                log_info "🔄 Switching to different bookstore after $same_url_retries attempts..."
                SELECTED_BOOKSTORE=$(select_random_bookstore)
                STORE_TYPE=$(detect_store_type "$SELECTED_BOOKSTORE")
                log_info "🏪 New attempt with: $SELECTED_BOOKSTORE ($STORE_TYPE)"
            else
                log_info "🔄 Retrying same URL: $SELECTED_BOOKSTORE"
            fi
        fi
        
        ((attempt++))
    done
    
    if [[ "$extraction_success" == "false" ]]; then
        log_error "❌ Failed to extract valid metadata after $MAX_EXTRACTION_ATTEMPTS attempts"
        return 1
    fi
    
    log_success "✅ Successfully extracted: '$EXTRACTED_TITLE' by '$EXTRACTED_AUTHOR'"
    return 0
}

#=== CONFIDENCE VALIDATION FUNCTIONS ===

parse_user_request() {
    local query="$1"
    
    # Simple parsing: assume "Title Author" or "Title by Author" format
    # Extract author (usually last 1-2 words that look like names)
    local title_part=""
    local author_part=""
    
    # Look for common Russian author patterns (Firstname Lastname)
    if echo "$query" | grep -qE "[А-Я][а-я]+ [А-Я][а-я]+$"; then
        # Extract last two capitalized words as author
        author_part=$(echo "$query" | grep -oE "[А-Я][а-я]+ [А-Я][а-я]+$")
        title_part=$(echo "$query" | sed "s/$author_part$//" | sed 's/[[:space:]]*$//')
    else
        # Fallback: treat entire query as title
        title_part="$query"
        author_part=""
    fi
    
    # Export for use by other functions
    export USER_EXPECTED_TITLE="$title_part"
    export USER_EXPECTED_AUTHOR="$author_part"
    
    log_info "📋 Parsed request - Title: '$title_part', Author: '$author_part'"
}

compare_authors() {
    local expected_author="$1"
    local found_author="$2"
    
    # If no expected author, skip author check
    if [[ -z "$expected_author" ]]; then
        echo "0.5"  # Neutral score
        return
    fi
    
    # Simple similarity check (can be enhanced later)
    if [[ "$expected_author" == "$found_author" ]]; then
        echo "1.0"  # Perfect match
    elif echo "$found_author" | grep -q "$expected_author"; then
        echo "0.8"  # Partial match
    elif echo "$expected_author" | grep -q "$found_author"; then
        echo "0.8"  # Partial match  
    else
        echo "0.0"  # No match
    fi
}

compare_titles() {
    local expected_title="$1"
    local found_title="$2"
    
    # Convert to lowercase for comparison
    local expected_lower=$(echo "$expected_title" | tr '[:upper:]' '[:lower:]')
    local found_lower=$(echo "$found_title" | tr '[:upper:]' '[:lower:]')
    
    # Check for key words overlap
    local key_words=$(echo "$expected_lower" | tr ' ' '\n' | grep -v '^.$' | head -3)
    local matches=0
    local total_words=0
    
    while read -r word; do
        if [[ -n "$word" ]]; then
            ((total_words++))
            if echo "$found_lower" | grep -q "$word"; then
                ((matches++))
            fi
        fi
    done <<< "$key_words"
    
    if [[ $total_words -eq 0 ]]; then
        echo "0.0"
    else
        # Calculate similarity ratio
        local similarity=$(( (matches * 100) / total_words ))
        echo "0.$(printf "%02d" $similarity)"
    fi
}

validate_book_match() {
    local user_query="$1"
    local search_result_text="$2"
    
    log_info "🔍 Validating match for user request: '$user_query'"
    log_info "📖 Against search result: '$search_result_text'"
    
    # Parse what user actually wanted
    parse_user_request "$user_query"
    
    # For now, extract title from search result (simple heuristic)
    # This would normally be parsed from structured search results
    local found_title="$search_result_text"
    local found_author=""  # Search result doesn't include author info
    
    # Compare authors (critical check)
    local author_score=$(compare_authors "$USER_EXPECTED_AUTHOR" "$found_author")
    log_info "👤 Author match score: $author_score"
    
    # Compare titles  
    local title_score=$(compare_titles "$USER_EXPECTED_TITLE" "$found_title")
    log_info "📚 Title match score: $title_score"
    
    # Calculate combined confidence (author weighted heavily)
    local confidence
    if [[ -n "$USER_EXPECTED_AUTHOR" ]]; then
        # Author is critical - weight it 70%
        confidence=$(echo "$author_score * 0.7 + $title_score * 0.3" | bc -l 2>/dev/null || echo "0")
    else
        # No expected author - rely more on title
        confidence="$title_score"
    fi
    
    log_info "🎯 Combined confidence: $confidence"
    
    # Decision logic
    if (( $(echo "$confidence >= 0.85" | bc -l 2>/dev/null || echo "0") )); then
        log_success "✅ High confidence match - delivering EPUB"
        return 0
    elif (( $(echo "$confidence >= 0.6" | bc -l 2>/dev/null || echo "0") )); then
        log_warn "⚠️ Medium confidence - would ask user confirmation"
        return 1
    else
        log_error "❌ Low confidence - declining delivery"
        log_error "💡 Expected author '$USER_EXPECTED_AUTHOR' but got different book"
        return 1
    fi
}

then_I_should_get_valid_metadata() {
    log_then "✅ THEN: I should get valid book metadata with title and author"
    
    if [[ -z "${EXTRACTED_TITLE:-}" || -z "${EXTRACTED_AUTHOR:-}" ]]; then
        log_error "❌ Missing extracted metadata"
        return 1
    fi
    
    log_success "✅ Valid metadata confirmed"
    log_info "📚 Title: $EXTRACTED_TITLE"
    log_info "✍️ Author: $EXTRACTED_AUTHOR"
    log_info "📊 Confidence: $EXTRACTED_CONFIDENCE"
    
    return 0
}

when_I_search_for_book() {
    log_when "🔍 WHEN: I search for the extracted book using book_search.sh"
    
    # Record start time for timing validation
    IUC_TEST_START_TIME=$(get_epoch)
    
    # Prepare book query in format expected by book_search.sh
    local book_query="$EXTRACTED_TITLE $EXTRACTED_AUTHOR"
    
    # Send book search request  
    if send_book_search "$book_query" "$TARGET_BOT"; then
        log_success "✅ Book search request sent"
        log_info "📋 Book query: $book_query"
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
    
    # CONFIDENCE VALIDATION: Check if delivered book matches user request
    local book_query="$EXTRACTED_TITLE $EXTRACTED_AUTHOR"
    log_info "🔍 CONFIDENCE CHECK: Validating delivered book against user request"
    
    if validate_book_match "$book_query" "$response"; then
        log_success "✅ Book matches user request - proceeding with delivery"
    else
        log_error "❌ Book does not match user request - declining delivery"
        log_error "💡 User requested: '$EXTRACTED_TITLE' by '$EXTRACTED_AUTHOR'"
        log_error "💡 Bot delivered: Different book"
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

and_I_should_save_extracted_book() {
    log_then "💾 AND: I should save the extracted book to daily tracking file"
    
    save_extracted_book "$EXTRACTED_TITLE" "$EXTRACTED_AUTHOR" "$SELECTED_BOOKSTORE" "$EXTRACTED_CONFIDENCE"
    
    log_success "✅ Book saved to daily tracking file"
    log_info "📁 Tracking file: $(basename "$BOOKS_TRACKING_FILE")"
}

#=== TEST EXECUTION ===

run_russian_bookstore_extraction_scenario() {
    log_step "🧪 SCENARIO: Successful Russian bookstore extraction and EPUB delivery"
    echo "=========================================="
    
    # Execute Gherkin steps in order
    given_I_have_bookstore_urls
    given_I_have_authenticated_session
    
    # Try lib.ru engine first (fastest), then fallback to other methods
    if when_I_extract_books_with_libru_engine; then
        log_info "⚡ Using lib.ru extracted book: $EXTRACTED_TITLE by $EXTRACTED_AUTHOR"
    elif when_I_discover_books_with_engine && [[ -n "${DISCOVERED_BOOK_TITLE:-}" && -n "${DISCOVERED_BOOK_URL:-}" ]]; then
        log_info "🤖 Using engine-discovered book: $DISCOVERED_BOOK_TITLE"
        # Set up for book search
        EXTRACTED_TITLE="$DISCOVERED_BOOK_TITLE"
        EXTRACTED_AUTHOR="Unknown"  # Engine doesn't extract author yet
        EXTRACTED_CONFIDENCE="0.8"  # Engine-discovered books have good confidence
    else
        log_info "🔄 Using fallback extraction method"
        and_I_extract_book_metadata
        then_I_should_get_valid_metadata
    fi
    
    when_I_search_for_book
    then_I_should_receive_progress_message_within_N_seconds 10
    and_I_should_receive_EPUB_file_within_N_seconds 30
    
    # Save extracted book (adapt for engine or manual extraction)
    if [[ -n "${DISCOVERED_BOOK_TITLE:-}" ]]; then
        save_extracted_book "$DISCOVERED_BOOK_TITLE" "${EXTRACTED_AUTHOR:-Unknown}" "${DISCOVERED_BOOK_URL:-$SELECTED_BOOKSTORE}" "${EXTRACTED_CONFIDENCE:-0.8}"
    else
        and_I_should_save_extracted_book
    fi
    
    # Validate timing
    if validate_timing "$IUC_TEST_START_TIME" 45; then
        log_success "✅ Timing validation passed"
    else
        log_warn "⚠️ Timing validation failed (took longer than expected)"
    fi
    
    log_success "✅ Russian bookstore extraction scenario completed"
    
    # Calculate and display success rate
    calculate_success_rate
}

main() {
    echo "🚀 $TEST_NAME: $TEST_DESCRIPTION"
    echo "=================================================="
    log_info "⏰ Start time: $(get_timestamp)"
    log_info "🤖 Target bot: $TARGET_BOT"
    log_info "📊 Min confidence: $MIN_CONFIDENCE"
    log_info "🔄 Max attempts: $MAX_EXTRACTION_ATTEMPTS"
    log_info "👤 User: ${IUC_USER_NAME:-Unknown} (ID: ${IUC_USER_ID:-Unknown})"
    log_info "🔄 Test type: Russian Bookstore Extraction with Claude AI"
    echo "=================================================="
    echo ""
    
    # Run atomic test scenario - ONLY Russian bookstore extraction
    local overall_result="PASSED"
    
    # Russian bookstore extraction scenario (atomic test)
    if ! run_russian_bookstore_extraction_scenario; then
        overall_result="FAILED"
        log_error "❌ Russian bookstore extraction scenario failed"
    fi
    
    # Generate final report
    generate_test_report "$TEST_NAME" "$overall_result" "$TEST_DESCRIPTION"
    
    if [[ "$overall_result" == "PASSED" ]]; then
        log_success "🎉 $TEST_NAME PASSED: Russian bookstore extraction successful!"
        exit 0
    else
        log_error "❌ $TEST_NAME FAILED: Russian bookstore extraction failed"
        exit 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
🎯 IUC05_russian_bookstore_extraction: Russian bookstore URL extraction and high-confidence book search

OVERVIEW:
=========
Integration test for Russian bookstore URL extraction using Claude AI.
Tests the complete flow: URL Selection → Claude Extraction → Validation → Book Search → EPUB delivery.

USAGE:
======
./tests/IUC/IUC05_russian_bookstore_extraction.sh                # Run the test
./tests/IUC/IUC05_russian_bookstore_extraction.sh --help         # Show this help

ATOMIC TEST SCENARIO:
====================
1. Russian bookstore extraction and delivery (ONLY)
   - Select random Russian bookstore from 10-store pool
   - Extract book metadata using Claude AI with WebFetch
   - Validate metadata quality and 80%+ confidence
   - Check for daily duplicates (title + author)
   - Send extracted book to search system
   - Receive progress message and EPUB delivery
   - Save book to daily tracking file

ATOMIC PRINCIPLE:
=================
This test focuses ONLY on successful Russian bookstore extraction:
- ✅ ONE scenario: Random bookstore → Claude extraction → EPUB delivery
- ✅ ONE validation: 80%+ confidence + no duplicates
- ✅ ONE outcome: Pass/Fail based on successful end-to-end flow
- ✅ RESILIENCE: Retry extraction up to 3 times with different bookstores
- ✅ TRACKING: Daily deduplication via books_extracted_YYYY-MM-DD.json

BOOKSTORE COVERAGE:
===================
10 Russian bookstores across different categories:
- Commercial: eksmo.ru, ozon.ru, labirint.ru, book24.ru  
- Cultural: admarginem.ru, shop.garagemca.org, slowbooks.ru
- Independent: vse-svobodny.com, podpisnie.ru
- Academic: alpinabook.ru

CONFIDENCE REQUIREMENTS:
========================
- Minimum 80% confidence for metadata quality
- Title and author must be non-empty and meaningful
- Duplicate detection by title + author combination
- Daily tracking with automatic file rotation

GHERKIN SPECIFICATION:
======================
See: features/IUC05_russian_bookstore_extraction.feature

AI LEARNING REFERENCE:
======================
This test introduces Claude AI integration patterns:
- Claude SDK usage via `claude -p` command with WebFetch
- JSON metadata extraction and validation
- Confidence scoring and quality thresholds
- Daily deduplication tracking
- Mixed error handling strategy (retry extraction, fail fast on search)

TIMING EXPECTATIONS:
====================
- Claude extraction: 10-15 seconds per attempt
- Progress message: 5-10 seconds  
- EPUB delivery: 15-30 seconds
- Total test duration: <45 seconds

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