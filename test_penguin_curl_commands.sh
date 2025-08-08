#!/bin/bash
# Penguin 2025 Best Books - Raw cURL API Testing
# Tests Z-Library microservice with curl commands for each book

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if credentials are set
if [[ -z "$ZLOGIN" || -z "$ZPASSW" ]]; then
    echo -e "${RED}❌ Error: ZLOGIN and ZPASSW environment variables must be set${NC}"
    echo "Example: export ZLOGIN='your-email@example.com'"
    echo "         export ZPASSW='your-password'"
    exit 1
fi

echo -e "${BLUE}🚀 Penguin 2025 Best Books - cURL API Test${NC}"
echo -e "${BLUE}============================================${NC}"

# Book list array
books=(
    "The Emperor of Gladness|Ocean Vuong"
    "Murderland|Caroline Fraser"
    "One Golden Summer|Carley Fortune"
    "Beyond Anxiety|Martha Beck"
    "We Can Do Hard Things|Glennon Doyle"
    "The Note|Alafair Burke"
    "The Stolen Queen|Fiona Davis"
    "We Do Not Part|Han Kang"
    "Dream Count|Chimamanda Ngozi Adichie"
    "Problematic Summer Romance|Ali Hazelwood"
    "All the Other Mothers Hate Me|Sarah Harman"
    "Witchcraft for Wayward Girls|Grady Hendrix"
    "Water Moon|Samantha Sotto Yambao"
    "Mask of the Deer Woman|Laurie L. Dove"
    "Theft|Abdulrazak Gurnah"
    "The Missing Half|Ashley Flowers"
    "The Listeners|Maggie Stiefvater"
    "Let's Call Her Barbie|Renée Rosen"
    "The Favorites|Layne Fargo"
    "All That Life Can Afford|Emily Everett"
    "Good Dirt|Charmaine Wilkerson"
    "One Good Thing|Georgia Hunter"
    "Great Big Beautiful Life|Emily Henry"
    "Stag Dance|Torrey Peters"
    "Dream State|Eric Puchner"
    "The Dream Hotel|Laila Lalami"
    "No More Tears|Gardiner Harris"
    "The Girls Who Grew Big|Leila Mottley"
    "Memorial Days|Geraldine Brooks"
    "Dead Money|Jakob Kerr"
    "Atmosphere|Taylor Jenkins Reid"
)

# Initialize counters
total_books=${#books[@]}
found_count=0
error_count=0

echo -e "${YELLOW}📋 Testing $total_books books from Penguin Random House 2025 Best Books${NC}"
echo

# Create results directory
mkdir -p downloads/penguin_2025_curl_results

# Function to test a single book
test_book() {
    local book_data="$1"
    local book_num="$2"
    
    # Split title and author
    IFS='|' read -r title author <<< "$book_data"
    local search_query="$title $author"
    
    echo -e "${BLUE}📚 [$book_num/$total_books] Testing: $title by $author${NC}"
    echo -e "${BLUE}🔍 Search query: $search_query${NC}"
    
    # Create result file for this book
    local result_file="downloads/penguin_2025_curl_results/book_${book_num}_result.json"
    
    # Test 1: Basic search using our shell script
    echo -e "${YELLOW}   → Running basic search...${NC}"
    
    if timeout 30 ./scripts/zlib_book_search.sh --json "$search_query" > "$result_file" 2>&1; then
        # Check if we got results
        if grep -q '"found":' "$result_file"; then
            local results_count=$(grep -o '"found": [0-9]*' "$result_file" | grep -o '[0-9]*' || echo "0")
            if [ "$results_count" -gt 0 ]; then
                echo -e "${GREEN}   ✅ Found $results_count results${NC}"
                ((found_count++))
                
                # Extract first result details
                local first_title=$(grep -o '"title": "[^"]*"' "$result_file" | head -1 | cut -d'"' -f4)
                local first_author=$(grep -o '"author": "[^"]*"' "$result_file" | head -1 | cut -d'"' -f4)
                local first_year=$(grep -o '"year": "[^"]*"' "$result_file" | head -1 | cut -d'"' -f4)
                local first_format=$(grep -o '"extension": "[^"]*"' "$result_file" | head -1 | cut -d'"' -f4)
                
                echo -e "${GREEN}   📖 Best match: $first_title${NC}"
                echo -e "${GREEN}   👤 Author: $first_author${NC}"
                echo -e "${GREEN}   📅 Year: $first_year | 📄 Format: $first_format${NC}"
            else
                echo -e "${RED}   ❌ No results found${NC}"
            fi
        else
            echo -e "${RED}   ❌ Search failed - invalid response${NC}"
            ((error_count++))
        fi
    else
        echo -e "${RED}   ❌ Search timeout or error${NC}"
        ((error_count++))
        echo "Error details:" >> "$result_file"
        echo "Search timed out or failed" >> "$result_file"
    fi
    
    # Test 2: Check download availability (if found)
    if [ "$results_count" -gt 0 ] 2>/dev/null; then
        echo -e "${YELLOW}   → Checking download availability...${NC}"
        
        # Try to get download info
        if timeout 15 ./scripts/zlib_book_search.sh --limits > /dev/null 2>&1; then
            echo -e "${GREEN}   ✅ Download system accessible${NC}"
        else
            echo -e "${YELLOW}   ⚠️  Download check failed${NC}"
        fi
    fi
    
    echo
    sleep 1  # Be respectful to the server
}

# Test all books
for i in "${!books[@]}"; do
    book_num=$((i + 1))
    test_book "${books[$i]}" "$book_num"
done

# Generate summary report
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}📊 PENGUIN 2025 BOOKS CURL TEST SUMMARY${NC}"
echo -e "${BLUE}============================================${NC}"

