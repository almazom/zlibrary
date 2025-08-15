#!/bin/bash

# Feedback Loop Test System
# Continuously tests manual vs UC automated message pipeline equivalence
# Provides real-time feedback on system performance and consistency

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Test configuration
LOOP_DELAY=${LOOP_DELAY:-30}  # Seconds between test cycles
MAX_CYCLES=${MAX_CYCLES:-100}  # Maximum test cycles (0 = infinite)
RESULTS_DIR="$SCRIPT_DIR/feedback_results"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Statistics
TOTAL_CYCLES=0
SUCCESSFUL_CYCLES=0
FAILED_CYCLES=0
START_TIME=$(date +%s)

echo -e "${MAGENTA}🔄 Feedback Loop Test System${NC}"
echo -e "${MAGENTA}============================${NC}"
echo "🎯 Goal: Continuous verification of manual = UC automated pipeline"
echo "⏱️  Loop delay: ${LOOP_DELAY}s"
echo "🔢 Max cycles: ${MAX_CYCLES} (0 = infinite)"
echo "📁 Results: $RESULTS_DIR"
echo ""

# Create results directory
mkdir -p "$RESULTS_DIR"

# Initialize results log
RESULTS_LOG="$RESULTS_DIR/feedback_loop_${TIMESTAMP}.log"
STATS_FILE="$RESULTS_DIR/feedback_stats_${TIMESTAMP}.json"

# Function to print colored output
log_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> "$RESULTS_LOG"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] $1" >> "$RESULTS_LOG"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> "$RESULTS_LOG"
}

log_cycle() {
    echo -e "${CYAN}🔄 $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [CYCLE] $1" >> "$RESULTS_LOG"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" >> "$RESULTS_LOG"
}

# Function to update statistics
update_stats() {
    local cycle_result="$1"
    local cycle_duration="$2"
    local current_time=$(date +%s)
    local total_runtime=$((current_time - START_TIME))
    
    if [[ "$cycle_result" == "success" ]]; then
        ((SUCCESSFUL_CYCLES++))
    else
        ((FAILED_CYCLES++))
    fi
    
    local success_rate=0
    if [[ $TOTAL_CYCLES -gt 0 ]]; then
        success_rate=$((SUCCESSFUL_CYCLES * 100 / TOTAL_CYCLES))
    fi
    
    # Create JSON stats
    cat > "$STATS_FILE" << EOF
{
    "test_session": {
        "start_time": "$START_TIME",
        "current_time": "$current_time",
        "total_runtime_seconds": $total_runtime,
        "timestamp": "$TIMESTAMP"
    },
    "cycles": {
        "total": $TOTAL_CYCLES,
        "successful": $SUCCESSFUL_CYCLES,
        "failed": $FAILED_CYCLES,
        "success_rate": $success_rate
    },
    "performance": {
        "last_cycle_duration": $cycle_duration,
        "average_cycle_time": $((total_runtime / (TOTAL_CYCLES > 0 ? TOTAL_CYCLES : 1))),
        "cycles_per_hour": $((TOTAL_CYCLES * 3600 / (total_runtime > 0 ? total_runtime : 1)))
    },
    "configuration": {
        "loop_delay": $LOOP_DELAY,
        "max_cycles": $MAX_CYCLES
    }
}
EOF
}

