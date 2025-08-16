#!/bin/bash

# CLAUDE SDK BOOK NORMALIZER - Bash wrapper
# Uses claude command directly with proper prompt

normalize_book() {
    local input="$1"
    
    echo "🔍 Normalizing: '$input'"
    echo "----------------------------------------"
    
    # Use claude command with JSON output format
    claude -p "You are a book title normalization expert. Fix this book query and return ONLY valid JSON:

Input: \"$input\"

Fix these issues if present:
- Spelling errors and typos
- Missing soft signs (ь) in Russian (e.g., ведмак → ведьмак)  
- Complete partial titles
- Separate title from author
- Add proper punctuation

For 'ведмак 3 дикая охота':
- Fix to 'Ведьмак 3: Дикая Охота'
- Recognize as The Witcher 3: Wild Hunt

Return ONLY this JSON (no other text):
{
  \"original\": \"$input\",
  \"normalized\": \"corrected version\",
  \"confidence\": 0.95,
  \"language\": \"ru/en/mixed\",
  \"problems_found\": [\"typo\", \"missing_soft_sign\"],
  \"title\": \"book title\",
  \"author\": \"author if present\",
  \"series\": \"series if applicable\",
  \"explanation\": \"what was fixed\"
}" --json
}

# Test specific book
if [ $# -eq 0 ]; then
    echo "📚 CLAUDE SDK BOOK NORMALIZER TEST"
    echo "===================================="
    echo
    
    # Test cases
    echo "Test 1: Russian with typo"
    normalize_book "ведмак 3 дикая охота"
    echo
    
    echo "Test 2: English with typo"
    normalize_book "hary poter and the filosfer stone"
    echo
    
    echo "Test 3: Mixed/Modern"
    normalize_book "метро2033 глуховски"
    
else
    # Normalize provided input
    normalize_book "$*"
fi