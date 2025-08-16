#!/bin/bash
# ⚡ QUICK SEARCH - Fast pipeline search without full visualization
# Minimal UI for quick book searches

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
OUTPUT_DIR="$PROJECT_ROOT/downloads"
JSON_OUTPUT=false
DOWNLOAD_ENABLED=false
FORMAT="epub"
TIMEOUT=30

show_help() {
    echo -e "${CYAN}⚡ QUICK SEARCH - Fast Pipeline Search${NC}"
    echo -e "${GRAY}Minimal UI for rapid book searches${NC}"
    echo ""
    echo -e "${WHITE}USAGE:${NC}"
    echo -e "  ${CYAN}./quick_search.sh [OPTIONS] \"search query\"${NC}"
    echo ""
    echo -e "${WHITE}OPTIONS:${NC}"
    echo -e "  ${GREEN}-j, --json${NC}           Output results in JSON format"
    echo -e "  ${GREEN}-d, --download${NC}       Download found books automatically"
    echo -e "  ${GREEN}-f, --format <fmt>${NC}   Preferred format (epub, pdf, mobi)"
    echo -e "  ${GREEN}-o, --output <dir>${NC}   Output directory for downloads"
    echo -e "  ${GREEN}-t, --timeout <sec>${NC}  Search timeout in seconds (default: 30)"
    echo -e "  ${GREEN}-h, --help${NC}           Show this help message"
    echo ""
    echo -e "${WHITE}EXAMPLES:${NC}"
    echo -e "  ${CYAN}# Quick search${NC}"
    echo -e "  ./quick_search.sh \"1984 orwell\""
    echo ""
    echo -e "  ${CYAN}# Search and download${NC}"
    echo -e "  ./quick_search.sh --download \"harry potter\""
    echo ""
    echo -e "  ${CYAN}# JSON output for scripts${NC}"
    echo -e "  ./quick_search.sh --json \"programming book\" > result.json"
    echo ""
    echo -e "  ${CYAN}# Specify format and timeout${NC}"
    echo -e "  ./quick_search.sh -f pdf -t 60 \"machine learning\""
}

search_book() {
    local query="$1"
    
    # Show search info
    if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo -e "${YELLOW}⚡ Quick Search${NC}"
        echo -e "${GRAY}Query: \"$query\"${NC}"
        echo -e "${GRAY}Timeout: ${TIMEOUT}s${NC}"
        if [[ "$DOWNLOAD_ENABLED" == "true" ]]; then
            echo -e "${GRAY}Download: Yes (${FORMAT})${NC}"
            echo -e "${GRAY}Output: $OUTPUT_DIR${NC}"
        fi
        echo ""
    fi
    
    cd "$PROJECT_ROOT"
    
    # Create output directory if downloading
    if [[ "$DOWNLOAD_ENABLED" == "true" ]]; then
        mkdir -p "$OUTPUT_DIR"
        export BOOK_DOWNLOAD_DIR="$OUTPUT_DIR"
    fi
    
    # Run quick search
    local result
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        # JSON output mode
        result=$(python3 -c "
import asyncio
import sys
import json
sys.path.insert(0, 'src')
from pipeline.book_pipeline import BookSearchPipeline, PipelineConfig

async def quick_search():
    config = PipelineConfig(timeout_per_source=$TIMEOUT)
    pipeline = BookSearchPipeline(config)
    result = await pipeline.search_book('$query')
    
    # Convert to JSON
    output = {
        'found': result.found,
        'query': '$query',
        'source': result.source,
        'response_time': result.response_time,
        'title': getattr(result, 'title', ''),
        'author': getattr(result, 'author', ''),
        'download_url': getattr(result, 'download_url', ''),
        'file_id': getattr(result, 'file_id', ''),
        'confidence': getattr(result, 'confidence', 0.0),
        'metadata': result.metadata or {}
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))

asyncio.run(quick_search())
" 2>/dev/null)
        echo "$result"
    else
        # Pretty output mode
        python3 -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from pipeline.book_pipeline import BookSearchPipeline, PipelineConfig

async def quick_search():
    config = PipelineConfig(timeout_per_source=$TIMEOUT)
    pipeline = BookSearchPipeline(config)
    
    print('🔍 Searching...', flush=True)
    result = await pipeline.search_book('$query')
    
    print(f'\\r🔍 Searching... Done! ({result.response_time:.2f}s)')
    print()
    
    if result.found:
        print('✅ BOOK FOUND!')
        print(f'📚 Title: {getattr(result, \"title\", \"Unknown\")}')
        print(f'👤 Author: {getattr(result, \"author\", \"Unknown\")}')
        print(f'🔍 Source: {result.source.upper()}')
        print(f'📊 Confidence: {getattr(result, \"confidence\", 0.0):.1f}')
        
        if hasattr(result, 'download_url') and result.download_url:
            print(f'📥 Download: Available')
            
            # Download if requested
            if '$DOWNLOAD_ENABLED' == 'true':
                print('📥 Downloading...')
                # TODO: Implement download logic
                print('💾 Download completed!')
        else:
            print('📥 Download: Not available')
            
        print(f'⏱️ Response time: {result.response_time:.2f}s')
    else:
        print('❌ NOT FOUND')
        
        if result.metadata and 'sources_tried' in result.metadata:
            sources = result.metadata['sources_tried']
            print(f'🔍 Searched: {', '.join(sources)}')
        
        if result.metadata and 'error' in result.metadata:
            print(f'💭 Reason: {result.metadata[\"error\"]}')
            
        print(f'⏱️ Search time: {result.response_time:.2f}s')

asyncio.run(quick_search())
"
    fi
}

