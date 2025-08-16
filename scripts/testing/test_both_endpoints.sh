#!/bin/bash

# Test Both Endpoints: book_search.sh and Telegram Bot Integration
# This script demonstrates:
# 1. Direct book_search.sh functionality
# 2. Bot service integration with book_search.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== TESTING BOTH ENDPOINTS ===${NC}"
echo ""

# Test 1: Direct book_search.sh script
echo -e "${YELLOW}1. Testing book_search.sh script directly${NC}"
echo "   Command: ./scripts/book_search.sh \"Python Programming\""

if ./scripts/book_search.sh "Python Programming" > /tmp/book_search_result.json 2>/dev/null; then
    echo -e "${GREEN}   ✓ book_search.sh script works${NC}"
    
    # Show key results
    confidence=$(cat /tmp/book_search_result.json | jq -r '.result.confidence.score // "N/A"')
    title=$(cat /tmp/book_search_result.json | jq -r '.result.book_info.title // "N/A"')
    status=$(cat /tmp/book_search_result.json | jq -r '.status // "N/A"')
    
    echo -e "   Status: ${status}"
    echo -e "   Found: ${title}"
    echo -e "   Confidence: ${confidence}"
else
    echo -e "${RED}   ✗ book_search.sh script failed${NC}"
fi

echo ""

# Test 2: Bot service integration test
echo -e "${YELLOW}2. Testing Bot Service Integration${NC}"

# Check if bot is running
if docker ps | grep -q epub-bot; then
    echo -e "${GREEN}   ✓ Bot container is running${NC}"
    
    # Test the book search service directly
    echo "   Testing BookSearchService integration..."
    
    # Create a simple Python test for the service
    cat > /tmp/test_bot_service.py << 'EOF'
import asyncio
import sys
import os

# Add the telegram_bot path to sys.path
sys.path.insert(0, '/home/almaz/microservices/zlibrary_api_module/telegram_bot')

from models import UserInput
from services.book_search_service import BookSearchService

async def test_service():
    """Test the BookSearchService integration with book_search.sh"""
    
    service = BookSearchService(confidence_threshold=0.4, timeout=60)
    
    # Test with text input
    user_input = UserInput(text="Clean Code Robert Martin", input_type="text")
    
    try:
        result = await service.search_book(user_input)
        
        if result:
            print(f"SUCCESS: Found book - {result.title}")
            print(f"Author: {result.author}")
            print(f"Confidence: {result.confidence}")
            print(f"EPUB Path: {result.epub_path}")
            return True
        else:
            print("INFO: No book found with sufficient confidence")
            return False
            
    except Exception as e:
        print(f"ERROR: Service test failed - {e}")
        return False

# Run the test
if __name__ == "__main__":
    try:
        result = asyncio.run(test_service())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"FATAL: {e}")
        sys.exit(1)
EOF

    # Run the service test
    cd telegram_bot
    if python /tmp/test_bot_service.py; then
        echo -e "${GREEN}   ✓ Bot service integration works${NC}"
        echo -e "     Bot service successfully calls book_search.sh"
    else
        echo -e "${RED}   ✗ Bot service integration failed${NC}"
    fi
    cd ..
else
    echo -e "${RED}   ✗ Bot container is not running${NC}"
    echo -e "     Use: cd telegram_bot && docker-compose up -d"
fi

echo ""

# Test 3: Show integration architecture
echo -e "${YELLOW}3. Integration Architecture Summary${NC}"
echo -e "   Flow: ${BLUE}Telegram Message → Bot Handler → BookSearchService → book_search.sh → Z-Library → EPUB${NC}"
echo ""
echo -e "   Components:"
echo -e "   • ${GREEN}book_search.sh${NC}        - Core script with Z-Library integration"
echo -e "   • ${GREEN}BookSearchService${NC}     - Python service wrapper"
echo -e "   • ${GREEN}Bot Handlers${NC}          - Telegram message processors"
echo -e "   • ${GREEN}Docker Container${NC}      - Isolated bot environment"

echo ""

# Test 4: Show available options
echo -e "${YELLOW}4. Available Endpoints & Options${NC}"
echo ""
echo -e "${BLUE}book_search.sh options:${NC}"
./scripts/book_search.sh --help | head -20

echo ""
echo -e "${BLUE}Bot interaction:${NC}"
echo "   • Send any text to @epub_toc_based_sample_bot"
echo "   • Bot processes it as a book search query"
echo "   • Returns EPUB download or search results"
echo "   • Uses book_search.sh backend with --claude-extract for URLs"

echo ""
echo -e "${GREEN}=== ENDPOINT TESTING COMPLETE ===${NC}"

# Cleanup
rm -f /tmp/book_search_result.json /tmp/test_bot_service.py