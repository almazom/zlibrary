#!/bin/bash

# UC26: Russian Classics with MCP Telegram Verification
# Tests Russian literature classics with comprehensive message reading
# Expected: EPUB downloads for famous Russian books

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
NC='\033[0m'

log_info() { echo -e "${BLUE}[UC26]${NC} $1"; }
log_success() { echo -e "${GREEN}[UC26]${NC} $1"; }
log_error() { echo -e "${RED}[UC26]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[UC26]${NC} $1"; }

# Russian classics test books
RUSSIAN_CLASSICS=(
    "Война и мир Толстой"
    "Преступление и наказание Достоевский" 
    "Анна Каренина Толстой"
    "Мастер и Маргарита Булгаков"
    "Евгений Онегин Пушкин"
)

# Enhanced message verification for Russian content
verify_russian_epub_delivery() {
    local book_title="$1"
    local message_id="$2"
    local wait_time=35  # Longer wait for Russian content
    
    log_info "⏳ Waiting ${wait_time}s for Russian book processing: '$book_title'"
    sleep $wait_time
    
    # Read recent messages with detailed format
    log_info "📖 Reading Telegram messages with MCP reader (Russian support)..."
    
    local messages_text=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 15 --format text 2>/dev/null || echo "")
    local messages_json=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 10 --format json 2>/dev/null || echo "")
    
    # Save both formats for analysis
    echo "$messages_text" > "test_results/UC26_text_${book_title// /_}_$message_id.txt"
    echo "$messages_json" > "test_results/UC26_json_${book_title// /_}_$message_id.json"
    
    if [[ -n "$messages_text" ]]; then
        log_info "📨 Messages captured (text: $(echo "$messages_text" | wc -l) lines)"
        
        # Check for various EPUB delivery indicators
        local epub_found=0
        local search_found=0
        local error_found=0
        
        # EPUB delivery patterns
        if echo "$messages_text" | grep -i -E "(epub|\.epub|книга.*отправлена|файл.*отправлен|book.*sent|document|attachment)" >/dev/null; then
            log_success "📄 EPUB delivery indicators found!"
            epub_found=1
        fi
        
        # Search activity patterns  
        if echo "$messages_text" | grep -i -E "(поиск|searching|ищу|found|найдено|результат)" >/dev/null; then
            log_info "🔍 Search activity detected"
            search_found=1
        fi
        
        # Error patterns
        if echo "$messages_text" | grep -i -E "(error|ошибка|не найдено|not found|failed)" >/dev/null; then
            log_warn "❌ Error indicators detected"
            error_found=1
        fi
        
        # Russian-specific success patterns
        if echo "$messages_text" | grep -i -E "(толстой|достоевский|пушкин|булгаков|русская литература)" >/dev/null; then
            log_info "🇷🇺 Russian literature context confirmed"
        fi
        
        # Determine result
        if [[ $epub_found -eq 1 ]]; then
            return 0  # Clear success
        elif [[ $search_found -eq 1 && $error_found -eq 0 ]]; then
            return 1  # Partial success (search but unclear result)
        elif [[ $error_found -eq 1 ]]; then
            return 2  # Clear failure
        else
            return 3  # Unclear result
        fi
    else
        log_error "❌ No messages retrieved from MCP reader"
        return 4  # MCP reader failure
    fi
}

