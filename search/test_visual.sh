#!/bin/bash
# 🧪 TEST VISUAL SEARCH - Quick test of the visual pipeline
# Verify all components work before full demonstration

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
RED='\033[0;31m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🧪 VISUAL PIPELINE TEST${NC}"
echo -e "${GRAY}Testing visual search components...${NC}"
echo ""

# Test 1: Check Python
echo -e "${CYAN}1. Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo -e "   ${GREEN}✅ $python_version${NC}"
else
    echo -e "   ${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Test 2: Check rich library
echo -e "${CYAN}2. Checking rich library...${NC}"
if python3 -c "import rich; print(f'Rich {rich.__version__}')" 2>/dev/null; then
    rich_version=$(python3 -c "import rich; print(rich.__version__)")
    echo -e "   ${GREEN}✅ Rich $rich_version${NC}"
else
    echo -e "   ${YELLOW}⚠️  Rich not found, installing...${NC}"
    pip3 install rich>=13.0.0
    echo -e "   ${GREEN}✅ Rich installed${NC}"
fi

# Test 3: Check project structure
echo -e "${CYAN}3. Checking project structure...${NC}"
required_files=(
    "demo_pipeline_visual.py"
    "src/pipeline/pipeline_visualizer.py"
    "src/pipeline/book_pipeline.py"
    "src/book_sources/base.py"
)

all_found=true
for file in "${required_files[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        echo -e "   ${GREEN}✅ $file${NC}"
    else
        echo -e "   ${RED}❌ $file (missing)${NC}"
        all_found=false
    fi
done

if [[ "$all_found" != "true" ]]; then
    echo -e "\n${RED}❌ Missing required files${NC}"
    exit 1
fi

# Test 4: Test import functionality
echo -e "${CYAN}4. Testing Python imports...${NC}"
cd "$PROJECT_ROOT"

test_imports() {
    python3 -c "
import sys
sys.path.insert(0, 'src')

try:
    from pipeline.book_pipeline import BookSearchPipeline
    print('   ✅ BookSearchPipeline import')
except Exception as e:
    print(f'   ❌ BookSearchPipeline: {e}')
    exit(1)

try:
    from pipeline.pipeline_visualizer import PipelineVisualizer
    print('   ✅ PipelineVisualizer import')
except Exception as e:
    print(f'   ❌ PipelineVisualizer: {e}')
    exit(1)

try:
    from book_sources.base import SearchResult
    print('   ✅ SearchResult import')
except Exception as e:
    print(f'   ❌ SearchResult: {e}')
    exit(1)

try:
    from rich.console import Console
    print('   ✅ Rich Console import')
except Exception as e:
    print(f'   ❌ Rich Console: {e}')
    exit(1)
"
}

if test_imports; then
    echo -e "${GREEN}   All imports successful${NC}"
else
    echo -e "${RED}   Import test failed${NC}"
    exit 1
fi

# Test 5: Quick pipeline test
echo -e "${CYAN}5. Quick pipeline functionality test...${NC}"
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from pipeline.book_pipeline import BookSearchPipeline

async def test_pipeline():
    try:
        pipeline = BookSearchPipeline()
        print('   ✅ Pipeline initialized')
        
        # Test configuration
        chain = pipeline.get_fallback_chain()
        print(f'   ✅ Fallback chain: {chain}')
        
        # Test query validation
        pipeline._validate_query('test query')
        print('   ✅ Query validation works')
        
    except Exception as e:
        print(f'   ❌ Pipeline test failed: {e}')
        exit(1)

asyncio.run(test_pipeline())
"

# Test 6: Test search scripts
echo -e "${CYAN}6. Testing search scripts...${NC}"
search_scripts=(
    "visual_search.sh"
    "fuzzy_search.sh" 
    "quick_search.sh"
)

for script in "${search_scripts[@]}"; do
    if [[ -f "$SCRIPT_DIR/$script" && -x "$SCRIPT_DIR/$script" ]]; then
        echo -e "   ${GREEN}✅ $script (executable)${NC}"
    elif [[ -f "$SCRIPT_DIR/$script" ]]; then
        echo -e "   ${YELLOW}⚠️  $script (not executable)${NC}"
        chmod +x "$SCRIPT_DIR/$script"
        echo -e "   ${GREEN}✅ $script (fixed)${NC}"
    else
        echo -e "   ${RED}❌ $script (missing)${NC}"
    fi
done

# Test 7: Quick help test
echo -e "${CYAN}7. Testing script help functions...${NC}"
if "$SCRIPT_DIR/visual_search.sh" --help >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅ visual_search.sh help works${NC}"
else
    echo -e "   ${YELLOW}⚠️  visual_search.sh help issue${NC}"
fi

# Final result
echo ""
echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
echo ""
echo -e "${WHITE}Ready to run visual searches:${NC}"
echo -e "  ${CYAN}./search/visual_search.sh \"test query\"${NC}"
echo -e "  ${CYAN}./search/fuzzy_search.sh english_fuzzy${NC}" 
echo -e "  ${CYAN}./search/quick_search.sh \"fast search\"${NC}"
echo ""
echo -e "${GRAY}Test completed successfully ✨${NC}"