#!/bin/bash
# Claude Cognitive Wrapper - MANDATORY for URL book extraction
# This script demonstrates how to use Claude's WebFetch for accurate extraction

set -euo pipefail

URL="${1:-}"
if [[ -z "$URL" ]]; then
    echo '{"error": "no_url", "message": "URL required"}'
    exit 1
fi

# Load extraction prompts
PROMPTS_FILE="${SCRIPT_DIR:-$(dirname "$0")/../config}/extraction_prompts.yaml"

# Determine domain and get appropriate prompt
DOMAIN=$(echo "$URL" | sed -E 's|https?://([^/]+).*|\1|' | sed 's/www\.//')

# Get prompt for this domain
if [[ "$DOMAIN" == "eksmo.ru" ]]; then
    PROMPT="This is a URL to a page with a book. Extract the following information:
- title: Book title EXACTLY as written on the page in its ORIGINAL LANGUAGE (Russian/English/etc)
- author: Author's FULL NAME exactly as written on the page in its ORIGINAL LANGUAGE
- year: publication year if available
- isbn: ISBN if available
- publisher: publisher name
- language: the language the book is written in

CRITICAL: Keep title and author in the EXACT language shown on the page!
Return ONLY a JSON object. Example: {\"title\": \"Лунный камень\", \"author\": \"Милорад Павич\"}"
else
    # Generic prompt for other domains
    PROMPT="This is a URL to a page with a book. Extract book title and author EXACTLY as written on the page:
- title: Book title in the ORIGINAL LANGUAGE it appears on the page
- author: Author name in the ORIGINAL LANGUAGE it appears on the page
- year: publication year if available
- isbn: ISBN if available
- language: detected language of the book

IMPORTANT: Preserve the exact language and spelling from the page!
Return ONLY a JSON object with available fields. No additional text."
fi

# This is where Claude's WebFetch would be called
# In the actual Claude environment, this would be:
# claude_result=$(claude webfetch "$URL" "$PROMPT")

# For now, output the instruction for Claude to execute
cat << EOF
{
  "claude_action": "webfetch",
  "url": "$URL",
  "prompt": $(echo "$PROMPT" | jq -Rs .),
  "instruction": "Execute WebFetch with this URL and prompt to extract book information"
}
EOF