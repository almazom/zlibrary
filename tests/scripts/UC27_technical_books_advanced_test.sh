#!/bin/bash

# UC27: Advanced Technical Books Test with Enhanced Verification
# Tests specific technical books with detailed MCP message analysis
# Expected: EPUB downloads for technical/engineering books

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
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[UC27]${NC} $1"; }
log_success() { echo -e "${GREEN}[UC27]${NC} $1"; }
log_error() { echo -e "${RED}[UC27]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[UC27]${NC} $1"; }
log_tech() { echo -e "${PURPLE}[UC27]${NC} $1"; }

# Advanced technical books
TECHNICAL_BOOKS=(
    "Introduction to Algorithms CLRS Cormen"
    "Computer Networks Tanenbaum"
    "Operating System Concepts Silberschatz" 
    "Database System Concepts Silberschatz"
    "Artificial Intelligence Russell Norvig"
)

# Enhanced verification with technical book analysis
analyze_technical_response() {
    local book_title="$1"
    local message_id="$2"
    local test_num="$3"
    local processing_time=40  # Longer for technical books
    
    log_tech "🔬 TECHNICAL ANALYSIS for '$book_title'"
    log_info "⏳ Processing time: ${processing_time}s (technical books need more time)"
    sleep $processing_time
    
    # Multi-format message capture
    log_info "📊 Capturing messages in multiple formats..."
    
    local text_msgs=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 20 --format text --type all 2>/dev/null || echo "")
    local json_msgs=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 15 --format json --type all 2>/dev/null || echo "")
    local csv_msgs=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 10 --format csv --type documents 2>/dev/null || echo "")
    
    # Save all formats for detailed analysis
    local safe_title=$(echo "$book_title" | tr ' ' '_' | tr '/' '_')
    echo "$text_msgs" > "test_results/UC27_${test_num}_${safe_title}_text.txt"
    echo "$json_msgs" > "test_results/UC27_${test_num}_${safe_title}.json"
    echo "$csv_msgs" > "test_results/UC27_${test_num}_${safe_title}_docs.csv"
    
    log_info "💾 Saved analysis files: UC27_${test_num}_${safe_title}_*"
    
    if [[ -n "$text_msgs" ]]; then
        # Detailed technical book analysis
        local epub_score=0
        local search_score=0
        local quality_score=0
        local error_score=0
        
        log_tech "🔍 Analyzing message content..."
        
        # EPUB delivery indicators (stronger scoring)
        if echo "$text_msgs" | grep -i -E "epub|\.epub" >/dev/null; then
            epub_score=$((epub_score + 3))
            log_success "📄 EPUB format detected"
        fi
        
        if echo "$text_msgs" | grep -i -E "book.*sent|file.*sent|document.*sent|attachment" >/dev/null; then
            epub_score=$((epub_score + 2))
            log_success "📤 File delivery detected"
        fi
        
        if echo "$text_msgs" | grep -i -E "download|downloadable|size.*mb|\..*mb" >/dev/null; then
            epub_score=$((epub_score + 2))
            log_success "📦 Download indicators found"
        fi
        
        # Search activity analysis
        if echo "$text_msgs" | grep -i -E "searching|looking|search.*complete|found.*results" >/dev/null; then
            search_score=$((search_score + 1))
            log_info "🔍 Search activity confirmed"
        fi
        
        # Technical book quality indicators
        if echo "$text_msgs" | grep -i -E "algorithms|networks|database|operating.*system|artificial.*intelligence" >/dev/null; then
            quality_score=$((quality_score + 1))
            log_tech "🎯 Technical content match detected"
        fi
        
        if echo "$text_msgs" | grep -i -E "clrs|tanenbaum|silberschatz|russell.*norvig|cormen" >/dev/null; then
            quality_score=$((quality_score + 2))
            log_tech "👨‍🏫 Author match confirmed"
        fi
        
        # Error detection
        if echo "$text_msgs" | grep -i -E "error|failed|not.*found|unavailable|timeout" >/dev/null; then
            error_score=$((error_score + 2))
            log_warn "❌ Error indicators detected"
        fi
        
        # Calculate overall score
        local total_score=$((epub_score + search_score + quality_score - error_score))
        
        log_tech "📊 ANALYSIS SCORES:"
        log_tech "   📄 EPUB Score: $epub_score/7"
        log_tech "   🔍 Search Score: $search_score/1"  
        log_tech "   🎯 Quality Score: $quality_score/3"
        log_tech "   ❌ Error Penalty: -$error_score"
        log_tech "   📈 Total Score: $total_score"
        
        # Advanced result classification
        if [[ $epub_score -ge 4 && $error_score -eq 0 ]]; then
            log_success "🎉 HIGH CONFIDENCE: EPUB delivered successfully"
            return 0  # Clear success
        elif [[ $epub_score -ge 2 && $search_score -ge 1 && $error_score -eq 0 ]]; then
            log_success "✅ GOOD CONFIDENCE: Likely EPUB delivery"
            return 1  # Probable success
        elif [[ $search_score -ge 1 && $epub_score -ge 1 && $error_score -le 1 ]]; then
            log_warn "⚠️ MODERATE: Search active, delivery unclear"
            return 2  # Partial success
        elif [[ $error_score -ge 2 ]]; then
            log_error "❌ HIGH ERROR: Delivery likely failed"
            return 3  # Clear failure
        else
            log_warn "❓ UNCLEAR: Mixed or weak signals"
            return 4  # Unclear result
        fi
    else
        log_error "🔧 TECHNICAL ISSUE: No messages captured by MCP reader"
        return 5  # Technical failure
    fi
}

