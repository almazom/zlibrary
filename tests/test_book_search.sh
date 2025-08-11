#!/bin/bash
# BDD Test Suite for Book Search API
# UC1: Book Search and Download

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local query="$2"
    local expected_found="$3"
    local check_file="$4"
    
    echo -e "\n📚 Testing: $test_name"
    echo "   Query: '$query'"
    
    # Run search
    local result=$(../scripts/book_search.sh "$query" 2>/dev/null || echo '{"status":"error"}')
    
    # Check if found matches expectation
    local found=$(echo "$result" | jq -r '.result.found' 2>/dev/null || echo "error")
    
    if [[ "$found" == "$expected_found" ]]; then
        echo -e "   ${GREEN}✅ Found status: $found (expected: $expected_found)${NC}"
        
        # If we expect to find it and need to check file
        if [[ "$expected_found" == "true" ]] && [[ "$check_file" == "true" ]]; then
            local file_path=$(echo "$result" | jq -r '.result.epub_download_url' 2>/dev/null || echo "")
            if [[ -f "$file_path" ]]; then
                local file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null || echo "0")
                if [[ $file_size -gt 10000 ]]; then
                    echo -e "   ${GREEN}✅ File downloaded: $(basename "$file_path") ($(numfmt --to=iec-i --suffix=B $file_size))${NC}"
                    
                    # Check confidence scores
                    local confidence=$(echo "$result" | jq -r '.result.confidence.level' 2>/dev/null || echo "")
                    local readability=$(echo "$result" | jq -r '.result.readability.level' 2>/dev/null || echo "")
                    echo -e "   ${GREEN}✅ Confidence: $confidence, Readability: $readability${NC}"
                    ((PASSED++))
                else
                    echo -e "   ${RED}❌ File too small: $file_size bytes${NC}"
                    ((FAILED++))
                fi
            else
                echo -e "   ${RED}❌ File not found at: $file_path${NC}"
                ((FAILED++))
            fi
        else
            ((PASSED++))
        fi
    else
        echo -e "   ${RED}❌ Found status: $found (expected: $expected_found)${NC}"
        echo "   Response: $(echo "$result" | jq -c '.' 2>/dev/null || echo "$result")"
        ((FAILED++))
    fi
}

echo "========================================="
echo "    Z-Library Book Search BDD Tests     "
echo "========================================="

# Scenario 1: Successful downloads
echo -e "\n${YELLOW}SCENARIO 1: Successful Book Downloads${NC}"
run_test "Popular Programming Book" "Clean Code Robert Martin" "true" "true"
run_test "Classic Literature" "1984 George Orwell" "true" "true"
run_test "Modern Self-Help" "Atomic Habits James Clear" "true" "true"

# Scenario 2: Books not found
echo -e "\n${YELLOW}SCENARIO 2: Non-Existent Books${NC}"
run_test "Gibberish Title" "xyzabc123 nonexistent fake book" "false" "false"
run_test "Random Characters" "qwerty99999 imaginary programming" "false" "false"

# Scenario 3: Partial matches
echo -e "\n${YELLOW}SCENARIO 3: Partial Match Tests${NC}"
run_test "Single Word Query" "Python" "true" "true"
run_test "Author Only" "Stephen King" "true" "true"

# Scenario 4: Edge cases
echo -e "\n${YELLOW}SCENARIO 4: Edge Cases${NC}"
run_test "Special Characters" "C++ Programming" "true" "true"
run_test "Numbers in Title" "1984" "true" "true"

# Scenario 5: Russian books
echo -e "\n${YELLOW}SCENARIO 5: Russian Books${NC}"
run_test "Russian Classic" "Война и мир Толстой" "true" "true"
run_test "Russian Modern" "Мастер и Маргарита Булгаков" "true" "true"
run_test "Russian Crime" "Преступление и наказание Достоевский" "true" "true"
run_test "Russian Poetry" "Евгений Онегин Пушкин" "true" "true"

# Scenario 6: URL inputs
echo -e "\n${YELLOW}SCENARIO 6: URL Input Support${NC}"
run_test "Podpisnie URL" "https://www.podpisnie.ru/books/maniac/" "true" "true"

# Summary
echo -e "\n========================================="
echo -e "              TEST SUMMARY               "
echo -e "========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [[ $FAILED -eq 0 ]]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  SOME TESTS FAILED${NC}"
    exit 1
fi