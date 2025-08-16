#!/bin/bash

# UC29: Comprehensive Multi-Category Verification Test
# Master test combining multiple categories with full MCP verification
# Expected: Complete system validation across all book types

set -euo pipefail

# Configuration
BOT_USERNAME="epub_toc_based_sample_bot"
USER_ID="5282615364"
API_ID="29950132"
API_HASH="e0bf78283481e2341805e3e4e90d289a"
CHAT_ID="5282615364"
MCP_TELEGRAM_READER="/home/almaz/MCP/SCRIPTS/telegram-read-manager.sh"

# Enhanced colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[UC29]${NC} $1"; }
log_success() { echo -e "${GREEN}[UC29]${NC} $1"; }
log_error() { echo -e "${RED}[UC29]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[UC29]${NC} $1"; }
log_master() { echo -e "${BOLD}${CYAN}[UC29]${NC} $1"; }

# Comprehensive test books across multiple categories
declare -A COMPREHENSIVE_TESTS=(
    ["PROGRAMMING"]="Clean Code Robert Martin"
    ["RUSSIAN_CLASSIC"]="Война и мир Толстой"
    ["TECHNICAL"]="Introduction to Algorithms CLRS"  
    ["FICTION"]="Harry Potter Sorcerer Stone"
    ["ACADEMIC"]="Database System Concepts"
)