echo -e "${YELLOW}📚 Total books tested: $total_books${NC}"
echo -e "${GREEN}✅ Books found: $found_count${NC}"
echo -e "${RED}❌ Errors: $error_count${NC}"

if [ $total_books -gt 0 ]; then
    success_rate=$((found_count * 100 / total_books))
    echo -e "${YELLOW}📈 Success rate: $success_rate%${NC}"
fi

echo
echo -e "${BLUE}🎯 SUCCESS CRITERIA ANALYSIS:${NC}"
echo -e "${BLUE}────────────────────────────${NC}"

if [ $found_count -gt 0 ]; then
    echo -e "${GREEN}• Z-Library microservice connection: ✅ Working${NC}"
    echo -e "${GREEN}• Book search functionality: ✅ Working${NC}"
    echo -e "${GREEN}• Search result parsing: ✅ Working${NC}"
    echo -e "${GREEN}• API response handling: ✅ Working${NC}"
else
    echo -e "${RED}• Z-Library microservice: ❌ Failed${NC}"
fi

if [ $error_count -eq 0 ]; then
    echo -e "${GREEN}• Error handling: ✅ Robust${NC}"
else
    echo -e "${YELLOW}• Error handling: ⚠️  Some issues ($error_count errors)${NC}"
fi

echo
echo -e "${BLUE}📄 Individual results saved in: downloads/penguin_2025_curl_results/${NC}"

# Create summary report
summary_file="downloads/penguin_2025_curl_results/SUMMARY.txt"
{
    echo "Penguin Random House 2025 Best Books - cURL Test Summary"
    echo "========================================================"
    echo "Test Date: $(date)"
    echo "Total Books: $total_books"
    echo "Books Found: $found_count"
    echo "Errors: $error_count"
    echo "Success Rate: $success_rate%"
    echo ""
    echo "Book-by-Book Results:"
    echo "--------------------"
    
    for i in "${!books[@]}"; do
        book_num=$((i + 1))
        IFS='|' read -r title author <<< "${books[$i]}"
        result_file="downloads/penguin_2025_curl_results/book_${book_num}_result.json"
        
        if [ -f "$result_file" ]; then
            if grep -q '"found": [1-9]' "$result_file" 2>/dev/null; then
                echo "$book_num. ✅ $title by $author"
            else
                echo "$book_num. ❌ $title by $author"
            fi
        else
            echo "$book_num. ❌ $title by $author (no result file)"
        fi
    done
} > "$summary_file"

echo -e "${GREEN}📄 Summary report saved to: $summary_file${NC}"

# Final result
if [ $found_count -gt $((total_books / 2)) ]; then
    echo -e "${GREEN}🎉 Test PASSED: Z-Library microservice is working well!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Test PARTIAL: Some issues found, check individual results${NC}"
    exit 1
fi