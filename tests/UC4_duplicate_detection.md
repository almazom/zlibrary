# UC4: Duplicate Detection Test Cases

## Feature: Prevent Re-downloading Already Downloaded Books
As a system managing downloads
I want to detect if a book is already downloaded
So that I avoid duplicate files and save bandwidth

## Scenario 1: Book Already Downloaded - Exact Match
**Given** I have "Clean_Code_Robert_Martin.epub" in downloads
**When** I search for "Clean Code Robert Martin" again
**Then** System should:
  - Detect existing file
  - Return path to existing file
  - NOT download again
  - Add flag `already_downloaded: true` in JSON

### Test Cases:
```bash
# Test 1.1: Exact title match
./scripts/book_search.sh "Clean Code Robert Martin"
# First run: Downloads file
# Second run: Returns existing file path

# Test 1.2: Case insensitive match
./scripts/book_search.sh "clean code robert martin"
# Should find existing "Clean_Code_Robert_Martin.epub"

# Test 1.3: Partial author match
./scripts/book_search.sh "Clean Code Martin"
# Should find if confidence high enough
```

## Scenario 2: Different Editions Detection
**Given** I have "1984_George_Orwell_2016.epub"
**When** I search for "1984 Orwell" 
**Then** System should:
  - Detect similar file exists
  - Check file size/year differences
  - Decide if it's same book or different edition
  - Return `similar_exists: true` with details

### Test Cases:
```bash
# Test 2.1: Same book, different year
existing: "1984_George_Orwell_2016.epub" (667KB)
search: "1984 George Orwell 2020 edition"
# Should detect as similar, ask user preference

# Test 2.2: Same title, different author
existing: "Clean_Code_Robert_Martin.epub"
search: "Clean Code Steve McConnell"  
# Should download as different book
```

## Scenario 3: Filename Variations
**Given** Downloaded files may have different naming patterns
**When** Searching for a book
**Then** System should handle:
  - Underscores vs spaces
  - Special characters removed
  - Truncated long titles
  - Unicode characters

### Test Cases:
```bash
# Test 3.1: Unicode handling
existing: "最危险的书_为乔伊斯的《尤利西斯》而战.epub"
search: "Ulysses James Joyce"
# Should detect as same book

# Test 3.2: Truncated title
existing: "The_Pragmatic_Programmer_From_Journey.epub" 
search: "The Pragmatic Programmer From Journeyman to Master"
# Should match despite truncation
```

## Implementation Strategy:

### 1. Create Downloads Index
```python
def build_downloads_index():
    index = {}
    for file in Path('./downloads').glob('*.epub'):
        # Normalize filename for matching
        normalized = normalize_title(file.stem)
        index[normalized] = {
            'path': str(file),
            'size': file.stat().st_size,
            'modified': file.stat().st_mtime
        }
    return index
```

### 2. Similarity Checking
```python
def check_duplicate(search_title, search_author):
    index = build_downloads_index()
    
    for normalized, file_info in index.items():
        # Check exact match
        if normalized == normalize_title(f"{search_title}_{search_author}"):
            return {'status': 'exact_match', 'file': file_info}
        
        # Check similarity score
        similarity = calculate_similarity(normalized, search_title)
        if similarity > 0.8:
            return {'status': 'similar_found', 'file': file_info, 'similarity': similarity}
    
    return {'status': 'not_found'}
```

### 3. Normalization Rules
```python
def normalize_title(title):
    # Lowercase
    title = title.lower()
    # Remove special chars
    title = re.sub(r'[^\w\s]', '', title)
    # Replace multiple spaces
    title = re.sub(r'\s+', '_', title)
    # Remove common words
    stop_words = ['the', 'a', 'an', 'and', 'or', 'but']
    words = title.split('_')
    title = '_'.join([w for w in words if w not in stop_words])
    return title
```

## Scenario 4: Storage Management
**Given** Limited disk space
**When** Duplicate detected
**Then** Options:
  - Replace if new version is better quality
  - Keep both with version suffix
  - Skip download and use existing

### Decision Matrix:
| Existing Size | New Size | Action |
|--------------|----------|---------|
| < 100KB | > 1MB | Replace (better quality) |
| > 1MB | > 1MB | Keep existing |
| Any | Same | Skip download |

## Scenario 5: Cache Management
**Given** System maintains download cache
**When** Cache becomes stale
**Then** System should:
  - Rebuild index on startup
  - Update after each download
  - Handle deleted files gracefully

## Edge Cases:
1. **Corrupted existing file** - Re-download if file < 10KB
2. **Multiple versions** - Keep best quality version
3. **Series detection** - "Harry Potter 1" vs "Harry Potter 2"
4. **Compilation books** - "Complete Works" vs individual books
5. **Translated titles** - Same book in different languages

## Success Metrics:
- ✅ Zero duplicate downloads for exact matches
- ✅ 90% detection rate for similar books
- ✅ < 100ms to check duplicates
- ✅ Correct handling of edge cases
- ✅ User-friendly duplicate warnings

## JSON Response Enhancement:
```json
{
  "result": {
    "found": true,
    "already_downloaded": true,
    "existing_file": {
      "path": "/downloads/Clean_Code.epub",
      "size": "4.1MB",
      "downloaded_date": "2025-08-08"
    },
    "duplicate_check": {
      "performed": true,
      "match_type": "exact",
      "confidence": 1.0
    }
  }
}
```

## Test Script:
```bash
#!/bin/bash
# Test duplicate detection

# Download a book
./scripts/book_search.sh "Atomic Habits"
file1=$(ls -t downloads/Atomic*.epub | head -1)

# Try downloading again
result=$(./scripts/book_search.sh "Atomic Habits")
already=$(echo "$result" | jq -r '.result.already_downloaded')

if [[ "$already" == "true" ]]; then
    echo "✅ Duplicate detection working"
else
    echo "❌ Duplicate not detected"
fi
```