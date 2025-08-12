#!/bin/bash

# UC28: Popular Fiction with Real-time MCP Verification
# Tests popular fiction books with real-time message monitoring
# Expected: EPUB downloads for bestselling fiction

set -euo pipefail

# Configuration  
BOT_USERNAME="epub_toc_based_sample_bot"
USER_ID="5282615364"
API_ID="29950132"
API_HASH="e0bf78283481e2341805e3e4e90d289a"
CHAT_ID="5282615364"
MCP_TELEGRAM_READER="/home/almaz/MCP/SCRIPTS/telegram-read-manager.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[UC28]${NC} $1"; }
log_success() { echo -e "${GREEN}[UC28]${NC} $1"; }
log_error() { echo -e "${RED}[UC28]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[UC28]${NC} $1"; }
log_fiction() { echo -e "${MAGENTA}[UC28]${NC} $1"; }

# Popular fiction books
FICTION_BOOKS=(
    "Harry Potter Sorcerer Stone Rowling"
    "The Great Gatsby Fitzgerald"
    "To Kill a Mockingbird Harper Lee"
    "1984 George Orwell"
    "Pride and Prejudice Jane Austen"
)

# Real-time message monitoring
monitor_realtime_response() {
    local book_title="$1"
    local message_id="$2"
    local test_num="$3"
    
    log_fiction "🎬 REAL-TIME MONITORING for '$book_title'"
    
    local monitoring_duration=45
    local check_interval=5
    local checks_total=$((monitoring_duration / check_interval))
    
    log_info "⏱️ Monitoring for ${monitoring_duration}s (${checks_total} checks every ${check_interval}s)"
    
    # Initialize tracking
    local progress_detected=0
    local epub_detected=0
    local final_result=""
    local check_count=0
    
    # Real-time monitoring loop
    for ((i=1; i<=checks_total; i++)); do
        check_count=$i
        log_info "📡 Check $i/$checks_total ($((i*check_interval))s elapsed)"
        
        # Read recent messages
        local recent_msgs=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 8 --format text --type all 2>/dev/null || echo "")
        
        if [[ -n "$recent_msgs" ]]; then
            # Check for progress indicators
            if [[ $progress_detected -eq 0 ]] && echo "$recent_msgs" | grep -i -E "searching|looking|processing|найдено" >/dev/null; then
                progress_detected=$i
                log_fiction "🔍 PROGRESS detected at check $i!"
            fi
            
            # Check for EPUB delivery
            if echo "$recent_msgs" | grep -i -E "epub|\.epub|book.*sent|document|attachment|file.*sent" >/dev/null; then
                epub_detected=$i
                log_success "📄 EPUB DELIVERY detected at check $i!"
                final_result="$recent_msgs"
                break
            fi
            
            # Check for errors
            if echo "$recent_msgs" | grep -i -E "error|failed|not.*found|unavailable" >/dev/null; then
                log_warn "❌ Error detected at check $i"
                final_result="$recent_msgs"
                break
            fi
        else
            log_warn "📭 No messages at check $i"
        fi
        
        # Wait between checks (except last)
        if [[ $i -lt $checks_total ]]; then
            sleep $check_interval
        fi
    done
    
    # Save monitoring results
    local safe_title=$(echo "$book_title" | tr ' ' '_' | tr '/' '_')
    echo "=== UC28 REAL-TIME MONITORING RESULTS ===" > "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "Book: $book_title" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "Message ID: $message_id" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "Total Checks: $check_count/$checks_total" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "Progress Detected: Check $progress_detected" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "EPUB Detected: Check $epub_detected" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "=== FINAL MESSAGES ===" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    echo "$final_result" >> "test_results/UC28_${test_num}_${safe_title}_monitoring.txt"
    
    # Analyze results
    log_fiction "📊 REAL-TIME ANALYSIS:"
    log_fiction "   🔍 Progress: Check $progress_detected/$checks_total"
    log_fiction "   📄 EPUB: Check $epub_detected/$checks_total"
    
    if [[ $epub_detected -gt 0 ]]; then
        local response_time=$((epub_detected * check_interval))
        log_success "🎉 EPUB delivered in ${response_time}s!"
        return 0  # Clear success
    elif [[ $progress_detected -gt 0 ]]; then
        log_warn "⚠️ Progress detected but no clear EPUB delivery"
        return 1  # Partial success
    else
        log_error "❌ No significant activity detected"
        return 2  # No activity
    fi
}

