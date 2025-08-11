#!/bin/bash

# Test script for complete URL → EPUB pipeline
# Shows how book_search.sh works as a complete solution

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}URL → EPUB Pipeline Test${NC}"
echo -e "${BLUE}================================${NC}\n"

# Test URLs
URLs=(
    "https://www.shakespeareandcompany.com/books/the-hunchback-of-notre-dame-special-edition"
    "https://www.goodreads.com/book/show/6483624"
    "https://www.podpisnie.ru/books/maniac/"
)

echo -e "${YELLOW}Testing URL extraction and download pipeline:${NC}\n"

for url in "${URLs[@]}"; do
    echo -e "${GREEN}Testing URL:${NC} $url"
    echo "---"
    
    # Run the book search (which automatically downloads for URLs)
    result=$(./scripts/book_search.sh "$url" 2>/dev/null || echo '{"status": "error"}')
    
    # Parse result
    status=$(echo "$result" | jq -r '.status')
    query=$(echo "$result" | jq -r '.query_info.extracted_query // "N/A"')
    
    if [[ "$status" == "success" ]]; then
        title=$(echo "$result" | jq -r '.result.book_info.title // "N/A"')
        epub_path=$(echo "$result" | jq -r '.result.epub_download_url // "N/A"')
        confidence=$(echo "$result" | jq -r '.result.confidence.score // 0')
        
        echo -e "  ${GREEN}✓ SUCCESS${NC}"
        echo "  Extracted Query: $query"
        echo "  Found Book: $title"
        echo "  Confidence: $confidence"
        echo "  EPUB Location: $epub_path"
        
        # Check if file exists
        if [[ -f "$epub_path" ]]; then
            size=$(ls -lh "$epub_path" | awk '{print $5}')
            echo -e "  ${GREEN}✓ EPUB Downloaded${NC} (Size: $size)"
        fi
    else
        error=$(echo "$result" | jq -r '.result.message // "Unknown error"')
        echo -e "  Status: $status"
        echo "  Extracted Query: $query"
        echo "  Error: $error"
    fi
    
    echo ""
done

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "The pipeline automatically:"
echo "1. Detects URL input"
echo "2. Extracts book information from ANY book URL"
echo "3. Searches Z-Library for the book"
echo "4. Downloads the EPUB automatically"
echo "5. Returns structured JSON with all details"
echo ""
echo -e "${GREEN}Usage:${NC}"
echo "  ./scripts/book_search.sh <URL>        # Automatic extraction + download"
echo "  ./scripts/book_search.sh \"book title\" # Direct search"
echo ""
echo "Downloaded EPUBs are in: ./downloads/"