# Send technical book request
send_technical_book() {
    local book_title="$1"
    local test_number="$2"
    
    log_tech "📚 TECHNICAL TEST $test_number: '$book_title'"
    
    local result=$(python3 -c "
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def send_tech_book():
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

asyncio.run(send_tech_book())
")

    if [[ "$result" == SUCCESS:* ]]; then
        local info="${result#SUCCESS:}"
        local msg_id="${info%%:*}"
        local remaining="${info#*:}"
        local user_id="${remaining%%:*}"
        local user_name="${remaining#*:}"
        
        log_success "✅ Technical book sent! ID: $msg_id From: $user_name ($user_id)"
        echo "$msg_id"
        return 0
    else
        log_error "❌ Failed to send technical book: $result"
        return 1
    fi
}

# Test technical book with advanced analysis
test_technical_book() {
    local book="$1"
    local test_num="$2"
    local total="$3"
    
    log_info "🔥 ADVANCED TECHNICAL TEST $test_num/$total"
    log_tech "📖 Book: '$book'"
    log_tech "🎓 Category: Computer Science/Engineering"
    echo "$(printf '=%.0s' {1..80})"
    
    local message_id
    if message_id=$(send_technical_book "$book" "$test_num"); then
        
        case $(analyze_technical_response "$book" "$message_id" "$test_num"; echo $?) in
            0)
                log_success "🎉 TEST $test_num: HIGH SUCCESS - EPUB confirmed"
                return 0 ;;
            1)
                log_success "✅ TEST $test_num: GOOD SUCCESS - Likely delivered"
                return 1 ;;
            2)
                log_warn "⚠️ TEST $test_num: PARTIAL - Search detected"
                return 2 ;;
            3)
                log_error "❌ TEST $test_num: FAILED - Error detected"
                return 3 ;;
            4)
                log_warn "❓ TEST $test_num: UNCLEAR - Mixed signals"
                return 4 ;;
            *)
                log_error "🔧 TEST $test_num: TECHNICAL ISSUE"
                return 5 ;;
        esac
    else
        log_error "❌ TEST $test_num: SEND FAILED"
        return 6
    fi
}

# Main technical books test
main() {
    log_info "🚀 UC27: Advanced Technical Books Test"
    log_info "======================================="
    log_tech "📚 Technical books: ${#TECHNICAL_BOOKS[@]}"
    log_tech "🎓 Domain: Computer Science & Engineering"
    log_tech "🔬 Analysis: Advanced scoring system"
    log_info "🎯 Target: @$BOT_USERNAME"
    log_info "👤 User: $USER_ID"
    log_tech "📊 MCP Reader: Multi-format analysis"
    log_info "======================================="
    
    mkdir -p test_results
    
    local total_tests=${#TECHNICAL_BOOKS[@]}
    local high_success=0
    local good_success=0
    local partial=0
    local failed=0
    local unclear=0
    local technical=0
    
    # Test each technical book
    for i in "${!TECHNICAL_BOOKS[@]}"; do
        local book="${TECHNICAL_BOOKS[$i]}"
        local test_num=$((i + 1))
        
        echo ""
        case $(test_technical_book "$book" "$test_num" "$total_tests"; echo $?) in
            0) ((high_success++)) ;;
            1) ((good_success++)) ;;
            2) ((partial++)) ;;
            3|6) ((failed++)) ;;
            4) ((unclear++)) ;;
            *) ((technical++)) ;;
        esac
        
        # Wait between technical tests
        if [[ $test_num -lt $total_tests ]]; then
            log_info "⏸️ Waiting 10s before next technical test..."
            sleep 10
        fi
    done
    
    # Comprehensive technical analysis
    echo ""
    log_info "🎯 UC27 ADVANCED TECHNICAL RESULTS"
    log_info "==================================="
    log_tech "Total Technical Tests: $total_tests"
    log_success "🎉 High Confidence Success: $high_success"
    log_success "✅ Good Confidence Success: $good_success"
    log_warn "⚠️ Partial Success: $partial"
    log_error "❌ Failed: $failed"
    log_warn "❓ Unclear: $unclear"
    log_error "🔧 Technical Issues: $technical"
    
    local total_success=$((high_success + good_success))
    local success_rate=$(( (total_success * 100) / total_tests ))
    local high_confidence_rate=$(( (high_success * 100) / total_tests ))
    
    log_tech "📊 Success Rate: ${success_rate}%"
    log_tech "🎯 High Confidence Rate: ${high_confidence_rate}%"
    log_info "📁 Detailed analysis: test_results/UC27_*"
    log_info "==================================="
    
    # Technical recommendations
    echo ""
    log_tech "🔬 TECHNICAL ANALYSIS:"
    
    if [[ $high_success -ge 3 ]]; then
        log_success "📈 Excellent technical book support"
        log_tech "🎓 Computer science books: WORKING"
        log_tech "📄 EPUB delivery: RELIABLE"
    fi
    
    if [[ $good_success -ge 2 ]]; then
        log_success "📊 Good technical content processing"
        log_tech "🔍 Search algorithms: EFFECTIVE"
    fi
    
    if [[ $partial -ge 2 ]]; then
        log_warn "⚙️ Some technical books need longer processing"
        log_tech "📚 Large technical files may require more time"
    fi
    
    # Overall result
    if [[ $total_success -ge 4 ]]; then
        log_success "🎉 UC27 PASSED: Technical books working excellently!"
        return 0
    elif [[ $total_success -ge 3 ]]; then
        log_success "✅ UC27 GOOD: Technical books mostly working"
        return 1
    elif [[ $total_success -ge 2 ]]; then
        log_warn "⚠️ UC27 PARTIAL: Some technical book success"
        return 2
    else
        log_error "❌ UC27 FAILED: Technical books not working reliably"
        return 3
    fi
}

# Execute main
main "$@"