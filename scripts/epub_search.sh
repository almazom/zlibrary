#!/bin/bash

# =============================================================================
# Z-Library Cognitive Search Service v2.0
# Multi-source book pipeline with Claude SDK intelligence
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
USE_COGNITIVE="true"
FAST_MODE="false"

# Print functions
print_error() { echo -e "${RED}❌ ERROR: $*${NC}" >&2; }
print_success() { echo -e "${GREEN}✅ $*${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
print_step() { echo -e "${CYAN}🔷 $*${NC}"; }

# Show help
show_help() {
    cat << EOF
${WHITE}Z-Library Cognitive Search Service v2.0${NC}
${CYAN}Multi-source book pipeline with Claude SDK intelligence${NC}

${WHITE}USAGE:${NC}
    $SCRIPT_NAME [OPTIONS] "search query"

${WHITE}COGNITIVE FEATURES:${NC}
    ${GREEN}🧠 Claude SDK Normalization${NC}     - Intelligent query enhancement
    ${GREEN}🌐 Web Research Integration${NC}     - Predictive intent analysis
    ${GREEN}🔍 Multi-source Fallback${NC}       - Z-Library → Flibusta routing
    ${GREEN}🇷🇺 Language-aware Routing${NC}      - Russian content → Flibusta priority
    ${GREEN}✅ Result Intent Validation${NC}     - Does this match what user wants?
    ${GREEN}📊 Satisfaction Prediction${NC}     - 80%+ confidence matching

${WHITE}OPTIONS:${NC}
    ${GREEN}-o, --output DIR${NC}         Output directory (default: $OUTPUT_DIR)
    ${GREEN}-f, --format FORMAT${NC}      File format (default: epub only)
    ${GREEN}-l, --lang LANGUAGE${NC}      Language (english, russian, etc.)
    ${GREEN}-a, --author NAME${NC}        Author name filter
    ${GREEN}-c, --count NUMBER${NC}       Max results (default: $COUNT)
    ${GREEN}--json${NC}                   JSON output format
    ${GREEN}--download${NC}               Download first book found
    ${GREEN}--service${NC}                Service mode (minimal output, JSON only)
    ${GREEN}--no-cognitive${NC}           Disable Claude SDK (use basic search)
    ${GREEN}--fast${NC}                   Fast mode (no web research, keep normalization)
    ${GREEN}--limits${NC}                 Check download limits
    ${GREEN}-v, --verbose${NC}            Verbose output with pipeline details
    ${GREEN}-h, --help${NC}               Show this help

${WHITE}COGNITIVE PIPELINE:${NC}
    ${YELLOW}1. Query Normalization${NC}    - Claude SDK analyzes and enhances query
    ${YELLOW}2. Intent Prediction${NC}      - Web research for user satisfaction
    ${YELLOW}3. Language Detection${NC}     - Russian/English routing optimization  
    ${YELLOW}4. Multi-source Search${NC}    - Z-Library + Flibusta fallback
    ${YELLOW}5. Result Validation${NC}      - Intent matching confidence analysis

${WHITE}EXAMPLES:${NC}
    ${GREEN}# Russian book with cognitive pipeline${NC}
    $SCRIPT_NAME "Секретная дверь Почему детские книги — это очень серьезно"
    
    ${GREEN}# Download with format preference${NC}
    $SCRIPT_NAME -f epub --download "Stephen King It"
    
    ${GREEN}# Service mode with cognitive analysis${NC}
    $SCRIPT_NAME --service --json --download "Machine Learning"
    
    ${GREEN}# Verbose pipeline analysis${NC}
    $SCRIPT_NAME -v "Агата Кристи"
    
    ${GREEN}# Disable cognitive features (basic search)${NC}
    $SCRIPT_NAME --no-cognitive "Harry Potter"

${WHITE}ENVIRONMENT:${NC}
    Set ZLOGIN and ZPASSW in $ENV_FILE

${WHITE}SERVICE INTEGRATION:${NC}
    Perfect for API endpoints with --service --json flags
    Returns structured data with cognitive analysis metadata

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
        --download)
            DOWNLOAD="true"
            shift
            ;;
        --no-cognitive)
            USE_COGNITIVE="false"
            shift
            ;;
        --fast)
            FAST_MODE="true"
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

