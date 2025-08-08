# Memory Card: Book Downloads & Service Tracking
---
id: mc_book_downloads_20250808
type: memory_card
category: operations
created: 2025-08-08
status: active
---

## Recent Book Downloads

### Book: "No More Tears: The Dark Secrets of Johnson & Johnson"
- **Author**: Gardiner Harris
- **Publisher**: Random House
- **Year**: 2025
- **Format**: EPUB
- **Size**: 863 KB (883,221 bytes)
- **Rating**: 5.0/5.0
- **Service Used**: Z-Library (zlibrary)
- **Download Path**: `/home/almaz/microservices/zlibrary_api_module/downloads/No More Tears The Dark Secrets of Johnson Johnson.epub`
- **Download Date**: 2025-08-08
- **Description**: An explosive, deeply reported exposé of Johnson & Johnson, one of America's oldest and most trusted pharmaceutical companies—from an award-winning investigative journalist

## Service Selection Features (Added 2025-08-08)

### New Parameters in `zlib_book_search_fixed.sh`
- **`--force-zlib`**: Force search in Z-Library only (no Flibusta fallback)
- **`--force-flibusta`**: Force search in Flibusta only (good for Russian literature)
- **Default behavior**: Z-Library first, then automatic fallback to Flibusta if no results

### Service Tracking
All JSON responses now include `service_used` field:
- `"service_used": "zlibrary"` - Book found in Z-Library
- `"service_used": "flibusta"` - Book found in Flibusta

### Usage Examples
```bash
# Force Z-Library only
./scripts/zlib_book_search_fixed.sh --force-zlib --json "book title"

# Force Flibusta only (Russian books)
./scripts/zlib_book_search_fixed.sh --force-flibusta --json "название книги"

# Auto-fallback (default)
./scripts/zlib_book_search_fixed.sh --json "book title"
```

## Multi-Source Pipeline Architecture

### Service Priority
1. **Z-Library** (Primary)
   - Fast response (2-5 seconds)
   - ~75% success rate
   - 10 downloads/day per account
   - English & international content

2. **Flibusta** (Fallback)
   - Slower response (25-35 seconds)
   - ~60% success rate for Russian content
   - No authentication required
   - Specializes in Russian literature

### Fallback Logic
```
User Query → Z-Library Search
    ├─ Found → Return with service_used: "zlibrary"
    └─ Not Found → Check if --force-zlib
        ├─ Yes → Return error
        └─ No → Try Flibusta
            ├─ Found → Return with service_used: "flibusta"
            └─ Not Found → Return error with services_tried: ["zlibrary", "flibusta"]
```

## JSON Response Structure with Service Tracking

### Search Response
```json
{
  "status": "success",
  "query": "search terms",
  "service_used": "zlibrary",
  "total_results": 3,
  "results": [...]
}
```

### Download Response
```json
{
  "status": "success",
  "message": "Download completed successfully",
  "service_used": "zlibrary",
  "book": {
    "name": "Book Title",
    "authors": ["Author Name"],
    "extension": "epub",
    "size_bytes": 883221
  },
  "file": {
    "path": "/absolute/path/to/book.epub",
    "size": 883221
  }
}
```

### Error Response with Fallback Info
```json
{
  "status": "error",
  "message": "Book not found",
  "services_tried": ["zlibrary", "flibusta"],
  "query": "search terms"
}
```

## Implementation Files

### Updated Scripts
- `/scripts/zlib_book_search_fixed.sh` - Main script with service selection
- `/scripts/epub_search.sh` - Advanced cognitive pipeline with fallback
- `/scripts/flibusta_fallback.sh` - Direct Flibusta search script
- `/scripts/flibusta_direct.py` - Python Flibusta interface

### Source Modules
- `/src/book_sources/zlibrary_source.py` - Z-Library interface
- `/src/book_sources/flibusta_source.py` - Flibusta interface
- `/src/pipeline/book_pipeline.py` - Multi-source orchestrator

## Service Statistics

### Combined Success Rate
- With fallback: ~95% success rate
- Z-Library alone: ~75% success rate
- Flibusta alone: ~60% success rate (Russian content)

### Download Capacity
- 30 downloads/day with 3 Z-Library accounts
- Unlimited searches with Flibusta (no auth required)

## Related Memory Cards
- `mc_zlibrary_service_implementation_20250807.md` - Service implementation details
- `mc_pipeline_implementation_tdd_20250807.md` - Pipeline architecture
- `mc_technical_multi_account_system_20250806.md` - Account management