# Send Russian book request
send_russian_book() {
    local book_title="$1"
    local test_number="$2"
    
    log_info "📚 TEST $test_number: Russian book '$book_title'"
    
    local result=$(python3 -c "
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def send_russian_book():
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

asyncio.run(send_russian_book())
")

    if [[ "$result" == SUCCESS:* ]]; then
        local info="${result#SUCCESS:}"
        local msg_id="${info%%:*}"
        local remaining="${info#*:}"
        local user_id="${remaining%%:*}"
        local user_name="${remaining#*:}"
        
        log_success "✅ Russian message sent! ID: $msg_id From: $user_name ($user_id)"
        echo "$msg_id"
        return 0
    else
        log_error "❌ Failed to send Russian book: $result"
        return 1
    fi
}

# Test Russian book with comprehensive verification
test_russian_classic() {
    local book="$1"
    local test_num="$2"
    local total="$3"
    
    log_info "🔥 RUSSIAN TEST $test_num/$total"
    log_info "📖 Book: '$book'"
    log_info "🇷🇺 Language: Russian (Cyrillic)"
    echo "$(printf '=%.0s' {1..80})"
    
    local message_id
    if message_id=$(send_russian_book "$book" "$test_num"); then
        
        case $(verify_russian_epub_delivery "$book" "$message_id"; echo $?) in
            0) 
                log_success "✅ TEST $test_num PASSED: Russian EPUB verified"
                return 0 ;;
            1)
                log_warn "⚠️ TEST $test_num PARTIAL: Search detected, EPUB unclear"
                return 1 ;;
            2)
                log_error "❌ TEST $test_num FAILED: Error detected"
                return 2 ;;
            3)
                log_warn "❓ TEST $test_num UNCLEAR: Mixed signals"
                return 3 ;;
            *)
                log_error "🔧 TEST $test_num TECHNICAL: MCP reader issue"
                return 4 ;;
        esac
    else
        log_error "❌ TEST $test_num FAILED: Could not send Russian message"
        return 5
    fi
}

# Main Russian classics test
main() {
    log_info "🚀 UC26: Russian Classics Verification Test"
    log_info "============================================="
    log_info "📚 Russian books: ${#RUSSIAN_CLASSICS[@]}"
    log_info "🇷🇺 Language: Russian (Cyrillic text)"
    log_info "🎯 Target: @$BOT_USERNAME" 
    log_info "👤 User: $USER_ID"
    log_info "📖 MCP Reader: v4 with Russian support"
    log_info "============================================="
    
    mkdir -p test_results
    
    local total_tests=${#RUSSIAN_CLASSICS[@]}
    local passed=0
    local partial=0
    local failed=0
    local unclear=0
    local technical=0
    
    # Test each Russian classic
    for i in "${!RUSSIAN_CLASSICS[@]}"; do
        local book="${RUSSIAN_CLASSICS[$i]}"
        local test_num=$((i + 1))
        
        echo ""
        case $(test_russian_classic "$book" "$test_num" "$total_tests"; echo $?) in
            0) ((passed++)) ;;
            1) ((partial++)) ;;  
            2|5) ((failed++)) ;;
            3) ((unclear++)) ;;
            *) ((technical++)) ;;
        esac
        
        # Longer wait between Russian tests
        if [[ $test_num -lt $total_tests ]]; then
            log_info "⏸️ Waiting 8s before next Russian test..."
            sleep 8
        fi
    done
    
    # Comprehensive results
    echo ""
    log_info "🎯 UC26 RUSSIAN CLASSICS RESULTS"
    log_info "================================="
    log_info "Total Russian Tests: $total_tests"
    log_info "✅ EPUB Verified: $passed"
    log_info "⚠️ Partial Success: $partial"
    log_info "❌ Failed: $failed"
    log_info "❓ Unclear: $unclear"
    log_info "🔧 Technical Issues: $technical"
    
    local success_rate=$(( ((passed + partial) * 100) / total_tests ))
    log_info "📊 Overall Success Rate: ${success_rate}%"
    log_info "📁 Detailed logs: test_results/UC26_*"
    log_info "================================="
    
    # Analysis and recommendations
    if [[ $passed -ge 3 ]]; then
        log_success "🎉 UC26 PASSED: Russian classics working well!"
        log_info "🇷🇺 Cyrillic text processing: VERIFIED"
        log_info "📚 Russian literature search: WORKING"
        return 0
    elif [[ $((passed + partial)) -ge 3 ]]; then
        log_warn "⚠️ UC26 PARTIAL: Some Russian books working"
        log_info "🔍 Search functionality appears active"
        log_warn "📄 EPUB delivery needs verification"
        return 1
    else
        log_error "❌ UC26 FAILED: Russian classics not working reliably"
        log_error "🇷🇺 Check Russian language support"
        log_error "🔧 Review MCP reader functionality"
        return 2
    fi
}

# Execute main
main "$@"