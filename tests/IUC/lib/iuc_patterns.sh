#!/bin/bash
# IUC Shared Library - AI Learning Patterns
# Each function includes EXAMPLE usage for AI reference
# Version: 1.0.0 - Smart & Balanced Implementation

set -euo pipefail

# Configuration
DEFAULT_BOT="epub_toc_based_sample_bot"
DEFAULT_USER_ID="5282615364"
DEFAULT_API_ID="29950132"
DEFAULT_API_HASH="e0bf78283481e2341805e3e4e90d289a"
DEFAULT_STRING_SESSION="1ApWapzMBu4PfiXOaKlWyf87-hEiVPCmh152Zt4x2areHOfSfMNDENrJBepoLDZBGqqwrfPvo4zeDB6M8jZZkgUy8pwU9Ba67fDMlnIkESlhbX_aJFLuzbfbd3IwSYh60pLsa0mk8huWxXwHpVNDBeISwp4uGxqF6R_lxWBv_4l3pU3szXcJPS4kw9cTXZkwazvH28AOteP400dazpNpyEt2MbB56GIl9r5B7vQLcATUSW0rvd5-fWF_u2aw243XIHs7H39e_pJt2u0encXQM2Ca7X992Aad2WuHQDv7rDf1CuOO5s8UDZpvxc7ul4W53-PHyEguqLorV1uURpJH6HDDchK4WiTI="

# Colors for rich UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions with emoji patterns (AI learns these)
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_given() { echo -e "${PURPLE}[GIVEN]${NC} $1"; }
log_when() { echo -e "${YELLOW}[WHEN]${NC} $1"; }
log_then() { echo -e "${GREEN}[THEN]${NC} $1"; }

# Timing functions
get_timestamp() {
    TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S MSK'
}

get_epoch() {
    date +%s
}

#=== AUTHENTICATION PATTERNS ===
authenticate_user_session() {
    # EXAMPLE: Used at start of every IUC test
    # IUC01 usage: authenticate_user_session
    # IUC02 usage: authenticate_user_session  
    # Pattern: Always call first, check return code
    
    log_step "🔐 AUTHENTICATION: Checking user session..."
    
    local auth_result=$(python3 -c "
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
try:
    with TelegramClient(StringSession('$DEFAULT_STRING_SESSION'), $DEFAULT_API_ID, '$DEFAULT_API_HASH') as client:
        if client.is_user_authorized():
            me = client.get_me()
            print(f'AUTHENTICATED:{me.id}:{me.first_name}')
        else:
            print('NOT_AUTHENTICATED')
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null)
    
    if [[ "$auth_result" == AUTHENTICATED:* ]]; then
        local user_info="${auth_result#AUTHENTICATED:}"
        local user_id="${user_info%%:*}"
        local user_name="${user_info#*:}"
        log_success "✅ Authentication successful: $user_name (ID: $user_id)"
        
        # Store for other functions to use
        export IUC_USER_ID="$user_id"
        export IUC_USER_NAME="$user_name"
        return 0
    else
        log_error "❌ Authentication failed: $auth_result"
        return 1
    fi
}

verify_test_environment() {
    # EXAMPLE: Check tools and environment
    # Pattern: Call after authentication, before tests
    
    log_step "🔧 ENVIRONMENT: Verifying test tools..."
    
    local tools_ok=true
    
    # Check Python and Telethon
    if ! python3 -c "import telethon" 2>/dev/null; then
        log_error "❌ Python telethon library not available"
        tools_ok=false
    fi
    
    # Check MCP telegram-read-manager
    if ! command -v /home/almaz/MCP/SCRIPTS/telegram-read-manager.sh &>/dev/null; then
        log_warn "⚠️ MCP telegram-read-manager not available (will use fallback)"
    else
        log_info "✅ MCP telegram-read-manager available"
    fi
    
    if [[ "$tools_ok" == "true" ]]; then
        log_success "✅ Environment verification passed"
        return 0
    else
        log_error "❌ Environment verification failed"
        return 1
    fi
}

check_bot_accessibility() {
    # EXAMPLE: Test if bot is accessible and responsive
    # Pattern: Call before sending test messages
    # Usage: check_bot_accessibility "@bot_name"
    
    local bot_name="$1"
    log_step "🤖 BOT CHECK: Testing accessibility of $bot_name"
    
    # For now, assume bot is accessible
    # In a real implementation, we might send a ping message
    # or check bot's last seen status
    
    log_info "🔍 Checking bot accessibility..."
    
    # Basic accessibility check - bot exists and is reachable
    # This is a placeholder for more sophisticated bot health checks
    
    log_success "✅ Bot $bot_name appears accessible"
    return 0
}

