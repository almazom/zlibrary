# Memory Card: Z-Library API Complete Reference
---
id: mc_technical_api_reference_20250806
type: memory_card
category: technical
created: 2025-08-06
updated: 2025-08-07
status: active
---

## AsyncZlib Class

### Constructor
```python
AsyncZlib(onion: bool = False, proxy_list: Optional[list] = None, disable_semaphore: bool = False)
```
- `onion`: Use Tor onion domains
- `proxy_list`: List of proxy URLs
- `disable_semaphore`: Disable 64-request limiter

### Authentication
```python
async def login(email: str, password: str) -> ZlibProfile
async def logout()
```

### Search Methods
```python
async def search(
    q: str,
    exact: bool = False,
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    lang: List[Union[Language, str]] = [],
    extensions: List[Union[Extension, str]] = [],
    count: int = 10
) -> SearchPaginator

async def full_text_search(
    q: str,
    phrase: bool = False,
    words: bool = False,
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    lang: List[Union[Language, str]] = [],
    extensions: List[Union[Extension, str]] = [],
    count: int = 10
) -> SearchPaginator

async def get_by_id(id: str) -> dict
```

## SearchPaginator Class

### Properties
- `page`: Current page number
- `total`: Total pages
- `count`: Results per page
- `result`: Current page results

### Methods
```python
async def init()              # Initialize paginator
async def next() -> List[BookItem]    # Next result set
async def prev() -> List[BookItem]    # Previous result set
async def next_page()         # Next page
async def prev_page()         # Previous page
```

## BookItem Class

### Properties
- `id`: Book ID
- `name`: Title
- `authors`: Author list
- `year`: Publication year
- `language`: Language
- `extension`: File format
- `size`: File size
- `rating`: Book rating
- `publisher`: Publisher name
- `isbn`: ISBN
- `cover`: Cover URL
- `url`: Book page URL

### Methods
```python
async def fetch() -> dict     # Get full book details with download URL
```

### Fetch Return Dictionary
```python
{
    'name': str,
    'authors': List[dict],
    'cover': str,
    'description': str,
    'year': str,
    'publisher': str,
    'language': str,
    'extension': str,
    'size': str,
    'rating': str,
    'download_url': str,       # Key field for downloading
    'categories': str,
    'isbn': str,
    'isbn10': str,
    'isbn13': str
}
```

## ZlibProfile Class

### Methods
```python
async def get_limits() -> dict
# Returns: {
#     'daily_amount': int,
#     'daily_allowed': int,
#     'daily_remaining': int,
#     'daily_reset': str
# }

async def download_history(
    page: int = 1,
    date_from: date = None,
    date_to: date = None
) -> DownloadsPaginator

async def search_public_booklists(
    q: str,
    count: int = 10,
    order: OrderOptions = ""
) -> BooklistPaginator

async def search_private_booklists(
    q: str,
    count: int = 10,
    order: OrderOptions = ""
) -> BooklistPaginator
```

## Constants and Enums

### Extension
```python
Extension.PDF
Extension.EPUB
Extension.MOBI
Extension.TXT
Extension.RTF
Extension.FB2
Extension.AZW
Extension.AZW3
Extension.LIT
Extension.DJV
Extension.DJVU
```

### Language (200+ languages)
```python
Language.ENGLISH
Language.SPANISH
Language.FRENCH
Language.GERMAN
Language.CHINESE
Language.RUSSIAN
# ... and many more
```

### OrderOptions
```python
OrderOptions.POPULAR   # Sort by popularity
OrderOptions.NEWEST    # Sort by creation date
OrderOptions.RECENT    # Sort by last updated
```

## Exception Classes
```python
LoginFailed         # Authentication errors
ParseError         # HTML parsing failures
EmptyQueryError    # Invalid search queries
ProxyNotMatchError # Proxy configuration issues
NoProfileError     # Operations requiring auth
NoDomainError      # Missing domain config
NoIdError         # Missing required book ID
LoopError         # Asyncio loop closure errors
```

## Usage Patterns

### Basic Search
```python
results = await client.search(q="python", count=10)
await results.init()
books = results.result
```

### Filtered Search
```python
results = await client.search(
    q="machine learning",
    from_year=2020,
    to_year=2024,
    lang=[Language.ENGLISH],
    extensions=[Extension.PDF, Extension.EPUB],
    count=25
)
```

### Sequential Processing
```python
for book in books:
    details = await book.fetch()
    print(details['download_url'])
    await asyncio.sleep(1)  # Rate limiting
```

### Error Handling
```python
try:
    await client.login(email, password)
except LoginFailed as e:
    print(f"Auth failed: {e}")
except NoDomainError as e:
    print(f"No working domain: {e}")
```

## CLI Script Integration

### Bash Script: `scripts/zlib_book_search_fixed.sh`
Production-ready CLI wrapper for the Python API.

#### Key Parameters
- `-o, --output DIR`: Output directory for downloads
- `-f, --format FORMAT`: File format filter (epub, pdf, mobi, etc.)
- `-l, --lang LANGUAGE`: Language filter
- `-a, --author NAME`: Author name filter
- `-c, --count NUMBER`: Max results (default: 10, max: 50)
- `--json`: JSON output format
- `--service`: Service mode (clean JSON only)
- `--download`: Download first book found
- `--limits`: Check download limits

#### Service Mode Usage
```bash
# Download with absolute path in response
./scripts/zlib_book_search_fixed.sh \
    --service --json \
    -o /tmp/shared_books \
    -f epub \
    --download "Python programming"
```

#### JSON Response Structure
```json
{
  "status": "success",
  "book": {
    "name": "Book Title",
    "id": "book_id",
    "authors": ["Author Name"],
    "extension": "epub",
    "size_bytes": 1234567
  },
  "file": {
    "path": "/absolute/path/to/file.epub",
    "filename": "file.epub",
    "size": 1234567
  }
}