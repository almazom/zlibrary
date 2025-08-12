#!/bin/bash

# Full batch URL testing with all prepared URLs
set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTERACTIVE_TEST="$SCRIPT_DIR/interactive_url_test.sh"

# Test URLs with focus on Russian bookstores
URLS=(
    # Russian bookstores
    "https://www.podpisnie.ru/books/maniac/"
    "https://www.podpisnie.ru/books/misticheskiy-mir-novalisa/"
    "https://alpinabook.ru/catalog/book-atomnye-privychki/"
    # International
    "https://www.goodreads.com/book/show/3735293-clean-code"
    "https://www.goodreads.com/book/show/11084145-steve-jobs"
    # Technical books
    "https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882"
    "https://www.amazon.com/Pragmatic-Programmer-journey-mastery-Anniversary/dp/0135957052"
)

echo -e "${BLUE}Starting full batch URL testing...${NC}"
echo -e "${BLUE}Testing ${#URLS[@]} URLs with Russian focus${NC}\n"

# Create input for interactive test
{
    for url in "${URLS[@]}"; do
        echo "$url"
        sleep 0.5  # Small delay between URLs
    done
    echo "done"
} | "$INTERACTIVE_TEST"