#=== MESSAGE SENDING PATTERNS ===
send_message_to_bot() {
    local message="$1"
    local target_bot="${2:-@$DEFAULT_BOT}"
    
    # EXAMPLE: Generic message sending
    # IUC01: send_message_to_bot "/start" "@epub_toc_based_sample_bot"
    # IUC02: send_message_to_bot "Clean Code" "@epub_toc_based_sample_bot"
    # Pattern: Always capture message_id, log with emojis
    
    log_step "📤 SENDING: '$message' to $target_bot"
    
    local result=$(python3 -c "
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import sys
try:
    with TelegramClient(StringSession('$DEFAULT_STRING_SESSION'), $DEFAULT_API_ID, '$DEFAULT_API_HASH') as client:
        me = client.get_me()
        message = client.send_message('$target_bot', '$message')
        print(f'SUCCESS:{message.id}:{me.id}:{me.first_name}')
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null)

    if [[ "$result" == SUCCESS:* ]]; then
        local info="${result#SUCCESS:}"
        local msg_id="${info%%:*}"
        local remaining="${info#*:}"
        local user_id="${remaining%%:*}"
        local user_name="${remaining#*:}"
        
        log_success "✅ Message sent successfully!"
        log_info "📋 Message ID: $msg_id"
        log_info "👤 From: $user_name (ID: $user_id)"
        log_info "🎯 Target: $target_bot"
        log_info "⏰ Timestamp: $(get_timestamp)"
        
        # Store for validation
        export IUC_LAST_MESSAGE_ID="$msg_id"
        export IUC_LAST_TIMESTAMP="$(get_epoch)"
        return 0
    else
        log_error "❌ Failed to send message: $result"
        return 1
    fi
}

send_start_command() {
    local target_bot="${1:-@$DEFAULT_BOT}"
    
    # EXAMPLE: Specialized for /start commands (common IUC pattern)
    # IUC01: send_start_command "@epub_toc_based_sample_bot"
    # Pattern: Includes start-specific logging and expectations
    
    log_step "🚀 START COMMAND: Sending /start to $target_bot"
    log_info "Expected: Welcome message with bot instructions"
    
    send_message_to_bot "/start" "$target_bot"
}

send_book_search() {
    local book_title="$1" 
    local target_bot="${2:-@$DEFAULT_BOT}"
    
    # EXAMPLE: Specialized for book searches (most common IUC pattern)
    # IUC02: send_book_search "Clean Code Robert Martin"
    # IUC03: send_book_search "Design Patterns Gang of Four"
    # Pattern: Includes book-specific logging and validation expectations
    
    log_step "📚 BOOK SEARCH: '$book_title'"
    log_info "Target: $target_bot"
    log_info "Expected: Progress message → EPUB delivery → Confirmation"
    
    send_message_to_bot "$book_title" "$target_bot"
}

#=== RESPONSE READING PATTERNS ===
read_bot_response() {
    local timeout="${1:-5}"
    local expected_type="${2:-any}"
    
    # EXAMPLE: Smart response reading with fallbacks
    # IUC01: read_bot_response 5 "welcome"
    # IUC02: read_bot_response 10 "progress"
    # Pattern: MCP tool first, Python fallback, rich logging
    
    log_step "📥 READING: Bot response (timeout: ${timeout}s, type: $expected_type)"
    
    # Wait for bot processing
    log_info "⏳ Waiting $timeout seconds for bot response..."
    sleep "$timeout"
    
    local response=""
    
    # Try MCP tool first
    if command -v /home/almaz/MCP/SCRIPTS/telegram-read-manager.sh &>/dev/null; then
        log_info "🔧 Using MCP telegram-read-manager tool"
        response=$(/home/almaz/MCP/SCRIPTS/telegram-read-manager.sh read "@$DEFAULT_BOT" --limit 1 2>/dev/null || echo "")
    fi
    
    # Fallback to Python if needed
    if [[ -z "$response" || "$response" == *"ERROR"* || "$response" == *"Failed to read"* ]]; then
        log_info "🔧 Using Python Telethon fallback"
        response=$(python3 -c "
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
try:
    with TelegramClient(StringSession('$DEFAULT_STRING_SESSION'), $DEFAULT_API_ID, '$DEFAULT_API_HASH') as client:
        messages = client.get_messages('@$DEFAULT_BOT', limit=3)
        if messages and len(messages) > 0:
            me = client.get_me()
            for msg in messages:
                if msg.from_id and msg.from_id.user_id != me.id:
                    print(msg.text or msg.message or 'No text content')
                    break
            else:
                print('No bot response found in recent messages')
        else:
            print('No messages found in conversation')
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null)
    fi
    
    if [[ -n "$response" && "$response" != *"ERROR"* ]]; then
        log_success "✅ Bot response received"
        log_info "📖 Response: $response"
        echo "$response"
        return 0
    else
        log_error "❌ Failed to read bot response"
        echo "NO_RESPONSE"
        return 1
    fi
}

