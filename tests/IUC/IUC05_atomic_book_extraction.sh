#!/bin/bash

# IUC05_atomic_book_extraction: Atomic book title/author extraction with structured JSON output
# Purpose: Extract random book metadata from various Russian bookstores using Claude AI
# Output: Structured JSON for pipeline usage
# Version: 2.0.0 - Simplified atomic version

set -euo pipefail

# Test configuration
TEST_NAME="IUC05_atomic_book_extraction"
TEST_DESCRIPTION="Atomic book title/author extraction with structured JSON output"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# JSON Schema for output
JSON_SCHEMA='{
  "type": "object",
  "required": ["status", "timestamp", "source", "extraction"],
  "properties": {
    "status": {"type": "string", "enum": ["success", "failed"]},
    "timestamp": {"type": "string"},
    "source": {
      "type": "object",
      "required": ["url", "store_type"],
      "properties": {
        "url": {"type": "string"},
        "store_type": {"type": "string"},
        "domain": {"type": "string"}
      }
    },
    "extraction": {
      "type": "object",
      "required": ["title", "author", "confidence"],
      "properties": {
        "title": {"type": "string"},
        "author": {"type": "string"},
        "year": {"type": ["string", "number", "null"]},
        "publisher": {"type": ["string", "null"]},
        "isbn": {"type": ["string", "null"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "attempts": {"type": "number"},
        "duration_seconds": {"type": "number"},
        "claude_version": {"type": "string"}
      }
    }
  }
}'

# Diverse Russian bookstore pool for randomness
RUSSIAN_BOOKSTORES=(
    # Academic & Science
    "https://alpinabook.ru/catalog/book-nezapadnaya-istoriya-nauki/"
    "https://alpinabook.ru/catalog/book-pishi-sokrashchay-2025/"
    
    # Major Publishers
    "https://eksmo.ru/book/k-sebe-nezhno-ITD1083100/"
    "https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"
    
    # Independent Bookstores
    "https://www.podpisnie.ru/"
    "https://www.slowbooks.ru/"
    
    # Cultural & Art
    "https://admarginem.ru/"
    "https://shop.garagemca.org/"
    
    # Digital Platforms
    "https://www.litres.ru"
    "https://mybook.ru"
    
    # Major Retailers
    "https://www.labirint.ru"
    "https://chitai-gorod.ru"
)

# Store type detection for optimized extraction
detect_store_type() {
    local url="$1"
    case "$url" in
        *alpinabook*) echo "academic" ;;
        *eksmo*) echo "publisher" ;;
        *labirint*|*chitai-gorod*) echo "commercial" ;;
        *litres*|*mybook*) echo "digital" ;;
        *podpisnie*|*slowbooks*|*admarginem*|*garagemca*) echo "independent" ;;
        *) echo "general" ;;
    esac
}

# Get extraction prompt optimized for store type
get_extraction_prompt() {
    local store_type="$1"
    local base_prompt="Use WebFetch to visit this URL and extract Russian book metadata. Look for book title and author in original Russian language. Return ONLY valid JSON with exact fields: title, author, year, publisher, isbn, confidence. Set confidence: 0.9 for complete data, 0.8 for good data, 0.6 for partial data, 0.3 for minimal data."
    
    case "$store_type" in
        "academic")
            echo "$base_prompt Focus on academic/science book metadata in page title, breadcrumbs, and product details."
            ;;
        "publisher")  
            echo "$base_prompt Focus on publisher's book information, publication details, and author bio sections."
            ;;
        "commercial"|"digital")
            echo "$base_prompt Look in product pages, meta tags, structured data, and catalog information."
            ;;
        "independent")
            echo "$base_prompt Look for curated book information in page content and editorial descriptions."
            ;;
        *)
            echo "$base_prompt Search throughout the page for any book-related information."
            ;;
    esac
}

