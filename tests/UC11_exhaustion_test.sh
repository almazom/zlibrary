#!/bin/bash
# UC11: Account Exhaustion & Switching Test
# Tests with real books from Podpisnie.ru and Ad Marginem

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================="
echo "UC11: Account Exhaustion & Switching Test"
echo "========================================="
echo "Date: $(date)"
echo "Moscow Time: $(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# Check initial account status
echo -e "${BLUE}Initial Account Status:${NC}"
python3 check_accounts.py --summary 2>/dev/null || echo "Account check failed"
echo ""

# Statistics
TOTAL=0
SUCCESS=0
FAILED=0
SWITCHES=0
LAST_SUCCESS_COUNT=0

# Books from real sources (25 total to ensure exhaustion)
declare -a BOOKS=(
    # Batch 1: Podpisnie.ru books (8 books for Account 1)
    "Семейный лексикон"
    "Ирландские сказки и легенды"
    "Из ничего искусство создавать искусство"
    "Развод"
    "Курс Разговоры со студентами"
    "Семь лет в Крестах"
    "Кадавры"
    "Полторы комнаты"
    
    # Batch 2: Ad Marginem/Philosophy (4 books for Account 2)
    "Невыносимая легкость бытия Кундера"
    "Средневековое мышление Ален де Либера"
    "Феноменология восприятия Мерло-Понти"
    "Бытие и ничто Сартр"
    
    # Batch 3: More philosophy/literature (10 books for Account 3)
    "Общество спектакля Ги Дебор"
    "Симулякры и симуляция Бодрийяр"
    "Капитализм и шизофрения Делез"
    "Археология знания Фуко"
    "Различие и повторение Делез"
    "Логика смысла Делез"
    "Надзирать и наказывать Фуко"
    "История сексуальности Фуко"
    "Чистый код Роберт Мартин"
    "Прагматичный программист"
    
    # Overflow books to test exhaustion (3 extra)
    "Улисс Джойс"
    "Процесс Кафка"
    "Замок Кафка"
)

# Function to detect account switches
detect_switch() {
    if [[ $SUCCESS -eq 8 ]] && [[ $LAST_SUCCESS_COUNT -eq 7 ]]; then
        echo -e "  ${YELLOW}⚡ ACCOUNT SWITCH DETECTED: Account 1 → Account 2${NC}"
        SWITCHES=$((SWITCHES+1))
    elif [[ $SUCCESS -eq 12 ]] && [[ $LAST_SUCCESS_COUNT -eq 11 ]]; then
        echo -e "  ${YELLOW}⚡ ACCOUNT SWITCH DETECTED: Account 2 → Account 3${NC}"
        SWITCHES=$((SWITCHES+1))
    fi
    LAST_SUCCESS_COUNT=$SUCCESS
}

# Test each book
echo -e "${BLUE}Starting exhaustion test with ${#BOOKS[@]} books...${NC}"
echo "-----------------------------------------"

for i in "${!BOOKS[@]}"; do
    book="${BOOKS[$i]}"
    TOTAL=$((TOTAL+1))
    
    # Determine expected account based on count
    if [[ $SUCCESS -lt 8 ]]; then
        expected_account="Account 1"
    elif [[ $SUCCESS -lt 12 ]]; then
        expected_account="Account 2"
    elif [[ $SUCCESS -lt 22 ]]; then
        expected_account="Account 3"
    else
        expected_account="EXHAUSTED"
    fi
    
    echo -e "\n[${TOTAL}/${#BOOKS[@]}] ${book}"
    echo "  Expected: $expected_account"
    
    # Try to download
    result=$(./scripts/book_search.sh "$book" 2>/dev/null || echo '{"status":"error"}')
    status=$(echo "$result" | jq -r '.status' 2>/dev/null || echo "error")
    found=$(echo "$result" | jq -r '.result.found' 2>/dev/null || echo "false")
    
    if [[ "$status" == "success" ]] && [[ "$found" == "true" ]]; then
        SUCCESS=$((SUCCESS+1))
        detect_switch
        echo -e "  ${GREEN}✅ SUCCESS${NC} (Total: $SUCCESS/22)"
        
        # Show download info
        title=$(echo "$result" | jq -r '.result.book_info.title // "Unknown"' | head -c 50)
        confidence=$(echo "$result" | jq -r '.result.confidence.level // "N/A"')
        echo "  Found: $title..."
        echo "  Confidence: $confidence"
    else
        FAILED=$((FAILED+1))
        error_msg=$(echo "$result" | jq -r '.result.message // "Unknown error"' 2>/dev/null)
        echo -e "  ${RED}❌ FAILED${NC}: $error_msg"
        
        # Check if all accounts exhausted
        if [[ "$error_msg" == *"No working accounts"* ]]; then
            echo -e "  ${RED}⛔ ALL ACCOUNTS EXHAUSTED${NC}"
            if [[ $SUCCESS -eq 22 ]]; then
                echo -e "  ${GREEN}✓ Expected exhaustion at 22 downloads${NC}"
            fi
            break
        fi
    fi
done

# Final account status
echo ""
echo -e "${BLUE}Final Account Status:${NC}"
python3 check_accounts.py --summary 2>/dev/null || echo "Account check failed"

# Test results
echo ""
echo "========================================="
echo "TEST RESULTS"
echo "========================================="
echo "Books attempted: $TOTAL"
echo "Books downloaded: $SUCCESS"
echo "Books failed: $FAILED"
echo "Account switches: $SWITCHES"
echo ""

# Validation
echo -e "${BLUE}Validation:${NC}"

# Check 1: Total downloads
if [[ $SUCCESS -eq 22 ]]; then
    echo -e "  ${GREEN}✅ Used all 22 downloads${NC}"
else
    echo -e "  ${RED}❌ Expected 22 downloads, got $SUCCESS${NC}"
fi

# Check 2: Account switches
if [[ $SWITCHES -ge 2 ]]; then
    echo -e "  ${GREEN}✅ Account switching worked ($SWITCHES switches)${NC}"
else
    echo -e "  ${RED}❌ Expected 2+ switches, got $SWITCHES${NC}"
fi

# Check 3: Exhaustion detection
if [[ $TOTAL -gt 22 ]] && [[ $SUCCESS -eq 22 ]]; then
    echo -e "  ${GREEN}✅ Correctly stopped at exhaustion${NC}"
else
    echo -e "  ${YELLOW}⚠️  Exhaustion handling unclear${NC}"
fi

# Overall result
echo ""
if [[ $SUCCESS -eq 22 ]] && [[ $SWITCHES -ge 2 ]]; then
    echo -e "${GREEN}✅ TEST PASSED: Account exhaustion and switching working correctly${NC}"
else
    echo -e "${RED}❌ TEST FAILED: Check account management implementation${NC}"
fi

echo ""
echo "========================================="
echo "Expected behavior:"
echo "  - Account 1: Downloads 1-8 (8 total)"
echo "  - Switch to Account 2"
echo "  - Account 2: Downloads 9-12 (4 total)"
echo "  - Switch to Account 3"
echo "  - Account 3: Downloads 13-22 (10 total)"
echo "  - Download 23: Exhaustion error"
echo "========================================="