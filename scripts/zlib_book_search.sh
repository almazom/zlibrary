#!/bin/bash

# =============================================================================
# Z-Library Book Search & Download CLI Tool
# Simple and Working Approach
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
FORMAT=""
LANGUAGE=""
COUNT="10"
JSON_OUTPUT="false"
DOWNLOAD="false"
QUERY=""
VERBOSE="false"
ENV_FILE="$PROJECT_ROOT/.env"

# Print functions
print_error() { echo -e "${RED}❌ ERROR: $*${NC}" >&2; }
print_success() { echo -e "${GREEN}✅ $*${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
print_step() { echo -e "${CYAN}🔷 $*${NC}"; }

# Show help
show_help() {
    cat << EOF
${WHITE}Z-Library CLI - Simple & Working${NC}

${WHITE}USAGE:${NC}
    $SCRIPT_NAME [OPTIONS] "search query"

${WHITE}OPTIONS:${NC}
    ${GREEN}-o, --output DIR${NC}      Output directory (default: $OUTPUT_DIR)
    ${GREEN}-f, --format FORMAT${NC}   File format (epub, pdf, mobi, etc.)
    ${GREEN}-l, --lang LANGUAGE${NC}   Language (english, russian, etc.)
    ${GREEN}-c, --count NUMBER${NC}    Max results (default: $COUNT)
    ${GREEN}--json${NC}                JSON output format
    ${GREEN}--download${NC}            Download first book found
    ${GREEN}--limits${NC}              Check download limits
    ${GREEN}-v, --verbose${NC}         Verbose output
    ${GREEN}-h, --help${NC}            Show this help

${WHITE}EXAMPLES:${NC}
    ${GREEN}$SCRIPT_NAME "python programming"${NC}
    ${GREEN}$SCRIPT_NAME -f epub -l english "machine learning"${NC}
    ${GREEN}$SCRIPT_NAME --download "data science"${NC}
    ${GREEN}$SCRIPT_NAME --json "neural networks"${NC}
    ${GREEN}$SCRIPT_NAME --limits${NC}

${WHITE}ENVIRONMENT:${NC}
    Set ZLOGIN and ZPASSW in $ENV_FILE

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -l|--lang)
            LANGUAGE="$2"
            shift 2
            ;;
        -c|--count)
            COUNT="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT="true"
            shift
            ;;
        --download)
            DOWNLOAD="true"
            shift
            ;;
        --limits)
            ACTION="limits"
            shift
            ;;
        -v|--verbose)
            VERBOSE="true"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            print_error "Unknown option: $1"
            exit 2
            ;;
        *)
            if [[ -z "$QUERY" ]]; then
                QUERY="$1"
            else
                print_error "Multiple queries not supported"
                exit 2
            fi
            shift
            ;;
    esac
done

# Load environment
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    print_error "Environment file not found: $ENV_FILE"
    exit 1
fi

# Check credentials
if [[ -z "${ZLOGIN:-}" ]] || [[ -z "${ZPASSW:-}" ]]; then
    print_error "ZLOGIN and ZPASSW must be set in $ENV_FILE"
    exit 3
fi

# Ensure Python path
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"

# Check limits function
check_limits() {
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        print_step "Checking download limits..."
    fi
    
    python3 -c "
import asyncio
import sys
import json
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

# Check dependencies
missing_deps = []
try:
    import aiohttp
except ImportError:
    missing_deps.append('aiohttp')

if missing_deps:
    error_msg = f'Missing dependencies: {missing_deps}. Install with: pip install {\" \".join(missing_deps)}'
    if '$JSON_OUTPUT' == 'true':
        error_output = {'status': 'error', 'message': error_msg}
        print(json.dumps(error_output))
    else:
        print(f'❌ {error_msg}', file=sys.stderr)
    sys.exit(1)

from zlibrary import AsyncZlib

async def main():
    try:
        lib = AsyncZlib()
        await lib.login('$ZLOGIN', '$ZPASSW')
        limits = await lib.profile.get_limits()
        
        if '$JSON_OUTPUT' == 'true':
            output = {
                'status': 'success',
                'limits': {
                    'daily_allowed': limits.get('daily_allowed', 0),
                    'daily_remaining': limits.get('daily_remaining', 0),
                    'daily_amount': limits.get('daily_amount', 0),
                    'daily_reset': limits.get('daily_reset', 0)
                },
                'warnings': []
            }
            
            if limits.get('daily_remaining', 0) <= 0:
                output['warnings'].append('Daily download limit reached')
            elif limits.get('daily_remaining', 0) <= 2:
                output['warnings'].append('Low download quota remaining')
                
            print(json.dumps(output, indent=2))
        else:
            daily_allowed = limits.get('daily_allowed', 0)
            daily_remaining = limits.get('daily_remaining', 0)
            daily_amount = limits.get('daily_amount', 0)
            daily_reset = limits.get('daily_reset', 0)
            
            print(f'📊 Daily Allowed: {daily_allowed}')
            print(f'🔄 Remaining: {daily_remaining}')
            print(f'📈 Total Amount: {daily_amount}')
            print(f'🕐 Reset in: {daily_reset} hours')
            
            if daily_remaining <= 0:
                print('⚠️  Daily limit reached!')
            elif daily_remaining <= 2:
                print('⚠️  Low quota remaining!')
            else:
                print('✅ Download quota available')
                
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            error_output = {'status': 'error', 'message': str(e)}
            print(json.dumps(error_output))
        else:
            print(f'❌ Error: {e}', file=sys.stderr)
        sys.exit(3)

asyncio.run(main())
"
}

