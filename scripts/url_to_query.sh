#!/bin/bash
# KISS: Simple URL to search query converter
# DRY: One method for ALL URLs - use Claude's intelligence

URL="$1"

if [[ -z "$URL" ]]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

# The RIGHT way - let Claude figure it out for ANY URL
# No hardcoding, no patterns, just intelligence

cat << EOF
=====================================
To extract book info from ANY URL:
=====================================

In Claude Code:
  WebFetch("$URL", "Extract book title and author as search query")

With Claude SDK:
  client.messages.create(
    model="claude-3-opus",
    messages=[{
      "role": "user", 
      "content": "Extract book from $URL. Return search query."
    }]
  )

Result: Claude intelligently extracts the book info
        No hardcoding needed!
=====================================

For testing, you can use:
  ./scripts/book_search.sh "Пиши сокращай Ильяхов"
  ./scripts/book_search.sh "Atomic Habits James Clear"
  ./scripts/book_search.sh "Clean Code Robert Martin"
EOF