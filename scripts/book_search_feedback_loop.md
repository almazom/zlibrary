# Book Search Feedback Development Loop

## Problem Statement
When searching for books from URLs, the system may find incorrect books with the same title but different authors. Example: "Лунный камень" by Милорад Павич vs. Уилки Коллинз.

## Current Issues Identified

### 1. Language Detection Issue
- **Problem**: URL extraction returns transliterated text instead of original language
- **Example**: "lunnyy kamen" instead of "Лунный камень"
- **Solution**: ALWAYS use Claude cognitive extraction with `--claude-extract` flag

### 2. Author Mismatch Issue  
- **Problem**: Z-Library returns first match by title, ignoring author
- **Example**: Searching "Лунный камень Милорад Павич" returns Wilkie Collins book
- **Solution**: Implement author validation and confidence scoring

### 3. Language Preference Issue
- **Problem**: System doesn't prioritize books in the request language
- **Example**: Russian URL should prioritize Russian language books
- **Solution**: Detect source language and add language filters

## Feedback Loop Implementation

### Step 1: Enhanced URL Extraction (COMPLETED)
```bash
# Always use Claude cognitive layer for extraction
CLAUDE_EXTRACT=true ./scripts/book_search.sh --claude-extract "URL"
```

**Extraction Prompt Template:**
```
This is a URL to a page with a book. Extract:
- title: Book title EXACTLY as written in ORIGINAL LANGUAGE
- author: Author's FULL NAME in ORIGINAL LANGUAGE
- language: detected language of the book
Return ONLY JSON object.
```

### Step 2: Author Validation (TO IMPLEMENT)
```python
def validate_author(extracted_author, found_author):
    """
    Compare extracted author from URL with found book author
    Returns confidence score 0.0 to 1.0
    """
    # Normalize names for comparison
    # Handle different name formats (First Last vs Last, First)
    # Handle Cyrillic vs Latin transliteration
    pass
```

### Step 3: Language-Aware Search (TO IMPLEMENT)
```bash
# Detect language from extracted data
if [[ "$extracted_language" == "Russian" ]]; then
    SEARCH_LANGUAGES="--lang ru,russian"
elif [[ "$extracted_language" == "English" ]]; then
    SEARCH_LANGUAGES="--lang en,english"
fi
```

### Step 4: Confidence Scoring Enhancement
Current confidence factors:
- Title match
- Year match  
- Publisher match

**Add new factors:**
- Author match (weight: 0.4)
- Language match (weight: 0.2)
- Source domain match (weight: 0.1)

### Step 5: Fallback Strategies
If confidence < 0.6:
1. Try searching with quotes: "\"Лунный камень\" \"Милорад Павич\""
2. Try author-first search: "Милорад Павич Лунный камень"
3. Try with transliteration: "Milorad Pavić Moonstone"
4. Alert user about mismatch

## Testing Protocol

### Test Cases
1. **Same title, different authors:**
   - URL: https://eksmo.ru/book/lunnyy-kamen-ITD1334449/ (Павич)
   - Expected: "Лунный камень" by Милорад Павич
   - Current: FAILS - returns Wilkie Collins

2. **Russian books from Russian sites:**
   - URL: https://alpinabook.ru/catalog/book-pishi-sokrashchay/
   - Expected: "Пиши, сокращай" by Ильяхов
   - Current: Works with extraction

3. **English books from English sites:**
   - URL: https://www.goodreads.com/book/show/[id]
   - Expected: Correct English book
   - Current: Needs testing

### Validation Script
```bash
#!/bin/bash
# test_book_extraction.sh

test_urls=(
    "https://eksmo.ru/book/lunnyy-kamen-ITD1334449/|Милорад Павич|Лунный камень"
    "https://alpinabook.ru/catalog/book-atomnye-privychki/|James Clear|Atomic Habits"
)

for test_case in "${test_urls[@]}"; do
    IFS='|' read -r url expected_author expected_title <<< "$test_case"
    result=$(CLAUDE_EXTRACT=true ./scripts/book_search.sh --claude-extract "$url")
    # Validate author and title match
done
```

## Monitoring & Metrics

### Success Metrics
- **Extraction Accuracy**: % of URLs correctly parsed
- **Author Match Rate**: % of correct author matches
- **Language Match Rate**: % of correct language books
- **User Satisfaction**: Reduced wrong book downloads

### Logging Enhancement
```json
{
  "extraction": {
    "url": "...",
    "extracted_title": "...",
    "extracted_author": "...",
    "extracted_language": "..."
  },
  "search": {
    "query_used": "...",
    "results_count": 10,
    "top_result": {...}
  },
  "validation": {
    "author_match": 0.2,
    "title_match": 0.9,
    "language_match": 0.5,
    "final_confidence": 0.4
  },
  "decision": "rejected_low_confidence"
}
```

## Implementation Priority

1. **IMMEDIATE**: Always use `--claude-extract` for URL inputs
2. **HIGH**: Implement author validation in confidence scoring
3. **MEDIUM**: Add language detection and filtering
4. **LOW**: Create comprehensive test suite

## User Communication

When confidence is low, inform user:
```
⚠️ Found: "Лунный камень" by Уильям Уилки Коллинз
   Expected: "Лунный камень" by Милорад Павич
   Confidence: 40% (author mismatch)
   
   Try searching manually with: "Милорад Павич Лунный камень"
```

## Next Steps

1. Implement author validation function
2. Add language detection to extraction
3. Enhance confidence scoring algorithm
4. Create test suite with diverse URLs
5. Add user feedback mechanism