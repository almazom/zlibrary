# Book Search Improvement Plan

## Success Criteria

### Primary Goals
1. **Author Accuracy**: ≥95% correct author matches for URL inputs
2. **Language Accuracy**: ≥90% correct language books for source website language
3. **ISBN Priority**: 100% exact matches when ISBN is available
4. **User Clarity**: 100% transparency when confidence is low

### Measurable Metrics
- **Extraction Success Rate**: % of URLs successfully parsed with title + author
- **Author Match Rate**: % of searches returning correct author
- **Language Match Rate**: % of searches returning book in expected language
- **ISBN Hit Rate**: % of successful searches when ISBN provided
- **User Warning Rate**: % of low-confidence results with clear warnings

## Implementation Plan

### Phase 1: Author Validation (PRIORITY: HIGH)
**Goal**: Detect and warn about author mismatches

#### Step 1.1: Add Author Comparison Function
```bash
# In book_search.sh
compare_authors() {
    local expected_author="$1"
    local found_author="$2"
    
    # Normalize for comparison (lowercase, remove punctuation)
    local norm_expected=$(echo "$expected_author" | tr '[:upper:]' '[:lower:]' | sed 's/[.,]//g')
    local norm_found=$(echo "$found_author" | tr '[:upper:]' '[:lower:]' | sed 's/[.,]//g')
    
    if [[ "$norm_expected" == *"$norm_found"* ]] || [[ "$norm_found" == *"$norm_expected"* ]]; then
        echo "1.0"  # Full match
    elif [[ "${norm_expected:0:3}" == "${norm_found:0:3}" ]]; then
        echo "0.3"  # Partial match
    else
        echo "0.0"  # No match
    fi
}
```

#### Step 1.2: Integrate into Confidence Scoring
```bash
# Add to calculate_confidence()
if [[ -n "$EXTRACTED_AUTHOR" ]]; then
    author_score=$(compare_authors "$EXTRACTED_AUTHOR" "$found_author")
    confidence=$(echo "$confidence + ($author_score * 0.4)" | bc)
fi
```

#### Success Test:
```bash
URL="https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"
# Should detect: Expected "Милорад Павич", Found "Уилки Коллинз"
# Confidence should drop below 0.5
```

### Phase 2: ISBN-Based Search (PRIORITY: HIGH)
**Goal**: Use ISBN for exact matches when available

#### Step 2.1: Extract ISBN from URLs
```python
# In extraction process
isbn = extract_isbn_from_page(url)
if isbn:
    return {"isbn": isbn, "title": title, "author": author}
```

#### Step 2.2: Search by ISBN First
```python
# In zlibrary search
if isbn:
    result = await client.search(q=isbn, exact=True)
    if result and result.found:
        return result
# Fallback to title+author search
```

#### Success Test:
```bash
# Book with ISBN should return exact match
URL="https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"  # ISBN: 978-5-04-185167-5
# Should find exact book by ISBN
```

### Phase 3: Search Retry Strategies (PRIORITY: MEDIUM)
**Goal**: Try alternative search patterns on mismatch

#### Step 3.1: Implement Retry Logic
```bash
search_with_retries() {
    local query="$1"
    local expected_author="$2"
    
    # Try 1: Original query
    result=$(search_zlibrary "$query")
    
    # Try 2: If author mismatch, search "author title"
    if [[ $(compare_authors "$expected_author" "$result_author") < 0.5 ]]; then
        result=$(search_zlibrary "$expected_author $title")
    fi
    
    # Try 3: Try with quotes
    if [[ $(compare_authors "$expected_author" "$result_author") < 0.5 ]]; then
        result=$(search_zlibrary "\"$title\" \"$expected_author\"")
    fi
    
    return "$result"
}
```

#### Success Test:
```bash
# Should try multiple search patterns
./scripts/book_search.sh "https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"
# Log should show: Try 1, Try 2, Try 3 attempts
```

### Phase 4: Language Filtering (PRIORITY: MEDIUM)
**Goal**: Prioritize books in source website language

#### Step 4.1: Detect Source Language
```bash
detect_source_language() {
    local domain="$1"
    case "$domain" in
        *.ru) echo "russian" ;;
        *.fr) echo "french" ;;
        *.de) echo "german" ;;
        *) echo "english" ;;
    esac
}
```