# Function to display real-time statistics
display_stats() {
    local current_time=$(date +%s)
    local total_runtime=$((current_time - START_TIME))
    local success_rate=0
    
    if [[ $TOTAL_CYCLES -gt 0 ]]; then
        success_rate=$((SUCCESSFUL_CYCLES * 100 / TOTAL_CYCLES))
    fi
    
    echo ""
    echo -e "${BLUE}📊 Real-time Statistics${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "🔄 Total Cycles: ${CYAN}$TOTAL_CYCLES${NC}"
    echo -e "✅ Successful: ${GREEN}$SUCCESSFUL_CYCLES${NC}"
    echo -e "❌ Failed: ${RED}$FAILED_CYCLES${NC}"
    echo -e "📈 Success Rate: ${GREEN}$success_rate%${NC}"
    echo -e "⏱️  Runtime: ${YELLOW}$((total_runtime / 60))m $((total_runtime % 60))s${NC}"
    
    if [[ $TOTAL_CYCLES -gt 0 ]]; then
        local avg_cycle_time=$((total_runtime / TOTAL_CYCLES))
        echo -e "⚡ Avg Cycle Time: ${YELLOW}${avg_cycle_time}s${NC}"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Function to check if unified system is running
check_unified_system() {
    if curl -s -f http://localhost:8765/health >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to test single cycle
test_single_cycle() {
    local cycle_num="$1"
    local cycle_start=$(date +%s)
    
    log_cycle "Starting cycle $cycle_num"
    
    # Test book titles - rotating through different types
    local books=(
        "Clean Code Robert Martin:Programming"
        "Python Programming:Technical"
        "Война и мир:Russian Literature"
        "Data Structures:Computer Science"
        "Design Patterns:Software Engineering"
    )
    
    # Select book for this cycle
    local book_index=$((cycle_num % ${#books[@]}))
    IFS=':' read -r book_title book_type <<< "${books[$book_index]}"
    
    log_info "Testing: '$book_title' ($book_type)"
    
    # Create temporary test files
    local manual_result="/tmp/feedback_manual_$cycle_num.json"
    local uc_result="/tmp/feedback_uc_$cycle_num.json"
    
    # Test manual message
    log_info "Running manual message test..."
    if cd "$SCRIPT_DIR" && timeout 90 python3 manual_message_sender.py "$book_title" --json > "$manual_result" 2>/dev/null; then
        local manual_success=$(cat "$manual_result" | jq -r '.success // false' 2>/dev/null || echo "false")
        log_info "Manual test result: $manual_success"
    else
        log_error "Manual message test failed"
        echo '{"success": false, "error": "manual test timeout"}' > "$manual_result"
    fi
    
    # Wait between tests
    sleep 5
    
    # Test UC automated message
    log_info "Running UC automated test..."
    local uc_test_script="/tmp/uc_single_$cycle_num.py"
    
    cat > "$uc_test_script" << EOF
#!/usr/bin/env python3
import asyncio
import json
import sys
import os
sys.path.append('$SCRIPT_DIR')

from conflict_free_uc_test_v2 import ConflictFreeUCTestV2

async def main():
    try:
        tester = ConflictFreeUCTestV2()
        result = await tester.test_single_book_request("$book_title", "Feedback Cycle $cycle_num")
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"success": false, "error": str(e)}, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
EOF
    
    if cd "$SCRIPT_DIR" && timeout 120 python3 "$uc_test_script" > "$uc_result" 2>/dev/null; then
        local uc_success=$(cat "$uc_result" | jq -r '.success // false' 2>/dev/null || echo "false")
        log_info "UC test result: $uc_success"
    else
        log_error "UC automated test failed"
        echo '{"success": false, "error": "uc test timeout"}' > "$uc_result"
    fi
    
    # Clean up test script
    rm -f "$uc_test_script"
    
    # Compare results
    local manual_success=$(cat "$manual_result" | jq -r '.success // false' 2>/dev/null || echo "false")
    local uc_success=$(cat "$uc_result" | jq -r '.success // false' 2>/dev/null || echo "false")
    
    local cycle_end=$(date +%s)
    local cycle_duration=$((cycle_end - cycle_start))
    
    if [[ "$manual_success" == "$uc_success" ]]; then
        log_success "Cycle $cycle_num: PIPELINE IDENTICAL ✅ (Manual: $manual_success, UC: $uc_success)"
        
        # Save successful results
        cp "$manual_result" "$RESULTS_DIR/cycle_${cycle_num}_manual.json"
        cp "$uc_result" "$RESULTS_DIR/cycle_${cycle_num}_uc.json"
        
        update_stats "success" "$cycle_duration"
        return 0
    else
        log_error "Cycle $cycle_num: PIPELINE DIFFERENT ❌ (Manual: $manual_success, UC: $uc_success)"
        
        # Save failed results for analysis
        cp "$manual_result" "$RESULTS_DIR/cycle_${cycle_num}_manual_FAILED.json"
        cp "$uc_result" "$RESULTS_DIR/cycle_${cycle_num}_uc_FAILED.json"
        
        update_stats "failure" "$cycle_duration"
        return 1
    fi
    
    # Clean up temporary files
    rm -f "$manual_result" "$uc_result"
}

# Signal handler for graceful shutdown
cleanup() {
    echo ""
    log_warn "Received shutdown signal"
    log_info "Final statistics:"
    display_stats
    log_info "Results saved to: $RESULTS_DIR"
    log_info "Statistics file: $STATS_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main feedback loop
main() {
    log_info "Starting feedback loop test system..."
    
    # Check if unified system is running
    if ! check_unified_system; then
        log_error "Unified system is not running!"
        log_error "Please start it first: ./telegram_bot/start_unified_system.sh"
        exit 1
    fi
    
    log_info "✅ Unified system is running"
    log_info "Starting continuous testing..."
    
    # Initialize statistics
    update_stats "init" 0
    
    while true; do
        ((TOTAL_CYCLES++))
        
        echo ""
        log_cycle "═══ CYCLE $TOTAL_CYCLES ═══"
        
        # Run single test cycle
        if test_single_cycle "$TOTAL_CYCLES"; then
            log_success "Cycle $TOTAL_CYCLES completed successfully"
        else
            log_error "Cycle $TOTAL_CYCLES failed"
        fi
        
        # Display current statistics
        display_stats
        
        # Check if we've reached max cycles
        if [[ $MAX_CYCLES -gt 0 ]] && [[ $TOTAL_CYCLES -ge $MAX_CYCLES ]]; then
            log_info "Reached maximum cycles ($MAX_CYCLES)"
            break
        fi
        
        # Wait before next cycle
        log_info "Waiting ${LOOP_DELAY}s before next cycle..."
        
        # Progressive wait with countdown
        for ((i=LOOP_DELAY; i>0; i--)); do
            echo -ne "\r${YELLOW}⏳ Next cycle in: ${i}s${NC} "
            sleep 1
        done
        echo ""
    done
    
    # Final summary
    echo ""
    echo -e "${MAGENTA}🏁 Feedback Loop Test Complete${NC}"
    echo -e "${MAGENTA}==============================${NC}"
    display_stats
    
    local current_time=$(date +%s)
    local total_runtime=$((current_time - START_TIME))
    
    log_info "Test session completed"
    log_info "Total runtime: $((total_runtime / 3600))h $((total_runtime % 3600 / 60))m $((total_runtime % 60))s"
    log_info "Results directory: $RESULTS_DIR"
    log_info "Statistics file: $STATS_FILE"
    
    # Final verdict
    local success_rate=$((SUCCESSFUL_CYCLES * 100 / TOTAL_CYCLES))
    if [[ $success_rate -ge 90 ]]; then
        echo ""
        echo -e "${GREEN}🎉 EXCELLENT: $success_rate% pipeline consistency achieved!${NC}"
        echo -e "${GREEN}✅ CONFIRMED: Manual and UC automated messages are 100% identical${NC}"
    elif [[ $success_rate -ge 75 ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  GOOD: $success_rate% pipeline consistency${NC}"
        echo -e "${YELLOW}🔧 Minor inconsistencies detected - review failed cycles${NC}"
    else
        echo ""
        echo -e "${RED}❌ POOR: Only $success_rate% pipeline consistency${NC}"
        echo -e "${RED}🚨 Significant issues detected - investigation required${NC}"
    fi
}

# Check dependencies
if ! command -v jq &> /dev/null; then
    log_error "jq is required for this test. Please install it:"
    log_error "  sudo apt-get install jq"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    log_error "curl is required for this test. Please install it:"
    log_error "  sudo apt-get install curl"
    exit 1
fi

# Show usage if help requested
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Environment variables:"
    echo "  LOOP_DELAY     Seconds between cycles (default: 30)"
    echo "  MAX_CYCLES     Maximum cycles (default: 100, 0 = infinite)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run with defaults"
    echo "  LOOP_DELAY=10 $0            # Faster cycles"
    echo "  MAX_CYCLES=0 $0             # Run indefinitely"
    echo "  MAX_CYCLES=5 LOOP_DELAY=5 $0 # Quick test"
    exit 0
fi

# Run main function
main "$@"