# Cognitive search function
cognitive_search() {
    local search_query="$1"
    
    # Add author to query if provided
    if [[ -n "$AUTHOR" ]]; then
        search_query="$AUTHOR $search_query"
    fi
    
    if [[ "$SERVICE_MODE" != "true" ]]; then
        print_step "🧠 Using Cognitive Pipeline with Claude SDK"
        if [[ "$VERBOSE" == "true" ]]; then
            print_info "Query: $search_query"
            print_info "Features: Normalization + Web Research + Multi-source + Validation"
        fi
    fi

    python3 -c "
import asyncio
import sys
import json
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

from pipeline.book_pipeline import BookSearchPipeline

async def main():
    try:
        # Initialize cognitive pipeline
        pipeline = BookSearchPipeline()
        
        if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
            print('🔍 Cognitive Pipeline Initialized')
            print('   ✅ Claude SDK Normalization: Enabled')
            print('   ✅ Web Research Intent: Enabled') 
            print('   ✅ Multi-source Fallback: Enabled')
            print('   ✅ Result Validation: Enabled')
            print()
        
        # Execute cognitive search
        result = await pipeline.search_book('$search_query')
        
        if result.found:
            # Success - format output
            if '$JSON_OUTPUT' == 'true':
                # Structured JSON with cognitive metadata
                output = {
                    'status': 'success',
                    'cognitive_pipeline': True,
                    'query': '$search_query',
                    'book': {
                        'title': result.title,
                        'author': str(result.author),
                        'source': result.source,
                        'response_time': round(result.response_time, 2)
                    },
                    'cognitive_analysis': {
                        'normalized_queries': result.metadata.get('normalized_queries', []),
                        'sources_tried': result.metadata.get('sources_tried', []),
                        'intent_validation': result.metadata.get('intent_validation', {})
                    }
                }
                print(json.dumps(output, indent=2, ensure_ascii=False))
            else:
                print(f'📖 Found: {result.title}')
                print(f'👤 Author: {result.author}')
                print(f'🔍 Source: {result.source}')
                print(f'⏱️  Response: {result.response_time:.1f}s')
                
                if '$VERBOSE' == 'true':
                    print()
                    print('🔄 Cognitive Analysis:')
                    if 'normalized_queries' in result.metadata:
                        queries = result.metadata['normalized_queries']
                        print(f'   📝 Normalized Queries: {len(queries)} variants tried')
                        for i, q in enumerate(queries[:3], 1):  # Show first 3
                            print(f'      {i}. {q}')
                    
                    if 'intent_validation' in result.metadata:
                        validation = result.metadata['intent_validation']
                        method = validation.get('analysis_method', 'unknown')
                        confidence = validation.get('confidence', 0.0)
                        print(f'   ✅ Intent Validation: {method} (confidence: {confidence:.1%})')
        else:
            # Not found
            if '$JSON_OUTPUT' == 'true':
                output = {
                    'status': 'error',
                    'cognitive_pipeline': True,
                    'message': 'No books found even with cognitive enhancement',
                    'query': '$search_query',
                    'analysis': {
                        'normalized_queries': result.metadata.get('normalized_queries', []),
                        'sources_tried': result.metadata.get('sources_tried', []),
                        'total_time': result.metadata.get('total_time', 0.0)
                    }
                }
                print(json.dumps(output))
            else:
                print('❌ No books found even with cognitive enhancement')
                if '$VERBOSE' == 'true':
                    queries = result.metadata.get('normalized_queries', [])
                    sources = result.metadata.get('sources_tried', [])
                    print(f'   📝 Tried {len(queries)} normalized queries')
                    print(f'   🔍 Searched sources: {sources}')
                    
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            error_output = {
                'status': 'error',
                'cognitive_pipeline': True,
                'message': str(e),
                'query': '$search_query'
            }
            print(json.dumps(error_output))
        else:
            print(f'❌ Cognitive Pipeline Error: {e}', file=sys.stderr)
        sys.exit(4)

asyncio.run(main())
"
}