#### Step 4.2: Add Language Filter
```python
# In search
source_lang = detect_source_language(url)
results = await client.search(q=query, lang=[source_lang])
```

#### Success Test:
```bash
# Russian URL should prioritize Russian books
URL="https://eksmo.ru/..."  # Should add lang=russian filter
URL="https://amazon.com/..." # Should add lang=english filter
```

### Phase 5: User Warnings (PRIORITY: HIGH)
**Goal**: Clear communication about mismatches

#### Step 5.1: Add Warning Messages
```json
{
  "warning": {
    "type": "author_mismatch",
    "message": "⚠️ Author mismatch detected",
    "expected": "Милорад Павич",
    "found": "Уилки Коллинз",
    "suggestion": "Try manual search: 'Милорад Павич Лунный камень'"
  }
}
```

#### Success Test:
```bash
# Should show warning when confidence < 0.5
./scripts/book_search.sh "https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"
# Output: "⚠️ Author mismatch: Expected 'Милорад Павич', found 'Уилки Коллинз'"
```

## Test Suite

### Test Cases
```bash
#!/bin/bash
# test_book_accuracy.sh

test_urls=(
    # Russian books
    "https://eksmo.ru/book/lunnyy-kamen-ITD1334449/|Милорад Павич|Лунный камень|ru"
    "https://alpinabook.ru/catalog/book-pishi-sokrashchay-2025/|Максим Ильяхов|Пиши сокращай|ru"
    
    # English books  
    "https://www.goodreads.com/book/show/3735293-clean-code|Robert Martin|Clean Code|en"
    "https://amazon.com/Atomic-Habits-dp-0735211299|James Clear|Atomic Habits|en"
    
    # Books with ISBN
    "https://eksmo.ru/book/978-5-04-185167-5|Милорад Павич|Лунный камень|978-5-04-185167-5"
    
    # Edge cases
    "https://podpisnie.ru/books/misticheskiy-mir|Новалис|Мистический мир|ru"
)

PASSED=0
FAILED=0

for test_case in "${test_urls[@]}"; do
    IFS='|' read -r url expected_author expected_title expected_lang <<< "$test_case"
    
    echo "Testing: $url"
    result=$(./scripts/book_search.sh "$url")
    
    # Validate author match
    found_author=$(echo "$result" | jq -r '.result.book_info.authors[0]')
    if [[ "$found_author" == *"$expected_author"* ]]; then
        echo "✓ Author match"
        ((PASSED++))
    else
        echo "✗ Author mismatch: Expected '$expected_author', got '$found_author'"
        ((FAILED++))
    fi
done

echo "Results: $PASSED passed, $FAILED failed"
echo "Success rate: $(( PASSED * 100 / (PASSED + FAILED) ))%"
```

## Execution Timeline

### Week 1 (Immediate)
- [x] Day 1: Define success criteria
- [ ] Day 2: Implement author validation
- [ ] Day 3: Add ISBN search priority
- [ ] Day 4: Implement user warnings
- [ ] Day 5: Initial testing

### Week 2 (Enhancement)
- [ ] Day 6-7: Search retry strategies
- [ ] Day 8-9: Language filtering
- [ ] Day 10: Comprehensive testing

### Week 3 (Polish)
- [ ] Day 11-12: Performance optimization
- [ ] Day 13: Documentation
- [ ] Day 14: Final validation

## Success Validation

### Acceptance Criteria
✅ All test URLs return correct author (≥95% accuracy)
✅ ISBN searches return exact matches (100% accuracy)
✅ User sees clear warnings for mismatches (100% coverage)
✅ Russian sites prioritize Russian books (≥90% accuracy)
✅ Search retries improve success rate by ≥20%

### Monitoring
```bash
# Run daily validation
./test_book_accuracy.sh | tee -a test_results_$(date +%Y%m%d).log

# Generate metrics
grep "Success rate" test_results_*.log | tail -7  # Weekly trend
```

## Rollback Plan
If new changes cause issues:
1. Keep original `book_search.sh` as `book_search_v1.sh`
2. Test new version as `book_search_v2.sh`
3. Symlink active version: `ln -sf book_search_v2.sh book_search.sh`
4. Easy rollback: `ln -sf book_search_v1.sh book_search.sh`