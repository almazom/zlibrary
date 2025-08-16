#!/bin/bash
# Claude Integrated Book Search - Demonstrates proper URL extraction flow

set -euo pipefail

URL="${1:-}"
if [[ -z "$URL" ]]; then
    echo "Usage: $0 <book-url>"
    exit 1
fi

echo "Step 1: Extracting book information from URL using Claude WebFetch..."

# THIS IS THE INTEGRATION POINT
# When running this script, Claude will see this marker and perform WebFetch
echo "[CLAUDE_PERFORM_WEBFETCH]"
echo "URL: $URL"
echo "SCHEMA: {title: string, author: string, year: number, publisher: string, isbn: string}"

# In production, Claude provides the result here
# For testing, we'll check if result was provided via environment
if [[ -n "${CLAUDE_EXTRACTION_RESULT:-}" ]]; then
    EXTRACTED_JSON="$CLAUDE_EXTRACTION_RESULT"
else
    # Placeholder for when WebFetch hasn't been performed
    EXTRACTED_JSON='{}'
fi

echo "Extracted: $EXTRACTED_JSON"

# Extract title and author for search
TITLE=$(echo "$EXTRACTED_JSON" | jq -r '.title // empty')
AUTHOR=$(echo "$EXTRACTED_JSON" | jq -r '.author // empty')

if [[ -n "$TITLE" ]] && [[ -n "$AUTHOR" ]]; then
    SEARCH_QUERY="$TITLE $AUTHOR"
    echo "Step 2: Searching for: $SEARCH_QUERY"
    
    # Execute the actual search
    ./scripts/book_search.sh "$SEARCH_QUERY"
else
    echo "Error: Could not extract book information from URL"
    exit 1
fi