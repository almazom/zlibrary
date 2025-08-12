#!/bin/bash

# UC2: Telegram Bot Book Variety Test
# Tests different types of books: programming, fiction, Russian, academic
# Bot: @epub_toc_based_sample_bot
# Usage: ./UC2_telegram_bot_variety_test.sh

set -euo pipefail

# Load from .env file
source .env 2>/dev/null || true
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls}"
CHAT_ID="${CHAT_ID:-14835038}"

# Different book categories to test
declare -a PROGRAMMING_BOOKS=(
    "Clean Code Robert Martin"
    "Python Programming" 
    "JavaScript The Good Parts"
    "Design Patterns Gang of Four"
)

declare -a FICTION_BOOKS=(
    "1984 George Orwell"
    "The Great Gatsby Fitzgerald"
    "To Kill a Mockingbird Harper Lee"
    "Harry Potter Stone"
)

declare -a RUSSIAN_BOOKS=(
    "Война и мир Толстой"
    "Преступление и наказание Достоевский"
    "Мастер и Маргарита Булгаков"
    "Анна Каренина Толстой"
)

declare -a ACADEMIC_BOOKS=(
    "Introduction to Algorithms CLRS"
    "Artificial Intelligence Russell Norvig" 
    "Operating System Concepts"
    "Database System Concepts"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Send message to bot
send_book_query() {
    local query="$1"
    local api_url="https://api.telegram.org/bot${BOT_TOKEN}/sendMessage"
    local payload='{"chat_id": "'$CHAT_ID'", "text": "'$query'"}'
    
    log_info "📤 Sending: '$query'"
    
    local response
    if response=$(curl -s -X POST -H "Content-Type: application/json" -d "$payload" "$api_url" 2>/dev/null); then
        if [[ "$response" == *'"ok":true'* ]]; then
            log_success "✅ Message sent successfully"
            return 0
        else
            log_error "❌ Send failed: $(echo "$response" | grep -o '"description":"[^"]*"' || echo 'Unknown error')"
            return 1
        fi
    else
        log_error "❌ Failed to send query"
        return 1
    fi
}

# Monitor for bot responses
monitor_response() {
    local query="$1"
    local timeout=60
    local start_time=$(date +%s)
    
    log_info "👁️ Monitoring response for '$query' (${timeout}s timeout)..."
    
    local last_update_id=0
    local found_response=false
    
    while [[ $(date +%s) -lt $((start_time + timeout)) ]] && [[ "$found_response" == "false" ]]; do
        local api_url="https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=$((last_update_id + 1))&timeout=5"
        local response
        
        if response=$(curl -s "$api_url" 2>/dev/null); then
            if [[ "$response" == *'"result"'* ]] && [[ "$response" != *'"result":[]'* ]]; then
                # Check for documents (EPUB files)
                if [[ "$response" == *'"document"'* ]]; then
                    if [[ "$response" == *'.epub'* ]] || [[ "$response" == *'application/epub'* ]]; then
                        log_success "📖 EPUB file received!"
                        found_response=true
                        return 0
                    else
                        log_warn "📄 Non-EPUB document received"
                        found_response=true
                        return 1
                    fi
                fi
                
                # Check for progress/error messages
                if [[ "$response" == *'"text"'* ]]; then
                    if [[ "$response" == *'🔍'* ]] || [[ "$response" == *'Searching'* ]]; then
                        log_info "🔍 Progress message detected"
                    elif [[ "$response" == *'❌'* ]] || [[ "$response" == *'not found'* ]]; then
                        log_warn "❌ Book not found"
                        found_response=true
                        return 1
                    elif [[ "$response" == *'✅'* ]] || [[ "$response" == *'found'* ]]; then
                        log_success "✅ Success message detected"
                    fi
                fi
                
                # Update last_update_id
                local new_update_id
                new_update_id=$(echo "$response" | grep -o '"update_id":[0-9]*' | tail -1 | grep -o '[0-9]*$' || echo "$last_update_id")
                if [[ "$new_update_id" -gt "$last_update_id" ]]; then
                    last_update_id="$new_update_id"
                fi
            fi
        fi
        
        sleep 3
    done
    
    if [[ "$found_response" == "false" ]]; then
        log_warn "⏰ Timeout - no response received"
        return 1
    fi
}

# Test a single book query
test_book_query() {
    local query="$1"
    local category="$2"
    
    log_info ""
    log_info "📚 Testing [$category]: '$query'"
    log_info "$(date '+%Y-%m-%d %H:%M:%S')"
    
    if send_book_query "$query"; then
        if monitor_response "$query"; then
            log_success "✅ SUCCESS: '$query' → EPUB received"
            return 0
        else
            log_warn "⚠️ PARTIAL: '$query' → Bot responded but no EPUB"
            return 1
        fi
    else
        log_error "❌ FAILED: '$query' → Could not send message"
        return 1
    fi
}

# Test book category
test_category() {
    local category="$1"
    local -n books_array=$2
    local max_books="${3:-3}"
    
    log_info ""
    log_info "=== TESTING CATEGORY: $category ==="
    
    local success_count=0
    local total_count=0
    
    for ((i=0; i<${#books_array[@]} && i<max_books; i++)); do
        local book="${books_array[$i]}"
        total_count=$((total_count + 1))
        
        if test_book_query "$book" "$category"; then
            success_count=$((success_count + 1))
        fi
        
        # Wait between tests to avoid rate limiting
        if [[ $((i + 1)) -lt $max_books ]] && [[ $((i + 1)) -lt ${#books_array[@]} ]]; then
            log_info "⏳ Waiting 15 seconds before next test..."
            sleep 15
        fi
    done
    
    local success_rate=$(( success_count * 100 / total_count ))
    log_info ""
    log_info "📊 $category Results: $success_count/$total_count successful (${success_rate}%)"
    
    return $success_count
}

# Main test function
main() {
    log_info "🚀 Starting Book Variety Test Suite"
    log_info "🤖 Bot: @epub_toc_based_sample_bot (epub_extractor_bot)"
    log_info "💬 Chat ID: $CHAT_ID"
    log_info "$(date '+%Y-%m-%d %H:%M:%S')"
    log_info ""
    
    local total_success=0
    local total_tests=0
    
    # Test each category
    test_category "PROGRAMMING" PROGRAMMING_BOOKS 2
    local prog_success=$?
    total_success=$((total_success + prog_success))
    total_tests=$((total_tests + 2))
    
    test_category "FICTION" FICTION_BOOKS 2  
    local fiction_success=$?
    total_success=$((total_success + fiction_success))
    total_tests=$((total_tests + 2))
    
    test_category "RUSSIAN" RUSSIAN_BOOKS 2
    local russian_success=$?
    total_success=$((total_success + russian_success))
    total_tests=$((total_tests + 2))
    
    test_category "ACADEMIC" ACADEMIC_BOOKS 1
    local academic_success=$?
    total_success=$((total_success + academic_success))
    total_tests=$((total_tests + 1))
    
    # Final summary
    local overall_rate=$(( total_success * 100 / total_tests ))
    log_info ""
    log_info "🎯 FINAL RESULTS"
    log_info "===================="
    log_info "Total Books Tested: $total_tests"
    log_info "Successful EPUBs: $total_success"
    log_info "Success Rate: ${overall_rate}%"
    log_info "Test Duration: $(date '+%Y-%m-%d %H:%M:%S')"
    
    if [[ $total_success -gt $((total_tests / 2)) ]]; then
        log_success "🎉 OVERALL SUCCESS - Bot is working well!"
        return 0
    else
        log_error "❌ OVERALL FAILURE - Bot needs investigation"
        return 1
    fi
}

# Execute main function
main "$@"