# Select random bookstore with weighted selection for variety
select_random_bookstore() {
    local count=${#RUSSIAN_BOOKSTORES[@]}
    local random_index=$((RANDOM % count))
    echo "${RUSSIAN_BOOKSTORES[$random_index]}"
}

# Extract book metadata using Claude
extract_book_metadata() {
    local url="$1"
    local store_type="$2"
    local attempt_num="$3"
    
    local prompt=$(get_extraction_prompt "$store_type")
    local full_prompt="$prompt Visit this URL: $url"
    
    echo "🤖 Extraction attempt $attempt_num from $store_type store" >&2
    echo "🔗 URL: $url" >&2
    
    # Extract using Claude
    local claude_result
    if claude_result=$(timeout 45 claude -p "$full_prompt" --allowedTools "WebFetch" --output-format json 2>/dev/null); then
        echo "📥 Raw Claude result: $claude_result" >&2
        
        # Parse Claude response
        local book_data="$claude_result"
        
        # Handle Claude response format - extract from .result field
        if echo "$claude_result" | jq -e '.result' >/dev/null 2>&1; then
            book_data=$(echo "$claude_result" | jq -r '.result' 2>/dev/null)
            echo "📋 Extracted .result: $book_data" >&2
        fi
        
        # Extract from markdown code blocks if present
        if echo "$book_data" | grep -q '```json'; then
            book_data=$(echo "$book_data" | sed -n '/```json/,/```/p' | sed '1d;$d')
            echo "📋 Extracted from markdown: $book_data" >&2
        fi
        
        # Handle array responses
        if echo "$book_data" | jq -e 'type == "array"' >/dev/null 2>&1; then
            book_data=$(echo "$book_data" | jq -r '.[0]' 2>/dev/null)
            echo "📋 Extracted from array: $book_data" >&2
        fi
        
        # Validate that we have valid JSON
        if echo "$book_data" | jq . >/dev/null 2>&1; then
            echo "$book_data"
            return 0
        else
            echo "❌ Failed to parse valid JSON from Claude response" >&2
            echo "❌ Final book_data: $book_data" >&2
            return 1
        fi
    else
        echo "❌ Claude extraction failed or timed out" >&2
        return 1
    fi
}

# Validate extracted metadata
validate_extraction() {
    local json_data="$1"
    
    # Check if valid JSON
    if ! echo "$json_data" | jq . >/dev/null 2>&1; then
        echo "❌ Invalid JSON format" >&2
        return 1
    fi
    
    # Extract fields
    local title=$(echo "$json_data" | jq -r '.title // empty' 2>/dev/null)
    local author=$(echo "$json_data" | jq -r '.author // empty' 2>/dev/null)
    local confidence=$(echo "$json_data" | jq -r '.confidence // 0' 2>/dev/null)
    
    # Validate required fields
    if [[ -z "$title" || "$title" == "null" ]]; then
        echo "❌ Missing or invalid title" >&2
        return 1
    fi
    
    if [[ -z "$author" || "$author" == "null" ]]; then
        echo "❌ Missing or invalid author" >&2
        return 1
    fi
    
    # Validate confidence (basic check for 0.0 to 1.0 range)
    if ! echo "$confidence" | grep -qE '^0\.[0-9]+$|^1\.0*$'; then
        echo "❌ Invalid confidence score: $confidence" >&2
        return 1
    fi
    
    echo "✅ Validation passed: '$title' by '$author' (confidence: $confidence)" >&2
    return 0
}

# Generate daily tracking entry
log_to_tracking() {
    local result_json="$1"
    local tracking_file="extracted_books_$(date '+%Y-%m-%d').json"
    
    # Create tracking file if doesn't exist
    if [[ ! -f "$tracking_file" ]]; then
        echo "[]" > "$tracking_file"
    fi
    
    # Add entry to tracking
    if command -v jq >/dev/null 2>&1; then
        local temp_file=$(mktemp)
        jq --argjson entry "$result_json" '. += [$entry]' "$tracking_file" > "$temp_file" && mv "$temp_file" "$tracking_file"
        echo "📝 Logged to tracking: $tracking_file" >&2
    fi
}

# Main atomic extraction function
run_atomic_extraction() {
    local start_time=$(date +%s)
    local timestamp=$(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')
    
    echo "🚀 Starting atomic book extraction..." >&2
    echo "⏰ Time: $timestamp" >&2
    
    # Select random bookstore
    local selected_url=$(select_random_bookstore)
    local store_type=$(detect_store_type "$selected_url")
    local domain=$(echo "$selected_url" | sed 's|https\?://||' | cut -d'/' -f1)
    
    echo "🏪 Selected: $selected_url ($store_type)" >&2
    
    # Attempt extraction (max 3 tries)
    local max_attempts=3
    local attempt=1
    local extraction_success=false
    local book_data=""
    
    while [[ $attempt -le $max_attempts && "$extraction_success" == "false" ]]; do
        if book_data=$(extract_book_metadata "$selected_url" "$store_type" "$attempt"); then
            if validate_extraction "$book_data"; then
                extraction_success=true
                break
            fi
        fi
        ((attempt++))
        
        # Switch to different URL if multiple attempts fail
        if [[ $attempt -le $max_attempts ]]; then
            selected_url=$(select_random_bookstore)
            store_type=$(detect_store_type "$selected_url")
            domain=$(echo "$selected_url" | sed 's|https\?://||' | cut -d'/' -f1)
            echo "🔄 Switching to: $selected_url" >&2
        fi
    done
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Generate structured output
    if [[ "$extraction_success" == "true" ]]; then
        # Parse extracted data safely
        local title=$(echo "$book_data" | jq -r '.title')
        local author=$(echo "$book_data" | jq -r '.author')
        local year=$(echo "$book_data" | jq '.year // null')
        local publisher=$(echo "$book_data" | jq '.publisher // null')
        local isbn=$(echo "$book_data" | jq '.isbn // null')
        local confidence=$(echo "$book_data" | jq -r '.confidence')
        
        # Build success result using proper jq construction
        local result_json=$(echo "$book_data" | jq --arg status "success" \
            --arg timestamp "$timestamp" \
            --arg url "$selected_url" \
            --arg store_type "$store_type" \
            --arg domain "$domain" \
            --argjson attempts "$attempt" \
            --argjson duration "$duration" \
            --arg claude_version "claude-opus-4-1" \
            '{
                status: $status,
                timestamp: $timestamp,
                source: {
                    url: $url,
                    store_type: $store_type,
                    domain: $domain
                },
                extraction: {
                    title: .title,
                    author: .author,
                    year: .year,
                    publisher: .publisher,
                    isbn: .isbn,
                    confidence: .confidence
                },
                metadata: {
                    attempts: $attempts,
                    duration_seconds: $duration,
                    claude_version: $claude_version
                }
            }')
        
        echo "✅ Success: '$title' by '$author'" >&2
        log_to_tracking "$result_json"
        echo "$result_json"
        return 0
    else
        # Build failure result
        local result_json=$(jq -n \
            --arg status "failed" \
            --arg timestamp "$timestamp" \
            --arg url "$selected_url" \
            --arg store_type "$store_type" \
            --arg domain "$domain" \
            --argjson attempts "$attempt" \
            --argjson duration "$duration" \
            --arg claude_version "claude-opus-4-1" \
            '{
                status: $status,
                timestamp: $timestamp,
                source: {
                    url: $url,
                    store_type: $store_type,
                    domain: $domain
                },
                extraction: {
                    title: "",
                    author: "",
                    year: null,
                    publisher: null,
                    isbn: null,
                    confidence: 0
                },
                metadata: {
                    attempts: $attempts,
                    duration_seconds: $duration,
                    claude_version: $claude_version
                }
            }')
        
        echo "❌ Failed to extract valid book metadata after $attempt attempts" >&2
        echo "$result_json"
        return 1
    fi
}

# Help function
show_help() {
    cat << 'EOF'
🎯 IUC05_atomic_book_extraction: Atomic book title/author extraction

PURPOSE:
========
Extract random book metadata from Russian bookstores using Claude AI.
Produces structured JSON output for pipeline usage.

USAGE:
======
./IUC05_atomic_book_extraction.sh                    # Run extraction
./IUC05_atomic_book_extraction.sh --help             # Show help
./IUC05_atomic_book_extraction.sh --schema           # Show JSON schema

ATOMIC PRINCIPLE:
=================
- ONE function: Book title/author extraction
- ONE output: Structured JSON
- ONE source: Random Russian bookstore  
- REUSABLE: Output can be used in other test pipelines

OUTPUT FORMAT:
==============
{
  "status": "success|failed",
  "timestamp": "2024-08-14 15:30:45 MSK",
  "source": {
    "url": "https://eksmo.ru/book/...",
    "store_type": "publisher",
    "domain": "eksmo.ru"
  },
  "extraction": {
    "title": "К себе нежно",
    "author": "Ольга Примаченко",
    "year": 2020,
    "publisher": "БОМБОРА",
    "isbn": "978-5-04-117369-2",
    "confidence": 0.9
  },
  "metadata": {
    "attempts": 1,
    "duration_seconds": 12,
    "claude_version": "claude-opus-4-1"
  }
}

RANDOMNESS:
===========
- 12 diverse Russian bookstores
- Academic, publisher, commercial, digital, independent stores
- Random selection with automatic fallback
- Different books each run for test variety

TRACKING:
=========
- Daily deduplication via extracted_books_YYYY-MM-DD.json
- Success rate monitoring
- Performance metrics collection

VERSION: 2.0.0 - Atomic
EOF
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --schema)
        echo "JSON Schema for output:"
        echo "$JSON_SCHEMA" | jq .
        exit 0
        ;;
    *)
        # Run atomic extraction
        if ! command -v claude >/dev/null 2>&1; then
            echo '{"status":"failed","error":"Claude command not found","timestamp":"'$(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')'"}' >&2
            exit 1
        fi
        
        if ! command -v jq >/dev/null 2>&1; then
            echo '{"status":"failed","error":"jq command not found","timestamp":"'$(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')'"}' >&2
            exit 1
        fi
        
        # Execute atomic extraction
        run_atomic_extraction
        ;;
esac