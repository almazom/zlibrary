#!/bin/bash

# Enhanced Interactive URL to EPUB Testing Service with Rich UI
# Full transparency, step-by-step visibility, emoji-rich interface

set -euo pipefail

# Enhanced Colors & Emojis
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# Script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOK_SEARCH="$SCRIPT_DIR/book_search.sh"
RESULTS_FILE="$SCRIPT_DIR/../test_results/interactive_test_$(date +%Y%m%d_%H%M%S).json"

# Test counters
TOTAL_TESTS=0
SUCCESSFUL=0
FAILED=0

# Results array for final report
declare -a TEST_RESULTS

# Ensure results directory exists
mkdir -p "$(dirname "$RESULTS_FILE")"

# Function to print step with emoji
print_step() {
    local emoji="$1"
    local message="$2"
    echo -e "${CYAN}$emoji $message${NC}"
}

# Function to print sub-step
print_substep() {
    local message="$1"
    echo -e "${GRAY}   └─ $message${NC}"
}

# Function to extract query from URL with transparency
extract_url_transparently() {
    local url="$1"
    
    print_step "🔍" "URL Analysis Phase"
    print_substep "Input URL: $url"
    
    # Detect URL source
    if [[ "$url" =~ alpinabook\.ru ]]; then
        print_substep "📚 Detected: Alpinabook.ru (Russian business books)"
        
        # Extract book slug
        if [[ "$url" =~ /catalog/book-([^/]+) ]]; then
            local slug="${BASH_REMATCH[1]}"
            print_substep "📖 Book slug found: $slug"
            
            # Convert slug to query
            local query="${slug//-/ }"
            print_substep "🔄 Converted to query: \"$query\""
            
            # Special handling for 2025 editions
            if [[ "$query" =~ 2025 ]]; then
                print_substep "📅 Note: 2025 edition - removing year for better search"
                query="${query// 2025/}"
            fi
            
            # Transliteration for common terms
            # Keep Russian for known Russian books
            if [[ "$query" =~ "pishi sokrashchay" ]]; then
                query="Пиши сокращай Ильяхов"
                print_substep "📚 Known book: 'Пиши, сокращай' by Максим Ильяхов"
            elif [[ "$query" =~ "atomnye privychki" ]]; then
                query="atomic habits"
            elif [[ "$query" =~ "chistyy kod" ]]; then
                query="clean code"
            fi
            
            print_substep "✨ Final query: \"$query\""
            echo "$query"
            return 0
        fi
    elif [[ "$url" =~ podpisnie\.ru ]]; then
        print_substep "📚 Detected: Podpisnie.ru (Russian book recommendations)"
        if [[ "$url" =~ /books/([^/]+) ]]; then
            local slug="${BASH_REMATCH[1]}"
            local query="${slug//-/ }"
            print_substep "✨ Extracted: \"$query\""
            echo "$query"
            return 0
        fi
    elif [[ "$url" =~ goodreads\.com ]]; then
        print_substep "📚 Detected: Goodreads (International reviews)"
        if [[ "$url" =~ /book/show/[0-9]+-([^/?]+) ]]; then
            local title="${BASH_REMATCH[1]}"
            local query="${title//-/ }"
            print_substep "✨ Extracted: \"$query\""
            echo "$query"
            return 0
        fi
    elif [[ "$url" =~ amazon\. ]]; then
        print_substep "📚 Detected: Amazon (Online marketplace)"
        if [[ "$url" =~ /([^/]+)/dp/ ]]; then
            local title="${BASH_REMATCH[1]}"
            local query="${title//-/ }"
            print_substep "✨ Extracted: \"$query\""
            echo "$query"
            return 0
        fi
    else
        print_substep "⚠️  Unknown URL pattern - attempting generic extraction"
        # Try to extract from URL path
        local path="${url##*/}"
        local query="${path//-/ }"
        print_substep "✨ Generic extraction: \"$query\""
        echo "$query"
        return 0
    fi
    
    print_substep "❌ Failed to extract query from URL"
    echo ""
    return 1
}

