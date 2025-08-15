#!/bin/bash
# SIUC-001: Atomic Book Search Test

# --- Test Configuration ---
SEARCH_QUERY="1984 George Orwell"
BOOK_SEARCH_SCRIPT="/home/almaz/microservices/zlibrary_api_module/scripts/book_search.sh"

# --- Execution ---
echo "Executing SIUC-001: Atomic Book Search for query: '$SEARCH_QUERY'"
output=$($BOOK_SEARCH_SCRIPT "$SEARCH_QUERY")
exit_code=$?

# --- Verification ---
if [ $exit_code -ne 0 ]; then
    echo "FAIL: book_search.sh exited with non-zero status: $exit_code"
    exit 1
fi

status=$(echo "$output" | jq -r '.status')
found=$(echo "$output" | jq -r '.result.found')

if [ "$status" != "success" ] || [ "$found" != "true" ]; then
    echo "FAIL: Unexpected response."
    echo "Expected: status=success, found=true"
    echo "Got:      status=$status, found=$found"
    echo "Full output: $output"
    exit 1
fi

echo "PASS: Successfully found book."
exit 0
