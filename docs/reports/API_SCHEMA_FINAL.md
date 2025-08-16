# Book Search API - Final Schema Documentation

## Overview
This service provides a standardized JSON API for converting book URLs to EPUB downloads with confidence scoring.

## Usage
```bash
python3 book_search_api_cli.py "URL"
```

## Response Schema
The API ALWAYS returns this exact JSON structure:

### Success Response
```json
{
  "status": "success",
  "timestamp": "2025-08-08T15:45:11.633463",
  "query_info": {
    "original_url": "https://www.podpisnie.ru/books/maniac/",
    "extracted_query": "maniac"
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
      "title": "Maniac",
      "authors": ["Benjamín Labatut"],
      "year": "2023",
      "publisher": "Anagrama",
      "size": "576 KB",
      "description": "Una novela vertiginosa sobre los límites del pensamiento..."
    },
    "service_used": "zlibrary"
  }
}
```

### Not Found Response
```json
{
  "status": "not_found",
  "timestamp": "2025-08-08T15:45:11.633463",
  "query_info": {
    "original_url": "https://example.com/book-not-found/",
    "extracted_query": "book not found"
  },
  "result": {
    "found": false,
    "message": "No EPUB books found for query: 'book not found'"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "timestamp": "2025-08-08T15:45:11.633463",
  "query_info": {
    "original_url": "invalid-url",
    "extracted_query": ""
  },
  "result": {
    "error": "search_failed",
    "message": "Search service error: Invalid URL format"
  }
}
```

## Response Fields

### Root Level
- **status** (string): "success", "not_found", or "error"
- **timestamp** (string): ISO 8601 timestamp
- **query_info** (object): Information about the search
- **result** (object): Main result data

### Query Info
- **original_url** (string): Original URL provided
- **extracted_query** (string): Search query extracted from URL

### Success Result
- **found** (boolean): Always true for success
- **epub_download_url** (string|null): Direct EPUB download URL
- **confidence** (object): Confidence scoring
- **book_info** (object): Book metadata
- **service_used** (string): "zlibrary" or "flibusta"

### Confidence Object
- **score** (number): 0.0 to 1.0 confidence score
- **level** (string): VERY_HIGH, HIGH, MEDIUM, LOW, VERY_LOW
- **description** (string): Human-readable description in Russian
- **recommended** (boolean): Whether download is recommended

### Book Info Object
- **title** (string): Book title
- **authors** (array): List of author names
- **year** (string|null): Publication year
- **publisher** (string|null): Publisher name
- **size** (string|null): File size (e.g., "1.2 MB")
- **description** (string|null): Book description

## Confidence Levels
- **VERY_HIGH** (≥80%): Точно искомая книга
- **HIGH** (≥60%): Скорее всего нужная книга
- **MEDIUM** (≥40%): Возможно нужная книга
- **LOW** (≥20%): Вряд ли искомая книга
- **VERY_LOW** (<20%): Точно не та книга

## Error Codes
- **invalid_usage**: Wrong command line usage
- **search_failed**: Search service error
- **timeout**: Request timeout (30s)
- **invalid_response**: Invalid JSON from search service
- **interrupted**: User interrupted
- **cli_error**: CLI processing error
- **unexpected_error**: Unknown error

## Integration Example

### From Another Python Service
```python
import subprocess
import json

def search_book(url):
    result = subprocess.run([
        'python3', 'book_search_api_cli.py', url
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)
```

### From Shell Script
```bash
#!/bin/bash
URL="$1"
RESULT=$(python3 book_search_api_cli.py "$URL")
echo "$RESULT" | jq '.result.confidence.recommended'
```

### From Web API
```python
from fastapi import FastAPI
import subprocess
import json

app = FastAPI()

@app.get("/search")
async def search_book(url: str):
    result = subprocess.run([
        'python3', 'book_search_api_cli.py', url
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)
```

## Files Structure
```
/project/
├── schemas/book_search_response_schema.json    # JSON Schema
├── book_search_api_cli.py                      # CLI Interface
├── standardized_book_search.py                 # Core Service
└── scripts/zlib_book_search_fixed.sh          # Backend Script
```

This API provides a predictable, standardized interface for book search with confidence scoring, suitable for integration into any microservice architecture.