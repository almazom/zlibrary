#!/bin/bash

# =============================================================================
# Z-Library Book Search & Download Service
# Fixed version with proper metadata handling
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
LANGUAGE=""
COUNT="10"
JSON_OUTPUT="false"
DOWNLOAD="false"
QUERY=""
VERBOSE="false"
ENV_FILE="$PROJECT_ROOT/.env"
AUTHOR=""
SERVICE_MODE="false"
FORCE_SERVICE="" # Can be 'zlib', 'flibusta', or empty for auto-fallback
USED_SERVICE="" # Track which service was actually used

# Print functions
print_error() { echo -e "${RED}❌ ERROR: $*${NC}" >&2; }
print_success() { echo -e "${GREEN}✅ $*${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
print_step() { echo -e "${CYAN}🔷 $*${NC}"; }

# Show help
show_help() {
    cat << EOF
${WHITE}Z-Library Service - Book Search & Download${NC}

${WHITE}USAGE:${NC}
    $SCRIPT_NAME [OPTIONS] "search query"

${WHITE}OPTIONS:${NC}
    ${GREEN}-o, --output DIR${NC}      Output directory (default: $OUTPUT_DIR)
    ${GREEN}-f, --format FORMAT${NC}   File format (epub, pdf, mobi, etc.)
    ${GREEN}-l, --lang LANGUAGE${NC}   Language (english, russian, etc.)
    ${GREEN}-a, --author NAME${NC}     Author name filter
    ${GREEN}-c, --count NUMBER${NC}    Max results (default: $COUNT)
    ${GREEN}--json${NC}                JSON output format
    ${GREEN}--download${NC}            Download first book found
    ${GREEN}--service${NC}             Service mode (minimal output, JSON only)
    ${GREEN}--limits${NC}              Check download limits
    ${GREEN}--force-zlib${NC}          Force search in Z-Library only (no fallback)
    ${GREEN}--force-flibusta${NC}      Force search in Flibusta only (Russian books)
    ${GREEN}-v, --verbose${NC}         Verbose output
    ${GREEN}-h, --help${NC}            Show this help

${WHITE}SERVICE MODE:${NC}
    Use --service with --json for clean service integration:
    - Returns only JSON output
    - Includes absolute file paths
    - No colored output or progress messages
    - Perfect for API endpoints

${WHITE}SERVICE SELECTION:${NC}
    By default, searches Z-Library first, then falls back to Flibusta if needed.
    ${GREEN}--force-zlib${NC}       Only search Z-Library (no Flibusta fallback)
    ${GREEN}--force-flibusta${NC}   Only search Flibusta (good for Russian literature)
    
    The JSON response includes 'service_used' field to track which service provided the book.

${WHITE}EXAMPLES:${NC}
    ${GREEN}# Search by title and author${NC}
    $SCRIPT_NAME -a "J.K. Rowling" "Harry Potter"
    
    ${GREEN}# Download specific format${NC}
    $SCRIPT_NAME -f epub --download "Python programming"
    
    ${GREEN}# Service mode with custom output${NC}
    $SCRIPT_NAME --service --json -o /tmp/books --download "Machine Learning"
    
    ${GREEN}# Get search results as JSON${NC}
    $SCRIPT_NAME --json -c 5 "Data Science"

${WHITE}ENVIRONMENT:${NC}
    Set ZLOGIN and ZPASSW in $ENV_FILE

${WHITE}OUTPUT FILE STRUCTURE:${NC}
    Downloaded files are saved as:
    <output_dir>/<safe_title>.<extension>
    
    In service mode with JSON, the response includes:
    - file.path: Full path to downloaded file
    - file.size: File size in bytes
    - book.name: Original book title
    - book.authors: List of authors
    - book.id: Z-Library book ID

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
        -a|--author)
            AUTHOR="$2"
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
        --service)
            SERVICE_MODE="true"
            JSON_OUTPUT="true"
            shift
            ;;
        --force-zlib)
            FORCE_SERVICE="zlib"
            shift
            ;;
        --force-flibusta)
            FORCE_SERVICE="flibusta"
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
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        echo '{"status": "error", "message": "Environment file not found"}'
    else
        print_error "Environment file not found: $ENV_FILE"
    fi
    exit 1
fi

# Check credentials
if [[ -z "${ZLOGIN:-}" ]] || [[ -z "${ZPASSW:-}" ]]; then
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        echo '{"status": "error", "message": "ZLOGIN and ZPASSW must be set in .env file"}'
    else
        print_error "ZLOGIN and ZPASSW must be set in $ENV_FILE"
    fi
    exit 3
