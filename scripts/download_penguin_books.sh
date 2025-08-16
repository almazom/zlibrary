#!/bin/bash

# Download Penguin Classics one by one
set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# List of Penguin classics to download
BOOKS=(
    "1984 George Orwell"
    "Animal Farm George Orwell"
    "Pride and Prejudice Jane Austen"
    "Wuthering Heights Emily Bronte"
    "Jane Eyre Charlotte Bronte"
    "Great Expectations Charles Dickens"
    "To Kill a Mockingbird Harper Lee"
    "The Great Gatsby F Scott Fitzgerald"
    "Lord of the Flies William Golding"
    "Of Mice and Men John Steinbeck"
)

OUTPUT_DIR="./penguin_downloads"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}Starting Penguin Classics Download${NC}"
echo "=================================="
echo

# Check limits first
echo -e "${YELLOW}Checking download limits...${NC}"
./scripts/zlib_book_search.sh --limits

echo
echo -e "${BLUE}Downloading books one by one...${NC}"
echo "=================================="

SUCCESS_COUNT=0
FAIL_COUNT=0

for BOOK in "${BOOKS[@]}"; do
    echo
    echo -e "${YELLOW}Book: $BOOK${NC}"
    echo "-----------------------------------"
    
    # Search for the book first
    echo -e "${BLUE}Searching...${NC}"
    ./scripts/zlib_book_search.sh "$BOOK"
    
    # Wait a bit between operations
    sleep 2
    
    # Download the book
    echo -e "${BLUE}Downloading...${NC}"
    if ./scripts/zlib_book_search.sh --download -o "$OUTPUT_DIR" "$BOOK"; then
        echo -e "${GREEN}✅ Successfully downloaded: $BOOK${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}❌ Failed to download: $BOOK${NC}"
        ((FAIL_COUNT++))
    fi
    
    # Wait between downloads to avoid rate limiting
    echo -e "${YELLOW}Waiting 3 seconds before next book...${NC}"
    sleep 3
done

echo
echo "=================================="
echo -e "${BLUE}Download Summary${NC}"
echo "=================================="
echo -e "${GREEN}Successful downloads: $SUCCESS_COUNT${NC}"
echo -e "${RED}Failed downloads: $FAIL_COUNT${NC}"
echo -e "${BLUE}Files saved in: $OUTPUT_DIR${NC}"

# List downloaded files
echo
echo -e "${BLUE}Downloaded files:${NC}"
ls -la "$OUTPUT_DIR"