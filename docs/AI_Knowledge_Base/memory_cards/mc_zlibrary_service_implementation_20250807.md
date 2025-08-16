# Memory Card: Z-Library Service Implementation
---
id: mc_zlibrary_service_implementation_20250807
type: memory_card
category: implementation
created: 2025-08-07
status: active
---

## Service Overview
Production-ready Z-Library book search and download service with JSON API support for external integration.

## Working Scripts

### Primary Script: `scripts/zlib_book_search_fixed.sh`
Fixed version with proper metadata extraction and service mode support.

#### Key Features
- **Search & Download**: Books by title/author with format filtering
- **Service Mode**: `--service` flag for clean JSON-only output
- **Custom Output**: `-o` parameter for file destination control
- **Author Filter**: `-a` parameter for author-specific searches
- **Format Support**: epub, pdf, mobi, txt, fb2, rtf, azw, azw3, djvu, lit

#### Usage Examples
```bash
# Search books (JSON output)
./scripts/zlib_book_search_fixed.sh --json "Python programming"

# Download EPUB to custom directory
./scripts/zlib_book_search_fixed.sh -o /tmp/shared_books -f epub --download "Data Science"

# Service mode for API integration
./scripts/zlib_book_search_fixed.sh --service --json -o /path/to/output --download "book name"

# Search by author
./scripts/zlib_book_search_fixed.sh --json -a "William Gray" -c 2 "Python"

# Check download limits
./scripts/zlib_book_search_fixed.sh --limits
```

## JSON Response Structure

### Search Response
```json
{
  "status": "success",
  "query": "search terms",
  "total_results": 3,
  "page": 1,
  "total_pages": 10,
  "results": [
    {
      "id": "book_id",
      "name": "Book Title",
      "authors": [...],
      "year": "2024",
      "extension": "EPUB",
      "size": "1.2 MB",
      "publisher": "Publisher Name",
      "rating": "5.0/5.0",
      "description": "Book description..."
    }
  ]
}
```

### Download Response
```json
{
  "status": "success",
  "message": "Download completed successfully",
  "book": {
    "name": "Book Title",
    "id": "book_id",
    "authors": ["Author Name"],
    "year": "2024",
    "extension": "epub",
    "size_bytes": 1995851
  },
  "file": {
    "path": "/absolute/path/to/file.epub",
    "filename": "file.epub",
    "size": 1995851
  }
}
```

## File Sharing Strategy

### 1. Output Directory Control
- Use `-o` parameter to specify destination
- Supports absolute and relative paths
- Creates directory if not exists

### 2. Service Integration Points
- **Shared Storage**: `/tmp/shared_books/` for temporary access
- **Web API**: Return JSON with file path for HTTP serving
- **Network Share**: Save to mounted network drives
- **Container Volume**: Use Docker volume mounts

### 3. Access Patterns
```bash
# Local service
OUTPUT_DIR="./downloads"

# Shared temporary
OUTPUT_DIR="/tmp/shared_books"

# Network mount
OUTPUT_DIR="/mnt/library/books"

# Docker volume
OUTPUT_DIR="/app/data/books"
```

## Implementation Details

### Authentication
- Requires `ZLOGIN` and `ZPASSW` in `.env` file
- Cookie-based session management
- Personalized mirror domain per user

### Rate Limiting
- 64 concurrent requests (semaphore-controlled)
- Daily download limits per account
- Check limits with `--limits` flag

### Error Handling
- JSON error responses in service mode
- Proper HTTP status codes
- Detailed error messages

### File Naming
- Safe filename generation (alphanumeric + spaces/dashes)
- Maximum 80 characters for title
- Format: `<safe_title>.<extension>`
- Fallback: `book_<id>.<extension>` or `downloaded_book.<extension>`

## Known Issues & Solutions

### Issue 1: Empty Book Metadata
**Problem**: Original script returned empty book data
**Solution**: Fixed in `zlib_book_search_fixed.sh` with proper fetch() calls

### Issue 2: Author Data Parsing
**Problem**: Authors array contains non-author data (comments, links)
**Solution**: Filter author data in production use

### Issue 3: Service Output
**Problem**: Colored output mixed with JSON
**Solution**: Added `--service` flag for clean JSON-only mode

## Production Recommendations

1. **Error Recovery**: Implement retry logic for failed downloads
2. **Caching**: Cache search results to reduce API calls
3. **Queue System**: Use job queue for bulk downloads
4. **Monitoring**: Track success/failure rates
5. **Cleanup**: Implement file cleanup for old downloads
6. **Security**: Validate and sanitize file paths

## Environment Variables
```bash
# Required in .env
ZLOGIN=your_email@example.com
ZPASSW=your_password

# Optional
PYTHONPATH=/path/to/src
OUTPUT_DIR=/default/output/path
```

## Testing Commands
```bash
# Test search
./scripts/zlib_book_search_fixed.sh --json -c 3 "test query"

# Test download
./scripts/zlib_book_search_fixed.sh --download "test book"

# Test service mode
./scripts/zlib_book_search_fixed.sh --service --json --download "test"

# Verify output
ls -la /tmp/shared_books/
```

## Integration Examples

### Web API Endpoint
```python
@app.post("/download-book")
async def download_book(query: str, format: str = "epub"):
    result = subprocess.run([
        "./scripts/zlib_book_search_fixed.sh",
        "--service", "--json",
        "-o", "/app/downloads",
        "-f", format,
        "--download", query
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)
```

### Docker Service
```dockerfile
VOLUME ["/app/downloads"]
ENV OUTPUT_DIR=/app/downloads
```

### Systemd Service
```ini
[Service]
Environment="OUTPUT_DIR=/var/lib/zlibrary/books"
ExecStart=/path/to/zlib_book_search_fixed.sh --service
```

## Related Files
- `scripts/zlib_book_search.sh` - Original script (has issues)
- `scripts/zlib_book_search_fixed.sh` - Production-ready version
- `.env` - Credentials configuration
- `src/zlibrary/` - Python library implementation