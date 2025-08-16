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

## API Reference

### AsyncZlib (Main Client)

The primary class for interacting with Z-Library.

#### Constructor

```python
AsyncZlib(onion: bool = False, proxy_list: Optional[list] = None, disable_semaphore: bool = False)
```

**Parameters:**
- `onion` (bool): Use Tor onion domains instead of clearnet (default: False)
- `proxy_list` (Optional[list]): List of proxy URLs for routing requests
- `disable_semaphore` (bool): Disable the 64-concurrent request limiter (default: False)

**Raises:**
- `ProxyNotMatchError`: If proxy_list is not a list type

#### Authentication Methods

##### `async def login(email: str, password: str) -> ZlibProfile`

Authenticates with Z-Library and initializes the user profile.

**Parameters:**
- `email` (str): Z-Library account email
- `password` (str): Z-Library account password

**Returns:**
- `ZlibProfile`: User profile object with download limits and history access

**Raises:**
- `LoginFailed`: If authentication fails
- `NoDomainError`: If no working domain is found

##### `async def logout()`

Clears authentication cookies and session data.

#### Search Methods

##### `async def search(...) -> SearchPaginator`

Performs a standard book search.

**Parameters:**
- `q` (str): Search query string
- `exact` (bool): Enable exact match search (default: False)
- `from_year` (Optional[int]): Filter books from this year onwards
- `to_year` (Optional[int]): Filter books up to this year
- `lang` (List[Union[Language, str]]): Filter by languages
- `extensions` (List[Union[Extension, str]]): Filter by file extensions
- `count` (int): Number of results per page (max 50, default: 10)

**Returns:**
- `SearchPaginator`: Paginated search results

**Raises:**
- `NoProfileError`: If not logged in
- `EmptyQueryError`: If search query is empty

##### `async def full_text_search(...) -> SearchPaginator`

Performs full-text search within book contents.

**Additional Parameters:**
- `phrase` (bool): Search for exact phrase (requires 2+ words)
- `words` (bool): Search for individual words

##### `async def get_by_id(id: str) -> dict`

Retrieves detailed book information by Z-Library book ID.

**Parameters:**
- `id` (str): Z-Library book ID

**Returns:**
- `dict`: Detailed book information including metadata and download URL

**Raises:**
- `NoIdError`: If no ID is provided

### SearchPaginator Class

Handles paginated search results with caching and navigation.

#### Properties

- `page` (int): Current page number
- `total` (int): Total number of pages
- `count` (int): Results per page
- `result` (list): Current page results

#### Navigation Methods

##### `async def init()`

Initializes the paginator by fetching and parsing the first page.

##### `async def next() -> List[BookItem]`

Advances to the next set of results.

##### `async def prev() -> List[BookItem]`

Returns to the previous set of results.

##### `async def next_page()`

Advances to the next page of results.

##### `async def prev_page()`

Returns to the previous page of results.

### BookItem Class

Represents individual books with fetch capabilities for detailed metadata.

##### `async def fetch() -> dict`

Fetches comprehensive book details from Z-Library.

**Returns:**
- `dict`: Complete book information including:
  - `name` (str): Book title
  - `authors` (List[dict]): Author information with URLs
  - `cover` (str): Cover image URL
  - `description` (str): Book description
  - `year` (str): Publication year
  - `publisher` (str): Publisher name
  - `language` (str): Book language
  - `extension` (str): File format
  - `size` (str): File size
  - `rating` (str): Book rating
  - `download_url` (str): Download link or availability status
  - `categories` (str): Book categories
  - `isbn` fields: Various ISBN identifiers

**Raises:**
- `ParseError`: If book details cannot be parsed

### ZlibProfile Class

Manages user profile, download limits, and history.

##### `async def get_limits() -> dict`

Retrieves current download limits and usage.

