#!/bin/bash
# 🎨 VISUAL PIPELINE SEARCH - Beautiful terminal visualization
# Interactive book search with real-time pipeline transparency

set -euo pipefail

# Colors and emojis for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
SEARCH_MODE="visual"
QUERY=""
OUTPUT_DIR="$PROJECT_ROOT/downloads"
INTERACTIVE_MODE=false

# Help function
show_help() {
    echo -e "${BLUE}🎨 VISUAL PIPELINE SEARCH${NC}"
    echo -e "${GRAY}Beautiful terminal visualization for book search pipeline${NC}"
    echo ""
    echo -e "${WHITE}USAGE:${NC}"
    echo -e "  ${CYAN}./visual_search.sh [OPTIONS] \"search query\"${NC}"
    echo ""
    echo -e "${WHITE}OPTIONS:${NC}"
    echo -e "  ${GREEN}-i, --interactive${NC}     Interactive mode for multiple searches"
    echo -e "  ${GREEN}-d, --demo${NC}            Run fuzzy input demonstration"
    echo -e "  ${GREEN}-q, --quick <query>${NC}   Quick search with minimal UI"
    echo -e "  ${GREEN}-o, --output <dir>${NC}    Output directory for downloads"
    echo -e "  ${GREEN}-h, --help${NC}            Show this help message"
    echo ""
    echo -e "${WHITE}EXAMPLES:${NC}"
    echo -e "  ${CYAN}# Visual search with fuzzy input${NC}"
    echo -e "  ./visual_search.sh \"hary poter filosofer stone\""
    echo ""
    echo -e "  ${CYAN}# Interactive mode${NC}"
    echo -e "  ./visual_search.sh --interactive"
    echo ""
    echo -e "  ${CYAN}# Quick demo with fuzzy inputs${NC}"
    echo -e "  ./visual_search.sh --demo"
    echo ""
    echo -e "  ${CYAN}# Russian fuzzy input${NC}"
    echo -e "  ./visual_search.sh \"malenkiy prinz\""
    echo ""
    echo -e "${WHITE}PIPELINE VISUALIZATION:${NC}"
    echo -e "  ${YELLOW}🔍${NC} Input validation and sanitization"
    echo -e "  ${YELLOW}🤖${NC} Claude AI normalization (fuzzy → clean)"
    echo -e "  ${YELLOW}🎯${NC} Language-aware source routing"
    echo -e "  ${YELLOW}⚡${NC} Z-Library search (primary, fast)"
    echo -e "  ${YELLOW}🇷🇺${NC} Flibusta search (fallback, comprehensive)"
    echo -e "  ${YELLOW}📊${NC} Result compilation and statistics"
    echo ""
    echo -e "${GRAY}Requires: Python 3.8+, rich library${NC}"
}

# Check dependencies
check_dependencies() {
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Error: Python 3 is required${NC}"
        echo -e "${YELLOW}📦 Install Python 3.8+ and try again${NC}"
        exit 1
    fi
    
    # Check rich library
    if ! python3 -c "import rich" &> /dev/null; then
        echo -e "${YELLOW}⚠️  Warning: 'rich' library not found${NC}"
        echo -e "${CYAN}📦 Installing visualization dependencies...${NC}"
        
        if [[ -f "$PROJECT_ROOT/install_viz.sh" ]]; then
            cd "$PROJECT_ROOT" && ./install_viz.sh
        else
            pip3 install rich>=13.0.0
        fi
        
        echo -e "${GREEN}✅ Dependencies installed!${NC}"
    fi
    
    # Check if demo script exists
    if [[ ! -f "$PROJECT_ROOT/demo_pipeline_visual.py" ]]; then
        echo -e "${RED}❌ Error: Pipeline visualizer not found${NC}"
        echo -e "${GRAY}Expected: $PROJECT_ROOT/demo_pipeline_visual.py${NC}"
        exit 1
    fi
}

# Run visual search
run_visual_search() {
    local query="$1"
    
    echo -e "${BLUE}🎨 Starting Visual Pipeline Search...${NC}"
    echo -e "${GRAY}Query: \"$query\"${NC}"
    echo -e "${GRAY}Output: $OUTPUT_DIR${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # Set output directory
    export BOOK_DOWNLOAD_DIR="$OUTPUT_DIR"
    
    # Run visualization
    python3 demo_pipeline_visual.py "$query"
    
    echo -e "\n${GREEN}✅ Visual search completed!${NC}"
}