# Send fiction book request  
send_fiction_book() {
    local book_title="$1"
    local test_number="$2"
    
    log_fiction "📚 FICTION TEST $test_number: '$book_title'"
    
    local result=$(python3 -c "
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def send_fiction():
    with open('telegram_bot/stable_string_session.txt', 'r') as f:
        string_session = f.read().strip()
    
    client = TelegramClient(StringSession(string_session), $API_ID, '$API_HASH')
    
    try:
        await client.connect()
        me = await client.get_me()
        message = await client.send_message('@$BOT_USERNAME', '''$book_title''')
        print(f'SUCCESS:{message.id}:{me.id}:{me.first_name}')
    except Exception as e:
        print(f'ERROR:{e}')
    finally:
        await client.disconnect()

asyncio.run(send_fiction())
")

    if [[ "$result" == SUCCESS:* ]]; then
        local info="${result#SUCCESS:}"
        local msg_id="${info%%:*}"
        local remaining="${info#*:}"
        local user_id="${remaining%%:*}"
        local user_name="${remaining#*:}"
        
        log_success "✅ Fiction book sent! ID: $msg_id From: $user_name ($user_id)"
        echo "$msg_id"
        return 0
    else
        log_error "❌ Failed to send fiction book: $result"
        return 1
    fi
}

# Test fiction book with real-time monitoring
test_fiction_book() {
    local book="$1"
    local test_num="$2"
    local total="$3"
    
    log_info "🔥 REAL-TIME FICTION TEST $test_num/$total"
    log_fiction "📖 Book: '$book'"
    log_fiction "🎭 Genre: Popular Fiction"
    log_fiction "⏱️ Mode: Real-time monitoring"
    echo "$(printf '=%.0s' {1..80})"
    
    local message_id
    if message_id=$(send_fiction_book "$book" "$test_num"); then
        
        case $(monitor_realtime_response "$book" "$message_id" "$test_num"; echo $?) in
            0)
                log_success "🎉 TEST $test_num SUCCESS: EPUB delivered with timing!"
                return 0 ;;
            1)
                log_warn "⚠️ TEST $test_num PARTIAL: Activity detected, unclear delivery"
                return 1 ;;
            *)
                log_error "❌ TEST $test_num NO ACTIVITY: No significant response"
                return 2 ;;
        esac
    else
        log_error "❌ TEST $test_num SEND FAILED"
        return 3
    fi
}

# Main fiction test
main() {
    log_info "🚀 UC28: Popular Fiction Real-time Test"
    log_info "========================================"
    log_fiction "📚 Fiction books: ${#FICTION_BOOKS[@]}"
    log_fiction "🎭 Genre: Popular/Classic Fiction"
    log_fiction "⏱️ Method: Real-time monitoring"
    log_info "🎯 Target: @$BOT_USERNAME"
    log_info "👤 User: $USER_ID"
    log_fiction "📡 MCP Reader: Real-time checks every 5s"
    log_info "========================================"
    
    mkdir -p test_results
    
    local total_tests=${#FICTION_BOOKS[@]}
    local delivered=0
    local partial=0
    local no_activity=0
    local send_failed=0
    
    # Test each fiction book
    for i in "${!FICTION_BOOKS[@]}"; do
        local book="${FICTION_BOOKS[$i]}"
        local test_num=$((i + 1))
        
        echo ""
        case $(test_fiction_book "$book" "$test_num" "$total_tests"; echo $?) in
            0) ((delivered++)) ;;
            1) ((partial++)) ;;
            2) ((no_activity++)) ;;
            *) ((send_failed++)) ;;
        esac
        
        # Wait between fiction tests
        if [[ $test_num -lt $total_tests ]]; then
            log_info "⏸️ Cooling down 12s before next fiction test..."
            sleep 12
        fi
    done
    
    # Real-time performance analysis
    echo ""
    log_info "🎯 UC28 REAL-TIME FICTION RESULTS"
    log_info "=================================="
    log_fiction "Total Fiction Tests: $total_tests"
    log_success "🎉 EPUB Delivered: $delivered"
    log_warn "⚠️ Partial Response: $partial"
    log_error "📭 No Activity: $no_activity"
    log_error "❌ Send Failed: $send_failed"
    
    local total_responsive=$((delivered + partial))
    local delivery_rate=$(( (delivered * 100) / total_tests ))
    local response_rate=$(( (total_responsive * 100) / total_tests ))
    
    log_fiction "📊 EPUB Delivery Rate: ${delivery_rate}%"
    log_fiction "📡 Response Rate: ${response_rate}%"
    log_info "📁 Real-time logs: test_results/UC28_*_monitoring.txt"
    log_info "=================================="
    
    # Performance insights
    echo ""
    log_fiction "⏱️ PERFORMANCE INSIGHTS:"
    
    if [[ $delivered -ge 4 ]]; then
        log_success "🚀 Excellent fiction book delivery performance"
        log_fiction "📚 Popular books: READILY AVAILABLE"
        log_fiction "⚡ Response times: FAST"
    elif [[ $delivered -ge 3 ]]; then
        log_success "✅ Good fiction book availability"
        log_fiction "📖 Classic literature: WORKING"
    elif [[ $total_responsive -ge 3 ]]; then
        log_warn "🔍 Fiction search active but delivery inconsistent"
        log_fiction "⏱️ May need longer processing times"
    else
        log_error "🔧 Fiction book system may need investigation"
    fi
    
    # Overall assessment
    if [[ $delivered -ge 4 ]]; then
        log_success "🎉 UC28 EXCELLENT: Real-time fiction delivery working!"
        return 0
    elif [[ $delivered -ge 3 ]]; then
        log_success "✅ UC28 GOOD: Fiction books mostly delivered"
        return 1
    elif [[ $total_responsive -ge 3 ]]; then
        log_warn "⚠️ UC28 PARTIAL: Some fiction response detected"
        return 2
    else
        log_error "❌ UC28 FAILED: Fiction delivery not working"
        return 3
    fi
}

# Execute main
main "$@"