#!/bin/bash

# =============================================================================
# Enhanced Z-Library Book Search Service
# Supports URL, TXT, and IMAGE inputs with confidence scoring
# Always returns standardized JSON schema
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Script info
SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Defaults
OUTPUT_DIR="./downloads"
FORMAT="epub"
COUNT="1"
JSON_OUTPUT="true"  # Always JSON by default now
DOWNLOAD="false"
QUERY=""
ENV_FILE="$PROJECT_ROOT/.env"
SERVICE_MODE="true"  # Always service mode
INPUT_FORMAT=""  # Will be detected: url, txt, image
CONFIDENCE_ENABLED="true"
MIN_CONFIDENCE="0.4"  # Default minimum confidence
MIN_QUALITY="ANY"     # Default minimum quality (ANY, FAIR, GOOD, EXCELLENT)
CLAUDE_EXTRACT="false"  # Use Claude AI for URL extraction

# Print functions (only for non-service mode)
print_error() { [[ "$SERVICE_MODE" != "true" ]] && echo -e "${RED}❌ ERROR: $*${NC}" >&2; }
print_success() { [[ "$SERVICE_MODE" != "true" ]] && echo -e "${GREEN}✅ $*${NC}"; }
print_info() { [[ "$SERVICE_MODE" != "true" ]] && echo -e "${BLUE}ℹ️  $*${NC}"; }

# Show help
show_help() {
    cat << 'EOF'
Enhanced Z-Library Book Search Service

USAGE:
    book_search.sh [OPTIONS] "INPUT"

OPTIONS:
    --format FORMAT       File format (epub, pdf, mobi, etc.)
    --count NUMBER        Max results (default: 1)
    --output DIR          Output directory
    --download            Download the book
    --no-confidence       Disable confidence scoring
    --min-confidence NUM  Minimum confidence score (0.0-1.0, default: 0.4)
    --min-quality LEVEL   Minimum quality (ANY|FAIR|GOOD|EXCELLENT, default: ANY)
    --strict              Use strict filtering (--min-confidence 0.8 --min-quality GOOD)
    --claude-extract      Use Claude AI to extract book info from URLs
    --help                Show this help

INPUT TYPES (auto-detected):
    URL:    https://www.podpisnie.ru/books/maniac/
    TXT:    "Harry Potter philosopher stone"
    IMAGE:  /path/to/book/cover.jpg (future)

OUTPUT:
    Always returns standardized JSON with:
    - status: success/not_found/error
    - input_format: url/txt/image
    - confidence scoring
    - book metadata
    - service attribution

EXAMPLES:
    # Search by URL
    ./scripts/book_search.sh "https://www.podpisnie.ru/books/maniac/"
    
    # Search by text  
    ./scripts/book_search.sh "Clean Code Robert Martin"
    
    # Download with confidence check
    ./scripts/book_search.sh --download "Harry Potter philosopher stone"

EOF
}

