#!/bin/bash

# UC22: Telegram Bot Basic Functionality Test
# Tests core bot functionality: /start, simple book request, progress messages
# Bot: @epub_toc_based_sample_bot
# Usage: ./UC22_telegram_bot_basic_test.sh

set -euo pipefail

# Configuration - Load from .env file 
source .env 2>/dev/null || true
BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls}"
BOT_USERNAME="epub_toc_based_sample_bot"
BOT_ID="7956300223"
CHAT_ID="${CHAT_ID:-14835038}"

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

# Test bot API connection
test_bot_api() {
    log_info "🔧 Testing bot API connection..."
    
    local api_url="https://api.telegram.org/bot${BOT_TOKEN}/getMe"
    local response
    
    if response=$(curl -s "$api_url" 2>/dev/null); then
        if [[ "$response" == *'"ok":true'* ]] && [[ "$response" == *"$BOT_USERNAME"* ]]; then
            log_success "✅ Bot API connection working: @$BOT_USERNAME"
            return 0
        else
            log_error "❌ Bot API response invalid: $response"
            return 1
        fi
    else
        log_error "❌ Failed to connect to bot API"
        return 1
    fi
}

# Send message to bot
send_message() {
    local text="$1"
    local api_url="https://api.telegram.org/bot${BOT_TOKEN}/sendMessage"
    local payload='{"chat_id": "'$CHAT_ID'", "text": "'$text'"}'
    
    log_info "📤 Sending: '$text'"
    
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
        log_error "❌ Failed to send message"
        return 1
    fi
}

# Monitor bot responses with detailed analysis
monitor_responses() {
    local expected_type="$1"  # "start_response", "book_response", or "general"
    local timeout=45
    local start_time=$(date +%s)
    
    log_info "👁️ Monitoring responses (expecting: $expected_type, timeout: ${timeout}s)..."
    
    local last_update_id=0
    local responses_found=()
    local progress_detected=false
    local epub_detected=false
    local error_detected=false
    
    while [[ $(date +%s) -lt $((start_time + timeout)) ]]; do
        local api_url="https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=$((last_update_id + 1))&timeout=5"
        local response
        
        if response=$(curl -s "$api_url" 2>/dev/null); then
            if [[ "$response" == *'"result"'* ]] && [[ "$response" != *'"result":[]'* ]]; then
                
                # Process each update
                while IFS= read -r update; do
                    [[ -z "$update" ]] && continue
                    
                    local message=$(echo "$update" | grep -o '"message":{[^}]*}' || echo "")
                    [[ -z "$message" ]] && continue
                    
                    # Skip our own messages
                    if [[ "$message" == *"\"id\":$CHAT_ID"* ]]; then
                        continue
                    fi
                    
                    # Check for document (EPUB file)
                    if [[ "$message" == *'"document"'* ]]; then
                        local doc_info=$(echo "$message" | grep -o '"document":{[^}]*}' || echo "")
                        if [[ "$doc_info" == *'.epub'* ]] || [[ "$doc_info" == *'application/epub'* ]]; then
                            log_success "📖 EPUB DOCUMENT RECEIVED!"
                            epub_detected=true
                            responses_found+=("epub_document")
                        else
                            log_info "📄 Other document received"
                            responses_found+=("other_document")
                        fi
                    fi
                    
                    # Check for text responses
                    if [[ "$message" == *'"text"'* ]]; then
                        local text_content=$(echo "$message" | grep -o '"text":"[^"]*"' | cut -d'"' -f4)
                        
                        # Analyze text content
                        if [[ "$text_content" == *'🔍'* ]] || [[ "$text_content" == *'Searching'* ]]; then
                            log_success "🔍 PROGRESS MESSAGE: ${text_content:0:50}..."
                            progress_detected=true
                            responses_found+=("progress_message")
                        elif [[ "$text_content" == *'❌'* ]] || [[ "$text_content" == *'not found'* ]] || [[ "$text_content" == *'error'* ]]; then
                            log_warn "❌ ERROR MESSAGE: ${text_content:0:50}..."
                            error_detected=true
                            responses_found+=("error_message")
                        elif [[ "$text_content" == *'✅'* ]] || [[ "$text_content" == *'success'* ]]; then
                            log_success "✅ SUCCESS MESSAGE: ${text_content:0:50}..."
                            responses_found+=("success_message")
                        elif [[ "$text_content" == *'Welcome'* ]] || [[ "$text_content" == *'/start'* ]]; then
                            log_success "🚀 WELCOME MESSAGE: ${text_content:0:50}..."
                            responses_found+=("welcome_message")
                        else
                            log_info "💬 TEXT RESPONSE: ${text_content:0:50}..."
                            responses_found+=("text_response")
                        fi
                    fi
                    
                done < <(echo "$response" | grep -o '"update_id":[0-9]*' | while read -r update_line; do
                    echo "$response" | grep -A 20 "$update_line"
                done)
                
                # Update last_update_id
                local new_update_id=$(echo "$response" | grep -o '"update_id":[0-9]*' | tail -1 | grep -o '[0-9]*$' || echo "$last_update_id")
                if [[ "$new_update_id" -gt "$last_update_id" ]]; then
                    last_update_id="$new_update_id"
                fi
            fi
        fi
        
        # Check if we have enough evidence for the expected type
        if [[ "$expected_type" == "book_response" ]]; then
            if [[ "$epub_detected" == "true" && "$progress_detected" == "true" ]]; then
                log_success "🎉 Complete book response detected (progress + EPUB)!"
                break
            elif [[ "$progress_detected" == "true" && "${#responses_found[@]}" -gt 1 ]]; then
                log_success "📊 Book processing detected (progress messages)!"
                break
            fi
        elif [[ "$expected_type" == "start_response" ]]; then
            if [[ "${#responses_found[@]}" -gt 0 ]]; then
                log_success "📝 Start response detected!"
                break
            fi
        fi
        
        sleep 2
    done
    
    local duration=$(( $(date +%s) - start_time ))
    
    # Summary
    log_info "📊 Response Summary ($duration seconds):"
    log_info "   Total responses: ${#responses_found[@]}"
    log_info "   Progress detected: $progress_detected"
    log_info "   EPUB detected: $epub_detected"
    log_info "   Error detected: $error_detected"
    
    # Determine success
    if [[ "${#responses_found[@]}" -eq 0 ]]; then
        log_error "❌ No responses detected"
        return 1
    elif [[ "$expected_type" == "book_response" ]]; then
        if [[ "$epub_detected" == "true" ]]; then
            log_success "🏆 PERFECT: Complete book delivery!"
            return 0
        elif [[ "$progress_detected" == "true" ]]; then
            log_success "✅ GOOD: Bot processing book request"
            return 0
        else
            log_warn "⚠️ PARTIAL: Bot responded but no clear book processing"
            return 1
        fi
    else
        log_success "✅ Bot responding appropriately"
        return 0
    fi
}