# Master verification with comprehensive analysis
comprehensive_verification() {
    local book_title="$1"
    local category="$2"
    local message_id="$3"
    local test_num="$4"
    
    log_master "🔍 COMPREHENSIVE VERIFICATION: $category"
    log_info "📖 Book: '$book_title'"
    
    # Category-specific wait times
    local wait_time
    case "$category" in
        "TECHNICAL"|"ACADEMIC") wait_time=50 ;;
        "RUSSIAN_CLASSIC") wait_time=40 ;;
        *) wait_time=35 ;;
    esac
    
    log_info "⏳ Processing time: ${wait_time}s (optimized for $category)"
    sleep $wait_time
    
    # Multi-dimensional message capture
    log_master "📊 Capturing comprehensive message data..."
    
    local text_data=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 25 --format text --type all 2>/dev/null || echo "")
    local json_data=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 20 --format json --type all 2>/dev/null || echo "")
    local doc_data=$($MCP_TELEGRAM_READER read "$CHAT_ID" --limit 15 --format csv --type documents 2>/dev/null || echo "")
    
    # Search for specific patterns in recent history
    local search_results=$($MCP_TELEGRAM_READER search "$CHAT_ID" "epub" --limit 10 --format text 2>/dev/null || echo "")
    
    # Save comprehensive data
    local safe_title=$(echo "${category}_${book_title}" | tr ' ' '_' | tr '/' '_')
    echo "$text_data" > "test_results/UC29_${test_num}_${safe_title}_full.txt"
    echo "$json_data" > "test_results/UC29_${test_num}_${safe_title}_data.json"
    echo "$doc_data" > "test_results/UC29_${test_num}_${safe_title}_docs.csv"
    echo "$search_results" > "test_results/UC29_${test_num}_${safe_title}_epub_search.txt"
    
    log_master "💾 Comprehensive data saved for $category"
    
    if [[ -n "$text_data" ]]; then
        # Advanced multi-factor scoring system
        local delivery_score=0
        local quality_score=0
        local speed_score=0
        local category_score=0
        local error_penalty=0
        
        log_master "🧮 Running comprehensive analysis..."
        
        # Delivery detection (weighted by strength)
        if echo "$text_data" | grep -i -E "\.epub|epub.*file|epub.*sent" >/dev/null; then
            delivery_score=$((delivery_score + 5))
            log_success "📄 Strong EPUB delivery signals"
        fi
        
        if echo "$text_data" | grep -i -E "book.*sent|file.*sent|document.*delivered" >/dev/null; then
            delivery_score=$((delivery_score + 3))
            log_success "📤 File delivery confirmed"
        fi
        
        if echo "$text_data" | grep -i -E "download|downloadable|attachment|size.*mb" >/dev/null; then
            delivery_score=$((delivery_score + 2))
            log_success "📦 Download indicators present"
        fi
        
        # Quality assessment based on content match
        case "$category" in
            "PROGRAMMING")
                if echo "$text_data" | grep -i -E "clean.*code|robert.*martin|programming|software" >/dev/null; then
                    quality_score=$((quality_score + 3))
                    log_success "💻 Programming content confirmed"
                fi ;;
            "RUSSIAN_CLASSIC")  
                if echo "$text_data" | grep -i -E "толстой|война.*мир|russian|classic" >/dev/null; then
                    quality_score=$((quality_score + 3))
                    log_success "🇷🇺 Russian classic content confirmed"
                fi ;;
            "TECHNICAL")
                if echo "$text_data" | grep -i -E "algorithms|clrs|computer.*science|cormen" >/dev/null; then
                    quality_score=$((quality_score + 3))
                    log_success "🔬 Technical content confirmed"
                fi ;;
            "FICTION")
                if echo "$text_data" | grep -i -E "harry.*potter|rowling|fiction|novel" >/dev/null; then
                    quality_score=$((quality_score + 3))
                    log_success "📚 Fiction content confirmed"
                fi ;;
            "ACADEMIC")
                if echo "$text_data" | grep -i -E "database|academic|textbook|system.*concepts" >/dev/null; then
                    quality_score=$((quality_score + 3))
                    log_success "🎓 Academic content confirmed"
                fi ;;
        esac
        
        # Speed assessment (based on response indicators within expected time)
        if echo "$text_data" | grep -i -E "searching.*complete|found.*results|processing.*done" >/dev/null; then
            speed_score=$((speed_score + 2))
            log_success "⚡ Fast processing detected"
        fi
        
        # Category-specific bonus scoring
        if [[ "$category" == "RUSSIAN_CLASSIC" ]] && echo "$text_data" | grep -P "[А-Яа-я]" >/dev/null; then
            category_score=$((category_score + 2))
            log_success "🇷🇺 Cyrillic text processing working"
        fi
        
        if [[ "$category" == "TECHNICAL" ]] && echo "$text_data" | grep -i -E "pdf|large.*file|technical" >/dev/null; then
            category_score=$((category_score + 1))
            log_success "🔬 Technical format handling detected"
        fi
        
        # Error detection with penalties
        if echo "$text_data" | grep -i -E "error|failed|timeout|unavailable" >/dev/null; then
            error_penalty=$((error_penalty + 3))
            log_warn "❌ Error indicators detected"
        fi
        
        if echo "$text_data" | grep -i -E "not.*found|no.*results|search.*failed" >/dev/null; then
            error_penalty=$((error_penalty + 2))
            log_warn "🔍 Search failure indicators"
        fi
        
        # Calculate comprehensive score
        local total_score=$((delivery_score + quality_score + speed_score + category_score - error_penalty))
        local max_possible=13  # 5+3+2+2+1
        local confidence=$(( (total_score * 100) / max_possible ))
        
        # Detailed scoring report
        log_master "📊 COMPREHENSIVE SCORING REPORT:"
        log_master "   📄 Delivery Score: $delivery_score/10"
        log_master "   🎯 Quality Score: $quality_score/3"
        log_master "   ⚡ Speed Score: $speed_score/2"
        log_master "   📋 Category Score: $category_score/2"
        log_master "   ❌ Error Penalty: -$error_penalty"
        log_master "   📈 Total Score: $total_score/$max_possible"
        log_master "   🎯 Confidence: ${confidence}%"
        
        # Comprehensive result classification
        if [[ $total_score -ge 8 && $error_penalty -eq 0 ]]; then
            log_success "🏆 EXCELLENT: High confidence EPUB delivery"
            return 0
        elif [[ $total_score -ge 6 && $error_penalty -le 1 ]]; then
            log_success "✅ GOOD: Strong evidence of delivery"
            return 1
        elif [[ $total_score -ge 4 && $delivery_score -ge 2 ]]; then
            log_success "👍 SATISFACTORY: Likely delivered"
            return 2
        elif [[ $total_score -ge 2 && $error_penalty -le 2 ]]; then
            log_warn "⚠️ PARTIAL: Some positive indicators"
            return 3
        elif [[ $error_penalty -ge 3 ]]; then
            log_error "❌ FAILED: Strong error indicators"
            return 4
        else
            log_warn "❓ UNCLEAR: Insufficient evidence"
            return 5
        fi
    else
        log_error "🔧 NO DATA: MCP reader returned no messages"
        return 6
    fi
}

