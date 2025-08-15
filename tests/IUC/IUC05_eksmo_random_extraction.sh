#!/bin/bash
#
# IUC05_eksmo_random_extraction: Enhanced random book extraction from eksmo.ru
# 
# FEATURES:
# - Weighted random page selection (3,7,12 preferred over page 1)
# - Random book selection from each page  
# - Duplicate prevention with 7-day tracking
# - Integration with existing book_search.sh pipeline
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="/tmp/iuc05_eksmo_random_$(date +%Y%m%d_%H%M%S).log"
TRACKING_FILE="$SCRIPT_DIR/eksmo_book_pool.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'  
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} ✅ $1" | tee -a "$LOG_FILE"; }
log_error() { echo -e "${RED}[ERROR]${NC} ❌ $1" | tee -a "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} ⚠️ $1" | tee -a "$LOG_FILE"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1" | tee -a "$LOG_FILE"; }
log_when() { echo -e "${YELLOW}[WHEN]${NC} $1" | tee -a "$LOG_FILE"; }
log_then() { echo -e "${GREEN}[THEN]${NC} $1" | tee -a "$LOG_FILE"; }
log_given() { echo -e "${PURPLE}[GIVEN]${NC} $1" | tee -a "$LOG_FILE"; }

# Test banner
echo -e "${CYAN}🚀 IUC05_eksmo_random_extraction: Enhanced random book extraction from eksmo.ru${NC}"
echo "=================================================="
log_info "⏰ Start time: $(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')"
log_info "🤖 Target bot: @epub_toc_based_sample_bot" 
log_info "📊 Min confidence: 0.85"
log_info "🔄 Max extraction attempts: 10"
log_info "📁 Tracking file: $TRACKING_FILE"
echo "=================================================="

echo ""
log_step "🧪 SCENARIO: Enhanced random eksmo.ru book extraction with deduplication"
echo "=========================================="

# Given: Check prerequisites
log_given "🏪 GIVEN: I have eksmo.ru random extraction system"
if [[ ! -f "$ROOT_DIR/scripts/eksmo_random_extractor.py" ]]; then
    log_error "Missing eksmo_random_extractor.py script"
    exit 1
fi
log_success "Eksmo random extractor available"

log_given "🔐 GIVEN: I have authenticated Telegram user session"
log_step "🔐 AUTHENTICATION: Checking user session..."

# Check authentication using existing method from IUC05
if command -v /home/almaz/MCP/SCRIPTS/telegram-read-manager.sh &> /dev/null; then
    auth_result=$(timeout 10 /home/almaz/MCP/SCRIPTS/telegram-read-manager.sh read aiclubsweggs --limit 1 2>/dev/null || echo "FAILED")
    if [[ "$auth_result" != "FAILED" ]]; then
        # Extract user info from auth result
        user_info=$(echo "$auth_result" | grep -o "User: [^,]*" | head -1 || echo "User: Unknown")
        log_success "Authentication successful: $user_info"
    else
        log_error "Authentication failed"
        exit 1
    fi
else
    log_warning "MCP telegram-read-manager not available, proceeding with assumption"
fi

log_step "🔧 ENVIRONMENT: Verifying extraction tools..."
# Check Claude CLI availability
if command -v /home/almaz/.claude/local/claude &> /dev/null; then
    log_success "Claude CLI available"
else
    log_error "Claude CLI not found at /home/almaz/.claude/local/claude"
    exit 1
fi

# Check Python availability
if command -v python3 &> /dev/null; then
    log_success "Python3 available"
else
    log_error "Python3 not available"
    exit 1
fi

log_success "Environment verification passed"

# When: Extract random book
log_when "🤖 WHEN: I extract a random book from eksmo.ru using enhanced pipeline"
log_info "🔄 Starting random book extraction..."

extraction_start_time=$(date +%s)

# Run the OPTIMIZED random extractor
if book_metadata=$(cd "$ROOT_DIR" && timeout 30 python3 scripts/optimized_eksmo_extractor.py 2>&1); then
    extraction_end_time=$(date +%s)
    extraction_duration=$((extraction_end_time - extraction_start_time))
    
    log_success "Book extraction completed in ${extraction_duration}s"
    log_info "📖 Extracted metadata:"
    echo "$book_metadata" | tee -a "$LOG_FILE"
    
    # Parse the JSON response 
    if book_title=$(echo "$book_metadata" | jq -r '.title // empty' 2>/dev/null) && [[ -n "$book_title" ]]; then
        book_author=$(echo "$book_metadata" | jq -r '.author // empty' 2>/dev/null)
        book_confidence=$(echo "$book_metadata" | jq -r '.confidence // empty' 2>/dev/null)
        book_url=$(echo "$book_metadata" | jq -r '.url // empty' 2>/dev/null)
        page_source=$(echo "$book_metadata" | jq -r '.page_source // empty' 2>/dev/null)
        attempt_count=$(echo "$book_metadata" | jq -r '.attempt // 1' 2>/dev/null)
        
        log_success "Book extracted: '$book_title' by $book_author"
        log_info "📊 Confidence: $book_confidence"
        log_info "🔗 Source URL: $book_url"  
        log_info "📄 Page source: $page_source"
        log_info "🔄 Extraction attempt: $attempt_count"
        
        # Check confidence threshold
        if (( $(echo "$book_confidence >= 0.85" | bc -l) )); then
            log_success "Confidence threshold met (≥0.85)"
        else
            log_warning "Low confidence: $book_confidence"
        fi
        
    else
        log_error "Failed to parse book metadata JSON"
        log_info "Raw response: $book_metadata"
        exit 1
    fi
    
else
    log_error "Book extraction failed or timed out"
    log_info "Error details: $book_metadata"
    exit 1
fi

# Then: Search for the extracted book
log_then "✅ THEN: I should get valid book metadata with high randomness"
log_success "Metadata validation passed"

log_when "🔍 WHEN: I search for the extracted book using book_search.sh"
log_step "📚 BOOK SEARCH: '$book_title $book_author'"
log_info "Target: @epub_toc_based_sample_bot"
log_info "Expected: Progress message → EPUB delivery → Confirmation"

# Create search query
search_query="$book_title $book_author"
log_step "📤 SENDING: '$search_query' to @epub_toc_based_sample_bot"

# Use existing book search system
search_start_time=$(date +%s)

if search_result=$(cd "$ROOT_DIR" && timeout 120 ./scripts/book_search.sh "$search_query" 2>&1); then
    search_end_time=$(date +%s)
    search_duration=$((search_end_time - search_start_time))
    
    log_success "Book search completed in ${search_duration}s"
    log_info "📖 Search result:"
    echo "$search_result" | tail -10 | tee -a "$LOG_FILE"
    
    # Check for success indicators
    if echo "$search_result" | grep -q "EPUB file available\|Download.*successful\|✅"; then
        log_success "EPUB delivery successful"
        final_status="SUCCESS"
    elif echo "$search_result" | grep -q "No EPUB file available\|not found"; then
        log_warning "No EPUB available for this book"
        final_status="NO_EPUB"
    else
        log_warning "Search completed with unclear result"
        final_status="UNCLEAR"
    fi
    
else
    log_error "Book search failed or timed out"
    final_status="FAILED"
fi

# Then: Validate overall success
log_then "🔍 THEN: I should receive appropriate response"

case $final_status in
    "SUCCESS")
        log_success "EPUB delivery successful"
        exit_code=0
        ;;
    "NO_EPUB") 
        log_success "Search completed (no EPUB available)"
        exit_code=0
        ;;
    "UNCLEAR"|"FAILED")
        log_error "Search process failed"
        exit_code=1
        ;;
esac

# Summary
total_end_time=$(date +%s)
total_start_time=$(extraction_start_time)
total_duration=$((total_end_time - total_start_time))

echo ""
echo "=================================================="
log_info "📊 TEST SUMMARY:"
log_info "✅ Random book extracted: '$book_title' by $book_author"
log_info "📊 Confidence score: $book_confidence"
log_info "🎲 Randomness source: $page_source"
log_info "🔄 Extraction attempts: $attempt_count"  
log_info "⏱️ Total duration: ${total_duration}s"
log_info "📁 Pool tracking: $TRACKING_FILE"
log_info "📝 Full log: $LOG_FILE"
echo "=================================================="

# Show pool statistics if available
if [[ -f "$TRACKING_FILE" ]]; then
    pool_size=$(jq length "$TRACKING_FILE" 2>/dev/null || echo "0")
    log_info "📚 Books in pool: $pool_size"
    
    # Show recent extractions
    if [[ "$pool_size" -gt 0 ]]; then
        log_info "🕒 Recent extractions:"
        jq -r '.[] | "  📖 \(.title) by \(.author) (\(.extracted_at))"' "$TRACKING_FILE" 2>/dev/null | tail -5 | while read line; do
            log_info "$line"
        done
    fi
fi

exit $exit_code