**Returns:**
- `dict`: Download limit information:
  - `daily_amount` (int): Downloads used today
  - `daily_allowed` (int): Total daily downloads allowed
  - `daily_remaining` (int): Remaining downloads today
  - `daily_reset` (str): Time when limits reset

**Raises:**
- `ParseError`: If download limits page cannot be parsed

##### `async def download_history(page: int = 1, date_from: date = None, date_to: date = None) -> DownloadsPaginator`

Retrieves download history with optional date filtering.

##### `async def search_public_booklists(q: str, count: int = 10, order: OrderOptions = "") -> BooklistPaginator`

Searches public user-created booklists.

##### `async def search_private_booklists(q: str, count: int = 10, order: OrderOptions = "") -> BooklistPaginator`

Searches user's private booklists.

### Constants and Enums

#### Extension Enum

Supported file formats:
- `Extension.PDF`, `Extension.EPUB`, `Extension.MOBI`
- `Extension.TXT`, `Extension.RTF`, `Extension.FB2`
- `Extension.AZW`, `Extension.AZW3`, `Extension.LIT`
- `Extension.DJV`, `Extension.DJVU`

#### Language Enum

200+ supported languages including:
- `Language.ENGLISH`, `Language.SPANISH`, `Language.FRENCH`
- `Language.GERMAN`, `Language.CHINESE`, `Language.RUSSIAN`

#### OrderOptions Enum

Sorting options for booklists:
- `OrderOptions.POPULAR`: Sort by popularity
- `OrderOptions.NEWEST`: Sort by creation date
- `OrderOptions.RECENT`: Sort by last updated

### Exception Classes

- `LoginFailed`: Authentication errors
- `ParseError`: HTML parsing failures
- `EmptyQueryError`: Invalid search queries
- `ProxyNotMatchError`: Proxy configuration issues
- `NoProfileError`: Operations requiring authentication
- `NoDomainError`: Missing domain configuration
- `NoIdError`: Missing required book ID
- `LoopError`: Asyncio loop closure errors

## Usage Examples

### Basic Usage

```python
import asyncio
from zlibrary import AsyncZlib, Language, Extension

async def main():
    # Initialize client
    client = AsyncZlib()
    
    # Login
    profile = await client.login("user@example.com", "password")
    
    # Check download limits
    limits = await profile.get_limits()
    print(f"Downloads remaining: {limits['daily_remaining']}")
    
    # Search for books
    results = await client.search(
        q="python programming",
        lang=[Language.ENGLISH],
        extensions=[Extension.PDF],
        count=10
    )
    
    # Navigate through results
    await results.init()
    books = results.result
    for book in books:
        details = await book.fetch()
        print(f"{details['name']} - {details['download_url']}")
    
    # Logout
    await client.logout()

asyncio.run(main())
```

### Advanced Search

```python
# Full-text search with filters
results = await client.full_text_search(
    q="machine learning algorithms",
    phrase=True,
    from_year=2020,
    to_year=2024,
    lang=[Language.ENGLISH],
    extensions=[Extension.PDF, Extension.EPUB],
    count=25
)

# Navigate through pages
await results.init()
while results.page <= results.total:
    for book in results.result:
        details = await book.fetch()
        print(f"Page {results.page}: {details['name']}")
    
    if results.page < results.total:
        await results.next_page()
    else:
        break
```

### Profile Management

```python
# Get download history
from datetime import date
history = await profile.download_history(
    date_from=date(2024, 1, 1),
    date_to=date(2024, 12, 31)
)

# Search booklists
public_lists = await profile.search_public_booklists("programming")
private_lists = await profile.search_private_booklists("my books")
```

### Tor/Proxy Usage

```python
# Using Tor
client = AsyncZlib(
    onion=True,
    proxy_list=['socks5://127.0.0.1:9050']
)

# Using HTTP proxy chain
client = AsyncZlib(
    proxy_list=[
        'http://proxy1:8080',
        'socks5://proxy2:1080'
    ]
)
```