# Send comprehensive test book
send_comprehensive_book() {
    local book_title="$1"
    local category="$2"
    local test_number="$3"
    
    log_master "📚 COMPREHENSIVE TEST $test_number: $category"
    log_info "📖 Book: '$book_title'"
    
    local result=$(python3 -c "
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def send_comprehensive():
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

asyncio.run(send_comprehensive())
")

    if [[ "$result" == SUCCESS:* ]]; then
        local info="${result#SUCCESS:}"
        local msg_id="${info%%:*}"
        local remaining="${info#*:}"
        local user_id="${remaining%%:*}"
        local user_name="${remaining#*:}"
        
        log_success "✅ $category book sent! ID: $msg_id From: $user_name ($user_id)"
        echo "$msg_id"
        return 0
    else
        log_error "❌ Failed to send $category book: $result"
        return 1
    fi
}

# Test comprehensive book category
test_comprehensive_category() {
    local category="$1"
    local book="$2"
    local test_num="$3"
    local total="$4"
    
    log_info "🔥 COMPREHENSIVE CATEGORY TEST $test_num/$total"
    log_master "📂 Category: $category"
    log_master "📖 Book: '$book'"
    echo "$(printf '=%.0s' {1..80})"
    
    local message_id
    if message_id=$(send_comprehensive_book "$book" "$category" "$test_num"); then
        
        case $(comprehensive_verification "$book" "$category" "$message_id" "$test_num"; echo $?) in
            0)
                log_success "🏆 TEST $test_num ($category): EXCELLENT"
                return 0 ;;
            1)
                log_success "✅ TEST $test_num ($category): GOOD" 
                return 1 ;;
            2)
                log_success "👍 TEST $test_num ($category): SATISFACTORY"
                return 2 ;;
            3)
                log_warn "⚠️ TEST $test_num ($category): PARTIAL"
                return 3 ;;
            4)
                log_error "❌ TEST $test_num ($category): FAILED"
                return 4 ;;
            5)
                log_warn "❓ TEST $test_num ($category): UNCLEAR"
                return 5 ;;
            *)
                log_error "🔧 TEST $test_num ($category): TECHNICAL ISSUE"
                return 6 ;;
        esac
    else
        log_error "❌ TEST $test_num ($category): SEND FAILED"
        return 7
    fi
}

