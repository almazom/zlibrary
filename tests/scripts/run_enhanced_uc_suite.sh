#!/bin/bash

# Enhanced UC Test Suite Runner with MCP Telegram Verification
# Runs all new UC tests with comprehensive EPUB delivery verification
# Created: 2025-08-12

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[SUITE]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUITE]${NC} $1"; }
log_error() { echo -e "${RED}[SUITE]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[SUITE]${NC} $1"; }
log_master() { echo -e "${BOLD}${CYAN}[SUITE]${NC} $1"; }

# Test suite configuration
TESTS_DIR="/home/almaz/microservices/zlibrary_api_module/tests"
RESULTS_DIR="$TESTS_DIR/suite_results"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Available UC tests
declare -A UC_TESTS=(
    ["UC25"]="UC25_english_programming_books_test.sh|English Programming Books|Programming"
    ["UC26"]="UC26_russian_classics_verification_test.sh|Russian Literature Classics|Literature" 
    ["UC27"]="UC27_technical_books_advanced_test.sh|Advanced Technical Books|Technical"
    ["UC28"]="UC28_popular_fiction_realtime_test.sh|Popular Fiction Real-time|Fiction"
    ["UC29"]="UC29_comprehensive_verification_test.sh|Comprehensive Multi-Category|Master"
)

# Test suite execution
run_single_uc() {
    local uc_name="$1"
    local test_info="${UC_TESTS[$uc_name]}"
    
    IFS='|' read -r script_name description category <<< "$test_info"
    
    log_master "🔥 EXECUTING $uc_name: $description"
    log_info "📂 Category: $category"
    log_info "📄 Script: $script_name"
    echo "$(printf '=%.0s' {1..80})"
    
    local start_time=$(date +%s)
    local result_code=0
    
    # Execute test
    if "$TESTS_DIR/$script_name"; then
        result_code=0
        log_success "✅ $uc_name COMPLETED SUCCESSFULLY"
    else
        result_code=$?
        log_error "❌ $uc_name FAILED (code: $result_code)"
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "⏱️ Duration: ${duration}s"
    echo ""
    
    return $result_code
}