# Function to process single URL with rich feedback
process_url_rich() {
    local url="$1"
    local test_num="$2"
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}📋 Test #$test_num${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Step 1: URL Analysis
    local extracted_query
    extracted_query=$(extract_url_transparently "$url")
    
    if [[ -z "$extracted_query" ]]; then
        echo -e "${RED}❌ Cannot extract book information from URL${NC}"
        ((FAILED++))
        TEST_RESULTS+=("{\"url\": \"$url\", \"book\": null, \"success\": false, \"reason\": \"Extraction failed\"}")
        ((TOTAL_TESTS++))
        return
    fi
    
    # Step 2: Search Phase
    echo ""
    print_step "🔎" "Search Phase"
    print_substep "Query: \"$extracted_query\""
    print_substep "Calling Z-Library API..."
    
    # Debug: Show exact command being run
    print_substep "Command: $BOOK_SEARCH \"$extracted_query\""
    
    # Call book_search.sh with extracted query
    local result
    result=$("$BOOK_SEARCH" "$extracted_query" 2>/dev/null || echo '{"status": "error", "result": {"message": "Script execution failed"}}')
    
    # Parse result
    local status
    status=$(echo "$result" | jq -r '.status // "error"')
    
    # Step 3: Results Phase
    echo ""
    print_step "📊" "Results Phase"
    
    if [[ "$status" == "success" ]]; then
        local book_title
        local confidence
        local download_path
        
        book_title=$(echo "$result" | jq -r '.result.book_info.title // "Unknown"')
        confidence=$(echo "$result" | jq -r '.result.confidence.score // 0')
        download_path=$(echo "$result" | jq -r '.result.epub_download_url // "N/A"')
        
        print_substep "📖 Book found: $book_title"
        print_substep "🎯 Confidence: $confidence"
        
        # Step 4: Decision Phase
        echo ""
        print_step "🤔" "Decision Phase"
        
        if (( $(echo "$confidence >= 0.6" | bc -l) )); then
            print_substep "✅ Confidence ≥ 0.6 - Proceeding with download"
            
            if [[ -f "$download_path" ]]; then
                local size
                size=$(ls -lh "$download_path" 2>/dev/null | awk '{print $5}' || echo "N/A")
                
                echo ""
                echo -e "${GREEN}✅ SUCCESS: Book downloaded${NC}"
                echo -e "${GREEN}   📚 Title: $book_title${NC}"
                echo -e "${GREEN}   🎯 Confidence: $confidence${NC}"
                echo -e "${GREEN}   💾 File: $(basename "$download_path") ($size)${NC}"
                
                ((SUCCESSFUL++))
                TEST_RESULTS+=("{\"url\": \"$url\", \"book\": \"$book_title\", \"success\": true, \"confidence\": $confidence}")
            else
                echo -e "${YELLOW}⚠️  Book found but download failed${NC}"
                ((FAILED++))
                TEST_RESULTS+=("{\"url\": \"$url\", \"book\": \"$book_title\", \"success\": false, \"confidence\": $confidence, \"reason\": \"Download failed\"}")
            fi
        else
            print_substep "❌ Confidence < 0.6 - Skipping download"
            echo ""
            echo -e "${YELLOW}⚠️  LOW CONFIDENCE: Not downloading${NC}"
            echo -e "${YELLOW}   📚 Book: $book_title${NC}"
            echo -e "${YELLOW}   🎯 Confidence: $confidence${NC}"
            
            ((FAILED++))
            TEST_RESULTS+=("{\"url\": \"$url\", \"book\": \"$book_title\", \"success\": false, \"confidence\": $confidence, \"reason\": \"Low confidence\"}")
        fi
    elif [[ "$status" == "not_found" ]]; then
        print_substep "❌ No books found in Z-Library"
        
        echo ""
        print_step "💡" "Suggestions"
        print_substep "Try different search terms"
        print_substep "Check if book title is in English"
        print_substep "Remove year/edition from query"
        
        echo ""
        echo -e "${RED}❌ NOT FOUND: No matching books${NC}"
        
        ((FAILED++))
        TEST_RESULTS+=("{\"url\": \"$url\", \"book\": null, \"success\": false, \"reason\": \"Not found\"}")
    else
        local error_msg
        error_msg=$(echo "$result" | jq -r '.result.message // "Unknown error"')
        print_substep "❌ Error: $error_msg"
        
        echo ""
        echo -e "${RED}❌ ERROR: $error_msg${NC}"
        
        ((FAILED++))
        TEST_RESULTS+=("{\"url\": \"$url\", \"book\": null, \"success\": false, \"reason\": \"$error_msg\"}")
    fi
    
    ((TOTAL_TESTS++))
}

