# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an unofficial Python API for Z-Library, providing async access to search, download, and manage books from the Z-Library service. The library supports both clearnet and Tor/onion domains with proxy support.

## Development Commands

### Build and Install
```bash
# Build the package
devenv shell -c build
# Or manually:
rm -r dist
python3 -m build 
uv pip install dist/zlibrary*.whl
```

### Testing
```bash
# Run the test script
devenv shell -c test
# Or manually:
python3 src/test.py
```

Note: Tests require environment variables `ZLOGIN` and `ZPASSW` for Z-Library credentials.

### Development Environment
The project uses devenv with Python 3.12 and uv for package management:
```bash
devenv shell  # Enter development environment
```

## Architecture

### Core Components

- **AsyncZlib** (`libasync.py`): Main async client class that handles authentication, search, and API interactions
- **SearchPaginator** (`abs.py`): Handles paginated search results with caching and navigation
- **BookItem** (`abs.py`): Represents individual books with fetch capabilities for detailed metadata
- **ZlibProfile** (`profile.py`): User profile management including download limits and history
- **Booklists** (`booklists.py`): Public and private booklist search and management

### Key Features

- Dual domain support: clearnet (z-library.sk) and Tor onion domains
- Proxy chain support (HTTP, SOCKS4, SOCKS5)
- Async/await throughout with semaphore-based concurrency control (64 concurrent requests)
- Cookie-based session management
- Comprehensive search with filters (language, extension, year range, full-text)
- Download history and limits tracking
- Booklist creation and management

### Constants and Enums

- **Extension**: Supported file formats (PDF, EPUB, MOBI, etc.)
- **Language**: Extensive language support (200+ languages)
- **OrderOptions**: Search result ordering (popular, newest, recent)

### Authentication Flow

1. Login via POST to `/rpc.php` endpoint
2. Extract session cookies and user-specific mirror domain
3. All subsequent requests use the personalized mirror domain with cookies

### Error Handling

Custom exceptions in `exception.py`:
- `LoginFailed`: Authentication errors
- `ParseError`: HTML parsing failures
- `EmptyQueryError`: Invalid search queries
- `ProxyNotMatchError`: Proxy configuration issues
- `NoProfileError`, `NoDomainError`, `NoIdError`: Missing required data

### Logging

Uses structured logging via the `logger.py` module. Enable debug logging:
```python
import logging
logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
logging.getLogger("zlibrary").setLevel(logging.DEBUG)
```