fi

# Ensure Python path
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"

# Check limits function
check_limits() {
    if [[ "$SERVICE_MODE" != "true" ]] && [[ "$JSON_OUTPUT" != "true" ]]; then
        print_step "Checking download limits..."
    fi
    
    python3 -c "
import asyncio
import sys
import json
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

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
    USED_SERVICE="zlibrary"
}

# Flibusta search function
search_flibusta() {
    local search_query="$1"
    
    if [[ "$SERVICE_MODE" != "true" ]] && [[ "$JSON_OUTPUT" != "true" ]]; then
        if [[ "$VERBOSE" == "true" ]]; then
            print_step "Searching in Flibusta: $search_query"
        else
            print_info "Fallback: Searching in Flibusta..."
        fi
    fi
    
    python3 -c "
import asyncio
import sys
import json
import os
sys.path.insert(0, '$PROJECT_ROOT/src')
sys.path.insert(0, '$PROJECT_ROOT')

from book_sources.flibusta_source import FlibustaSource

async def main():
    try:
        flibusta = FlibustaSource()
        result = await flibusta.search('$search_query')
        
        if '$JSON_OUTPUT' == 'true':
            if result.found:
                output = {
                    'status': 'success',
                    'query': '$search_query',
                    'service_used': 'flibusta',
                    'total_results': 1,
                    'results': [{
                        'name': result.title,
                        'authors': [{'author': result.author}] if result.author else [],
                        'year': result.year if hasattr(result, 'year') else '',
                        'extension': 'EPUB',
                        'size': result.size if hasattr(result, 'size') else '',
                        'file_path': result.file_path if result.file_path else '',
                        'description': f'Found in Flibusta: {result.title}'
                    }]
                }
            else:
                output = {
                    'status': 'error',
                    'message': 'No books found in Flibusta',
                    'query': '$search_query',
                    'service_used': 'flibusta'
                }
            print(json.dumps(output, indent=2))
        else:
            if result.found:
                print(f'✅ Found in Flibusta: {result.title}')
                if result.author:
                    print(f'   Author: {result.author}')
                if result.file_path:
                    print(f'   File: {result.file_path}')
            else:
                print('❌ No books found in Flibusta')
                sys.exit(5)
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            error_output = {
                'status': 'error',
                'message': str(e),
                'service_used': 'flibusta'
            }
            print(json.dumps(error_output))
        else:
            print(f'❌ Flibusta Error: {e}', file=sys.stderr)
        sys.exit(4)

asyncio.run(main())
"
    local python_exit=$?
    USED_SERVICE="flibusta"
    return $python_exit
}

