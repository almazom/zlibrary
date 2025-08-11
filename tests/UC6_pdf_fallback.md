# UC6: PDF Fallback Test Cases

## Feature: Download PDF When EPUB Unavailable
As a system ensuring content availability
I want to fallback to PDF format
So that users get the book even if EPUB doesn't exist

## Scenario 1: EPUB Not Available, PDF Exists
**Given** A book has no EPUB version
**When** I search for the book
**Then** System should:
  - First search for EPUB
  - If not found, search for PDF
  - Download PDF with format indication
  - Return `format: "pdf"` in response

### Test Cases:
```bash
# Test 1.1: Book with only PDF
./scripts/book_search.sh --format auto "Technical Manual XYZ"
# Expected: Downloads PDF when no EPUB

# Test 1.2: Explicit PDF request
./scripts/book_search.sh --format pdf "Clean Code"
# Expected: Downloads PDF version directly

# Test 1.3: Format preference order
./scripts/book_search.sh --format epub,pdf "Programming Book"
# Expected: Try EPUB first, then PDF
```

## Scenario 2: Both Formats Available
**Given** Book exists in both EPUB and PDF
**When** Searching with auto mode
**Then** System should:
  - Prefer EPUB (smaller, better for reading)
  - Allow user to specify preference
  - Show both options in response

### Test Cases:
```bash
# Test 2.1: Default preference (EPUB)
./scripts/book_search.sh "1984 George Orwell"
# Expected: Downloads EPUB by default

# Test 2.2: Force PDF even if EPUB exists
./scripts/book_search.sh --format pdf "1984 George Orwell"
# Expected: Downloads PDF version

# Test 2.3: List available formats
./scripts/book_search.sh --list-formats "Clean Code"
# Expected: Shows epub, pdf, mobi available
```

## Scenario 3: Neither Format Available
**Given** No EPUB or PDF exists
**When** Searching for book
**Then** System should:
  - Report no suitable format found
  - List available formats if any
  - Suggest alternatives

### Test Cases:
```bash
# Test 3.1: No digital format
./scripts/book_search.sh "Rare Manuscript 1823"
# Expected: "No EPUB or PDF available"

# Test 3.2: Only exotic formats
./scripts/book_search.sh "Book only in DJVU"
# Expected: Reports DJVU available, suggests conversion
```

## Implementation Strategy:

### 1. Modify Search Function
```python
async def search_with_fallback(query, formats=['epub', 'pdf']):
    for format_type in formats:
        if format_type == 'epub':
            extension = Extension.EPUB
        elif format_type == 'pdf':
            extension = Extension.PDF
        else:
            continue
            
        results = await client.search(
            q=query,
            extensions=[extension],
            count=1
        )
        
        await results.init()
        if results.result:
            return results, format_type
    
    return None, None
```

### 2. Format Detection
```python
def detect_available_formats(book_info):
    formats = []
    
    # Check download URL or extension field
    extension = book_info.get('extension', '').lower()
    if extension:
        formats.append(extension)
    
    # Check size hints
    size_str = book_info.get('size', '')
    if 'pdf' in size_str.lower():
        formats.append('pdf')
    elif 'epub' in size_str.lower():
        formats.append('epub')
    
    return formats
```

### 3. Response Structure
```json
{
  "result": {
    "found": true,
    "format_downloaded": "pdf",
    "format_searched": ["epub", "pdf"],
    "fallback_used": true,
    "available_formats": ["pdf", "mobi"],
    "download_info": {
      "format": "pdf",
      "size": "5.2MB",
      "path": "/downloads/book.pdf"
    }
  }
}
```

## Scenario 4: Format Quality Comparison
**Given** Different formats have different quality
**When** Choosing format
**Then** Consider:
  - File size (PDF usually larger)
  - Readability (EPUB better for e-readers)
  - Features (EPUB has reflow, PDF has fixed layout)

### Quality Matrix:
| Format | Size | E-Reader | Phone | Computer |
|--------|------|----------|-------|----------|
| EPUB | Small | Excellent | Good | Good |
| PDF | Large | Poor | Fair | Excellent |

## Scenario 5: Batch Processing with Format Preference
**Given** Processing multiple books
**When** Some lack EPUB
**Then** Automatically fallback to PDF

### Test Cases:
```bash
# Batch with fallback
for book in "Book1" "Book2" "Book3"; do
    ./scripts/book_search.sh --format auto "$book"
done

# Expected: Mix of EPUB and PDF based on availability
```

## Edge Cases:
1. **Corrupted EPUB** - Fallback to PDF
2. **PDF too large** (>50MB) - Warn user
3. **Format mismatch** - File claims EPUB but is PDF
4. **DRM protected** - Skip and report
5. **Preview only** - Detect partial content

## Configuration:
```bash
# Set format preference
export ZLIB_FORMAT_PREFERENCE="epub,pdf,mobi"

# Maximum PDF size (MB)
export ZLIB_MAX_PDF_SIZE="30"

# Auto-fallback enabled
export ZLIB_AUTO_FALLBACK="true"
```

## Success Metrics:
- ✅ 100% of books downloadable (EPUB or PDF)
- ✅ Clear indication of format downloaded
- ✅ < 2s to try fallback format
- ✅ User preference respected
- ✅ File size warnings for large PDFs

## Test Script:
```bash
#!/bin/bash
# Test format fallback

echo "Testing EPUB preference..."
result=$(./scripts/book_search.sh "Clean Code")
format=$(echo "$result" | jq -r '.result.format_downloaded')
echo "Downloaded format: $format"

echo "Testing PDF fallback..."
result=$(./scripts/book_search.sh --format pdf "Clean Code")
format=$(echo "$result" | jq -r '.result.format_downloaded')
echo "Downloaded format: $format"

echo "Testing auto mode..."
result=$(./scripts/book_search.sh --format auto "Rare Technical Book")
fallback=$(echo "$result" | jq -r '.result.fallback_used')
echo "Fallback used: $fallback"
```