# Main comprehensive test
main() {
    log_master "🚀 UC29: COMPREHENSIVE MULTI-CATEGORY VERIFICATION"
    log_master "=================================================="
    log_master "📊 Test Categories: ${#COMPREHENSIVE_TESTS[@]}"
    log_master "🎯 Verification: Multi-dimensional MCP analysis"
    log_info "🤖 Target: @$BOT_USERNAME"
    log_info "👤 User: $USER_ID"
    log_master "🔍 Analysis: Advanced scoring system"
    log_master "=================================================="
    
    mkdir -p test_results
    
    # Initialize counters
    local total_tests=${#COMPREHENSIVE_TESTS[@]}
    local excellent=0
    local good=0
    local satisfactory=0
    local partial=0
    local failed=0
    local unclear=0
    local technical=0
    
    # Test each category
    local test_num=0
    for category in "${!COMPREHENSIVE_TESTS[@]}"; do
        ((test_num++))
        local book="${COMPREHENSIVE_TESTS[$category]}"
        
        echo ""
        case $(test_comprehensive_category "$category" "$book" "$test_num" "$total_tests"; echo $?) in
            0) ((excellent++)) ;;
            1) ((good++)) ;;
            2) ((satisfactory++)) ;;
            3) ((partial++)) ;;
            4|7) ((failed++)) ;;
            5) ((unclear++)) ;;
            *) ((technical++)) ;;
        esac
        
        # Progressive wait times
        if [[ $test_num -lt $total_tests ]]; then
            log_info "⏸️ Comprehensive cooldown: 15s before next category..."
            sleep 15
        fi
    done
    
    # Comprehensive final analysis
    echo ""
    log_master "🎯 UC29 COMPREHENSIVE FINAL RESULTS"
    log_master "====================================="
    log_master "Total Categories Tested: $total_tests"
    log_success "🏆 Excellent Results: $excellent"
    log_success "✅ Good Results: $good" 
    log_success "👍 Satisfactory Results: $satisfactory"
    log_warn "⚠️ Partial Results: $partial"
    log_error "❌ Failed Results: $failed"
    log_warn "❓ Unclear Results: $unclear"
    log_error "🔧 Technical Issues: $technical"
    
    # Calculate comprehensive metrics
    local total_success=$((excellent + good + satisfactory))
    local total_positive=$((total_success + partial))
    local success_rate=$(( (total_success * 100) / total_tests ))
    local positive_rate=$(( (total_positive * 100) / total_tests ))
    local excellence_rate=$(( (excellent * 100) / total_tests ))
    
    log_master "📊 COMPREHENSIVE METRICS:"
    log_master "   🎯 Success Rate: ${success_rate}%"
    log_master "   📈 Positive Response Rate: ${positive_rate}%"
    log_master "   🏆 Excellence Rate: ${excellence_rate}%"
    log_info "📁 Complete analysis: test_results/UC29_*"
    log_master "====================================="
    
    # Category-specific insights
    echo ""
    log_master "🔍 CATEGORY INSIGHTS:"
    
    if [[ $excellent -ge 3 ]]; then
        log_success "🌟 Multiple categories showing excellent performance"
        log_master "   📚 Book delivery system: HIGHLY RELIABLE"
        log_master "   🔍 Search algorithms: VERY EFFECTIVE"
    fi
    
    if [[ $total_success -ge 4 ]]; then
        log_success "🎯 Strong cross-category performance"
        log_master "   📖 Multi-genre support: EXCELLENT"
        log_master "   🌍 Multi-language support: WORKING"
    fi
    
    if [[ $technical -eq 0 && $failed -le 1 ]]; then
        log_success "🔧 System stability: EXCELLENT"
        log_master "   📡 MCP integration: STABLE"
        log_master "   🔗 Telegram connectivity: RELIABLE"
    fi
    
    # Master assessment
    echo ""
    log_master "🏁 MASTER ASSESSMENT:"
    
    if [[ $excellent -ge 3 && $total_success -ge 4 ]]; then
        log_success "🏆 UC29 OUTSTANDING: System performing excellently across categories!"
        log_master "   ✨ Ready for production use"
        log_master "   📈 Scaling recommended"
        return 0
    elif [[ $total_success -ge 3 && $positive_rate -ge 80 ]]; then
        log_success "✅ UC29 EXCELLENT: Strong multi-category performance"
        log_master "   👍 System is reliable"
        log_master "   🔧 Minor optimizations may help"
        return 1
    elif [[ $total_positive -ge 3 ]]; then
        log_success "👍 UC29 GOOD: Decent cross-category functionality"
        log_master "   ⚠️ Some categories need attention"
        log_master "   🔍 Investigate partial results"
        return 2
    elif [[ $total_positive -ge 2 ]]; then
        log_warn "⚠️ UC29 PARTIAL: Limited multi-category success"
        log_master "   🔧 System needs optimization"
        log_master "   📊 Review individual category results"
        return 3
    else
        log_error "❌ UC29 FAILED: Multi-category system not working reliably"
        log_master "   🚨 Immediate investigation required"
        log_master "   🔧 Check core system components"
        return 4
    fi
}

# Execute comprehensive master test
main "$@"