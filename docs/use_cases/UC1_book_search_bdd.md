# UC1: Book Search and Download - BDD Test Cases

## Feature: Z-Library Book Search with Automatic EPUB Download
As an external system
I want to search for books via CLI command
So that I get downloaded EPUB files with confidence scoring

## Background:
- System has 3 Z-Library accounts with 22 total downloads
- Downloads are saved to `./downloads/` directory
- Response is always JSON format
- Dual confidence system: match confidence + readability quality

## Scenario 1: Successful Book Search and Download
**Given** I have a valid book title and author
**When** I run `./scripts/book_search.sh "Clean Code Robert Martin"`
**Then** I should receive JSON with:
  - `status`: "success"
  - `result.found`: true
  - `result.epub_download_url`: "/path/to/downloads/Clean_Code_*.epub"
  - `result.download_info.available`: true
  - `result.confidence.level`: "HIGH" or "VERY_HIGH"
  - `result.readability.level`: "EXCELLENT" or "GOOD"
**And** the EPUB file should exist in downloads directory
**And** file size should be > 100KB

### Test Data:
```bash
# Test Case 1.1: Programming Book
./scripts/book_search.sh "Clean Code Robert Martin"
# Expected: 4.1MB EPUB, HIGH confidence

# Test Case 1.2: Popular Fiction
./scripts/book_search.sh "1984 George Orwell"
# Expected: 667KB EPUB, HIGH confidence

# Test Case 1.3: Self-Help Book
./scripts/book_search.sh "Atomic Habits James Clear"
# Expected: 3.0MB EPUB, HIGH confidence
```

## Scenario 2: Book Not Found
**Given** I search for a non-existent book
**When** I run `./scripts/book_search.sh "xyzabc123 nonexistent book"`
**Then** I should receive JSON with:
  - `status`: "not_found"
  - `result.found`: false
  - `result.message`: "No books found matching the search criteria"
**And** no file should be created in downloads directory

### Test Data:
```bash
# Test Case 2.1: Gibberish Title
./scripts/book_search.sh "qwerty12345 fake book"
# Expected: found=false

# Test Case 2.2: Random Characters
./scripts/book_search.sh "zzzz9999 imaginary title"
# Expected: found=false
```

## Scenario 3: Partial Match with Lower Confidence
**Given** I search with partial or unclear information
**When** I run `./scripts/book_search.sh "Ulysses"`
**Then** I should receive JSON with:
  - `status`: "success"
  - `result.found`: true
  - `result.confidence.score`: < 0.6 (possibly)
  - `result.confidence.recommended`: true/false based on score
**And** EPUB should still be downloaded if found

## Scenario 4: Account Fallback
**Given** first account has no downloads remaining
**When** I run any book search
**Then** system should automatically try next account
**And** return successful result if any account works
**And** JSON should not expose which account was used

## Scenario 5: All Accounts Exhausted
**Given** all 3 accounts have 0 downloads remaining
**When** I run `./scripts/book_search.sh "Any Book Title"`
**Then** I should receive JSON with:
  - `status`: "success" (book found but not downloaded)
  - `result.found`: true
  - `result.download_info.available`: false
  - `result.epub_download_url`: null

## Confidence Scoring Rules:

### Match Confidence Levels:
- **VERY_HIGH** (≥0.8): Exact title and author match
- **HIGH** (≥0.6): Most words match, likely correct
- **MEDIUM** (≥0.4): Some words match, possibly correct
- **LOW** (<0.4): Few matches, probably wrong book

### Readability Quality Levels:
- **EXCELLENT** (≥0.8): Large file (>1MB), has publisher
- **GOOD** (≥0.65): Medium file, readable
- **FAIR** (<0.65): Small file, basic quality

## Validation Script:
```bash
#!/bin/bash
# test_book_search.sh

echo "=== UC1: Testing Book Search BDD Scenarios ==="

# Scenario 1: Successful download
echo -e "\n📚 Test 1: Valid Book"
result=$(./scripts/book_search.sh "Python Crash Course")
found=$(echo "$result" | jq -r '.result.found')
file=$(echo "$result" | jq -r '.result.epub_download_url')

if [[ "$found" == "true" ]] && [[ -f "$file" ]]; then
    echo "✅ PASS: Book found and downloaded"
else
    echo "❌ FAIL: Expected download"
fi

# Scenario 2: Not found
echo -e "\n📚 Test 2: Non-existent Book"
result=$(./scripts/book_search.sh "xyz999 fake book")
found=$(echo "$result" | jq -r '.result.found')

if [[ "$found" == "false" ]]; then
    echo "✅ PASS: Correctly reported not found"
else
    echo "❌ FAIL: Should report not found"
fi

# Scenario 3: Check confidence
echo -e "\n📚 Test 3: Confidence Scoring"
result=$(./scripts/book_search.sh "Clean Code")
confidence=$(echo "$result" | jq -r '.result.confidence.level')
readability=$(echo "$result" | jq -r '.result.readability.level')

echo "Confidence: $confidence"
echo "Readability: $readability"

if [[ -n "$confidence" ]] && [[ -n "$readability" ]]; then
    echo "✅ PASS: Dual confidence scores present"
else
    echo "❌ FAIL: Missing confidence scores"
fi
```

## API Contract:
```typescript
interface BookSearchResponse {
  status: "success" | "not_found" | "error";
  timestamp: string;
  input_format: "txt" | "url" | "image";
  query_info: {
    original_input: string;
    extracted_query: string;
  };
  result: {
    found: boolean;
    epub_download_url: string | null;  // Full path to downloaded file
    download_info: {
      available: boolean;
      url: string | null;
      local_path: string | null;
    };
    confidence?: {
      score: number;        // 0.0 to 1.0
      level: string;        // VERY_HIGH, HIGH, MEDIUM, LOW
      description: string;
      recommended: boolean;
    };
    readability?: {
      score: number;        // 0.0 to 1.0
      level: string;        // EXCELLENT, GOOD, FAIR
      description: string;
      factors: string[];
    };
    book_info?: {
      title: string;
      authors: string[];
      year: string;
      publisher: string;
      size: string;
      description: string;
    };
    service_used: "zlibrary";
  };
}
```

## Edge Cases to Test:
1. **Unicode titles**: "最危险的书 Ulysses"
2. **Special characters**: "C++ Programming"
3. **Long titles**: Books with 100+ character titles
4. **No author**: Just book title search
5. **Multiple results**: When multiple editions exist
6. **Network timeout**: Slow Z-Library response
7. **Corrupted download**: Partial file download

## Success Metrics:
- ✅ Book found → EPUB downloaded in < 10 seconds
- ✅ Not found → Clear JSON response in < 5 seconds
- ✅ Confidence score → Always between 0.0 and 1.0
- ✅ File integrity → Downloaded EPUB > 10KB
- ✅ Account fallback → Transparent to user