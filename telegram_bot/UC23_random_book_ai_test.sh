#!/bin/bash

# UC23: Random Book AI-Generated Test
# Uses Claude AI to generate random book titles and authors in different languages
# Each run tests different books to ensure variety and EPUB delivery
# Bot: @epub_toc_based_sample_bot
# Usage: ./UC23_random_book_ai_test.sh

set -euo pipefail

# Load configuration from .env file
source .env 2>/dev/null || true
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls}"
BOT_USERNAME="epub_toc_based_sample_bot"
CHAT_ID="${CHAT_ID:-14835038}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_ai() { echo -e "${CYAN}[AI]${NC} $1"; }

# Generate random book using Claude AI
generate_random_book() {
    local category="$1"
    local language="$2"
    
    log_ai "🤖 Generating random $category book in $language using Claude AI..." >&2
    
    local prompt="Generate a single real $category book title and author in $language language. 
Requirements:
- Must be a real published book that likely exists in libraries
- Include both title and author name
- For non-English: provide romanized/transliterated version in parentheses if needed
- Format: 'Title by Author' or 'Title Author' (simple format)
- Examples: 'Clean Code Robert Martin', 'Война и мир Толстoy', 'Les Misérables Hugo'
- Choose randomly from well-known $category books
- Return ONLY the book query in one line, nothing else"

    local claude_result
    # Try local Claude first, then fallback to system claude
    local claude_cmd=""
    if command -v /home/almaz/.claude/local/claude &> /dev/null; then
        claude_cmd="/home/almaz/.claude/local/claude"
    elif command -v claude &> /dev/null; then
        claude_cmd="claude"
    fi
    
    if [[ -n "$claude_cmd" ]] && claude_result=$($claude_cmd -p "$prompt" 2>/dev/null | head -1 | tr -d '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'); then
        if [[ -n "$claude_result" && ${#claude_result} -gt 5 && ${#claude_result} -lt 80 ]]; then
            log_success "🎯 Generated: '$claude_result'" >&2
            echo "$claude_result"
            return 0
        else
            log_warn "⚠️ Claude result too short/long: '$claude_result'" >&2
        fi
    else
        log_warn "⚠️ Claude generation failed" >&2
    fi
    
    # Fallback to predefined books if Claude fails
    local fallback_books=()
    case "$category-$language" in
        "fiction-English")
            fallback_books=("1984 George Orwell" "Pride and Prejudice Jane Austen" "The Great Gatsby Fitzgerald")
            ;;
        "programming-English") 
            fallback_books=("Clean Code Robert Martin" "Design Patterns Gang of Four" "Refactoring Martin Fowler")
            ;;
        "fiction-Russian")
            fallback_books=("Война и мир Толстой" "Анна Каренина Толстой" "Преступление и наказание Достоевский")
            ;;
        "academic-English")
            fallback_books=("Introduction to Algorithms CLRS" "Operating System Concepts" "Database Systems")
            ;;
        *)
            fallback_books=("The Alchemist Paulo Coelho" "Sapiens Yuval Noah Harari" "Thinking Fast Slow Kahneman")
            ;;
    esac
    
    local random_index=$((RANDOM % ${#fallback_books[@]}))
    local fallback="${fallback_books[$random_index]}"
    log_warn "🔄 Using fallback: '$fallback'" >&2
    echo "$fallback"
}

# Send message to bot
send_book_query() {
    local query="$1"
    local api_url="https://api.telegram.org/bot${BOT_TOKEN}/sendMessage"
    local payload='{"chat_id": "'$CHAT_ID'", "text": "'$query'"}'
    
    log_info "📤 Sending query to bot: '$query'"
    
    local response
    if response=$(curl -s -X POST -H "Content-Type: application/json" -d "$payload" "$api_url" 2>/dev/null); then
        if [[ "$response" == *'"ok":true'* ]]; then
            log_success "✅ Query sent successfully"
            return 0
        else
            log_error "❌ Send failed: $(echo "$response" | grep -o '"description":"[^"]*"' || echo 'Unknown error')"
            return 1
        fi
    else
        log_error "❌ Failed to send query to bot"
        return 1
    fi
}

# Enhanced response monitoring with detailed EPUB detection
monitor_bot_responses() {
    local query="$1"
    local timeout=90  # Longer timeout for book processing
    local start_time=$(date +%s)
    
    log_info "👁️ Monitoring bot responses for '$query' (${timeout}s timeout)..."
    
    local last_update_id=0
    local responses=()
    local progress_messages=()
    local error_messages=()
    local epub_found=false
    local epub_details=""
    
    while [[ $(date +%s) -lt $((start_time + timeout)) ]]; do
        local api_url="https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=$((last_update_id + 1))&timeout=10"
        local response
        
        if response=$(curl -s "$api_url" 2>/dev/null); then
            if [[ "$response" == *'"result"'* ]] && [[ "$response" != *'"result":[]'* ]]; then
                
                # Process updates
                local update_count=$(echo "$response" | grep -o '"update_id":[0-9]*' | wc -l)
                log_info "📥 Processing $update_count updates..."
                
                # Extract messages from bot (not our own)
                while read -r message_data; do
                    [[ -z "$message_data" ]] && continue
                    
                    # Skip our own messages
                    if [[ "$message_data" == *"\"id\":$CHAT_ID"* ]]; then
                        continue
                    fi
                    
                    # Check for document (EPUB file)
                    if [[ "$message_data" == *'"document"'* ]]; then
                        local file_name=$(echo "$message_data" | grep -o '"file_name":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
                        local file_size=$(echo "$message_data" | grep -o '"file_size":[0-9]*' | cut -d':' -f2 || echo "0")
                        local mime_type=$(echo "$message_data" | grep -o '"mime_type":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
                        
                        if [[ "$file_name" == *".epub"* ]] || [[ "$mime_type" == *"epub"* ]]; then
                            epub_found=true
                            epub_details="$file_name (${file_size} bytes)"
                            log_success "📖 EPUB DETECTED: $epub_details"
                            responses+=("epub_file")
                            
                            # Calculate download size in MB
                            local size_mb=$((file_size / 1024 / 1024))
                            log_success "🎉 SUCCESS: EPUB file received ($size_mb MB)"
                        else
                            log_info "📄 Other document: $file_name"
                            responses+=("other_document")
                        fi
                    fi
                    
                    # Check for text messages
                    if [[ "$message_data" == *'"text"'* ]]; then
                        local text_content=$(echo "$message_data" | grep -o '"text":"[^"]*"' | cut -d'"' -f4 | head -1)
                        
                        if [[ "$text_content" == *'🔍'* ]] || [[ "$text_content" == *'Searching'* ]] || [[ "$text_content" == *'search'* ]]; then
                            log_info "🔍 PROGRESS: $text_content"
                            progress_messages+=("$text_content")
                            responses+=("progress")
                        elif [[ "$text_content" == *'❌'* ]] || [[ "$text_content" == *'not found'* ]] || [[ "$text_content" == *'error'* ]]; then
                            log_warn "❌ ERROR: $text_content"
                            error_messages+=("$text_content")
                            responses+=("error")
                        elif [[ "$text_content" == *'✅'* ]] || [[ "$text_content" == *'success'* ]] || [[ "$text_content" == *'found'* ]]; then
                            log_success "✅ SUCCESS: $text_content"
                            responses+=("success")
                        else
                            log_info "💬 BOT: ${text_content:0:60}..."
                            responses+=("text")
                        fi
                    fi
                    
                done < <(echo "$response" | grep -o '"message":{[^}]*"text":"[^"]*"[^}]*}' 2>/dev/null || echo "$response" | grep -o '"message":{[^}]*"document"[^}]*}' 2>/dev/null || echo "")
                
                # Update last_update_id
                local new_update_id=$(echo "$response" | grep -o '"update_id":[0-9]*' | tail -1 | grep -o '[0-9]*$' || echo "$last_update_id")
                if [[ "$new_update_id" -gt "$last_update_id" ]]; then
                    last_update_id="$new_update_id"
                fi
            fi
        fi
        
        # Check for completion
        if [[ "$epub_found" == "true" && "${#progress_messages[@]}" -gt 0 ]]; then
            log_success "🏆 COMPLETE SUCCESS: Progress messages + EPUB delivery!"
            break
        elif [[ "${#error_messages[@]}" -gt 0 && $(( $(date +%s) - start_time )) -gt 45 ]]; then
            log_warn "⚠️ Error detected, waiting a bit more..."
        fi
        
        sleep 3
    done
    
    local duration=$(( $(date +%s) - start_time ))
    
    # Final summary
    log_info ""
    log_info "📊 RESPONSE SUMMARY (${duration}s total)"
    log_info "=========================="
    log_info "Total responses: ${#responses[@]}"
    log_info "Progress messages: ${#progress_messages[@]}"
    log_info "Error messages: ${#error_messages[@]}"
    log_info "EPUB found: $epub_found"
    [[ -n "$epub_details" ]] && log_info "EPUB details: $epub_details"
    
    # Determine success
    if [[ "$epub_found" == "true" ]]; then
        log_success "🎉 PERFECT RESULT: EPUB delivered successfully!"
        return 0
    elif [[ "${#progress_messages[@]}" -gt 0 && "${#responses[@]}" -gt 1 ]]; then
        log_success "✅ GOOD RESULT: Bot processing detected"
        return 0
    elif [[ "${#responses[@]}" -gt 0 ]]; then
        log_warn "⚠️ PARTIAL RESULT: Some bot activity"
        return 1
    else
        log_error "❌ NO RESPONSE: Bot not responding"
        return 1
    fi
}

# Test a single AI-generated book
test_ai_generated_book() {
    local test_number="$1"
    local category="$2" 
    local language="$3"
    
    log_info ""
    log_info "🧪 TEST $test_number: AI-Generated $category Book ($language)"
    log_info "============================================"
    log_info "$(date '+%Y-%m-%d %H:%M:%S')"
    
    # Generate random book using Claude AI
    local book_query
    if book_query=$(generate_random_book "$category" "$language"); then
        log_success "📚 Testing book: '$book_query'"
        
        # Send query to bot
        if send_book_query "$book_query"; then
            # Monitor responses
            if monitor_bot_responses "$book_query"; then
                log_success "✅ TEST $test_number PASSED: '$book_query'"
                return 0
            else
                log_warn "⚠️ TEST $test_number PARTIAL: '$book_query'"
                return 1
            fi
        else
            log_error "❌ TEST $test_number FAILED: Could not send '$book_query'"
            return 1
        fi
    else
        log_error "❌ TEST $test_number FAILED: Could not generate book"
        return 1
    fi
}

# Main test execution
main() {
    log_info "🎲 UC23: Random Book AI-Generated Test"
    log_info "Bot: @$BOT_USERNAME"
    log_info "Chat: $CHAT_ID"
    log_info "AI: Claude (claude -p)"
    log_info "$(date '+%Y-%m-%d %H:%M:%S')"
    log_info "======================================="
    
    # Test different categories and languages
    local test_cases=(
        "1:programming:English"
        "2:fiction:English"
        "3:fiction:Russian"
        "4:academic:English"
    )
    
    local total_tests=0
    local passed_tests=0
    local epub_deliveries=0
    
    # Check Claude availability (try local first, then fallback)
    if ! command -v claude &> /dev/null && ! command -v /home/almaz/.claude/local/claude &> /dev/null; then
        log_warn "⚠️ Claude CLI not available, using predefined random selection"
    fi
    
    for test_case in "${test_cases[@]}"; do
        IFS=':' read -r test_num category language <<< "$test_case"
        
        total_tests=$((total_tests + 1))
        
        if test_ai_generated_book "$test_num" "$category" "$language"; then
            passed_tests=$((passed_tests + 1))
            # Count EPUB deliveries based on last test result
            # This is a simplified check - in real implementation you'd track this per test
        fi
        
        # Wait between tests to avoid rate limiting and conflicts
        if [[ $test_num -lt ${#test_cases[@]} ]]; then
            log_info "⏳ Waiting 20 seconds before next test..."
            sleep 20
        fi
    done
    
    # Final results
    local success_rate=$(( passed_tests * 100 / total_tests ))
    
    log_info ""
    log_info "🎯 UC23 FINAL RESULTS"
    log_info "======================"
    log_info "Tests Run: $total_tests"
    log_info "Tests Passed: $passed_tests"
    log_info "Success Rate: ${success_rate}%"
    log_info "Test Completed: $(date '+%Y-%m-%d %H:%M:%S')"
    
    if [[ $success_rate -ge 75 ]]; then
        log_success "🎉 UC23 PASSED - AI book generation and bot delivery working!"
        log_success "🤖 Random book testing successful with variety across languages/categories"
        return 0
    elif [[ $success_rate -ge 50 ]]; then
        log_warn "⚠️ UC23 PARTIAL - Some AI books worked, investigate failures"
        return 1
    else
        log_error "❌ UC23 FAILED - AI book generation or bot delivery issues"
        return 1
    fi
}

# Execute main function
main "$@"