# Search function
search_books() {
    local search_query="$1"
    
    if [[ "$VERBOSE" == "true" ]]; then
        print_step "Searching for: $search_query"
    fi

    python3 -c "
import asyncio
import sys
import json
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

# Check dependencies first
missing_deps = []
try:
    import aiohttp
except ImportError:
    missing_deps.append('aiohttp')
try:
    import aiofiles
except ImportError:
    missing_deps.append('aiofiles')

if missing_deps:
    error_msg = f'Missing dependencies: {missing_deps}. Install with: pip install {\" \".join(missing_deps)}'
    if '$JSON_OUTPUT' == 'true':
        error_output = {'status': 'error', 'message': error_msg}
        print(json.dumps(error_output))
    else:
        print(f'❌ {error_msg}', file=sys.stderr)
    sys.exit(1)

from zlibrary import AsyncZlib, Extension, Language

async def main():
    try:
        lib = AsyncZlib()
        await lib.login('$ZLOGIN', '$ZPASSW')
        
        # Build search parameters properly
        search_kwargs = {'q': '$search_query', 'count': $COUNT}
        
        # Handle format filter
        if '$FORMAT':
            format_map = {
                'pdf': Extension.PDF,
                'epub': Extension.EPUB, 
                'mobi': Extension.MOBI,
                'txt': Extension.TXT,
                'fb2': Extension.FB2,
                'rtf': Extension.RTF,
                'azw': Extension.AZW,
                'azw3': Extension.AZW3,
                'djv': Extension.DJV,
                'djvu': Extension.DJVU,
                'lit': Extension.LIT
            }
            format_lower = '$FORMAT'.lower()
            if format_lower in format_map:
                search_kwargs['extensions'] = [format_map[format_lower]]
            else:
                if '$JSON_OUTPUT' == 'true':
                    error_output = {'status': 'error', 'message': f'Unsupported format: $FORMAT'}
                    print(json.dumps(error_output))
                    sys.exit(2)
                else:
                    print(f'❌ Unsupported format: $FORMAT', file=sys.stderr)
                    sys.exit(2)
        
        # Handle language filter
        if '$LANGUAGE':
            lang_map = {
                'english': Language.ENGLISH,
                'russian': Language.RUSSIAN,
                'spanish': Language.SPANISH,
                'french': Language.FRENCH,
                'german': Language.GERMAN,
                'chinese': Language.CHINESE,
                'japanese': Language.JAPANESE,
                'italian': Language.ITALIAN,
                'portuguese': Language.PORTUGUESE,
                'arabic': Language.ARABIC,
                'korean': Language.KOREAN,
                'dutch': Language.DUTCH,
                'polish': Language.POLISH,
                'turkish': Language.TURKISH,
                'ukrainian': Language.UKRAINIAN
            }
            lang_lower = '$LANGUAGE'.lower()
            if lang_lower in lang_map:
                search_kwargs['lang'] = [lang_map[lang_lower]]
            else:
                if '$JSON_OUTPUT' == 'true':
                    error_output = {'status': 'error', 'message': f'Unsupported language: $LANGUAGE'}
                    print(json.dumps(error_output))
                    sys.exit(2)
                else:
                    print(f'❌ Unsupported language: $LANGUAGE', file=sys.stderr)
                    sys.exit(2)
        
        # Search with proper parameters
        paginator = await lib.search(**search_kwargs)
        books = await paginator.next()
        
        if not books:
            if '$JSON_OUTPUT' == 'true':
                output = {'status': 'error', 'message': 'No books found', 'query': '$search_query'}
                print(json.dumps(output))
            else:
                print('❌ No books found!', file=sys.stderr)
            sys.exit(5)
            
        if '$JSON_OUTPUT' == 'true':
            # JSON output - properly extract BookItem data
            results = []
            for book in books:
                book_data = {
                    'id': getattr(book, 'id', ''),
                    'name': getattr(book, 'name', ''),
                    'authors': [],
                    'year': getattr(book, 'year', ''),
                    'extension': getattr(book, 'extension', ''),
                    'size': getattr(book, 'size', ''),
                    'publisher': getattr(book, 'publisher', ''),
                    'rating': getattr(book, 'rating', ''),
                    'url': getattr(book, 'url', ''),
                    'cover': getattr(book, 'cover', ''),
                    'isbn': getattr(book, 'isbn', '')
                }
                
                # Handle authors properly
                authors = getattr(book, 'authors', [])
                if authors:
                    for author in authors:
                        if isinstance(author, dict):
                            book_data['authors'].append(author.get('author', ''))
                        elif hasattr(author, 'author'):
                            book_data['authors'].append(author.author)
                        else:
                            book_data['authors'].append(str(author))
                
                results.append(book_data)
            
            output = {
                'status': 'success',
                'query': '$search_query',
                'total_results': len(results),
                'page': getattr(paginator, 'page', 1),
                'total_pages': getattr(paginator, 'total', 0) // $COUNT + 1 if getattr(paginator, 'total', 0) > 0 else 1,
                'results': results
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            # Simple text output
            print(f'📚 Found {len(books)} books:')
            print()
            for i, book in enumerate(books, 1):
                name = getattr(book, 'name', 'Unknown')
                print(f'{i}. {name}')
                
                # Handle authors
                authors = getattr(book, 'authors', [])
                if authors:
                    author_names = []
                    for author in authors:
                        if isinstance(author, dict):
                            author_names.append(author.get('author', ''))
                        elif hasattr(author, 'author'):
                            author_names.append(author.author)
                        else:
                            author_names.append(str(author))
                    
                    if author_names:
                        print(f'   👥 Authors: {\", \".join(filter(None, author_names))}')
                
                year = getattr(book, 'year', 'Unknown')
                extension = getattr(book, 'extension', 'Unknown')
                size = getattr(book, 'size', 'Unknown')
                rating = getattr(book, 'rating', 'Unknown')
                
                print(f'   📅 Year: {year}')
                print(f'   📄 Format: {extension}')
                print(f'   💾 Size: {size}')
                if rating and rating != 'Unknown':
                    print(f'   ⭐ Rating: {rating}')
                print()
                
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            error_output = {'status': 'error', 'message': str(e), 'query': '$search_query'}
            print(json.dumps(error_output))
        else:
            print(f'❌ Error: {e}', file=sys.stderr)
        sys.exit(4)

asyncio.run(main())
"
}

# Download function
download_book() {
    local search_query="$1"
    
    print_step "Searching and downloading: $search_query"
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    python3 -c "
import asyncio
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, '$PROJECT_ROOT/src')

# Check dependencies first
missing_deps = []
try:
    import aiohttp
except ImportError:
    missing_deps.append('aiohttp')
try:
    import aiofiles
except ImportError:
    missing_deps.append('aiofiles')

if missing_deps:
    error_msg = f'Missing dependencies: {missing_deps}. Install with: pip install {\" \".join(missing_deps)}'
    if '$JSON_OUTPUT' == 'true':
        error_output = {'status': 'error', 'message': error_msg}
        print(json.dumps(error_output))
    else:
        print(f'❌ {error_msg}', file=sys.stderr)
    sys.exit(1)

from zlibrary import AsyncZlib, Extension, Language

async def main():
    try:
        lib = AsyncZlib()
        await lib.login('$ZLOGIN', '$ZPASSW')
        
        # Build search parameters properly
        search_kwargs = {'q': '$search_query', 'count': 1}
        
        # Handle format filter
        if '$FORMAT':
            format_map = {
                'pdf': Extension.PDF,
                'epub': Extension.EPUB, 
                'mobi': Extension.MOBI,
                'txt': Extension.TXT,
                'fb2': Extension.FB2,
                'rtf': Extension.RTF,
                'azw': Extension.AZW,
                'azw3': Extension.AZW3,
                'djv': Extension.DJV,
                'djvu': Extension.DJVU,
                'lit': Extension.LIT
            }
            format_lower = '$FORMAT'.lower()
            if format_lower in format_map:
                search_kwargs['extensions'] = [format_map[format_lower]]
        
        # Handle language filter
        if '$LANGUAGE':
            lang_map = {
                'english': Language.ENGLISH,
                'russian': Language.RUSSIAN,
                'spanish': Language.SPANISH,
                'french': Language.FRENCH,
                'german': Language.GERMAN,
                'chinese': Language.CHINESE,
                'japanese': Language.JAPANESE,
                'italian': Language.ITALIAN,
                'portuguese': Language.PORTUGUESE,
                'arabic': Language.ARABIC,
                'korean': Language.KOREAN,
                'dutch': Language.DUTCH,
                'polish': Language.POLISH,
                'turkish': Language.TURKISH,
                'ukrainian': Language.UKRAINIAN
            }
            lang_lower = '$LANGUAGE'.lower()
            if lang_lower in lang_map:
                search_kwargs['lang'] = [lang_map[lang_lower]]
        
        # Search
        paginator = await lib.search(**search_kwargs)
        books = await paginator.next()
        
        if not books:
            if '$JSON_OUTPUT' == 'true':
                output = {'status': 'error', 'message': 'No books found for download', 'query': '$search_query'}
                print(json.dumps(output))
            else:
                print('❌ No books found!', file=sys.stderr)
            sys.exit(5)
            
        book = books[0]
        book_name = getattr(book, 'name', 'Unknown')
        
        if '$JSON_OUTPUT' != 'true':
            print(f'📖 Found: {book_name}')
        
        # Get download URL
        book_details = await book.fetch()
        download_url = book_details.get('download_url')
        
        if not download_url:
            if '$JSON_OUTPUT' == 'true':
                output = {'status': 'error', 'message': 'No download URL available - check account limits', 'book': book_name}
                print(json.dumps(output))
            else:
                print('❌ No download URL available - check account limits', file=sys.stderr)
            sys.exit(6)
            
        # Create safe filename
        safe_title = ''.join(c for c in book_name[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_title:
            safe_title = 'downloaded_book'
        
        extension = getattr(book, 'extension', 'epub').lower()
        filename = f'{safe_title}.{extension}'
        filepath = Path('$OUTPUT_DIR') / filename
        
        if '$JSON_OUTPUT' != 'true':
            print(f'⬇️  Downloading to: {filepath}')
        
        # Download with proper session handling
        async with aiohttp.ClientSession(cookies=lib.cookies) as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Ensure output directory exists
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    
                    if '$JSON_OUTPUT' == 'true':
                        output = {
                            'status': 'success',
                            'message': 'Download completed successfully',
                            'book': {
                                'name': book_name,
                                'id': getattr(book, 'id', ''),
                                'extension': extension,
                                'size_bytes': len(content)
                            },
                            'file': {
                                'path': str(filepath),
                                'size': len(content)
                            }
                        }
                        print(json.dumps(output, indent=2))
                    else:
                        print(f'✅ Downloaded: {filepath} ({len(content):,} bytes)')
                else:
                    if '$JSON_OUTPUT' == 'true':
                        output = {
                            'status': 'error', 
                            'message': f'Download failed: HTTP {response.status}',
                            'book': book_name,
                            'download_url': download_url
                        }
                        print(json.dumps(output))
                    else:
                        print(f'❌ Download failed: HTTP {response.status}', file=sys.stderr)
                    sys.exit(6)
                    
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            error_output = {'status': 'error', 'message': str(e), 'query': '$search_query'}
            print(json.dumps(error_output))
        else:
            print(f'❌ Error: {e}', file=sys.stderr)
        sys.exit(4)

asyncio.run(main())
"
}

# Main execution
main() {
    # Check if Python and deps are available
    if ! command -v python3 >/dev/null; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"status": "error", "message": "python3 not found"}'
        else
            print_error "python3 not found"
        fi
        exit 1
    fi
    
    # Handle special actions
    if [[ "${ACTION:-}" == "limits" ]]; then
        check_limits
        exit 0
    fi
    
    # Validate query
    if [[ -z "$QUERY" ]]; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"status": "error", "message": "Search query required", "usage": "Use --help for usage information"}'
        else
            print_error "Search query required"
            echo
            show_help
        fi
        exit 2
    fi
    
    # Validate parameters
    if [[ -n "$COUNT" ]] && ! [[ "$COUNT" =~ ^[0-9]+$ ]]; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo "{\"status\": \"error\", \"message\": \"Count must be a number, got: $COUNT\"}"
        else
            print_error "Count must be a number, got: $COUNT"
        fi
        exit 2
    fi
    
    if [[ "$COUNT" -gt 50 ]]; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"status": "error", "message": "Count cannot exceed 50"}'
        else
            print_error "Count cannot exceed 50"
        fi
        exit 2
    fi
    
    # Create output directory if downloading
    if [[ "$DOWNLOAD" == "true" ]]; then
        if ! mkdir -p "$OUTPUT_DIR" 2>/dev/null; then
            if [[ "$JSON_OUTPUT" == "true" ]]; then
                echo "{\"status\": \"error\", \"message\": \"Cannot create output directory: $OUTPUT_DIR\"}"
            else
                print_error "Cannot create output directory: $OUTPUT_DIR"
            fi
            exit 1
        fi
    fi
    
    # Execute action
    if [[ "$DOWNLOAD" == "true" ]]; then
        download_book "$QUERY"
    else
        search_books "$QUERY"
    fi
}

# Run main function
main "$@" 