# Run interactive mode
run_interactive() {
    echo -e "${MAGENTA}🎮 Starting Interactive Visual Search...${NC}"
    echo -e "${GRAY}Output directory: $OUTPUT_DIR${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    export BOOK_DOWNLOAD_DIR="$OUTPUT_DIR"
    
    python3 demo_pipeline_visual.py --interactive
    
    echo -e "\n${GREEN}✅ Interactive session completed!${NC}"
}

# Run demo
run_demo() {
    echo -e "${CYAN}🌟 Starting Fuzzy Input Demonstration...${NC}"
    echo -e "${GRAY}This will show how the pipeline handles various fuzzy inputs${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    export BOOK_DOWNLOAD_DIR="$OUTPUT_DIR"
    
    python3 demo_pipeline_visual.py --demo
    
    echo -e "\n${GREEN}✅ Demo completed!${NC}"
}

# Quick search mode
run_quick_search() {
    local query="$1"
    
    echo -e "${YELLOW}⚡ Quick Search Mode${NC}"
    echo -e "${GRAY}Query: \"$query\"${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # Use simplified pipeline call
    python3 -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from pipeline.book_pipeline import BookSearchPipeline

async def quick_search():
    pipeline = BookSearchPipeline()
    result = await pipeline.search_book('$query')
    
    if result.found:
        print('✅ FOUND!')
        print(f'📚 Title: {result.title}')
        print(f'👤 Author: {result.author}') 
        print(f'🔍 Source: {result.source.upper()}')
        print(f'⏱️ Time: {result.response_time:.2f}s')
    else:
        print('❌ Not found')
        print(f'⏱️ Search time: {result.response_time:.2f}s')

asyncio.run(quick_search())
"
    
    echo -e "\n${GREEN}✅ Quick search completed!${NC}"
}

# Create output directory
ensure_output_dir() {
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        echo -e "${YELLOW}📁 Creating output directory: $OUTPUT_DIR${NC}"
        mkdir -p "$OUTPUT_DIR"
    fi
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--interactive)
                INTERACTIVE_MODE=true
                shift
                ;;
            -d|--demo)
                SEARCH_MODE="demo"
                shift
                ;;
            -q|--quick)
                SEARCH_MODE="quick"
                if [[ -n "${2:-}" && "${2:0:1}" != "-" ]]; then
                    QUERY="$2"
                    shift 2
                else
                    echo -e "${RED}❌ Error: --quick requires a search query${NC}"
                    exit 1
                fi
                ;;
            -o|--output)
                if [[ -n "${2:-}" && "${2:0:1}" != "-" ]]; then
                    OUTPUT_DIR="$2"
                    shift 2
                else
                    echo -e "${RED}❌ Error: --output requires a directory path${NC}"
                    exit 1
                fi
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                echo -e "${RED}❌ Error: Unknown option $1${NC}"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$QUERY" ]]; then
                    QUERY="$1"
                else
                    echo -e "${RED}❌ Error: Multiple queries not supported${NC}"
                    echo -e "${YELLOW}💡 Use --interactive for multiple searches${NC}"
                    exit 1
                fi
                shift
                ;;
        esac
    done
}

# Main function
main() {
    # Show banner
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} 🎨 ${WHITE}VISUAL PIPELINE SEARCH${NC} - Book Search Transparency ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Parse arguments
    parse_args "$@"
    
    # Check dependencies
    check_dependencies
    
    # Ensure output directory exists
    ensure_output_dir
    
    # Run appropriate mode
    if [[ "$INTERACTIVE_MODE" == "true" ]]; then
        run_interactive
    elif [[ "$SEARCH_MODE" == "demo" ]]; then
        run_demo
    elif [[ "$SEARCH_MODE" == "quick" ]]; then
        if [[ -z "$QUERY" ]]; then
            echo -e "${RED}❌ Error: Quick mode requires a search query${NC}"
            show_help
            exit 1
        fi
        run_quick_search "$QUERY"
    elif [[ "$SEARCH_MODE" == "visual" ]]; then
        if [[ -z "$QUERY" ]]; then
            echo -e "${YELLOW}💡 No query provided, starting demo mode${NC}"
            run_demo
        else
            run_visual_search "$QUERY"
        fi
    fi
    
    # Show final message
    echo ""
    echo -e "${BLUE}🎨 Visual Pipeline Search - Session Complete! ✨${NC}"
    echo -e "${GRAY}Results saved to: $OUTPUT_DIR${NC}"
}

# Run main function with all arguments
main "$@"