# Detect input format
detect_input_format() {
    local input="$1"
    
    # Check if it's a URL (including www.)
    if [[ "$input" =~ ^https?:// ]] || [[ "$input" =~ ^www\. ]]; then
        echo "url"
    # Check if it's an image file path
    elif [[ "$input" =~ \.(jpg|jpeg|png|gif|webp)$ ]]; then
        echo "image"
    # Default to text
    else
        echo "txt"
    fi
}

# Extract query from URL - enhanced with Claude extraction
extract_query_from_url() {
    local url="$1"
    local query=""
    
    # For ANY URL, try to extract book information
    # This now works with ALL URLs, not just specific domains
    if [[ "$url" =~ ^https?:// ]]; then
        # Only print info in non-service mode
        [[ "$SERVICE_MODE" != "true" ]] && echo "Extracting book information from URL..." >&2
        
        # Try different extractors in order of preference
        local extractor_scripts=(
            "$SCRIPT_DIR/universal_extractor.sh"
            "$SCRIPT_DIR/claude_url_extractor.py"
            "$SCRIPT_DIR/simple_claude_extractor.py"
        )
        
        local claude_result=""
        for extractor_script in "${extractor_scripts[@]}"; do
            if [[ -f "$extractor_script" ]]; then
                if [[ "$extractor_script" == *.sh ]]; then
                    claude_result=$(bash "$extractor_script" "$url" 2>/dev/null || echo "{}")
                else
                    claude_result=$(python3 "$extractor_script" "$url" 2>/dev/null || echo "{}")
                fi
                
                # If we got a valid result, use it
                if [[ -n "$claude_result" ]] && [[ "$claude_result" != "{}" ]] && [[ "$claude_result" != *"error"* ]]; then
                    break
                fi
            fi
        done
        
        # Process extraction result
        if [[ -n "$claude_result" ]] && [[ "$claude_result" != "{}" ]]; then
            local extracted_title
            local extracted_author
            
            extracted_title=$(echo "$claude_result" | jq -r '.title // empty' 2>/dev/null || echo "")
            extracted_author=$(echo "$claude_result" | jq -r '.author // empty' 2>/dev/null || echo "")
            
            if [[ -n "$extracted_title" ]]; then
                query="$extracted_title"
                if [[ -n "$extracted_author" ]] && [[ "$extracted_author" != "null" ]]; then
                    query="$query $extracted_author"
                fi
                
                # Store full extraction result for later use
                export CLAUDE_EXTRACTION_RESULT="$claude_result"
                
                if [[ -n "$query" ]]; then
                    echo "$query"
                    return 0
                fi
            fi
        fi
    fi
    
    # Fallback to pattern-based extraction
    # Extract from podpisnie.ru URLs
    if [[ "$url" =~ podpisnie\.ru/books/([^/]+) ]]; then
        local slug="${BASH_REMATCH[1]}"
        
        # Known patterns
        if [[ "$slug" =~ misticheskiy.*novalisa ]]; then
            query="новалис мистический мир философия"
        elif [[ "$slug" == "maniac" ]]; then
            query="maniac"
        elif [[ "$slug" =~ eto-nesluchayno.*yaponskaya ]]; then
            query="это неслучайно японская хроника"
        else
            # Generic: convert dashes to spaces, take first 3 words
            query=$(echo "$slug" | sed 's/-/ /g' | awk '{print $1 " " $2 " " $3}')
        fi
    
    # Extract from Goodreads URLs (fallback if Claude fails)
    elif [[ "$url" =~ goodreads\.com/book/show/[0-9]+-([^/?]+) ]]; then
        local title="${BASH_REMATCH[1]}"
        query=$(echo "$title" | sed 's/-/ /g' | sed 's/_/ /g')
    
    # Extract from Amazon URLs
    elif [[ "$url" =~ amazon\.[^/]+/.*/dp/([A-Z0-9]+) ]] || [[ "$url" =~ amazon\.[^/]+/([^/]+)/dp/ ]]; then
        # Try to extract title from URL path
        if [[ "$url" =~ amazon\.[^/]+/([^/]+)/dp/ ]]; then
            local title="${BASH_REMATCH[1]}"
            query=$(echo "$title" | sed 's/-/ /g' | awk '{for(i=1;i<=5 && i<=NF;i++) printf "%s ", $i; print ""}')
        else
            # Just ASIN, would need to lookup
            query="book ${BASH_REMATCH[1]}"
        fi
    fi
    
    echo "$query"
}

# Extract query from text (clean and limit)
extract_query_from_text() {
    local text="$1"
    
    # Clean text: remove special chars, keep alphanumeric and spaces
    local cleaned
    cleaned=$(echo "$text" | sed 's/[^a-zA-Zа-яёА-ЯЁ0-9 -]/ /g' | sed 's/  */ /g' | xargs)
    
    # Limit to 10 words
    echo "$cleaned" | awk '{for(i=1;i<=10 && i<=NF;i++) printf "%s ", $i; print ""}'
}

# Calculate confidence score
calculate_confidence() {
    local original_input="$1"
    local found_title="$2"
    local found_authors="$3"
    
    # Convert to lowercase for comparison
    local input_lower
    local title_lower
    input_lower=$(echo "$original_input" | tr '[:upper:]' '[:lower:]')
    title_lower=$(echo "$found_title" | tr '[:upper:]' '[:lower:]')
    
    # Start with word overlap calculation
    local input_words
    local title_words
    local overlap_count=0
    local total_input_words=0
    
    # Count word overlaps
    input_words=($(echo "$input_lower" | tr -s ' ' '\n'))
    title_words=($(echo "$title_lower" | tr -s ' ' '\n'))
    
    total_input_words=${#input_words[@]}
    
    if [[ $total_input_words -eq 0 ]]; then
        echo "0.0 VERY_LOW"
        return
    fi
    
    for input_word in "${input_words[@]}"; do
        if [[ ${#input_word} -gt 2 ]]; then  # Skip very short words
            for title_word in "${title_words[@]}"; do
                if [[ "$title_word" == *"$input_word"* ]] || [[ "$input_word" == *"$title_word"* ]]; then
                    ((overlap_count++))
                    break
                fi
            done
        fi
    done
    
    # Calculate base overlap score
    local overlap_score
    overlap_score=$(echo "scale=3; $overlap_count / $total_input_words * 0.5" | bc)
    
    # Bonus for exact phrase match
    local phrase_bonus=0
    if [[ ${#input_lower} -gt 3 ]] && [[ "$title_lower" == *"$input_lower"* ]]; then
        phrase_bonus=0.4
    fi
    
    # Bonus for author match
    local author_bonus=0
    if [[ -n "$found_authors" ]] && [[ "$found_authors" != "Unknown Author" ]]; then
        local authors_lower
        authors_lower=$(echo "$found_authors" | tr '[:upper:]' '[:lower:]')
        if [[ "$input_lower" == *"$authors_lower"* ]] || [[ "$authors_lower" == *"$input_lower"* ]]; then
            author_bonus=0.3
        fi
    fi
    
    # Language consistency bonus
    local lang_bonus=0
    local input_has_cyrillic
    local title_has_cyrillic
    input_has_cyrillic=$(echo "$original_input" | grep -c '[а-яё]' || true)
    title_has_cyrillic=$(echo "$found_title" | grep -c '[а-яё]' || true)
    
    if [[ ($input_has_cyrillic -gt 0 && $title_has_cyrillic -gt 0) ]] || [[ ($input_has_cyrillic -eq 0 && $title_has_cyrillic -eq 0) ]]; then
        lang_bonus=0.1
    fi
    
    # Calculate final confidence
    local final_confidence
    final_confidence=$(echo "scale=3; $overlap_score + $phrase_bonus + $author_bonus + $lang_bonus" | bc)
    
    # Ensure it doesn't exceed 1.0
    if (( $(echo "$final_confidence > 1.0" | bc -l) )); then
        final_confidence="1.000"
    fi
    
    # Determine confidence level
    local confidence_level
    if (( $(echo "$final_confidence >= 0.8" | bc -l) )); then
        confidence_level="VERY_HIGH"
    elif (( $(echo "$final_confidence >= 0.6" | bc -l) )); then
        confidence_level="HIGH"
    elif (( $(echo "$final_confidence >= 0.4" | bc -l) )); then
        confidence_level="MEDIUM"
    elif (( $(echo "$final_confidence >= 0.2" | bc -l) )); then
        confidence_level="LOW"
    else
        confidence_level="VERY_LOW"
    fi
    
    echo "$final_confidence $confidence_level"
}

# Generate standardized JSON response
generate_json_response() {
    local status="$1"
    local input_format="$2"
    local original_input="$3"
    local extracted_query="$4"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Start JSON
    cat << EOF
{
  "status": "$status",
  "timestamp": "$timestamp",
  "input_format": "$input_format",
  "query_info": {
    "original_input": $(echo "$original_input" | jq -R .),
    "extracted_query": $(echo "$extracted_query" | jq -R .)
  },
EOF

    # Add result based on status
    if [[ "$status" == "success" ]]; then
        # Get the rest of the parameters
        local found_title="$5"
        local found_authors="$6"
        local found_year="$7"
        local found_publisher="$8"
        local found_size="$9"
        local found_description="${10}"
        local service_used="${11}"
        local epub_url="${12:-null}"
        
        # Enhanced service now provides both match confidence and readability confidence
        # This old calculation is no longer needed as the enhanced backend handles it
        
        # Clean authors array
        local authors_json
        authors_json=$(echo "$found_authors" | jq -R 'split(",") | map(. | gsub("^\\s+|\\s+$"; "")) | map(select(length > 2 and (. | test("comment|support|amazon|litres|barnes|noble|bookshop"; "i") | not))) | .[0:3]')
        
        # Note: Enhanced service provides complete JSON response, so this old template is not used
        # The enhanced backend already provides the full standardized response
        echo "  \"result\": \"enhanced_service_response\""
    elif [[ "$status" == "not_found" ]]; then
        local message="$5"
        cat << EOF
  "result": {
    "found": false,
    "message": $(echo "$message" | jq -R .)
  }
EOF
    else
        # Error case
        local error_code="$5"
        local error_message="$6"
        cat << EOF
  "result": {
    "error": "$error_code",
    "message": $(echo "$error_message" | jq -R .)
  }
EOF
    fi
    
    echo "}"
}

# Load environment variables
load_env() {
    if [[ -f "$ENV_FILE" ]]; then
        export $(grep -v '^#' "$ENV_FILE" | xargs)
    fi
}

# Main search function using simple Python backend
search_book() {
    local input_format="$1"
    local original_input="$2"
    local extracted_query="$3"
    
    # Use the book search engine with filtering and format parameters
    local result
    result=$(FORMAT="$FORMAT" MIN_CONFIDENCE="$MIN_CONFIDENCE" MIN_QUALITY="$MIN_QUALITY" python3 "$SCRIPT_DIR/book_search_engine.py" "$extracted_query" 2>/dev/null || echo "")
    
    if [[ -n "$result" ]]; then
        echo "$result"
        return 0
    else
        generate_json_response "error" "$input_format" "$original_input" "$extracted_query" "backend_error" "Failed to get response from backend service"
        return 1
    fi
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--format)
                FORMAT="$2"
                shift 2
                ;;
            -c|--count)
                COUNT="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --download)
                DOWNLOAD="true"
                shift
                ;;
            --no-confidence)
                CONFIDENCE_ENABLED="false"
                shift
                ;;
            --min-confidence)
                MIN_CONFIDENCE="$2"
                shift 2
                ;;
            --min-quality)
                MIN_QUALITY="$2"
                shift 2
                ;;
            --strict)
                MIN_CONFIDENCE="0.8"
                MIN_QUALITY="GOOD"
                shift
                ;;
            --claude-extract)
                CLAUDE_EXTRACT="true"
                shift
                ;;
            -*)
                generate_json_response "error" "" "" "" "invalid_option" "Unknown option: $1" >&2
                exit 1
                ;;
            *)
                if [[ -z "$QUERY" ]]; then
                    QUERY="$1"
                else
                    generate_json_response "error" "" "" "" "extra_argument" "Extra argument: $1" >&2
                    exit 1
                fi
                shift
                ;;
        esac
    done
}

# Main function
main() {
    # Parse arguments
    parse_args "$@"
    
    # Check if query provided
    if [[ -z "$QUERY" ]]; then
        generate_json_response "error" "" "" "" "no_input" "No input provided. Use --help for usage information."
        exit 1
    fi
    
    # Load environment
    load_env
    
    # Detect input format
    INPUT_FORMAT=$(detect_input_format "$QUERY")
    
    # Auto-enable download for URLs if not explicitly set
    if [[ "$INPUT_FORMAT" == "url" ]] && [[ "$DOWNLOAD" == "false" ]]; then
        DOWNLOAD="true"  # Automatically download when URL is provided
    fi
    
    # Extract appropriate query
    local extracted_query
    case "$INPUT_FORMAT" in
        "url")
            extracted_query=$(extract_query_from_url "$QUERY")
            ;;
        "txt")
            extracted_query=$(extract_query_from_text "$QUERY")
            ;;
        "image")
            extracted_query="image_analysis_not_implemented"
            ;;
        *)
            extracted_query="$QUERY"
            ;;
    esac
    
    # Perform search
    search_book "$INPUT_FORMAT" "$QUERY" "$extracted_query"
}

# Run main function
main "$@"