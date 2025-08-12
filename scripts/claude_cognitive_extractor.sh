#!/bin/bash
# Claude Cognitive Extraction Layer
# MANDATORY for all book URL parsing - provides accurate title/author extraction

set -euo pipefail

URL="${1:-}"
if [[ -z "$URL" ]]; then
    echo '{"error": "no_url", "message": "URL required"}'
    exit 1
fi

# This script MUST be called by Claude with WebFetch capability
# It signals the requirement for cognitive extraction

cat << EOF
{
  "status": "cognitive_extraction_required",
  "instruction": "Use WebFetch to extract book metadata",
  "url": "$URL",
  "prompt": "Extract from this book page: 1) Book title in original language 2) Author full name in original language 3) ISBN if present 4) Publisher 5) Publication year. Return ONLY a JSON object with keys: title, author, isbn, publisher, year. If author is not found, set to null.",
  "mandatory": true,
  "reason": "Only Claude cognitive layer can accurately extract book metadata from diverse websites and languages"
}
EOF