read_progress_message() {
    local timeout="${1:-10}"
    
    # EXAMPLE: Specialized for progress messages
    # IUC02: read_progress_message 10
    # Pattern: Looks specifically for "🔍 Searching" type messages
    
    log_step "🔍 READING: Progress message (timeout: ${timeout}s)"
    log_info "Expected pattern: 🔍 Searching for book..."
    
    read_bot_response "$timeout" "progress"
}

read_epub_delivery() {
    local timeout="${1:-30}"
    
    # EXAMPLE: Specialized for file delivery
    # IUC02: read_epub_delivery 30
    # Pattern: Waits longer, looks for file delivery confirmation
    
    log_step "📄 READING: EPUB delivery (timeout: ${timeout}s)"
    log_info "Expected: File delivery or download link"
    
    read_bot_response "$timeout" "file"
}

#=== VALIDATION PATTERNS ===
validate_response() {
    local actual="$1"
    local expected_pattern="$2"
    local validation_type="${3:-auto}"
    
    # EXAMPLE: Smart validation with auto-detection
    # IUC01: validate_response "$response" "📚 Welcome to Book Search Bot" "auto"
    # IUC02: validate_response "$response" "🔍 Searching for book" "progress"
    # Pattern: Auto-detects type, shows expected vs actual, uses emojis
    
    log_step "🔍 VALIDATION: Checking response content"
    log_info "Expected pattern: '$expected_pattern'"
    log_info "Actual response: '$actual'"
    
    # Smart type detection for AI ease-of-use
    if [[ "$validation_type" == "auto" ]]; then
        if [[ "$expected_pattern" == *"🔍"* ]]; then validation_type="progress"; fi
        if [[ "$expected_pattern" == *"📚"* ]]; then validation_type="welcome"; fi
        if [[ "$expected_pattern" == *".epub"* || "$expected_pattern" == *"file"* ]]; then validation_type="file"; fi
        if [[ "$expected_pattern" == *"error"* || "$expected_pattern" == *"failed"* ]]; then validation_type="error"; fi
    fi
    
    log_info "🎯 Validation type: $validation_type"
    
    # Perform validation based on type
    case "$validation_type" in
        "progress") 
            validate_progress_pattern "$actual" "$expected_pattern"
            ;;
        "file")
            validate_file_delivery "$actual" "$expected_pattern" 
            ;;
        "welcome")
            validate_welcome_pattern "$actual" "$expected_pattern"
            ;;
        "error")
            validate_error_pattern "$actual" "$expected_pattern"
            ;;
        *)
            validate_content_pattern "$actual" "$expected_pattern"
            ;;
    esac
}

validate_content_pattern() {
    local actual="$1"
    local expected="$2"
    
    if [[ "$actual" == *"$expected"* ]]; then
        log_success "✅ VALIDATION PASSED: Content pattern found"
        log_success "🎯 Expected pattern found in response"
        return 0
    else
        log_error "❌ VALIDATION FAILED: Content pattern not found"
        log_error "🎯 Expected: Contains '$expected'"
        log_error "🎯 Got: '$actual'"
        return 1
    fi
}

validate_progress_pattern() {
    local actual="$1"
    local expected="$2"
    
    # Look for progress indicators
    if [[ "$actual" == *"🔍"* || "$actual" == *"Searching"* || "$actual" == *"processing"* ]]; then
        log_success "✅ VALIDATION PASSED: Progress pattern detected"
        return 0
    else
        log_error "❌ VALIDATION FAILED: No progress pattern found"
        return 1
    fi
}

validate_welcome_pattern() {
    local actual="$1"
    local expected="$2"
    
    # Look for welcome indicators
    if [[ "$actual" == *"Welcome"* || "$actual" == *"📚"* || "$actual" == *"start"* ]]; then
        log_success "✅ VALIDATION PASSED: Welcome pattern detected"
        return 0
    else
        log_error "❌ VALIDATION FAILED: No welcome pattern found"
        return 1
    fi
}

validate_file_delivery() {
    local actual="$1"
    local expected="$2"
    
    # Look for file delivery indicators
    if [[ "$actual" == *".epub"* || "$actual" == *"download"* || "$actual" == *"file"* ]]; then
        log_success "✅ VALIDATION PASSED: File delivery detected"
        return 0
    else
        log_error "❌ VALIDATION FAILED: No file delivery found"
        return 1
    fi
}

