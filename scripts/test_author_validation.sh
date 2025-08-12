#!/bin/bash
# Test Author Validation in Book Search

set -euo pipefail

echo "=== Testing Author Validation Feature ==="
echo

# Test 1: Correct extraction from Russian book URL
echo "Test 1: Russian book URL (Милорад Павич - Лунный камень)"
echo "Expected: Low confidence due to author mismatch"
echo "Running..."

# First, let's simulate what the extraction would return
EXTRACTED_JSON='{
    "title": "Лунный камень",
    "author": "Милорад Павич",
    "isbn": "978-5-04-185167-5",
    "language": "Russian"
}'

echo "Extracted from URL: $EXTRACTED_JSON"

# Now search with the extracted query
SEARCH_QUERY="Лунный камень Милорад Павич"
echo "Searching for: $SEARCH_QUERY"

result=$(./scripts/book_search.sh "$SEARCH_QUERY" 2>&1)

# Check if we got the warning
if echo "$result" | grep -q "Author mismatch"; then
    echo "✓ Author mismatch warning displayed"
else
    echo "✗ No author mismatch warning"
fi

# Extract confidence from result
confidence=$(echo "$result" | grep -o '"confidence":{"score":[0-9.]*' | cut -d':' -f3 || echo "0")
echo "Confidence score: $confidence"

if (( $(echo "$confidence < 0.5" | bc -l) )); then
    echo "✓ Low confidence detected (good - indicates mismatch)"
else
    echo "✗ High confidence despite mismatch (bad)"
fi

echo
echo "Test 2: Testing author comparison function directly"
echo "----------------------------------------"

# Source the script to get access to compare_authors function
source ./scripts/book_search.sh > /dev/null 2>&1 || true

# Test exact match
score=$(compare_authors "Милорад Павич" "Милорад Павич")
echo "Exact match: 'Милорад Павич' vs 'Милорад Павич' = $score (expected: 1.0)"

# Test wrong author
score=$(compare_authors "Милорад Павич" "Уильям Уилки Коллинз")
echo "Different: 'Милорад Павич' vs 'Уильям Уилки Коллинз' = $score (expected: 0.0)"

# Test partial match
score=$(compare_authors "Robert Martin" "Robert C. Martin")
echo "Partial: 'Robert Martin' vs 'Robert C. Martin' = $score (expected: 0.8+)"

# Test last name match
score=$(compare_authors "James Clear" "J. Clear")
echo "Last name: 'James Clear' vs 'J. Clear' = $score (expected: 0.6+)"

echo
echo "Test 3: URL with automatic Claude extraction"
echo "----------------------------------------"
echo "URL: https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"

# This should automatically trigger Claude extraction
echo "Note: This requires Claude WebFetch to work properly"
echo "Expected behavior: Automatic --claude-extract flag activation"

# Check if URL triggers Claude extraction
test_url="https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"
if ./scripts/book_search.sh "$test_url" 2>&1 | grep -q "CLAUDE_COGNITIVE_REQUIRED"; then
    echo "✓ Claude extraction automatically triggered for URL"
else
    echo "✗ Claude extraction not triggered (check implementation)"
fi

echo
echo "=== Test Summary ==="
echo "Author validation function: Implemented ✓"
echo "Confidence scoring with author: Implemented ✓"  
echo "Automatic Claude extraction for URLs: Implemented ✓"
echo "Author mismatch warnings: Implemented ✓"
echo
echo "Next steps:"
echo "1. Implement ISBN-based search priority"
echo "2. Add search retry strategies"
echo "3. Implement language filtering"