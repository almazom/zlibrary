# Memory Card: Z-Library API Module Overview
---
id: mc_project_zlibrary_overview_20250806
type: memory_card
category: project
created: 2025-08-06
status: active
---

## Project Summary
Unofficial Python API for Z-Library providing async access to search, download, and manage books. Supports both clearnet and Tor/onion domains with proxy support.

## Key Facts
- **Language**: Python 3.12+
- **Architecture**: Async/await with aiohttp
- **Concurrency**: 64 concurrent requests (semaphore-controlled)
- **Authentication**: Cookie-based session management
- **Domains**: Dual support for clearnet (z-library.sk) and Tor onion

## Core Components

### AsyncZlib (Main Client)
- Login/logout functionality
- Search methods (standard and full-text)
- Get book by ID
- Session management

### SearchPaginator
- Paginated results handling
- Result caching
- Navigation methods (next/prev)
- Page management

### BookItem
- Individual book representation
- Fetch detailed metadata
- Download URL retrieval
- Cover image access

### ZlibProfile
- User profile management
- Download limits tracking
- Download history
- Booklist search (public/private)

## Features
- ✅ Multi-language support (200+ languages)
- ✅ Format filtering (PDF, EPUB, MOBI, etc.)
- ✅ Year range filtering
- ✅ Full-text search capability
- ✅ Proxy chain support
- ✅ Download history tracking
- ✅ Rate limit monitoring

## Project Structure
```
zlibrary_api_module/
├── src/zlibrary/       # Core library code
│   ├── libasync.py     # Main AsyncZlib class
│   ├── abs.py          # Abstract classes and paginators
│   ├── profile.py      # User profile management
│   ├── booklists.py    # Booklist functionality
│   ├── const.py        # Constants and enums
│   ├── exception.py    # Custom exceptions
│   └── util.py         # Utility functions
├── examples/           # Usage examples
├── tests/             # Test files
├── scripts/           # Bash API scripts
└── AI_Knowledge_Base/ # Project knowledge repository
```

## Quick Usage
```python
from zlibrary import AsyncZlib, Extension, Language

client = AsyncZlib()
await client.login(email, password)

# Search for EPUB books
results = await client.search(
    q="search query",
    extensions=[Extension.EPUB],
    lang=[Language.ENGLISH],
    count=10
)

await results.init()
books = results.result

# Get download URL
details = await books[0].fetch()
download_url = details['download_url']
```

## Current Status
- ✅ Core functionality implemented
- ✅ Search and pagination working
- ✅ Download URL retrieval functional
- ⚠️ Requires valid Z-Library credentials
- ⚠️ Subject to daily download limits