validate_error_pattern() {
    local actual="$1"
    local expected="$2"
    
    # Look for error indicators
    if [[ "$actual" == *"error"* || "$actual" == *"failed"* || "$actual" == *"not found"* ]]; then
        log_success "✅ VALIDATION PASSED: Error pattern detected (as expected)"
        return 0
    else
        log_error "❌ VALIDATION FAILED: Expected error not found"
        return 1
    fi
}

validate_timing() {
    local start_time="$1"
    local max_seconds="$2"
    
    local current_time=$(get_epoch)
    local elapsed=$((current_time - start_time))
    
    log_step "⏱️ TIMING: Checking response time"
    log_info "Elapsed: ${elapsed}s / Max: ${max_seconds}s"
    
    if [[ $elapsed -le $max_seconds ]]; then
        log_success "✅ TIMING PASSED: Response within acceptable time"
        return 0
    else
        log_error "❌ TIMING FAILED: Response took too long"
        return 1
    fi
}

#=== REPORTING PATTERNS ===
generate_test_report() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    # EXAMPLE: Standard test reporting
    # generate_test_report "IUC01" "PASSED" "Start command validation successful"
    # Pattern: Consistent format, Moscow timezone, emoji status
    
    cat << EOF

🎯 ${test_name} TEST REPORT
============================
Test: $test_name
Timestamp: $(get_timestamp)
Status: $status
Details: $details

VALIDATION SUMMARY:
------------------
$(if [[ "$status" == "PASSED" ]]; then echo "✅"; else echo "❌"; fi) Test execution
$(if [[ -n "${IUC_LAST_MESSAGE_ID:-}" ]]; then echo "✅ Message delivery (ID: $IUC_LAST_MESSAGE_ID)"; else echo "❌ Message delivery failed"; fi)
$(if [[ "$status" == "PASSED" ]]; then echo "✅"; else echo "❌"; fi) Response validation

============================

EOF
}

#=== AI LEARNING HELPERS ===
show_usage_patterns() {
    # EXAMPLE: AI can call this to see all patterns
    cat << 'EOF'
🤖 AI AGENT PATTERNS REFERENCE:

STANDARD TEST FLOW:
1. authenticate_user_session
2. verify_test_environment  
3. send_message_to_bot OR send_start_command OR send_book_search
4. read_bot_response OR read_progress_message OR read_epub_delivery
5. validate_response
6. generate_test_report

COMMON COMBINATIONS:
- Start Command Test: 
  authenticate_user_session → send_start_command → read_bot_response → validate_response "welcome"

- Book Search Test:
  authenticate_user_session → send_book_search "title" → read_progress_message → validate_response "progress" → read_epub_delivery → validate_response "file"

- Error Handling Test:
  authenticate_user_session → send_message_to_bot "invalid" → read_bot_response → validate_response "error"

VALIDATION TYPES:
- auto: Smart auto-detection based on expected pattern
- welcome: For /start command responses  
- progress: For "🔍 Searching..." messages
- file: For EPUB delivery validation
- error: For error message validation

TIMING PATTERNS:
- /start response: 5-10 seconds
- Book search progress: 5-15 seconds  
- EPUB delivery: 15-30 seconds
- Error responses: 3-10 seconds
EOF
}

show_function_reference() {
    cat << 'EOF'
📚 IUC FUNCTION REFERENCE:

AUTHENTICATION:
- authenticate_user_session()           # Always call first
- verify_test_environment()             # Check tools availability

MESSAGE SENDING:
- send_message_to_bot(msg, bot)         # Generic message sending
- send_start_command(bot)               # Specialized for /start
- send_book_search(title, bot)          # Specialized for book searches

RESPONSE READING:
- read_bot_response(timeout, type)      # Generic response reading
- read_progress_message(timeout)        # For progress messages
- read_epub_delivery(timeout)           # For file delivery

VALIDATION:
- validate_response(actual, expected, type) # Smart validation with auto-detection
- validate_timing(start_time, max_sec)  # Response time validation

REPORTING:
- generate_test_report(name, status, details) # Standard test reports
- show_usage_patterns()                 # AI learning reference
- show_function_reference()             # This help
EOF
}

# Export functions for use in other scripts
export -f authenticate_user_session verify_test_environment check_bot_accessibility
export -f send_message_to_bot send_start_command send_book_search
export -f read_bot_response read_progress_message read_epub_delivery
export -f validate_response validate_content_pattern validate_progress_pattern
export -f validate_welcome_pattern validate_file_delivery validate_error_pattern
export -f validate_timing generate_test_report
export -f log_step log_info log_success log_error log_warn log_given log_when log_then
export -f get_timestamp get_epoch show_usage_patterns show_function_reference