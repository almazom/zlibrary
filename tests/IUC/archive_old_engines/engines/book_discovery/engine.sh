#!/bin/bash

# =============================================================================
# Book Discovery Engine v1.0.0
# Atomic engine that discovers random book URLs from Russian bookstore category pages
# Part of IUC Test Framework
# =============================================================================

set -euo pipefail

# Engine metadata
ENGINE_NAME="book_discovery"
ENGINE_VERSION="1.0.0"
ENGINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_CONFIG="${ENGINE_DIR}/config/defaults.yaml"

# Global variables
STORE=""
CATEGORY=""
PAGE=""
COUNT="5"
OUTPUT_FORMAT="json"
TIMEOUT="60"
CONFIG_FILE="$ENGINE_CONFIG"
VERBOSE=false

# Colors for output (if not piped)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m' 
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

# Logging functions
log_error() { [[ "$VERBOSE" == "true" ]] && echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_info() { [[ "$VERBOSE" == "true" ]] && echo -e "${BLUE}[INFO]${NC} $*" >&2; }
log_success() { [[ "$VERBOSE" == "true" ]] && echo -e "${GREEN}[SUCCESS]${NC} $*" >&2; }
log_warn() { [[ "$VERBOSE" == "true" ]] && echo -e "${YELLOW}[WARN]${NC} $*" >&2; }

# Utility functions
get_timestamp() {
    date -u '+%Y-%m-%dT%H:%M:%S.%3NZ'
}

output_json() {
    local status="$1"
    shift
    
    if [[ "$status" == "success" ]]; then
        local store="$1"
        local category="$2" 
        local page="$3"
        local count="$4"
        local books_json="$5"
        
        cat << EOF
{
  "status": "success",
  "engine": {
    "name": "$ENGINE_NAME",
    "version": "$ENGINE_VERSION"
  },
  "request": {
    "store": "$store",
    "category": "$category",
    "page": $page,
    "requested_count": $count
  },
  "result": {
    "discovered_count": $(echo "$books_json" | jq length),
    "books": $books_json
  },
  "timestamp": "$(get_timestamp)"
}
EOF
    else
        local error_code="$1"
        local message="$2"
        
        cat << EOF
{
  "status": "error",
  "engine": {
    "name": "$ENGINE_NAME", 
    "version": "$ENGINE_VERSION"
  },
  "error": {
    "code": "$error_code",
    "message": "$message"
  },
  "timestamp": "$(get_timestamp)"
}
EOF
    fi
}

# Store configuration functions
get_store_config() {
    local store="$1"
    local key="$2"
    
    if command -v yq >/dev/null 2>&1; then
        yq eval ".stores[\"$store\"].$key" "$CONFIG_FILE" 2>/dev/null || echo ""
    else
        # Fallback without yq - basic parsing
        grep -A 20 "^  ${store}:" "$CONFIG_FILE" | grep "    $key:" | cut -d':' -f2- | xargs || echo ""
    fi
}

is_store_enabled() {
    local store="$1"
    local enabled=$(get_store_config "$store" "enabled")
    [[ "$enabled" == "true" ]]
}

get_store_base_url() {
    local store="$1"
    get_store_config "$store" "base_url"
}

get_category_path() {
    local store="$1"
    local category="$2"
    
    if command -v yq >/dev/null 2>&1; then
        yq eval ".stores[\"$store\"].categories[\"$category\"]" "$CONFIG_FILE" 2>/dev/null || echo ""
    else
        # Fallback parsing
        grep -A 10 "categories:" "$CONFIG_FILE" | grep "$category:" | cut -d':' -f2- | xargs || echo ""
    fi
}

# Book discovery functions
discover_books_from_page() {
    local store="$1"
    local category="$2"
    local page="$3"
    local count="$4"
    
    local base_url=$(get_store_base_url "$store")
    local category_path=$(get_category_path "$store" "$category")
    local full_url="${base_url}${category_path}?page=${page}"
    
    log_info "Discovering books from: $full_url"
    
    # Use Claude to discover book URLs from the category page
    local claude_prompt="Use WebFetch to visit $full_url and find $count specific book URLs from this category page. Return JSON array with format: [{\"title\": \"Book Title\", \"url\": \"full_book_url\"}]. Only return valid book URLs, not category or navigation links."
    
    local claude_result
    if claude_result=$(timeout "$TIMEOUT" claude -p "$claude_prompt" --allowedTools "WebFetch" --output-format json 2>/dev/null); then
        # Extract the JSON array from Claude's response
        local json_result
        if json_result=$(echo "$claude_result" | jq -r '.result' 2>/dev/null); then
            # If the result is a JSON string, parse it
            if echo "$json_result" | jq . >/dev/null 2>&1; then
                echo "$json_result"
                return 0
            else
                # Try to extract JSON from the result string
                local extracted_json
                if extracted_json=$(echo "$json_result" | grep -o '\[.*\]' | head -1); then
                    echo "$extracted_json"
                    return 0
                fi
            fi
        fi
        
        # Fallback: try to parse the entire response as JSON array
        if echo "$claude_result" | jq . >/dev/null 2>&1; then
            echo "$claude_result"
            return 0
        fi
    fi
    
    log_error "Failed to discover books from $full_url"
    return 1
}

select_random_page() {
    local store="$1"
    local max_pages
    
    if command -v yq >/dev/null 2>&1; then
        max_pages=$(yq eval ".stores[\"$store\"].pagination.max_pages" "$CONFIG_FILE" 2>/dev/null || echo "10")
    else
        max_pages=10  # Fallback
    fi
    
    echo $((RANDOM % max_pages + 1))
}

# Validation functions
validate_store() {
    local store="$1"
    
    if ! is_store_enabled "$store"; then
        log_error "Store '$store' is not enabled or not supported"
        return 1
    fi
    
    local base_url=$(get_store_base_url "$store")
    if [[ -z "$base_url" ]]; then
        log_error "No base URL configured for store '$store'"
        return 1
    fi
    
    return 0
}

validate_category() {
    local store="$1"
    local category="$2"
    
    local category_path=$(get_category_path "$store" "$category")
    if [[ -z "$category_path" ]]; then
        log_error "Category '$category' not supported for store '$store'"
        return 1
    fi
    
    return 0
}

validate_dependencies() {
    local missing_deps=()
    
    # Check required system commands
    for cmd in bash curl jq; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Check Claude AI
    if ! command -v claude >/dev/null 2>&1; then
        missing_deps+=("claude")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    return 0
}

# Main discovery function
discover_books() {
    local store="$1"
    local category="$2"  
    local page="$3"
    local count="$4"
    
    log_info "Starting book discovery: store=$store, category=$category, page=$page, count=$count"
    
    # Validate inputs
    if ! validate_store "$store"; then
        output_json "error" "store_not_supported" "Store '$store' is not supported or enabled"
        exit 4
    fi
    
    if ! validate_category "$store" "$category"; then
        output_json "error" "invalid_category" "Category '$category' not supported for store '$store'"
        exit 2
    fi
    
    # Discover books
    local books_json
    if books_json=$(discover_books_from_page "$store" "$category" "$page" "$count"); then
        # Validate the JSON result
        if echo "$books_json" | jq . >/dev/null 2>&1; then
            local book_count=$(echo "$books_json" | jq length)
            if [[ "$book_count" -gt 0 ]]; then
                log_success "Successfully discovered $book_count books"
                output_json "success" "$store" "$category" "$page" "$count" "$books_json"
                exit 0
            else
                log_warn "No books found in the response"
                output_json "error" "no_books_found" "No books found on page $page of $store/$category"
                exit 1
            fi
        else
            log_error "Invalid JSON response from discovery"
            output_json "error" "parsing_error" "Could not parse book discovery response"
            exit 5
        fi
    else
        log_error "Book discovery failed"
        output_json "error" "network_error" "Failed to discover books from $store"
        exit 3
    fi
}

# Help function
show_help() {
    cat << 'EOF'
📚 Book Discovery Engine v1.0.0

DESCRIPTION:
    Atomic engine that discovers random book URLs from Russian bookstore category pages.
    Uses Claude AI with WebFetch to extract book URLs from store category pages.

USAGE:
    ./engine.sh --store <store> [options]

REQUIRED ARGUMENTS:
    --store <store>        Bookstore to discover from (eksmo.ru, alpinabook.ru)

OPTIONAL ARGUMENTS:
    --category <category>  Book category (default: books)
    --page <number>        Page number (default: random)
    --count <number>       Number of books to discover (default: 5)
    --output-format <fmt>  Output format: json (default: json)
    --timeout <seconds>    Request timeout (default: 60)
    --config <file>        Config file path (default: config/defaults.yaml)
    --verbose             Enable verbose logging
    --help                Show this help

SUPPORTED STORES:
    eksmo.ru              Russian commercial bookstore
    alpinabook.ru         Academic/business bookstore
    
EXAMPLES:
    # Discover 5 books from eksmo.ru fiction category
    ./engine.sh --store eksmo.ru --category fiction
    
    # Discover 3 books from alpinabook.ru business section, page 2
    ./engine.sh --store alpinabook.ru --category business --page 2 --count 3
    
    # Verbose discovery with custom timeout
    ./engine.sh --store eksmo.ru --verbose --timeout 90

OUTPUT FORMAT:
    JSON object with discovered book URLs and metadata.
    See manifest.json for complete output schema.

EXIT CODES:
    0  Success - books discovered
    1  No books found
    2  Invalid arguments
    3  Network error
    4  Store not supported  
    5  Parsing error

DOCUMENTATION:
    README.md           Complete documentation
    manifest.json       API specification
    examples/           Usage examples

VERSION: 1.0.0
AUTHOR: IUC Test Framework
EOF
}

# Argument parsing
while [[ $# -gt 0 ]]; do
    case $1 in
        --store)
            STORE="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2" 
            shift 2
            ;;
        --page)
            PAGE="$2"
            shift 2
            ;;
        --count)
            COUNT="$2"
            shift 2
            ;;
        --output-format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown argument: $1"
            output_json "error" "invalid_arguments" "Unknown argument: $1"
            exit 2
            ;;
    esac
done

# Validate required arguments
if [[ -z "$STORE" ]]; then
    log_error "Missing required argument: --store"
    output_json "error" "invalid_arguments" "Missing required argument: --store"
    exit 2
fi

# Set defaults
if [[ -z "$CATEGORY" ]]; then
    CATEGORY="books"
fi

if [[ -z "$PAGE" ]]; then
    PAGE=$(select_random_page "$STORE")
fi

# Validate dependencies
if ! validate_dependencies; then
    output_json "error" "missing_dependencies" "Required dependencies not available"
    exit 2
fi

# Validate config file
if [[ ! -f "$CONFIG_FILE" ]]; then
    log_error "Config file not found: $CONFIG_FILE"
    output_json "error" "config_not_found" "Config file not found: $CONFIG_FILE"
    exit 2
fi

# Main execution
log_info "Book Discovery Engine v$ENGINE_VERSION starting..."
discover_books "$STORE" "$CATEGORY" "$PAGE" "$COUNT"