# Run full test suite
run_full_suite() {
    log_master "🚀 ENHANCED UC TEST SUITE - FULL EXECUTION"
    log_master "=========================================="
    log_info "📊 Total Tests: ${#UC_TESTS[@]}"
    log_info "📁 Results Directory: $RESULTS_DIR"
    log_info "🕐 Started: $(date)"
    log_master "=========================================="
    
    mkdir -p "$RESULTS_DIR"
    
    # Initialize counters
    local passed=0
    local failed=0
    local total_duration=0
    local suite_start=$(date +%s)
    
    # Run each test
    local test_num=0
    for uc in "${!UC_TESTS[@]}"; do
        ((test_num++))
        echo ""
        log_master "📋 TEST $test_num/${#UC_TESTS[@]}: $uc"
        
        local test_start=$(date +%s)
        
        if run_single_uc "$uc"; then
            ((passed++))
        else
            ((failed++))
        fi
        
        local test_end=$(date +%s)
        local test_duration=$((test_end - test_start))
        total_duration=$((total_duration + test_duration))
        
        # Wait between tests for system stability
        if [[ $test_num -lt ${#UC_TESTS[@]} ]]; then
            log_info "⏸️ Suite cooldown: 20s before next test..."
            sleep 20
        fi
    done
    
    local suite_end=$(date +%s)
    local total_suite_time=$((suite_end - suite_start))
    
    # Final suite results
    echo ""
    log_master "🎯 ENHANCED UC TEST SUITE RESULTS" 
    log_master "=================================="
    log_master "📊 Total Tests: ${#UC_TESTS[@]}"
    log_success "✅ Passed: $passed"
    log_error "❌ Failed: $failed"
    
    local success_rate=$(( (passed * 100) / ${#UC_TESTS[@]} ))
    log_master "📈 Success Rate: ${success_rate}%"
    log_master "⏱️ Total Duration: ${total_suite_time}s ($(date -ud "@$total_suite_time" +%H:%M:%S))"
    log_master "🕐 Completed: $(date)"
    log_master "=================================="
    
    # Save suite summary
    {
        echo "Enhanced UC Test Suite Results - $TIMESTAMP"
        echo "============================================"
        echo "Total Tests: ${#UC_TESTS[@]}"
        echo "Passed: $passed"
        echo "Failed: $failed" 
        echo "Success Rate: ${success_rate}%"
        echo "Duration: ${total_suite_time}s"
        echo "Completed: $(date)"
        echo ""
        echo "Individual Test Results:"
        echo "========================"
    } > "$RESULTS_DIR/suite_summary_$TIMESTAMP.txt"
    
    # Overall assessment
    if [[ $passed -eq ${#UC_TESTS[@]} ]]; then
        log_success "🏆 PERFECT SUITE: All UC tests passed!"
        return 0
    elif [[ $success_rate -ge 80 ]]; then
        log_success "🎉 EXCELLENT SUITE: High success rate"
        return 0
    elif [[ $success_rate -ge 60 ]]; then
        log_warn "⚠️ GOOD SUITE: Most tests passed"
        return 1
    else
        log_error "❌ POOR SUITE: Many tests failed"
        return 2
    fi
}

# Run specific test categories
run_category() {
    local target_category="$1"
    
    log_master "🎯 RUNNING CATEGORY: $target_category"
    log_master "===================================="
    
    local category_passed=0
    local category_total=0
    
    for uc in "${!UC_TESTS[@]}"; do
        local test_info="${UC_TESTS[$uc]}"
        IFS='|' read -r script_name description category <<< "$test_info"
        
        if [[ "$category" == "$target_category" ]]; then
            ((category_total++))
            echo ""
            if run_single_uc "$uc"; then
                ((category_passed++))
            fi
            
            # Wait between category tests
            sleep 15
        fi
    done
    
    if [[ $category_total -eq 0 ]]; then
        log_error "❌ No tests found for category: $target_category"
        return 1
    fi
    
    echo ""
    log_master "🎯 CATEGORY RESULTS: $target_category"
    log_master "Passed: $category_passed/$category_total"
    
    return $((category_total - category_passed))
}

# Quick test runner (single UC)
run_quick() {
    local uc_name="$1"
    
    if [[ ! ${UC_TESTS[$uc_name]+_} ]]; then
        log_error "❌ Unknown UC test: $uc_name"
        echo "Available tests: ${!UC_TESTS[@]}"
        return 1
    fi
    
    log_master "⚡ QUICK TEST: $uc_name"
    run_single_uc "$uc_name"
}

# Display available tests
show_tests() {
    log_master "📋 AVAILABLE ENHANCED UC TESTS"
    log_master "==============================="
    
    for uc in "${!UC_TESTS[@]}"; do
        local test_info="${UC_TESTS[$uc]}"
        IFS='|' read -r script_name description category <<< "$test_info"
        
        echo -e "${CYAN}$uc${NC}: $description"
        echo -e "   📂 Category: $category"
        echo -e "   📄 Script: $script_name"
        echo ""
    done
}

# Help function
show_help() {
    echo "Enhanced UC Test Suite Runner with MCP Telegram Verification"
    echo ""
    echo "USAGE:"
    echo "  $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "COMMANDS:"
    echo "  full                    Run all UC tests in sequence"
    echo "  quick UC_NAME          Run single UC test (UC25, UC26, UC27, UC28, UC29)"
    echo "  category CATEGORY      Run all tests in category (Programming, Literature, Technical, Fiction, Master)"
    echo "  list                   Show all available tests"
    echo "  help                   Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 full                               # Run complete test suite"
    echo "  $0 quick UC25                         # Run only UC25"
    echo "  $0 category Programming               # Run programming tests"
    echo "  $0 list                              # Show available tests"
    echo ""
    echo "FEATURES:"
    echo "  • Real book requests with EPUB verification"
    echo "  • MCP Telegram reader integration"
    echo "  • Multi-language support (English + Russian)"
    echo "  • Multi-category testing (Programming, Fiction, Technical, etc.)"
    echo "  • Real-time message monitoring"
    echo "  • Comprehensive scoring and analysis"
    echo ""
    echo "TEST RESULTS:"
    echo "  Results are saved in: $RESULTS_DIR/"
}

# Main execution
main() {
    case "${1:-help}" in
        "full")
            run_full_suite ;;
        "quick")
            if [[ -n "${2:-}" ]]; then
                run_quick "$2"
            else
                log_error "❌ UC name required for quick test"
                echo "Usage: $0 quick UC_NAME"
                exit 1
            fi ;;
        "category")
            if [[ -n "${2:-}" ]]; then
                run_category "$2"
            else
                log_error "❌ Category name required"
                echo "Usage: $0 category CATEGORY_NAME"
                exit 1
            fi ;;
        "list")
            show_tests ;;
        "help"|*)
            show_help ;;
    esac
}

# Execute main
main "$@"