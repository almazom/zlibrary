#!/bin/bash

# UC25: English Programming Books Test with Message Verification
# Tests English programming books with MCP Telegram reader verification
# Expected: EPUB downloads for popular programming books

set -euo pipefail

# Configuration
BOT_USERNAME="epub_toc_based_sample_bot"
USER_ID="5282615364"
API_ID="29950132"
API_HASH="e0bf78283481e2341805e3e4e90d289a"
CHAT_ID="5282615364"  # Self-chat for testing
MCP_TELEGRAM_READER="/home/almaz/MCP/SCRIPTS/telegram-read-manager.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[UC25]${NC} $1"; }
log_success() { echo -e "${GREEN}[UC25]${NC} $1"; }
log_error() { echo -e "${RED}[UC25]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[UC25]${NC} $1"; }

# Test books - English Programming Books
PROGRAMMING_BOOKS=(
    "Clean Code Robert Martin"
    "Design Patterns Gang of Four"
    "The Pragmatic Programmer Hunt Thomas"
    "Effective Java Joshua Bloch"
    "Python Crash Course Eric Matthes"
)

# Send book request as real user
send_book_request() {
    local book_title="$1"
    local test_number="$2"
    
    log_info "📚 TEST $test_number: Sending '$book_title'"
    
    # Send via user session
    local result=$(python3 -c "
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def send_book():
    with open('stable_string_session.txt', 'r') as f:
        string_session = f.read().strip()
    
    client = TelegramClient(StringSession(string_session), $API_ID, '$API_HASH')
    
    try:
        await client.connect()
        me = await client.get_me()
        message = await client.send_message('@$BOT_USERNAME', '$book_title')
        print(f'SUCCESS:{message.id}:{me.id}:{me.first_name}')
    except Exception as e:
        print(f'ERROR:{e}')
    finally:
        await client.disconnect()

asyncio.run(send_book())
")

    if [[ "$result" == SUCCESS:* ]]; then
        local info="${result#SUCCESS:}"
        local msg_id="${info%%:*}"
        local remaining="${info#*:}"
        local user_id="${remaining%%:*}"
        local user_name="${remaining#*:}"
        
        log_success "✅ Message sent! ID: $msg_id From: $user_name ($user_id)"
        echo "$msg_id"  # Return message ID
        return 0
    else
        log_error "❌ Failed to send: $result"
        return 1
    fi
}

# Wait for bot response and check for EPUB
wait_and_check_response() {
    local book_title="$1"
    local message_id="$2"
    local timeout=30
    
    log_info "⏳ Waiting ${timeout}s for bot response to '$book_title'..."
    sleep $timeout
    
    # Use MCP Telegram reader to check for recent messages
    log_info "📖 Reading recent Telegram messages with MCP reader..."
    
    # Read recent messages from self-chat
    local messages=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 10 --format text 2>/dev/null || echo "")
    
    if [[ -n "$messages" ]]; then
        log_info "📨 Recent messages found"
        echo "$messages" > "test_results/UC25_messages_${book_title// /_}_$message_id.txt"
        
        # Check for EPUB indicators
        if echo "$messages" | grep -q -i "epub\|\.epub\|book.*sent\|file.*sent"; then
            log_success "📄 EPUB indicators found in messages!"
            return 0
        elif echo "$messages" | grep -q -i "searching\|looking\|found"; then
            log_warn "🔍 Search activity detected but no clear EPUB delivery"
            return 1
        else
            log_warn "❓ Messages found but no clear book delivery indicators"
            return 2
        fi
    else
        log_error "❌ No recent messages found via MCP reader"
        return 3
    fi
}

# Test single book with verification
test_single_book() {
    local book="$1"
    local test_num="$2"
    local total="$3"
    
    log_info "🔥 RUNNING TEST $test_num/$total: '$book'"
    echo "$(printf '=%.0s' {1..80})"
    
    # Send book request
    local message_id
    if message_id=$(send_book_request "$book" "$test_num"); then
        
        # Wait and verify response
        if wait_and_check_response "$book" "$message_id"; then
            log_success "✅ TEST $test_num PASSED: EPUB delivery verified"
            return 0
        else
            log_warn "⚠️ TEST $test_num PARTIAL: Message sent but EPUB unclear"
            return 1
        fi
    else
        log_error "❌ TEST $test_num FAILED: Could not send message"
        return 2
    fi
}

# Main test execution
main() {
    log_info "🚀 UC25: English Programming Books Test Suite"
    log_info "================================================="
    log_info "📊 Total books: ${#PROGRAMMING_BOOKS[@]}"
    log_info "🎯 Target: @$BOT_USERNAME"
    log_info "👤 User: $USER_ID"
    log_info "📖 MCP Reader: $(basename $MCP_TELEGRAM_READER)"
    log_info "================================================="
    
    # Create results directory
    mkdir -p test_results
    
    local total_tests=${#PROGRAMMING_BOOKS[@]}
    local passed=0
    local partial=0
    local failed=0
    
    # Test each book
    for i in "${!PROGRAMMING_BOOKS[@]}"; do
        local book="${PROGRAMMING_BOOKS[$i]}"
        local test_num=$((i + 1))
        
        echo ""
        case $(test_single_book "$book" "$test_num" "$total_tests"; echo $?) in
            0) ((passed++)) ;;
            1) ((partial++)) ;;
            *) ((failed++)) ;;
        esac
        
        # Wait between tests
        if [[ $test_num -lt $total_tests ]]; then
            log_info "⏸️ Waiting 5s before next test..."
            sleep 5
        fi
    done
    
    # Final results
    echo ""
    log_info "🎯 UC25 FINAL RESULTS"
    log_info "====================="
    log_info "Total Tests: $total_tests"
    log_info "✅ Passed (EPUB verified): $passed"
    log_info "⚠️ Partial (unclear): $partial"  
    log_info "❌ Failed: $failed"
    log_info "Success Rate: $(( (passed * 100) / total_tests ))%"
    log_info "Messages saved in: test_results/"
    log_info "====================="
    
    # Determine overall result
    if [[ $passed -ge $((total_tests * 70 / 100)) ]]; then
        log_success "🎉 UC25 PASSED: Good EPUB delivery rate"
        return 0
    else
        log_error "❌ UC25 FAILED: Low EPUB delivery success"
        return 1
    fi
}

# Execute main function
main "$@"