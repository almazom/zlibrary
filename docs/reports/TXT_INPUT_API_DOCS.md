# Text Input to EPUB API Documentation

## Overview
This service processes text input to find matching EPUB books with confidence scoring. It uses intelligent text analysis and the Z-Library search backend.

## API Endpoint

### CLI Interface
```bash
python3 txt_to_epub_cli.py "book title author keywords"
```

## Input Format
- **Type**: `txt` (text input)
- **Content**: Any text describing a book (title, author, keywords)
- **Examples**:
  - `"Harry Potter philosopher stone"`
  - `"Clean Code Robert Martin programming"`
  - `"Гарри Поттер философский камень"`

## Response Schema
The API ALWAYS returns this standardized JSON structure:

### Successful Search
```json
{
  "status": "success",
  "timestamp": "2025-08-08T15:49:19.840862",
  "input_format": "txt",
  "query_info": {
    "original_input": "Harry Potter philosopher stone",
    "extracted_query": "Harry Potter philosopher stone"
  },
  "result": {
    "found": true,
    "epub_download_url": null,
    "confidence": {
      "score": 1.0,
      "level": "VERY_HIGH",
      "description": "Очень высокая уверенность - это точно искомая книга",
      "recommended": true
    },
    "book_info": {
      "title": "Harry Potter and the Philosopher's Stone #1",
      "authors": ["J. K. Rowling"],
      "year": "1997",
      "publisher": "Pottermore P",
      "size": "761 KB",
      "description": "Rescued from the outrageous neglect of his aunt and uncle..."
    },
    "service_used": "zlibrary"
  }
}
```

## Text Processing Pipeline

### 1. Text Extraction
- Cleans and normalizes input text
- Removes special characters, keeps alphanumeric + spaces
- Limits to 10 words maximum for focused search

### 2. Query Building
- Converts cleaned text directly to search query
- Preserves important keywords and phrases
- Handles both Latin and Cyrillic text

### 3. Confidence Calculation
The confidence score (0.0-1.0) is calculated based on:

#### Word Overlap (Primary Factor)
- Compares input words with found book title
- Higher overlap = higher confidence

#### Exact Phrase Matching (+0.4 bonus)
- Significant boost if input text appears in book title

#### Author Detection (+0.3 bonus)
- Boost if author names from search result appear in input text

#### Language Consistency (+0.1 bonus)
- Bonus for matching Cyrillic/Latin text patterns

### 4. Confidence Levels
- **VERY_HIGH** (≥0.8): Точно искомая книга
- **HIGH** (≥0.6): Скорее всего нужная книга  
- **MEDIUM** (≥0.4): Возможно нужная книга
- **LOW** (≥0.2): Вряд ли искомая книга
- **VERY_LOW** (<0.2): Точно не та книга

## Test Results

### Comprehensive Testing (10 test cases)
- **Status OK**: 70.0% (7/10 tests)
- **Schema Valid**: 100.0% (10/10 tests)
- **Expectations Met**: 30.0% (3/10 tests)
- **Overall Score**: 66.7% - FAIR

### Sample Test Cases

#### ✅ Successful Cases
```bash
# VERY_HIGH confidence (1.0)
python3 txt_to_epub_cli.py "Harry Potter philosopher stone"

# HIGH confidence (0.6)  
python3 txt_to_epub_cli.py "Clean Code Robert Martin"

# MEDIUM confidence (0.433)
python3 txt_to_epub_cli.py "Maniac Benjamin Labatut"
```

#### ❌ Challenging Cases
- Random text: Search may fail
- Very short input: May cause search errors
- Gibberish text: Search will likely fail

## Error Handling

### Common Error Types
- `search_failed`: Backend search service error
- `timeout`: 30-second timeout exceeded
- `invalid_response`: Malformed JSON from search
- `invalid_usage`: Wrong command line usage

### Example Error Response
```json
{
  "status": "error",
  "timestamp": "2025-08-08T15:49:00Z",
  "input_format": "txt",
  "query_info": {
    "original_input": "invalid search text",
    "extracted_query": "invalid search text"
  },
  "result": {
    "error": "search_failed",
    "message": "Search service error: No results found"
  }
}
```

## Integration Examples

### Python Integration
```python
import subprocess
import json

def search_book_by_text(text):
    result = subprocess.run([
        'python3', 'txt_to_epub_cli.py', text
    ], capture_output=True, text=True)
    
    data = json.loads(result.stdout)
    
    if data['status'] == 'success':
        confidence = data['result']['confidence']
        if confidence['recommended']:
            return data['result']['book_info']
    
    return None

# Usage
book = search_book_by_text("Clean Code Robert Martin")
if book:
    print(f"Found: {book['title']} by {book['authors'][0]}")
```

### Shell Integration
```bash
#!/bin/bash
TEXT="$1"
RESULT=$(python3 txt_to_epub_cli.py "$TEXT")
RECOMMENDED=$(echo "$RESULT" | jq -r '.result.confidence.recommended // false')

if [ "$RECOMMENDED" = "true" ]; then
    echo "✅ Book found and recommended!"
    echo "$RESULT" | jq -r '.result.book_info.title'
else
    echo "❌ No suitable book found"
fi
```

### FastAPI Integration
```python
from fastapi import FastAPI
import subprocess
import json

app = FastAPI()

@app.post("/search-text")
async def search_by_text(text: str):
    result = subprocess.run([
        'python3', 'txt_to_epub_cli.py', text
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)
```

## Performance Notes
- Average response time: 3-5 seconds
- Timeout: 30 seconds maximum
- Rate limiting: Handled by backend Z-Library service
- Concurrent requests: Support multiple parallel searches

## Limitations
1. **Download URLs**: Currently null (not implemented)
2. **Search Quality**: Depends on Z-Library availability
3. **Language Support**: Primarily English and Russian
4. **Error Rate**: ~30% for edge cases and difficult searches

## Future Improvements
1. Implement actual EPUB download URLs
2. Add Flibusta fallback for Russian books
3. Improve confidence calculation algorithm
4. Add semantic text analysis
5. Support more languages
6. Better handling of edge cases

This API provides a solid foundation for text-to-EPUB search with room for enhancements based on usage patterns and feedback.