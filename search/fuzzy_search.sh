#!/bin/bash
# 🌟 FUZZY SEARCH RUNNER - Specialized fuzzy input demonstrations
# Showcase AI normalization and language-aware routing

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Predefined fuzzy queries for demonstration
declare -A FUZZY_QUERIES=(
    ["english_fuzzy"]="hary poter filosofer stone"
    ["russian_transliteration"]="malenkiy prinz"
    ["mixed_language"]="dostoevsky преступление punishment"
    ["war_peace"]="voyna i mir tolstoy"
    ["misspelled_classic"]="shakesbeer hamlet"
    ["author_fuzzy"]="tolken lord rings"
    ["russian_fuzzy"]="chekhov вишневый sad"
    ["numbers_fuzzy"]="orwell 1984 nineteen eighty four"
)

show_help() {
    echo -e "${MAGENTA}🌟 FUZZY SEARCH DEMONSTRATIONS${NC}"
    echo -e "${GRAY}Specialized runner for fuzzy input visualization${NC}"
    echo ""
    echo -e "${WHITE}USAGE:${NC}"
    echo -e "  ${CYAN}./fuzzy_search.sh [PRESET|QUERY]${NC}"
    echo ""
    echo -e "${WHITE}PRESET FUZZY QUERIES:${NC}"
    echo -e "  ${GREEN}english_fuzzy${NC}           \"hary poter filosofer stone\""
    echo -e "  ${GREEN}russian_transliteration${NC} \"malenkiy prinz\""
    echo -e "  ${GREEN}mixed_language${NC}          \"dostoevsky преступление punishment\""
    echo -e "  ${GREEN}war_peace${NC}              \"voyna i mir tolstoy\""
    echo -e "  ${GREEN}misspelled_classic${NC}     \"shakesbeer hamlet\""
    echo -e "  ${GREEN}author_fuzzy${NC}           \"tolken lord rings\""
    echo -e "  ${GREEN}russian_fuzzy${NC}          \"chekhov вишневый sad\""
    echo -e "  ${GREEN}numbers_fuzzy${NC}          \"orwell 1984 nineteen eighty four\""
    echo ""
    echo -e "${WHITE}EXAMPLES:${NC}"
    echo -e "  ${CYAN}# Run preset fuzzy query${NC}"
    echo -e "  ./fuzzy_search.sh english_fuzzy"
    echo ""
    echo -e "  ${CYAN}# Custom fuzzy query${NC}"
    echo -e "  ./fuzzy_search.sh \"your fuzzy query here\""
    echo ""
    echo -e "  ${CYAN}# Run all preset demonstrations${NC}"
    echo -e "  ./fuzzy_search.sh --all"
    echo ""
    echo -e "${WHITE}FUZZY INPUT FEATURES:${NC}"
    echo -e "  ${YELLOW}🤖${NC} AI normalization (Claude SDK)"
    echo -e "  ${YELLOW}🌍${NC} Language detection and routing"
    echo -e "  ${YELLOW}✨${NC} Spelling correction"
    echo -e "  ${YELLOW}🔤${NC} Transliteration handling"
    echo -e "  ${YELLOW}📚${NC} Context-aware book title recognition"
}

run_preset_query() {
    local preset="$1"
    local query="${FUZZY_QUERIES[$preset]}"
    
    echo -e "${CYAN}🌟 Running preset: ${WHITE}$preset${NC}"
    echo -e "${GRAY}Fuzzy input: \"$query\"${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    python3 demo_pipeline_visual.py "$query"
    
    echo -e "\n${GREEN}✅ Preset '$preset' completed!${NC}"
}

run_custom_query() {
    local query="$1"
    
    echo -e "${CYAN}🔍 Running custom fuzzy search${NC}"
    echo -e "${GRAY}Input: \"$query\"${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    python3 demo_pipeline_visual.py "$query"
    
    echo -e "\n${GREEN}✅ Custom fuzzy search completed!${NC}"
}

run_all_presets() {
    echo -e "${MAGENTA}🚀 COMPLETE FUZZY DEMONSTRATION${NC}"
    echo -e "${GRAY}Running all preset fuzzy queries to showcase AI normalization${NC}"
    echo ""
    
    local count=0
    local total=${#FUZZY_QUERIES[@]}
    
    for preset in "${!FUZZY_QUERIES[@]}"; do
        ((count++))
        echo -e "${BLUE}═══ Demo $count/$total: $preset ═══${NC}"
        
        run_preset_query "$preset"
        
        if [[ $count -lt $total ]]; then
            echo -e "\n${GRAY}⏳ Next demo in 2 seconds...${NC}"
            sleep 2
        fi
    done
    
    echo -e "\n${GREEN}🎉 All fuzzy demonstrations completed!${NC}"
    echo -e "${CYAN}📊 Tested $total different fuzzy input patterns${NC}"
}

show_fuzzy_examples() {
    echo -e "${YELLOW}🌟 FUZZY INPUT EXAMPLES${NC}"
    echo ""
    
    echo -e "${WHITE}English Misspellings:${NC}"
    echo -e "  \"hary poter\" → \"Harry Potter\""
    echo -e "  \"shakesbeer\" → \"Shakespeare\""
    echo -e "  \"tolken\" → \"Tolkien\""
    echo ""
    
    echo -e "${WHITE}Russian Transliteration:${NC}"
    echo -e "  \"malenkiy prinz\" → \"Маленький принц\""
    echo -e "  \"voyna i mir\" → \"Война и мир\""
    echo -e "  \"dostoevsky\" → \"Достоевский\""
    echo ""
    
    echo -e "${WHITE}Mixed Language:${NC}"
    echo -e "  \"dostoevsky преступление\" → Context-aware search"
    echo -e "  \"chekhov вишневый sad\" → \"Cherry Orchard\""
    echo ""
    
    echo -e "${WHITE}Number Variations:${NC}"
    echo -e "  \"1984 nineteen eighty four\" → \"1984\""
    echo -e "  \"451 fahrenheit\" → \"Fahrenheit 451\""
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Error: Python 3 is required${NC}"
        exit 1
    fi
    
    if [[ ! -f "$PROJECT_ROOT/demo_pipeline_visual.py" ]]; then
        echo -e "${RED}❌ Error: Pipeline visualizer not found${NC}"
        echo -e "${GRAY}Run from the project root directory${NC}"
        exit 1
    fi
}

main() {
    # Show banner
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║${NC} 🌟 ${WHITE}FUZZY SEARCH RUNNER${NC} - AI Normalization Demo ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Handle arguments
    if [[ $# -eq 0 ]]; then
        show_help
        echo ""
        show_fuzzy_examples
        exit 0
    fi
    
    case "$1" in
        -h|--help)
            show_help
            ;;
        --all)
            run_all_presets
            ;;
        --examples)
            show_fuzzy_examples
            ;;
        *)
            # Check if it's a preset
            if [[ -n "${FUZZY_QUERIES[$1]:-}" ]]; then
                run_preset_query "$1"
            else
                # Treat as custom query
                run_custom_query "$1"
            fi
            ;;
    esac
    
    echo ""
    echo -e "${MAGENTA}🌟 Fuzzy Search Runner - Session Complete! ✨${NC}"
}

main "$@"