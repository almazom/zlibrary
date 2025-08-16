# Book Search API - Single Clean Endpoint

## 🎯 **ONE Simple API: `./scripts/book_search.sh`**

This is the **ONLY** API endpoint for external CLI communication on the same server.

## 📚 **Basic Usage**

```bash
# Simple search and download EPUB
./scripts/book_search.sh "James Joyce Ulysses"

# Search for specific book - downloads automatically if found
./scripts/book_search.sh "1984 George Orwell"

# Book will be saved to ./downloads/ directory
ls -la downloads/*.epub

# Get help
./scripts/book_search.sh --help
```

## 📊 **JSON Response Structure**

### **Success Response (With Downloaded EPUB)**
```json
{
  "status": "success",
  "timestamp": "2025-08-08T17:43:18.506580",
  "input_format": "txt",
  "query_info": {
    "original_input": "1984 George Orwell",
    "extracted_query": "1984 George Orwell"
  },
  "result": {
    "found": true,
    "epub_download_url": "/home/almaz/microservices/zlibrary_api_module/downloads/1984_.epub",
    "download_info": {
      "available": true,
      "url": "https://z-library.sk/dl/11191604/58f487",
      "local_path": "/home/almaz/microservices/zlibrary_api_module/downloads/1984_.epub"
    },
    "confidence": {
      "score": 0.667,
      "level": "HIGH",
      "description": "Высокая уверенность - скорее всего это нужная книга",
      "recommended": true
    },
    "readability": {
      "score": 0.95,
      "level": "EXCELLENT",
      "description": "Отличное качество - высококачественный EPUB",
      "factors": ["Good file size", "Has publisher information"]
    },
    "book_info": {
      "title": "Book Title",
      "authors": ["Author Name"],
      "year": "2018",
      "publisher": "Publisher Name",
      "size": "2.80 MB",
      "description": "Book description..."
    },
    "service_used": "zlibrary"
  }
}
```

### **Not Found Response**
```json
{
  "status": "not_found",
  "result": {
    "found": false,
    "message": "No books found matching the search criteria"
  }
}
```

### **Error Response**
```json
{
  "status": "error",
  "result": {
    "error": "backend_error",
    "message": "Failed to get response from backend service"
  }
}
```

## 🔧 **External Integration Examples**

### **Bash Script Integration**
```bash
#!/bin/bash
# search_book.sh - External system using our API

search_book() {
    local query="$1"
    local result=$(./scripts/book_search.sh "$query")
    
    # Check if book found
    local found=$(echo "$result" | jq -r '.result.found')
    
    if [[ "$found" == "true" ]]; then
        echo "✅ Book found:"
        echo "$result" | jq -r '.result.book_info.title'
        
        # Check if recommended
        local recommended=$(echo "$result" | jq -r '.result.confidence.recommended')
        if [[ "$recommended" == "true" ]]; then
            echo "👍 High confidence match - recommended for download"
        fi
    else
        echo "❌ Book not found"
    fi
}

# Usage
search_book "James Joyce Ulysses"
```

### **One-liner Examples**
```bash
# Get book title
./scripts/book_search.sh "Ulysses" | jq -r '.result.book_info.title'

# Check if recommended
./scripts/book_search.sh "Clean Code" | jq -r '.result.confidence.recommended'

# Get confidence level
./scripts/book_search.sh "1984" | jq -r '.result.confidence.level'

# Get readability score
./scripts/book_search.sh "Harry Potter" | jq -r '.result.readability.score'
```

### **Process Multiple Books**
```bash
#!/bin/bash
# process_books.sh - Process list of books

while IFS= read -r book; do
    echo "Searching: $book"
    
    result=$(./scripts/book_search.sh "$book")
    status=$(echo "$result" | jq -r '.status')
    
    case "$status" in
        "success")
            title=$(echo "$result" | jq -r '.result.book_info.title')
            confidence=$(echo "$result" | jq -r '.result.confidence.level')
            echo "  ✅ Found: $title (Confidence: $confidence)"
            ;;
        "not_found")
            echo "  ❌ Not found"
            ;;
        "error")
            echo "  💥 Error occurred"
            ;;
    esac
done < book_list.txt
```

## 🎯 **Dual Confidence System**

### **Match Confidence** - How well the book matches your search
- `VERY_HIGH` (≥0.8): Definitely the book you want
- `HIGH` (≥0.6): Very likely the right book
- `MEDIUM` (≥0.4): Possibly the right book
- `LOW` (<0.4): Probably not what you're looking for

### **Readability Confidence** - EPUB file quality
- `EXCELLENT` (≥0.8): High quality EPUB
- `GOOD` (≥0.65): Good quality, readable
- `FAIR` (<0.65): Acceptable quality

## 🚀 **Why This Design Works**

1. **ONE endpoint** - No confusion, simple to use
2. **Clean JSON** - Structured, predictable output
3. **Multi-account** - 3 Z-Library accounts with automatic fallback
4. **Dual confidence** - Know both match quality and EPUB quality
5. **Same server** - Direct execution, no network overhead

## 📋 **Input Types Supported**

- **Text**: `"James Joyce Ulysses"`
- **URL**: `"https://www.podpisnie.ru/books/maniac/"`
- **Multiple words**: `"Clean Code Robert Martin"`

## ✅ **Backend Details**

- **Accounts**: 3 Z-Library accounts (22 total downloads available)
- **Fallback**: Automatically tries next account if one fails
- **Service**: Uses Z-Library API with asyncio
- **Backend**: `simple_book_search.py` (clean, minimal implementation)

## 📦 **Files Structure**

```
scripts/
├── book_search.sh          # Main API endpoint (USE THIS)
├── archived/               # Old scripts (don't use)
└── ...

simple_book_search.py       # Backend service (called by book_search.sh)
multi_account_manager.py    # Account management utility
```

## 🔍 **Testing the API**

```bash
# Test basic search
./scripts/book_search.sh "test query" | jq .

# Test specific book
./scripts/book_search.sh "1984 George Orwell" | jq '.result.confidence'

# Test with URL
./scripts/book_search.sh "https://example.com/book" | jq '.input_format'
```

**This is the ONLY API endpoint you need. Simple, clean, and works perfectly!**