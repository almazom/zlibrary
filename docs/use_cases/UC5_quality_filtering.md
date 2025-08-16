# UC5: Quality and Confidence Filtering Test Cases

## Feature: Filter Downloads by Quality and Confidence Thresholds
As a system ensuring quality
I want to only download books above certain thresholds
So that users get high-quality, accurate matches

## Scenario 1: Minimum Confidence Filtering
**Given** I set minimum confidence to 0.7
**When** I search for a book
**Then** System should:
  - Calculate match confidence
  - Skip download if confidence < 0.7
  - Return reason for skipping
  - Suggest manual review

### Test Cases:
```bash
# Test 1.1: High confidence - should download
./scripts/book_search.sh --min-confidence 0.7 "Clean Code Robert Martin"
# Expected: Downloads (confidence usually > 0.7)

# Test 1.2: Low confidence - should skip
./scripts/book_search.sh --min-confidence 0.9 "Code"
# Expected: Skip download, confidence too low

# Test 1.3: Exact match - maximum confidence
./scripts/book_search.sh --min-confidence 0.95 "1984 George Orwell"
# Expected: Downloads if exact match found
```

## Scenario 2: Minimum Quality Filtering
**Given** I set minimum quality to "GOOD"
**When** Book quality is assessed
**Then** System should:
  - Check file size (> 100KB)
  - Check metadata completeness
  - Verify it's actual EPUB (not placeholder)
  - Skip if quality below threshold

### Test Cases:
```bash
# Test 2.1: Quality threshold EXCELLENT
./scripts/book_search.sh --min-quality EXCELLENT "Atomic Habits"
# Expected: Only download if size > 1MB and has publisher

# Test 2.2: Quality threshold GOOD
./scripts/book_search.sh --min-quality GOOD "Python Crash Course"
# Expected: Download if reasonable size

# Test 2.3: Any quality accepted
./scripts/book_search.sh --min-quality ANY "Random Book"
# Expected: Download regardless of quality
```

## Scenario 3: Combined Filtering
**Given** Both confidence and quality thresholds set
**When** Searching for books
**Then** Both conditions must be met

### Test Cases:
```bash
# Test 3.1: High standards
./scripts/book_search.sh --min-confidence 0.8 --min-quality EXCELLENT "Clean Architecture"
# Expected: Only download if both conditions met

# Test 3.2: Balanced requirements
./scripts/book_search.sh --min-confidence 0.6 --min-quality GOOD "Design Patterns"
# Expected: More permissive, higher success rate
```

## Implementation Strategy:

### 1. Add Command Line Parameters
```bash
# In book_search.sh
--min-confidence FLOAT   # 0.0 to 1.0 (default: 0.4)
--min-quality LEVEL      # EXCELLENT|GOOD|FAIR|ANY (default: ANY)
--strict                 # Shortcut for --min-confidence 0.8 --min-quality GOOD
```

### 2. Quality Assessment Logic
```python
def assess_quality(book_info):
    score = 0.5  # Base score
    factors = []
    
    # File size check
    size_str = book_info.get('size', '')
    if 'MB' in size_str:
        size_mb = float(size_str.split()[0])
        if size_mb > 2:
            score += 0.3
            factors.append("Large file (>2MB)")
        elif size_mb > 0.5:
            score += 0.2
            factors.append("Good file size")
    elif 'KB' in size_str:
        size_kb = float(size_str.split()[0])
        if size_kb < 100:
            score -= 0.2
            factors.append("Small file (<100KB)")
    
    # Metadata completeness
    if book_info.get('publisher'):
        score += 0.1
        factors.append("Has publisher")
    if book_info.get('year'):
        score += 0.05
        factors.append("Has year")
    if book_info.get('description'):
        score += 0.05
        factors.append("Has description")
    
    # Rating check
    rating = book_info.get('rating', '0')
    if float(rating) > 4.0:
        score += 0.1
        factors.append("High rating")
    
    return min(score, 1.0), factors
```

### 3. Decision Matrix
```python
def should_download(confidence, quality, min_conf=0.4, min_qual="ANY"):
    # Check confidence threshold
    if confidence < min_conf:
        return False, f"Confidence {confidence:.2f} below threshold {min_conf}"
    
    # Check quality threshold
    quality_levels = {
        "EXCELLENT": 0.8,
        "GOOD": 0.65,
        "FAIR": 0.5,
        "ANY": 0.0
    }
    
    min_qual_score = quality_levels.get(min_qual, 0.0)
    if quality < min_qual_score:
        return False, f"Quality {quality:.2f} below {min_qual} threshold"
    
    return True, "Meets all criteria"
```

## Scenario 4: Batch Processing with Filters
**Given** Processing multiple books
**When** Filters applied
**Then** Report statistics

### Test Cases:
```bash
# Process book list with filters
cat book_list.txt | while read book; do
    ./scripts/book_search.sh --min-confidence 0.6 "$book"
done

# Expected output:
# ✅ 8/10 books downloaded
# ❌ 2 skipped (low confidence: 1, low quality: 1)
```

## Scenario 5: User Override
**Given** Book below thresholds
**When** User wants it anyway
**Then** Provide override option

### Test Cases:
```bash
# Force download despite low scores
./scripts/book_search.sh --force "obscure book title"
# Expected: Downloads regardless of scores

# Interactive mode
./scripts/book_search.sh --interactive "book title"
# Expected: Asks user when below threshold
```

## JSON Response Enhancement:
```json
{
  "result": {
    "found": true,
    "downloaded": false,
    "skip_reason": "confidence_below_threshold",
    "thresholds": {
      "confidence_required": 0.7,
      "confidence_actual": 0.5,
      "quality_required": "GOOD",
      "quality_actual": "FAIR"
    },
    "recommendation": "Lower confidence threshold or search with more specific terms"
  }
}
```

## Edge Cases:
1. **No quality data** - Default to FAIR
2. **Corrupted metadata** - Skip with error
3. **Multiple editions** - Pick highest quality
4. **Series books** - Apply same threshold to all
5. **Retries** - Gradually lower thresholds

## Success Metrics:
- ✅ 95% of downloads meet quality threshold
- ✅ Zero downloads below confidence threshold
- ✅ Clear feedback on why skipped
- ✅ Easy to adjust thresholds
- ✅ Statistics tracking for batch jobs

## Configuration File Support:
```yaml
# ~/.zlibrary/filters.yaml
default:
  min_confidence: 0.6
  min_quality: GOOD

strict:
  min_confidence: 0.85
  min_quality: EXCELLENT
  
relaxed:
  min_confidence: 0.3
  min_quality: ANY
```