# Test /start command
test_start_command() {
    log_info ""
    log_info "🚀 TEST 1: /start Command"
    log_info "========================"
    
    if send_message "/start"; then
        if monitor_responses "start_response"; then
            log_success "✅ /start command working"
            return 0
        else
            log_warn "⚠️ /start sent but no clear response"
            return 1
        fi
    else
        log_error "❌ Failed to send /start command"
        return 1
    fi
}

# Test simple book request
test_book_request() {
    local book_title="$1"
    
    log_info ""
    log_info "📚 TEST 2: Book Request - '$book_title'"
    log_info "=================================="
    
    if send_message "$book_title"; then
        if monitor_responses "book_response"; then
            log_success "✅ Book request processed successfully"
            return 0
        else
            log_warn "⚠️ Book request sent but incomplete response"
            return 1
        fi
    else
        log_error "❌ Failed to send book request"
        return 1
    fi
}

# Main test execution
main() {
    log_info "🤖 UC22: Telegram Bot Basic Functionality Test"
    log_info "Bot: @$BOT_USERNAME (ID: $BOT_ID)"
    log_info "Chat ID: $CHAT_ID"
    log_info "$(date '+%Y-%m-%d %H:%M:%S')"
    log_info "================================================"
    
    local total_tests=0
    local passed_tests=0
    
    # Test 0: Bot API Connection
    log_info ""
    log_info "🔧 TEST 0: Bot API Connection"
    log_info "=========================="
    total_tests=$((total_tests + 1))
    if test_bot_api; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # Test 1: Start command  
    total_tests=$((total_tests + 1))
    if test_start_command; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # Wait between tests
    log_info "⏳ Waiting 10 seconds between tests..."
    sleep 10
    
    # Test 2: Book request
    total_tests=$((total_tests + 1))
    if test_book_request "Clean Code Robert Martin"; then
        passed_tests=$((passed_tests + 1))
    fi
    
    # Final results
    local success_rate=$(( passed_tests * 100 / total_tests ))
    
    log_info ""
    log_info "🎯 FINAL RESULTS"
    log_info "================="
    log_info "Tests Passed: $passed_tests/$total_tests"
    log_info "Success Rate: ${success_rate}%"
    log_info "Test Completed: $(date '+%Y-%m-%d %H:%M:%S')"
    
    if [[ $success_rate -ge 67 ]]; then
        log_success "🎉 UC22 PASSED - Bot basic functionality working!"
        return 0
    else
        log_error "❌ UC22 FAILED - Bot needs investigation"
        return 1
    fi
}

# Execute main function
main "$@"