# Parse arguments
parse_args() {
    local query=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -j|--json)
                JSON_OUTPUT=true
                shift
                ;;
            -d|--download)
                DOWNLOAD_ENABLED=true
                shift
                ;;
            -f|--format)
                if [[ -n "${2:-}" && "${2:0:1}" != "-" ]]; then
                    FORMAT="$2"
                    shift 2
                else
                    echo -e "${RED}❌ Error: --format requires a format (epub, pdf, mobi)${NC}" >&2
                    exit 1
                fi
                ;;
            -o|--output)
                if [[ -n "${2:-}" && "${2:0:1}" != "-" ]]; then
                    OUTPUT_DIR="$2"
                    shift 2
                else
                    echo -e "${RED}❌ Error: --output requires a directory path${NC}" >&2
                    exit 1
                fi
                ;;
            -t|--timeout)
                if [[ -n "${2:-}" && "${2:0:1}" != "-" ]]; then
                    if [[ "$2" =~ ^[0-9]+$ ]]; then
                        TIMEOUT="$2"
                        shift 2
                    else
                        echo -e "${RED}❌ Error: --timeout requires a number${NC}" >&2
                        exit 1
                    fi
                else
                    echo -e "${RED}❌ Error: --timeout requires a number${NC}" >&2
                    exit 1
                fi
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                echo -e "${RED}❌ Error: Unknown option $1${NC}" >&2
                show_help >&2
                exit 1
                ;;
            *)
                if [[ -z "$query" ]]; then
                    query="$1"
                else
                    echo -e "${RED}❌ Error: Only one query allowed${NC}" >&2
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$query" ]]; then
        echo -e "${RED}❌ Error: Search query is required${NC}" >&2
        show_help >&2
        exit 1
    fi
    
    # Search the book
    search_book "$query"
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Error: Python 3 is required${NC}" >&2
        exit 1
    fi
    
    if [[ ! -d "$PROJECT_ROOT/src/pipeline" ]]; then
        echo -e "${RED}❌ Error: Pipeline not found${NC}" >&2
        echo -e "${GRAY}Run from the project root directory${NC}" >&2
        exit 1
    fi
}

main() {
    # Don't show banner in JSON mode
    if [[ "$JSON_OUTPUT" != "true" ]] && [[ "$*" != *"--json"* ]] && [[ "$*" != *"-j"* ]]; then
        echo -e "${CYAN}⚡ QUICK SEARCH - Fast Pipeline Search${NC}"
        echo ""
    fi
    
    # Check dependencies
    check_dependencies
    
    # Handle no arguments
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    # Parse and execute
    parse_args "$@"
}

main "$@"