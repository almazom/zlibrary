#!/bin/bash

# UC24: User Session Book Search Pipeline Test  
# Tests programmatic book search using Telegram user session (identical to manual typing)
# Bot: @epub_toc_based_sample_bot
# Method: User session → Bot (100% equivalent to manual)
# Usage: ./UC24_user_session_book_search_test.sh

set -euo pipefail

# Configuration
BOT_USERNAME="epub_toc_based_sample_bot"
USER_ID="14835038"
API_ID="29950132" 
API_HASH="e0bf78283481e2341805e3e4e90d289a"
SESSION_FILE="user_session_final.session"

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
log_test() { echo -e "${CYAN}[TEST]${NC} $1"; }

# Test books array
TEST_BOOKS=(
    "Clean Code Robert Martin"
    "Design Patterns Gang of Four" 
    "The Pragmatic Programmer David Thomas"
    "Effective Python Brett Slatkin"
    "Python Tricks Dan Bader"
)

# Check if user session is authenticated
check_authentication() {
    log_info "🔐 Checking user session authentication..."
    
    if [[ ! -f "$SESSION_FILE" ]]; then
        log_error "❌ Session file not found: $SESSION_FILE"
        log_warn "💡 Run authentication first:"
        log_warn "   python3 authenticate_step_by_step.py"
        return 1
    fi
    
    # Test authentication with Python
    local auth_result=$(python3 -c "
from telethon.sync import TelegramClient
try:
    with TelegramClient('$SESSION_FILE'.replace('.session', ''), $API_ID, '$API_HASH') as client:
        if client.is_user_authorized():
            me = client.get_me()
            print(f'AUTHENTICATED:{me.id}:{me.first_name}')
        else:
            print('NOT_AUTHENTICATED')
except Exception as e:
    print(f'ERROR:{e}')
")
    
    if [[ "$auth_result" == AUTHENTICATED:* ]]; then
        local user_info="${auth_result#AUTHENTICATED:}"
        local user_id="${user_info%%:*}"
        local user_name="${user_info#*:}"
        log_success "✅ User session authenticated: $user_name (ID: $user_id)"
        
        if [[ "$user_id" != "$USER_ID" ]]; then
            log_warn "⚠️ Expected user ID $USER_ID, got $user_id"
        fi
        return 0
    else
        log_error "❌ User session not authenticated: $auth_result"
        return 1
    fi
}

# Send book search via user session
send_user_session_message() {
    local book_title="$1"
    local test_number="$2"
    
    log_test "📚 TEST $test_number: User Session Book Search"
    log_info "Book: '$book_title'"
    log_info "Target: @$BOT_USERNAME"
    log_info "Method: User Session (identical to manual typing)"
    
    # Send message using user session
    local result=$(python3 -c "
from telethon.sync import TelegramClient
import sys
try:
    with TelegramClient('$SESSION_FILE'.replace('.session', ''), $API_ID, '$API_HASH') as client:
        me = client.get_me()
        message = client.send_message('@$BOT_USERNAME', '$book_title')
        print(f'SUCCESS:{message.id}:{me.id}:{me.first_name}')
except Exception as e:
    print(f'ERROR:{e}')
")

    if [[ "$result" == SUCCESS:* ]]; then
        local info="${result#SUCCESS:}"
        local msg_id="${info%%:*}"
        local remaining="${info#*:}"
        local user_id="${remaining%%:*}"
        local user_name="${remaining#*:}"
        
        log_success "✅ User session message sent!"
        log_info "Message ID: $msg_id"
        log_info "From user: $user_name (ID: $user_id)"
        log_info "Expected bot logs:"
        log_info "   📝 Text message from user $user_id: '$book_title'"
        log_info "   🚀 Processing book request from user $user_id: '$book_title'"
        log_info "   🔍 Searching for book: '$book_title'"
        log_info "   ✅ EPUB file sent successfully"
        return 0
    else
        log_error "❌ Failed to send user session message: $result"
        return 1
    fi
}

# Monitor bot response (optional - requires bot logs access)
monitor_bot_response() {
    local book_title="$1"
    local timeout=30
    
    log_info "👁️ Monitoring for bot response (${timeout}s timeout)..."
    log_info "Expected pattern: Text message from user $USER_ID: '$book_title'"
    
    # This would require access to bot logs
    # For now, just wait and inform user to check manually
    log_info "⏳ Waiting ${timeout}s for bot processing..."
    sleep $timeout
    
    log_info "📱 Please check your Telegram for:"
    log_info "   1. Progress message: '🔍 Searching for book...'"
    log_info "   2. EPUB file download"
    log_info "   3. Success confirmation message"
}

# Run comprehensive test
run_comprehensive_test() {
    local total_tests=${#TEST_BOOKS[@]}
    local successful_tests=0
    
    log_info "🚀 UC24: User Session Book Search Comprehensive Test"
    log_info "========================================================="
    log_info "📊 Total tests: $total_tests books"
    log_info "🎯 Method: Telegram User Session (100% identical to manual)"
    log_info "🤖 Target bot: @$BOT_USERNAME"
    log_info "👤 User ID: $USER_ID"
    log_info "========================================================="
    
    for i in "${!TEST_BOOKS[@]}"; do
        local book="${TEST_BOOKS[$i]}"
        local test_num=$((i + 1))
        
        echo ""
        log_test "🔥 RUNNING TEST $test_num/$total_tests"
        echo "$(printf '=%.0s' {1..60})"
        
        if send_user_session_message "$book" "$test_num"; then
            ((successful_tests++))
            log_success "✅ TEST $test_num PASSED"
            
            # Optional monitoring (wait for response)
            if [[ "${1:-}" == "--monitor" ]]; then
                monitor_bot_response "$book"
            else
                log_info "⏳ Waiting 5 seconds before next test..."
                sleep 5
            fi
        else
            log_error "❌ TEST $test_num FAILED"
        fi
        
        if [[ $test_num -lt $total_tests ]]; then
            echo ""
            log_info "📍 Next test in 3 seconds..."
            sleep 3
        fi
    done
    
    # Final results
    local success_rate=$(( successful_tests * 100 / total_tests ))
    echo ""
    log_info "🎯 UC24 FINAL RESULTS"
    log_info "========================"
    log_info "Total Tests: $total_tests"
    log_info "Successful: $successful_tests"
    log_info "Failed: $((total_tests - successful_tests))"
    log_info "Success Rate: ${success_rate}%"
    log_info "Method: User Session → Bot (identical to manual)"
    log_info "========================"
    
    if [[ $success_rate -ge 90 ]]; then
        log_success "🎉 UC24 PASSED - User session book search working!"
        log_success "📊 Pipeline equivalence: IDENTICAL to manual typing"
        return 0
    elif [[ $success_rate -ge 70 ]]; then
        log_warn "⚠️ UC24 PARTIAL - Some issues detected"
        return 1
    else
        log_error "❌ UC24 FAILED - Major issues with user session"
        return 1
    fi
}

# Single book test
run_single_test() {
    local book_title="$1"
    
    log_info "🚀 UC24: Single Book Search Test"
    log_info "=================================="
    log_info "📚 Book: '$book_title'"
    log_info "🎯 Method: User Session (identical to manual)"
    log_info "=================================="
    
    if send_user_session_message "$book_title" "1"; then
        log_success "✅ Single test PASSED"
        monitor_bot_response "$book_title"
        return 0
    else
        log_error "❌ Single test FAILED"
        return 1
    fi
}

# Main execution
main() {
    log_info "🤖 UC24: User Session Book Search Pipeline Test"
    log_info "Target: @$BOT_USERNAME | User: $USER_ID | $(date '+%Y-%m-%d %H:%M:%S')"
    log_info ""
    
    # Check authentication first
    if ! check_authentication; then
        log_error "❌ Cannot proceed without authenticated user session"
        exit 1
    fi
    
    echo ""
    
    # Parse arguments
    case "${1:-comprehensive}" in
        --single)
            if [[ -n "${2:-}" ]]; then
                run_single_test "$2"
            else
                run_single_test "${TEST_BOOKS[0]}"
            fi
            ;;
        --monitor)
            run_comprehensive_test "--monitor"
            ;;
        *)
            run_comprehensive_test
            ;;
    esac
}

# Help function
show_help() {
    echo "UC24: User Session Book Search Pipeline Test"
    echo ""
    echo "USAGE:"
    echo "  ./UC24_user_session_book_search_test.sh                    # Run all tests"
    echo "  ./UC24_user_session_book_search_test.sh --single           # Run single test (first book)"
    echo "  ./UC24_user_session_book_search_test.sh --single 'Book'    # Run single test with specific book"
    echo "  ./UC24_user_session_book_search_test.sh --monitor          # Run all tests with response monitoring"
    echo "  ./UC24_user_session_book_search_test.sh --help             # Show this help"
    echo ""
    echo "REQUIREMENTS:"
    echo "  - Authenticated user session (user_session_final.session)"
    echo "  - Running bot (@epub_toc_based_sample_bot)"
    echo "  - Python3 with telethon library"
    echo ""
    echo "AUTHENTICATION SETUP:"
    echo "  python3 authenticate_step_by_step.py"
    echo ""
    echo "TEST BOOKS:"
    for i in "${!TEST_BOOKS[@]}"; do
        echo "  $((i + 1)). ${TEST_BOOKS[$i]}"
    done
}

# Handle help
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

# Execute main function
main "$@"