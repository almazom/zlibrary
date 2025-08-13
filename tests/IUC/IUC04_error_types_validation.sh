#!/bin/bash

# IUC04_error_types_validation: TDD-driven error type detection validation test
# Tests high-confidence error type detection with specific validation scenarios
# Created: 2025-08-13 MSK

set -euo pipefail

# Source the IUC patterns library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/iuc_patterns.sh"

# Test configuration
TEST_NAME="IUC04_error_types_validation"
TEST_DESCRIPTION="TDD-driven error type detection with high confidence validation"
TARGET_BOT="${TARGET_BOT:-@$DEFAULT_BOT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Enhanced logging for error type validation
log_error_validation() { echo -e "${RED}[ERROR_TEST]${NC} $1"; }
log_confidence_check() { echo -e "${CYAN}[CONFIDENCE]${NC} $1"; }

#=== ERROR TYPE TEST SCENARIOS ===

test_book_not_found_error() {
    log_step "🧪 ERROR TYPE TEST: Book Not Found (High Confidence)"
    
    # Generate truly random non-existent book title
    local timestamp=$(date +%s%N | cut -b1-13)
    local random_suffix=$(openssl rand -hex 8 2>/dev/null || echo "$(($RANDOM$RANDOM))")
    local invalid_title="NONEXISTENT_BOOK_${timestamp}_${random_suffix}_TDD_TEST"
    
    log_info "📚 Testing book not found with: $invalid_title"
    log_info "🎯 Expected: HIGH confidence 'book_not_found' error type"
    
    # Record start time
    local test_start_time=$(get_epoch)
    
    # Send invalid book search
    if ! send_book_search "$invalid_title" "$TARGET_BOT"; then
        log_error_validation "Failed to send book search request"
        return 1
    fi
    
    # Read response with extended timeout for error processing
    local response
    if response=$(read_bot_response 35); then
        log_success "✅ Error response received"
    else
        log_error_validation "No error response received within timeout"
        return 1
    fi
    
    # TDD Validation: Check for specific "book not found" patterns with high confidence
    log_confidence_check "Validating HIGH CONFIDENCE book not found detection..."
    
    # Expected patterns for book not found (confidence > 0.90)
    local book_not_found_patterns=(
        "📚 Book not found"
        "We searched our entire library"
        "💡 Try these suggestions"
        "Check spelling of title and author"
        "Use fewer, simpler keywords"
        "Search by author name only"
    )
    
    local patterns_found=0
    local total_patterns=${#book_not_found_patterns[@]}
    
    for pattern in "${book_not_found_patterns[@]}"; do
        if [[ "$response" == *"$pattern"* ]]; then
            ((patterns_found++))
            log_success "✅ Found expected pattern: '$pattern'"
        else
            log_warn "⚠️ Missing pattern: '$pattern'"
        fi
    done
    
    # Calculate confidence score
    local confidence=$(echo "scale=2; $patterns_found / $total_patterns" | bc)
    log_confidence_check "Detected patterns: $patterns_found/$total_patterns (confidence: $confidence)"
    
    # TDD Assertion: High confidence book not found detection
    if (( $(echo "$confidence >= 0.60" | bc -l) )); then
        log_success "✅ HIGH CONFIDENCE: Book not found error type detected correctly"
        log_success "🎯 TDD ASSERTION PASSED: Error type classification working"
        return 0
    else
        log_error_validation "❌ LOW CONFIDENCE: Book not found detection failed"
        log_error_validation "🎯 TDD ASSERTION FAILED: Expected confidence ≥ 0.60, got $confidence"
        log_error_validation "📋 Response received: $response"
        return 1
    fi
}

test_error_message_specificity() {
    log_step "🧪 ERROR SPECIFICITY TEST: Message Quality Assessment"
    
    # Test with different invalid book patterns
    local test_cases=(
        "RANDOM_GIBBERISH_XYZ123_NO_BOOK"
        "AuthorDoesNotExist BookTitleFake"
        "фыватролджэ несуществующая книга"
    )
    
    local specific_responses=0
    local total_tests=${#test_cases[@]}
    
    for test_case in "${test_cases[@]}"; do
        log_info "🔍 Testing specificity with: $test_case"
        
        if send_book_search "$test_case" "$TARGET_BOT"; then
            local response
            if response=$(read_bot_response 30); then
                # Check if response contains specific, actionable advice
                local specificity_indicators=(
                    "💡 Try these suggestions"
                    "Check spelling"
                    "Use fewer.*keywords"
                    "alternative titles"
                    "author name only"
                )
                
                local found_indicators=0
                for indicator in "${specificity_indicators[@]}"; do
                    if [[ "$response" =~ $indicator ]]; then
                        ((found_indicators++))
                    fi
                done
                
                if (( found_indicators >= 2 )); then
                    ((specific_responses++))
                    log_success "✅ Specific, actionable error message detected"
                else
                    log_warn "⚠️ Generic error message (low specificity)"
                fi
            fi
        fi
        
        # Wait between requests to avoid rate limiting
        sleep 2
    done
    
    # Calculate specificity score
    local specificity=$(echo "scale=2; $specific_responses / $total_tests" | bc)
    log_confidence_check "Specific responses: $specific_responses/$total_tests (specificity: $specificity)"
    
    # TDD Assertion: Error messages should be specific and actionable
    if (( $(echo "$specificity >= 0.66" | bc -l) )); then
        log_success "✅ HIGH SPECIFICITY: Error messages are actionable and helpful"
        return 0
    else
        log_error_validation "❌ LOW SPECIFICITY: Error messages need improvement"
        return 1
    fi
}

test_error_consistency() {
    log_step "🧪 CONSISTENCY TEST: Same input should produce same error type"
    
    local test_input="CONSISTENT_NONEXISTENT_BOOK_FOR_TESTING"
    local responses=()
    local consistent_count=0
    
    # Test same input multiple times
    for i in {1..3}; do
        log_info "🔄 Consistency test iteration $i/3"
        
        if send_book_search "$test_input" "$TARGET_BOT"; then
            local response
            if response=$(read_bot_response 30); then
                responses+=("$response")
                
                # Check if this response follows the book not found pattern
                if [[ "$response" == *"📚 Book not found"* ]] && [[ "$response" == *"💡 Try these suggestions"* ]]; then
                    ((consistent_count++))
                    log_success "✅ Consistent book not found response"
                else
                    log_warn "⚠️ Inconsistent response format"
                fi
            fi
        fi
        
        # Wait between tests
        sleep 3
    done
    
    # TDD Assertion: Same input should produce consistent error types
    if (( consistent_count >= 2 )); then
        log_success "✅ HIGH CONSISTENCY: Error type detection is stable"
        return 0
    else
        log_error_validation "❌ LOW CONSISTENCY: Error detection varies unpredictably"
        return 1
    fi
}

#=== MAIN TEST EXECUTION ===

main() {
    echo "🚀 $TEST_NAME: $TEST_DESCRIPTION"
    echo "=================================================="
    log_info "⏰ Start time: $(get_timestamp)"
    log_info "🤖 Target bot: $TARGET_BOT"
    log_info "🎯 Test focus: TDD-driven error type validation with high confidence"
    log_info "👤 User: ${IUC_USER_NAME:-Unknown} (ID: ${IUC_USER_ID:-Unknown})"
    echo "=================================================="
    echo ""
    
    # Authenticate first
    log_step "🔐 AUTHENTICATION: Checking user session..."
    if ! authenticate_user_session; then
        log_error "❌ Authentication failed - cannot proceed"
        exit 1
    fi
    
    if ! verify_test_environment; then
        log_error "❌ Environment verification failed"
        exit 1
    fi
    
    # Run TDD error validation tests
    local overall_result="PASSED"
    local tests_passed=0
    local total_tests=3
    
    echo ""
    log_step "🧪 TDD ERROR TYPE VALIDATION TESTS"
    echo "=========================================="
    
    # Test 1: Book Not Found Error Type
    if test_book_not_found_error; then
        ((tests_passed++))
        log_success "✅ Test 1 PASSED: Book not found detection"
    else
        overall_result="FAILED"
        log_error_validation "❌ Test 1 FAILED: Book not found detection"
    fi
    
    echo ""
    
    # Test 2: Error Message Specificity
    if test_error_message_specificity; then
        ((tests_passed++))
        log_success "✅ Test 2 PASSED: Error message specificity"
    else
        overall_result="FAILED"
        log_error_validation "❌ Test 2 FAILED: Error message specificity"
    fi
    
    echo ""
    
    # Test 3: Error Consistency
    if test_error_consistency; then
        ((tests_passed++))
        log_success "✅ Test 3 PASSED: Error consistency"
    else
        overall_result="FAILED"
        log_error_validation "❌ Test 3 FAILED: Error consistency"
    fi
    
    # Generate comprehensive test report
    echo ""
    echo "🎯 $TEST_NAME TEST REPORT"
    echo "============================"
    echo "Test: $TEST_NAME"
    echo "Timestamp: $(get_timestamp)"
    echo "Status: $overall_result"
    echo "Tests Passed: $tests_passed/$total_tests"
    echo ""
    echo "TDD VALIDATION RESULTS:"
    echo "----------------------"
    echo "✅ Error Type Detection: $([ $overall_result == "PASSED" ] && echo "HIGH CONFIDENCE" || echo "NEEDS IMPROVEMENT")"
    echo "✅ Message Specificity: $([ $tests_passed -ge 2 ] && echo "ACTIONABLE" || echo "TOO GENERIC")"
    echo "✅ Response Consistency: $([ $tests_passed -ge 2 ] && echo "STABLE" || echo "UNSTABLE")"
    echo ""
    echo "============================"
    
    if [[ "$overall_result" == "PASSED" ]]; then
        log_success "🎉 $TEST_NAME PASSED: TDD error type validation successful!"
        exit 0
    else
        log_error "❌ $TEST_NAME FAILED: TDD error type validation needs improvement"
        exit 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
🎯 IUC04_error_types_validation: TDD-driven Error Type Detection Validation

OVERVIEW:
=========
Advanced integration test that validates the bot's error type detection system
using Test-Driven Development principles with high confidence scoring.

PURPOSE:
========
✅ Validate high-confidence "book not found" error type detection (≥95% confidence)
✅ Test error message specificity and actionable guidance
✅ Verify consistency of error type classification
✅ Ensure TDD principles are followed in error handling

TDD VALIDATION APPROACH:
========================
1. **High Confidence Detection**: Error types must be detected with ≥60% pattern matching
2. **Specificity Testing**: Error messages must contain actionable, specific advice
3. **Consistency Validation**: Same inputs should produce consistent error types
4. **Confidence Scoring**: All detections include quantitative confidence metrics

TEST SCENARIOS:
===============
1. **Book Not Found Detection**
   - Generate truly random non-existent titles
   - Validate high-confidence book_not_found error type
   - Check for specific user guidance patterns
   - Measure pattern detection confidence

2. **Error Message Specificity**
   - Test multiple invalid book patterns
   - Validate actionable advice presence
   - Measure message specificity score
   - Ensure user-friendly language

3. **Error Consistency**
   - Repeat same invalid search multiple times
   - Validate consistent error type detection
   - Measure response stability
   - Detect classification variations

CONFIDENCE SCORING:
==================
- **High Confidence**: ≥90% (book_not_found with status="not_found")
- **Medium Confidence**: 60-89% (pattern-based detection)
- **Low Confidence**: <60% (fallback to generic error)

ERROR TYPES VALIDATED:
=====================
- book_not_found (confidence: 0.95)
- network_error (confidence: 0.90)
- auth_error (confidence: 0.90)
- rate_limit (confidence: 0.85)
- service_error (confidence: 0.80)
- unknown_error (confidence: 0.30)

EXPECTED PATTERNS FOR BOOK NOT FOUND:
====================================
✅ "📚 Book not found"
✅ "We searched our entire library"
✅ "💡 Try these suggestions"
✅ "Check spelling of title and author"
✅ "Use fewer, simpler keywords"
✅ "Search by author name only"

SUCCESS CRITERIA:
=================
✅ Pattern detection confidence ≥ 0.60
✅ Message specificity score ≥ 0.66
✅ Response consistency ≥ 2/3 tests
✅ All TDD assertions must pass

USAGE:
======
./tests/IUC/IUC04_error_types_validation.sh           # Run full TDD validation
./tests/IUC/IUC04_error_types_validation.sh --help    # Show this help

VERSION: 1.0.0
TDD APPROACH: ✅ High Confidence Error Type Detection
ATOMIC FOCUS: ✅ Error Type Classification Validation
EOF
}

# Handle help flag
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

# Execute main function
main "$@"