# Search function
search_books() {
    local search_query="$1"
    
    # Add author to query if provided
    if [[ -n "$AUTHOR" ]]; then
        search_query="$AUTHOR $search_query"
    fi
    
    if [[ "$SERVICE_MODE" != "true" ]] && [[ "$VERBOSE" == "true" ]]; then
        print_step "Searching for: $search_query"
        if [[ -n "$FORCE_SERVICE" ]]; then
            print_info "Forced service: $FORCE_SERVICE"
        fi
    fi
    
    # If forcing Flibusta, use the Flibusta source directly
    if [[ "$FORCE_SERVICE" == "flibusta" ]]; then
        search_flibusta "$search_query"
        return
    fi

    python3 -c "
import asyncio
import sys
import json
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

from zlibrary import AsyncZlib, Extension, Language

async def main():
    try:
        lib = AsyncZlib()
        await lib.login('$ZLOGIN', '$ZPASSW')
        
        # Build search parameters
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
        await paginator.init()
        books = paginator.result
        
        if not books:
            if '$JSON_OUTPUT' != 'true':
                print('❌ No books found in Z-Library!', file=sys.stderr)
            # Exit with code 10 for fallback trigger (unless forcing Z-Library)
            if '$FORCE_SERVICE' == 'zlib':
                if '$JSON_OUTPUT' == 'true':
                    output = {'status': 'error', 'message': 'No books found in Z-Library', 'query': '$search_query', 'service_used': 'zlibrary'}
                    print(json.dumps(output))
                sys.exit(5)  # Normal error when forcing Z-Library only
            else:
                # Don't print JSON here - let fallback handle it
                sys.exit(10)  # Special code to trigger fallback
            
        if '$JSON_OUTPUT' == 'true':
            # JSON output with proper metadata extraction
            results = []
            for book in books:
                # Fetch detailed info for each book
                try:
                    details = await book.fetch()
                    book_data = {
                        'id': book.id if hasattr(book, 'id') else '',
                        'name': details.get('name', book.name if hasattr(book, 'name') else 'Unknown'),
                        'authors': details.get('authors', []),
                        'year': details.get('year', book.year if hasattr(book, 'year') else ''),
                        'extension': details.get('extension', book.extension if hasattr(book, 'extension') else ''),
                        'size': details.get('size', book.size if hasattr(book, 'size') else ''),
                        'publisher': details.get('publisher', book.publisher if hasattr(book, 'publisher') else ''),
                        'rating': details.get('rating', book.rating if hasattr(book, 'rating') else ''),
                        'url': book.url if hasattr(book, 'url') else '',
                        'cover': details.get('cover', book.cover if hasattr(book, 'cover') else ''),
                        'isbn': details.get('isbn', book.isbn if hasattr(book, 'isbn') else ''),
                        'description': details.get('description', '')[:200] if details.get('description') else ''
                    }
                except:
                    # Fallback to basic info if fetch fails
                    book_data = {
                        'id': book.id if hasattr(book, 'id') else '',
                        'name': book.name if hasattr(book, 'name') else 'Unknown',
                        'authors': [],
                        'year': book.year if hasattr(book, 'year') else '',
                        'extension': book.extension if hasattr(book, 'extension') else '',
                        'size': book.size if hasattr(book, 'size') else '',
                        'publisher': book.publisher if hasattr(book, 'publisher') else '',
                        'rating': book.rating if hasattr(book, 'rating') else '',
                        'url': book.url if hasattr(book, 'url') else '',
                        'cover': book.cover if hasattr(book, 'cover') else '',
                        'isbn': book.isbn if hasattr(book, 'isbn') else '',
                        'description': ''
                    }
                    
                    # Try to extract authors
                    if hasattr(book, 'authors'):
                        authors = book.authors
                        if authors:
                            author_list = []
                            for author in authors:
                                if isinstance(author, dict):
                                    author_list.append({'name': author.get('author', ''), 'url': author.get('url', '')})
                                elif hasattr(author, 'author'):
                                    author_list.append({'name': author.author, 'url': ''})
                                else:
                                    author_list.append({'name': str(author), 'url': ''})
                            book_data['authors'] = author_list
                
                results.append(book_data)
            
            output = {
                'status': 'success',
                'query': '$search_query',
                'service_used': 'zlibrary',
                'total_results': len(results),
                'page': paginator.page if hasattr(paginator, 'page') else 1,
                'total_pages': paginator.total if hasattr(paginator, 'total') else 1,
                'results': results
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            # Simple text output
            print(f'📚 Found {len(books)} books:')
            print()
            for i, book in enumerate(books, 1):
                try:
                    details = await book.fetch()
                    name = details.get('name', 'Unknown')
                    authors = details.get('authors', [])
                    year = details.get('year', 'Unknown')
                    extension = details.get('extension', 'Unknown')
                    size = details.get('size', 'Unknown')
                    rating = details.get('rating', 'Unknown')
                    
                    print(f'{i}. {name}')
                    if authors:
                        author_names = []
                        for author in authors:
                            if isinstance(author, dict):
                                author_names.append(author.get('author', ''))
                            else:
                                author_names.append(str(author))
                        if author_names:
                            print(f'   👥 Authors: {\", \".join(filter(None, author_names))}')
                    print(f'   📅 Year: {year}')
                    print(f'   📄 Format: {extension}')
                    print(f'   💾 Size: {size}')
                    if rating and rating != 'Unknown':
                        print(f'   ⭐ Rating: {rating}')
                    print()
                except:
                    # Basic fallback
                    name = book.name if hasattr(book, 'name') else 'Unknown'
                    print(f'{i}. {name}')
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
    local python_exit=$?
    USED_SERVICE="zlibrary"
    return $python_exit
}

# Download function
download_book() {
    local search_query="$1"
    
    # Add author to query if provided
    if [[ -n "$AUTHOR" ]]; then
        search_query="$AUTHOR $search_query"
    fi
    
    if [[ "$SERVICE_MODE" != "true" ]]; then
        print_step "Searching and downloading: $search_query"
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Get absolute path for output directory
    OUTPUT_DIR_ABS="$(cd "$OUTPUT_DIR" && pwd)"
    
    python3 -c "
import asyncio
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, '$PROJECT_ROOT/src')

from zlibrary import AsyncZlib, Extension, Language
import aiohttp
import aiofiles

async def main():
    try:
        lib = AsyncZlib()
        await lib.login('$ZLOGIN', '$ZPASSW')
        
        # Build search parameters
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
        await paginator.init()
        books = paginator.result
        
        if not books:
            if '$JSON_OUTPUT' == 'true':
                output = {'status': 'error', 'message': 'No books found for download', 'query': '$search_query'}
                print(json.dumps(output))
            else:
                print('❌ No books found!', file=sys.stderr)
            sys.exit(5)
            
        book = books[0]
        
        # Get detailed book info
        book_details = await book.fetch()
        book_name = book_details.get('name', book.name if hasattr(book, 'name') else 'Unknown')
        book_authors = book_details.get('authors', [])
        book_year = book_details.get('year', book.year if hasattr(book, 'year') else '')
        book_id = book.id if hasattr(book, 'id') else ''
        
        if '$SERVICE_MODE' != 'true' and '$JSON_OUTPUT' != 'true':
            print(f'📖 Found: {book_name}')
            if book_authors:
                author_names = []
                for author in book_authors:
                    if isinstance(author, dict):
                        author_names.append(author.get('author', ''))
                    else:
                        author_names.append(str(author))
                if author_names:
                    print(f'   👥 Authors: {\", \".join(filter(None, author_names))}')
        
        # Get download URL
        download_url = book_details.get('download_url')
        
        if not download_url:
            if '$JSON_OUTPUT' == 'true':
                output = {
                    'status': 'error',
                    'message': 'No download URL available - check account limits',
                    'book': {
                        'name': book_name,
                        'id': book_id,
                        'authors': book_authors
                    }
                }
                print(json.dumps(output))
            else:
                print('❌ No download URL available - check account limits', file=sys.stderr)
            sys.exit(6)
            
        # Create safe filename
        safe_title = ''.join(c for c in book_name[:80] if c.isalnum() or c in (' ', '-', '_', '.')).strip()
        if not safe_title:
            safe_title = f'book_{book_id}' if book_id else 'downloaded_book'
        
        # Replace multiple spaces with single space
        safe_title = ' '.join(safe_title.split())
        
        extension = book_details.get('extension', book.extension if hasattr(book, 'extension') else 'epub').lower()
        filename = f'{safe_title}.{extension}'
        filepath = Path('$OUTPUT_DIR_ABS') / filename
        
        if '$SERVICE_MODE' != 'true' and '$JSON_OUTPUT' != 'true':
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
                        # Extract author names for JSON
                        author_names = []
                        for author in book_authors:
                            if isinstance(author, dict):
                                author_names.append(author.get('author', ''))
                            else:
                                author_names.append(str(author))
                        
                        output = {
                            'status': 'success',
                            'message': 'Download completed successfully',
                            'service_used': 'zlibrary',
                            'book': {
                                'name': book_name,
                                'id': book_id,
                                'authors': list(filter(None, author_names)),
                                'year': book_year,
                                'extension': extension,
                                'size_bytes': len(content)
                            },
                            'file': {
                                'path': str(filepath.absolute()),
                                'filename': filename,
                                'size': len(content)
                            }
                        }
                        print(json.dumps(output, indent=2, ensure_ascii=False))
                    else:
                        print(f'✅ Downloaded: {filepath} ({len(content):,} bytes)')
                else:
                    if '$JSON_OUTPUT' == 'true':
                        output = {
                            'status': 'error', 
                            'message': f'Download failed: HTTP {response.status}',
                            'book': {
                                'name': book_name,
                                'id': book_id
                            },
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
    local python_exit=$?
    USED_SERVICE="zlibrary"
    return $python_exit
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
        # Try Z-Library first (unless forcing Flibusta)
        if [[ "$FORCE_SERVICE" != "flibusta" ]]; then
            set +e  # Don't exit on error
            search_books "$QUERY"
            exit_code=$?
            set -e  # Re-enable exit on error
            
            # Debug: Show exit code
            if [[ "$VERBOSE" == "true" ]]; then
                echo "[DEBUG] Z-Library search exit code: $exit_code" >&2
            fi
            
            # If Z-Library failed with exit code 10 (no results) and not forcing Z-Library, try Flibusta
            if [[ $exit_code -eq 10 ]] && [[ "$FORCE_SERVICE" != "zlib" ]]; then
                if [[ "$SERVICE_MODE" != "true" ]]; then
                    if [[ "$VERBOSE" == "true" ]]; then
                        print_info "No results in Z-Library, trying Flibusta..."
                    fi
                fi
                search_flibusta "$QUERY"
            elif [[ $exit_code -ne 0 ]]; then
                exit $exit_code
            fi
        else
            # Force Flibusta only
            search_flibusta "$QUERY"
        fi
    fi
}

# Run main function
main "$@"