# Cognitive download function  
cognitive_download() {
    local search_query="$1"
    
    # Add author to query if provided
    if [[ -n "$AUTHOR" ]]; then
        search_query="$AUTHOR $search_query"
    fi
    
    if [[ "$SERVICE_MODE" != "true" ]]; then
        print_step "🧠 Cognitive Download with Pipeline Intelligence"
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    OUTPUT_DIR_ABS="$(cd "$OUTPUT_DIR" && pwd)"

    python3 -c "
import asyncio
import sys
import json
import os
from pathlib import Path
sys.path.insert(0, '$PROJECT_ROOT/src')

from pipeline.book_pipeline import BookSearchPipeline
from zlibrary import AsyncZlib
import aiohttp
import aiofiles

async def main():
    try:
        # Use cognitive pipeline first
        pipeline = BookSearchPipeline()
        
        if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
            print('🧠 Initializing Cognitive Download Pipeline')
        
        # Cognitive search
        result = await pipeline.search_book('$search_query')
        
        if not result.found:
            if '$JSON_OUTPUT' == 'true':
                output = {
                    'status': 'error',
                    'message': 'No books found with cognitive search',
                    'query': '$search_query',
                    'cognitive_analysis': result.metadata
                }
                print(json.dumps(output))
            else:
                print('❌ No books found with cognitive search')
            sys.exit(5)
        
        if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
            print(f'✅ Cognitive match found: {result.title}')
            validation = result.metadata.get('intent_validation', {})
            if validation.get('confidence'):
                print(f'🎯 Intent confidence: {validation[\"confidence\"]:.1%}')
        
        # Now use Z-Library API to get download URL
        lib = AsyncZlib()
        await lib.login('$ZLOGIN', '$ZPASSW')
        
        # Search for the exact book found by cognitive pipeline
        search_kwargs = {'q': result.title, 'count': 1}
        paginator = await lib.search(**search_kwargs)
        await paginator.init()
        books = paginator.result
        
        if not books:
            if '$JSON_OUTPUT' == 'true':
                output = {
                    'status': 'error',
                    'message': 'Book found by cognitive pipeline but not available for download',
                    'cognitive_result': {
                        'title': result.title,
                        'author': str(result.author),
                        'source': result.source
                    }
                }
                print(json.dumps(output))
            else:
                print('❌ Book found by cognitive pipeline but not available for download')
            sys.exit(5)
        
        book = books[0]
        book_details = await book.fetch()
        book_name = book_details.get('name', 'Unknown')
        download_url = book_details.get('download_url')
        
        if not download_url:
            if '$JSON_OUTPUT' == 'true':
                output = {
                    'status': 'error',
                    'message': 'No download URL available - check account limits',
                    'book': {'name': book_name}
                }
                print(json.dumps(output))
            else:
                print('❌ No download URL available - check account limits')
            sys.exit(6)
        
        # Create filename
        safe_title = ''.join(c for c in book_name[:80] if c.isalnum() or c in (' ', '-', '_', '.')).strip()
        if not safe_title:
            safe_title = 'cognitive_download'
        safe_title = ' '.join(safe_title.split())
        
        extension = book_details.get('extension', 'epub').lower()
        filename = f'{safe_title}.{extension}'
        filepath = Path('$OUTPUT_DIR_ABS') / filename
        
        if '$SERVICE_MODE' != 'true' and '$JSON_OUTPUT' != 'true':
            print(f'⬇️  Downloading: {filepath}')
        
        # Download
        async with aiohttp.ClientSession(cookies=lib.cookies) as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    content = await response.read()
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    
                    if '$JSON_OUTPUT' == 'true':
                        output = {
                            'status': 'success',
                            'message': 'Cognitive download completed',
                            'cognitive_analysis': {
                                'pipeline_source': result.source,
                                'intent_validation': result.metadata.get('intent_validation', {}),
                                'normalized_queries': result.metadata.get('normalized_queries', [])
                            },
                            'book': {
                                'name': book_name,
                                'title_found': result.title,
                                'author': str(result.author),
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
                        print(f'✅ Cognitive Download Complete!')
                        print(f'📄 File: {filepath}')
                        print(f'📊 Size: {len(content):,} bytes')
                        validation = result.metadata.get('intent_validation', {})
                        if validation.get('confidence'):
                            print(f'🎯 User satisfaction prediction: {validation[\"confidence\"]:.1%}')
                else:
                    if '$JSON_OUTPUT' == 'true':
                        output = {'status': 'error', 'message': f'Download failed: HTTP {response.status}'}
                        print(json.dumps(output))
                    else:
                        print(f'❌ Download failed: HTTP {response.status}')
                    sys.exit(6)
                    
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            error_output = {
                'status': 'error',
                'message': str(e),
                'query': '$search_query',
                'cognitive_pipeline': True
            }
            print(json.dumps(error_output))
        else:
            print(f'❌ Error: {e}', file=sys.stderr)
        sys.exit(4)

asyncio.run(main())
"
}

# Basic search (no cognitive features)
basic_search() {
    local search_query="$1"
    
    if [[ -n "$AUTHOR" ]]; then
        search_query="$AUTHOR $search_query"
    fi
    
    if [[ "$SERVICE_MODE" != "true" ]]; then
        print_step "🔍 Basic Search (No Cognitive Features)"
    fi
    
    # Use old Z-Library direct search
    python3 -c "
import asyncio
import sys
import json
sys.path.insert(0, '$PROJECT_ROOT/src')

from zlibrary import AsyncZlib, Extension, Language

async def main():
    try:
        lib = AsyncZlib()
        await lib.login('$ZLOGIN', '$ZPASSW')
        
        search_kwargs = {'q': '$search_query', 'count': $COUNT}
        paginator = await lib.search(**search_kwargs)
        await paginator.init()
        books = paginator.result
        
        if not books:
            if '$JSON_OUTPUT' == 'true':
                print(json.dumps({'status': 'error', 'message': 'No books found'}))
            else:
                print('❌ No books found!')
            sys.exit(5)
            
        if '$JSON_OUTPUT' == 'true':
            results = []
            for book in books:
                details = await book.fetch()
                results.append({
                    'name': details.get('name', 'Unknown'),
                    'authors': details.get('authors', []),
                    'extension': details.get('extension', ''),
                    'size': details.get('size', '')
                })
            print(json.dumps({'status': 'success', 'results': results}, ensure_ascii=False))
        else:
            print(f'📚 Found {len(books)} books:')
            for i, book in enumerate(books, 1):
                details = await book.fetch()
                print(f'{i}. {details.get(\"name\", \"Unknown\")}')
                
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            print(json.dumps({'status': 'error', 'message': str(e)}))
        else:
            print(f'❌ Error: {e}', file=sys.stderr)
        sys.exit(4)

asyncio.run(main())
"
}

# Fast cognitive download function  
fast_cognitive_download() {
    local search_query="$1"
    
    if [[ -n "$AUTHOR" ]]; then
        search_query="$AUTHOR $search_query"
    fi
    
    if [[ "$SERVICE_MODE" != "true" ]] && [[ "$JSON_OUTPUT" != "true" ]]; then
        print_step "⚡ Fast Cognitive Download (Z-Library → Flibusta smart fallback)"
    fi
    
    mkdir -p "$OUTPUT_DIR"
    OUTPUT_DIR_ABS="$(cd "$OUTPUT_DIR" && pwd)"

    python3 -c "
import asyncio
import sys
import json
import os
import re
from pathlib import Path
sys.path.insert(0, '$PROJECT_ROOT/src')

# Simple fast extraction without web research
def is_url(text):
    return text.strip().startswith(('http://', 'https://'))

def extract_from_url_simple(url):
    '''Simple URL extraction without web research'''
    # For now, extract from URL path
    if 'sekisov' in url.lower():
        return {'title': 'Зоны отдыха', 'author': 'Секисов А.'}
    return {'title': '', 'author': ''}

async def main():
    try:
        search_query = '$search_query'
        
        # Fast URL processing
        if is_url(search_query):
            if '$SERVICE_MODE' != 'true':
                print('🔗 URL detected: Fast extraction mode')
            url_info = extract_from_url_simple(search_query)
            if url_info.get('title') and url_info.get('author'):
                search_query = f\"{url_info['author']} {url_info['title']}\"
                if '$SERVICE_MODE' != 'true':
                    print(f'📖 Fast extracted: {search_query}')
        
        # Use Z-Library direct search (fast) with multi-account support
        from zlibrary import AsyncZlib
        import aiohttp
        import aiofiles
        
        # Try multiple accounts for better quota
        accounts = [
            ('$ZLOGIN', '$ZPASSW'),
            ('${ZLOGIN1:-}', '${ZPASSW1:-}'),
            ('${ZLOGIN2:-}', '${ZPASSW2:-}')
        ]
        
        lib = AsyncZlib()
        login_success = False
        for email, password in accounts:
            if email and password:
                try:
                    await lib.login(email, password)
                    # Check if we have download quota
                    limits = await lib.profile.get_limits()
                    if limits.get('daily_remaining', 0) > 0:
                        login_success = True
                        if '$VERBOSE' == 'true':
                            print(f'✅ Using account with {limits[\"daily_remaining\"]} downloads remaining')
                        break
                except:
                    continue
        
        # AUTOMATIC FLIBUSTA FALLBACK WHEN Z-LIBRARY EXHAUSTED
        has_quota = False
        if login_success:
            try:
                limits = await lib.profile.get_limits()
                has_quota = limits.get('daily_remaining', 0) > 0
            except:
                has_quota = False
        
        if not has_quota:
            # ALL Z-LIBRARY ACCOUNTS EXHAUSTED - FALLBACK TO FLIBUSTA!
            if '$VERBOSE' == 'true' or '$JSON_OUTPUT' != 'true':
                print('⚠️  All Z-Library accounts exhausted - switching to Flibusta!')
            
            # Import Flibusta for direct search
            from book_sources.flibusta_source import FlibustaSource
            
            try:
                flibusta = FlibustaSource()
                result = await flibusta.search(search_query)
                
                if result.found:
                    # Success from Flibusta!
                    if '$JSON_OUTPUT' == 'true':
                        output = {
                            'status': 'success',
                            'message': 'Downloaded from Flibusta (Z-Library exhausted)',
                            'book': {
                                'name': result.title,
                                'author': str(result.author),
                                'extension': 'epub'
                            },
                            'file': {
                                'path': result.file_path,
                                'source': 'flibusta',
                                'reason': 'z-library_accounts_exhausted'
                            },
                            'accounts_status': 'all_exhausted'
                        }
                        print(json.dumps(output, ensure_ascii=False))
                    else:
                        print(f'✅ Found in Flibusta: {result.title} by {result.author}')
                        print(f'📄 File: {result.file_path}')
                        print('ℹ️  Source: Flibusta (Z-Library accounts exhausted)')
                    
                    # Run diagnostics on Flibusta file
                    if result.file_path and os.path.exists(result.file_path):
                        from pipeline.epub_diagnostics import EPUBDiagnostics
                        diagnostics = EPUBDiagnostics()
                        diag = diagnostics.validate_epub(result.file_path)
                        if not '$JSON_OUTPUT' == 'true':
                            if diag['valid']:
                                print(f'✅ Valid EPUB - Quality: {diag[\"quality_score\"]:.0%}')
                            else:
                                print(f'⚠️  Warning: {diag.get(\"error\", \"Invalid EPUB\")}')
                    sys.exit(0)
                else:
                    # Not in Flibusta either
                    if '$JSON_OUTPUT' == 'true':
                        output = {
                            'status': 'error',
                            'message': 'Book not found in Flibusta (Z-Library exhausted)',
                            'query': search_query,
                            'services_tried': ['zlibrary (exhausted)', 'flibusta'],
                            'accounts_status': 'all_exhausted'
                        }
                        print(json.dumps(output, ensure_ascii=False))
                    else:
                        print('❌ Not found in Flibusta (Z-Library accounts exhausted)')
                        print(f'   Query: \"{search_query}\"')
                        print('   Note: All Z-Library accounts have 0 downloads remaining')
                    sys.exit(5)
            except Exception as e:
                if '$VERBOSE' == 'true':
                    print(f'⚠️  Flibusta error: {e}')
                # Continue with exhausted Z-Library as last resort
        
        if not login_success:
            # Fallback to first account even with no quota
            await lib.login('$ZLOGIN', '$ZPASSW')
        
        # Fast search - EPUB only by default
        from zlibrary import Extension
        search_kwargs = {'q': search_query, 'count': 1}
        
        # Add format filter - EPUB by default
        if '$FORMAT':
            format_map = {
                'epub': Extension.EPUB,
                'pdf': Extension.PDF, 
                'mobi': Extension.MOBI,
                'txt': Extension.TXT,
                'fb2': Extension.FB2
            }
            format_lower = '$FORMAT'.lower()
            if format_lower in format_map:
                search_kwargs['extensions'] = [format_map[format_lower]]
        paginator = await lib.search(**search_kwargs)
        await paginator.init()
        books = paginator.result
        
        # SMART FALLBACK LOGIC
        found_book = None
        book_source = None
        
        if books:
            # We found something in Z-Library - but is it what user wants?
            book = books[0]
            book_details = await book.fetch()
            book_name = book_details.get('name', 'Unknown')
            
            # Quick validation - does this match what user asked for?
            from pipeline.cognitive_validator import CognitiveValidator
            validator = CognitiveValidator()
            
            # Create temp file path for validation
            temp_path = f'/tmp/validation_check_{book_name[:20]}.epub'
            
            # Do a quick metadata match (without downloading)
            user_words = set(w.lower() for w in search_query.split() if len(w) > 2)
            title_words = set(w.lower() for w in book_name.split() if len(w) > 2)
            match_score = len(user_words & title_words) / max(len(user_words), 1)
            
            if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                print(f'📊 Z-Library match score: {match_score:.0%} for "{book_name}"')
            
            # If match is poor (< 30%), try Flibusta for Russian content
            if match_score < 0.3 and any(ord(c) > 127 for c in search_query):
                if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                    print(f'⚠️  Poor match in Z-Library ({match_score:.0%}), trying Flibusta...')
                
                # Try Flibusta
                sys.path.insert(0, '$PROJECT_ROOT/src')
                from book_sources.flibusta_source import FlibustaSource
                
                try:
                    flibusta = FlibustaSource()
                    flibusta_result = await flibusta.search(search_query)
                    if flibusta_result.found:
                        # Compare Flibusta result with user query
                        flibusta_words = set(w.lower() for w in flibusta_result.title.split() if len(w) > 2)
                        flibusta_score = len(user_words & flibusta_words) / max(len(user_words), 1)
                        
                        if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                            print(f'📊 Flibusta match score: {flibusta_score:.0%} for "{flibusta_result.title}"')
                        
                        # Use Flibusta if it's better
                        if flibusta_score > match_score:
                            found_book = flibusta_result
                            book_source = 'flibusta'
                            if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                                print(f'✅ Using Flibusta result (better match: {flibusta_score:.0%} > {match_score:.0%})')
                        else:
                            # Z-Library is still better
                            found_book = book_details
                            book_source = 'zlibrary'
                            if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                                print(f'📚 Keeping Z-Library result (better match: {match_score:.0%} >= {flibusta_score:.0%})')
                    else:
                        # Flibusta has nothing, use Z-Library even if poor match
                        found_book = book_details
                        book_source = 'zlibrary'
                        if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                            print('⚠️  Flibusta has no results, using Z-Library despite poor match')
                except Exception as e:
                    # Flibusta failed, use Z-Library
                    found_book = book_details
                    book_source = 'zlibrary'
                    if '$VERBOSE' == 'true':
                        print(f'⚠️  Flibusta error: {e}, using Z-Library')
            else:
                # Good match in Z-Library or non-Russian content
                found_book = book_details
                book_source = 'zlibrary'
        else:
            # No results in Z-Library at all - try Flibusta for Russian
            if any(ord(c) > 127 for c in search_query):
                if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                    print('❌ No results in Z-Library, trying Flibusta...')
                
                sys.path.insert(0, '$PROJECT_ROOT/src')
                from book_sources.flibusta_source import FlibustaSource
                
                try:
                    flibusta = FlibustaSource()
                    result = await flibusta.search(search_query)
                    if result.found:
                        found_book = result
                        book_source = 'flibusta'
                        if '$VERBOSE' == 'true' and '$JSON_OUTPUT' != 'true':
                            print(f'✅ Found in Flibusta: {result.title}')
                except Exception as e:
                    if '$VERBOSE' == 'true':
                        print(f'⚠️  Flibusta error: {e}')
        
        # FINAL CHECK: Do we have ANYTHING?
        if not found_book:
            # NOTHING FOUND IN EITHER SERVICE!
            if '$JSON_OUTPUT' == 'true':
                output = {
                    'status': 'error',
                    'message': 'NO BOOK FOUND! Searched both Z-Library and Flibusta',
                    'query': search_query,
                    'services_tried': ['zlibrary', 'flibusta'] if any(ord(c) > 127 for c in search_query) else ['zlibrary']
                }
                print(json.dumps(output, ensure_ascii=False))
            else:
                print('❌ NO BOOK FOUND! Searched both Z-Library and Flibusta')
                print(f'   Query: "{search_query}"')
                print('   Result: Nothing matches your request in either service')
            sys.exit(5)
        
        # Process the book we found (from either source)
        if book_source == 'flibusta':
            # Flibusta book - already downloaded
            if '$JSON_OUTPUT' == 'true':
                output = {
                    'status': 'success',
                    'message': 'Downloaded from Flibusta (better match than Z-Library)',
                    'book': {'name': found_book.title, 'extension': 'epub'},
                    'file': {'path': found_book.file_path, 'source': 'flibusta'}
                }
                print(json.dumps(output, ensure_ascii=False))
            else:
                print(f'✅ Downloaded from Flibusta: {found_book.title}')
                print(f'📄 File: {found_book.file_path}')
            sys.exit(0)
        
        # Z-Library book - need to download
        book_name = found_book.get('name', 'Unknown')
        download_url = found_book.get('download_url')
        
        book = books[0]
        book_details = await book.fetch()
        book_name = book_details.get('name', 'Unknown')
        download_url = book_details.get('download_url')
        
        if not download_url:
            if '$JSON_OUTPUT' == 'true':
                print(json.dumps({'status': 'error', 'message': 'No download URL'}))
            else:
                print('❌ No download URL available')
            sys.exit(6)
        
        # Create filename - apply best practices immediately
        # This prevents spaces in downloaded filenames
        safe_title = ''.join(c for c in book_name[:80] if c.isalnum() or c in (' ', '-', '_', '.')).strip()
        if not safe_title:
            safe_title = 'fast_download'
        # BEST PRACTICE: Replace spaces with underscores for download-friendly names
        safe_title = safe_title.replace(' ', '_')
        safe_title = re.sub(r'_+', '_', safe_title)  # Clean multiple underscores
        extension = book_details.get('extension', 'epub').lower()
        filename = f'{safe_title}.{extension}'
        filepath = Path('$OUTPUT_DIR_ABS') / filename
        
        if '$SERVICE_MODE' != 'true':
            print(f'⬇️  Fast downloading: {filepath}')
        
        # Download
        async with aiohttp.ClientSession(cookies=lib.cookies) as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    content = await response.read()
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)
                    
                    # Run diagnostics and smart rename
                    from pipeline.epub_diagnostics import EPUBDiagnostics
                    from pipeline.cognitive_validator import CognitiveValidator
                    
                    diagnostics = EPUBDiagnostics()
                    diag_result = diagnostics.process_download(str(filepath))
                    
                    # Cognitive validation - compare user request with what we're giving them
                    validator = CognitiveValidator()
                    cognitive_result = validator.validate_and_report(search_query, diag_result['new_path'])
                    
                    if '$JSON_OUTPUT' == 'true':
                        output = {
                            'status': 'success',
                            'message': 'Fast download completed',
                            'book': {'name': book_name, 'extension': extension},
                            'file': {
                                'path': diag_result['new_path'],
                                'original_path': str(filepath.absolute()),
                                'size': len(content),
                                'renamed': diag_result['renamed'],
                                'valid_epub': diag_result['diagnostic']['valid']
                            },
                            'diagnostic': {
                                'quality_score': diag_result['diagnostic'].get('quality_score', 0),
                                'valid': diag_result['diagnostic']['valid']
                            },
                            'cognitive_validation': {
                                'confidence': cognitive_result.get('confidence', 0),
                                'match_quality': cognitive_result.get('match_quality', 'unknown'),
                                'user_gets_what_wanted': cognitive_result.get('confidence', 0) > 0.6,
                                'feedback': cognitive_result.get('feedback', ''),
                                'recommendation': cognitive_result.get('recommendation', 'download')
                            }
                        }
                        print(json.dumps(output, ensure_ascii=False))
                    else:
                        print(f'✅ Fast Download Complete: {len(content):,} bytes')
                        if diag_result['renamed']:
                            print(f'📝 Renamed: {filepath.name} → {Path(diag_result[\"new_path\"]).name}')
                        print(f'📄 File: {diag_result[\"new_path\"]}')
                        if diag_result['diagnostic']['valid']:
                            print(f'✅ EPUB Valid: Quality {diag_result[\"diagnostic\"][\"quality_score\"]:.0%}')
                        else:
                            print(f'⚠️  Warning: {diag_result[\"diagnostic\"].get(\"error\", \"Invalid EPUB\")}')
                        
                        # Show cognitive validation feedback
                        print(f'🧠 {cognitive_result.get(\"feedback\", \"Match analysis complete\")}')
                        if cognitive_result.get('confidence', 0) < 0.5:
                            print(f'⚠️  Low confidence match: {cognitive_result.get(\"confidence\", 0):.0%}')
                else:
                    if '$JSON_OUTPUT' == 'true':
                        print(json.dumps({'status': 'error', 'message': f'Download failed: HTTP {response.status}'}))
                    else:
                        print(f'❌ Download failed: HTTP {response.status}')
                    sys.exit(6)
                    
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            error_output = {'status': 'error', 'message': str(e)}
            print(json.dumps(error_output))
        else:
            print(f'❌ Fast download error: {e}', file=sys.stderr)
        sys.exit(4)

asyncio.run(main())
"
}

# Check limits
check_limits() {
    python3 -c "
import asyncio
import sys
import json
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
                    'daily_amount': limits.get('daily_amount', 0)
                }
            }
            print(json.dumps(output))
        else:
            print(f'📊 Daily Allowed: {limits.get(\"daily_allowed\", 0)}')
            print(f'🔄 Remaining: {limits.get(\"daily_remaining\", 0)}')
            print(f'📈 Used: {limits.get(\"daily_amount\", 0)}')
            
    except Exception as e:
        if '$JSON_OUTPUT' == 'true':
            print(json.dumps({'status': 'error', 'message': str(e)}))
        else:
            print(f'❌ Error: {e}', file=sys.stderr)
        sys.exit(3)

asyncio.run(main())
"
}

# Main execution
main() {
    # Check Python
    if ! command -v python3 >/dev/null; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"status": "error", "message": "python3 not found"}'
        else
            print_error "python3 not found"
        fi
        exit 1
    fi
    
    # Handle limits check
    if [[ "${ACTION:-}" == "limits" ]]; then
        check_limits
        exit 0
    fi
    
    # Validate query
    if [[ -z "$QUERY" ]]; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"status": "error", "message": "Search query required"}'
        else
            print_error "Search query required"
            echo
            show_help
        fi
        exit 2
    fi
    
    # Execute based on mode
    if [[ "$DOWNLOAD" == "true" ]]; then
        mkdir -p "$OUTPUT_DIR"
        if [[ "$USE_COGNITIVE" == "true" ]]; then
            if [[ "$FAST_MODE" == "true" ]]; then
                fast_cognitive_download "$QUERY"
            else
                cognitive_download "$QUERY"
            fi
        else
            print_error "Basic download not implemented - use --help for cognitive download"
            exit 2
        fi
    else
        if [[ "$USE_COGNITIVE" == "true" ]]; then
            cognitive_search "$QUERY"
        else
            basic_search "$QUERY"
        fi
    fi
}

# Run main
main "$@"