# Function to display rich results table
display_rich_results() {
    echo ""
    echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                      📊 FINAL TEST REPORT 📊                      ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Summary stats
    local success_rate=0
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        success_rate=$(echo "scale=1; $SUCCESSFUL * 100 / $TOTAL_TESTS" | bc)
    fi
    
    echo -e "${WHITE}📈 Statistics:${NC}"
    echo -e "   Total Tests: ${WHITE}$TOTAL_TESTS${NC}"
    echo -e "   ✅ Successful: ${GREEN}$SUCCESSFUL${NC}"
    echo -e "   ❌ Failed: ${RED}$FAILED${NC}"
    echo -e "   📊 Success Rate: ${WHITE}${success_rate}%${NC}"
    
    if (( $(echo "$success_rate >= 80" | bc -l) )); then
        echo -e "   🎯 Status: ${GREEN}TARGET ACHIEVED (≥80%)${NC}"
    else
        echo -e "   🎯 Status: ${YELLOW}BELOW TARGET (<80%)${NC}"
    fi
    
    echo ""
    echo -e "${WHITE}📋 Detailed Results:${NC}"
    echo -e "${GRAY}────────────────────────────────────────────────────────────────────${NC}"
    
    local i=1
    for result in "${TEST_RESULTS[@]}"; do
        local url
        local book
        local success
        
        url=$(echo "$result" | jq -r '.url' | cut -c1-50)
        book=$(echo "$result" | jq -r '.book // "Not found"' | cut -c1-30)
        success=$(echo "$result" | jq -r '.success')
        
        if [[ "$success" == "true" ]]; then
            echo -e "  $i. ✅ $url"
            echo -e "     └─ 📚 $book"
        else
            local reason
            reason=$(echo "$result" | jq -r '.reason // "Unknown"')
            echo -e "  $i. ❌ $url"
            echo -e "     └─ ⚠️  $reason"
        fi
        ((i++))
    done
    
    echo -e "${GRAY}────────────────────────────────────────────────────────────────────${NC}"
}

# Main interactive loop with rich UI
main() {
    clear
    echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║       🚀 Interactive URL to EPUB Testing Service (Rich UI) 🚀      ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}Features:${NC}"
    echo -e "  📍 Step-by-step transparency"
    echo -e "  🎯 Confidence-based decisions"
    echo -e "  📊 Rich visual feedback"
    echo -e "  🌍 Russian bookstore support"
    echo ""
    echo -e "${YELLOW}💡 Enter 'done' when finished testing${NC}"
    echo -e "${GRAY}────────────────────────────────────────────────────────────────────${NC}"
    
    local test_count=1
    
    while true; do
        echo ""
        echo -ne "${CYAN}🔗 Enter URL (or 'done'): ${NC}"
        read -r url
        
        # Check for exit
        if [[ "$url" == "done" ]] || [[ -z "$url" ]]; then
            break
        fi
        
        # Process the URL with rich feedback
        process_url_rich "$url" "$test_count"
        ((test_count++))
    done
    
    # Display final results
    if [[ $TOTAL_TESTS -gt 0 ]]; then
        display_rich_results
        
        # Save results
        echo ""
        print_step "💾" "Saving results to: $RESULTS_FILE"
        
        {
            echo "{"
            echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
            echo "  \"total_tests\": $TOTAL_TESTS,"
            echo "  \"successful\": $SUCCESSFUL,"
            echo "  \"failed\": $FAILED,"
            echo "  \"success_rate\": $(echo "scale=2; $SUCCESSFUL * 100 / $TOTAL_TESTS" | bc),"
            echo "  \"results\": ["
            for i in "${!TEST_RESULTS[@]}"; do
                echo -n "    ${TEST_RESULTS[$i]}"
                if [[ $i -lt $((${#TEST_RESULTS[@]} - 1)) ]]; then
                    echo ","
                else
                    echo ""
                fi
            done
            echo "  ]"
            echo "}"
        } > "$RESULTS_FILE"
        
        echo ""
        echo -e "${GREEN}✨ Test session complete!${NC}"
    else
        echo ""
        echo -e "${YELLOW}👋 No tests performed${NC}"
    fi
    
    echo ""
    echo -e "${GRAY}────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${CYAN}Thank you for using the Interactive URL Testing Service!${NC}"
}

# Run main function
main