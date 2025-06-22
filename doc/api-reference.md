# API Reference

## AsyncZlib Class

The main class for interacting with Z-Library.

### Constructor

```python
AsyncZlib(onion: bool = False, proxy_list: List[str] = None, semaphore: bool = True)
```

**Parameters:**
- `onion` (bool): Use Tor onion domains instead of clearnet
- `proxy_list` (List[str]): List of proxy URLs (HTTP, SOCKS4, SOCKS5)
- `semaphore` (bool): Enable request rate limiting (64 concurrent requests)

### Authentication Methods

#### `login(email: str, password: str) -> None`

Authenticate with Z-Library credentials.

**Parameters:**
- `email` (str): Z-Library account email
- `password` (str): Z-Library account password

**Raises:**
- `LoginFailed`: Invalid credentials or authentication error

### Search Methods

#### `search(q: str, **kwargs) -> SearchPaginator`

Search for books with various filters.

**Parameters:**
- `q` (str): Search query
- `count` (int, optional): Results per page (1-50, default: 10)
- `from_year` (int, optional): Start year filter
- `to_year` (int, optional): End year filter
- `lang` (List[Language], optional): Language filters
- `extensions` (List[Extension], optional): File format filters

**Returns:**
- `SearchPaginator`: Paginated search results

#### `full_text_search(q: str, **kwargs) -> SearchPaginator`

Search within book contents.

**Parameters:**
- `q` (str): Full-text search query
- `phrase` (bool, optional): Search as exact phrase
- `exact` (bool, optional): Exact word matching
- Additional parameters same as `search()`

### Book Retrieval

#### `get_by_id(book_id: str) -> dict`

Get book details by Z-Library ID.

**Parameters:**
- `book_id` (str): Book ID (format: "123456/abcdef")

**Returns:**
- `dict`: Complete book information

### Properties

#### `profile: ZlibProfile`

Access to user profile functionality after login.

## SearchPaginator Class

Handles paginated search results with caching.

### Methods

#### `next() -> List[BookItem]`

Get next set of results.

**Returns:**
- `List[BookItem]`: List of books in current result set

#### `prev() -> List[BookItem]`

Get previous set of results.

**Returns:**
- `List[BookItem]`: List of books in previous result set

#### `next_page() -> List[BookItem]`

Navigate to next page of results.

#### `prev_page() -> List[BookItem]`

Navigate to previous page of results.

### Properties

#### `result: List[BookItem]`

Current result set.

#### `page: int`

Current page number.

#### `total: int`

Total number of results.

#### `count: int`

Results per page.

## BookItem Class

Represents a single book in search results.

### Methods

#### `fetch() -> dict`

Fetch complete book details.

**Returns:**
- `dict`: Complete book information including download URL

### Properties

Standard book metadata:
- `id`: Z-Library book ID
- `isbn`: ISBN number
- `url`: Book page URL
- `cover`: Cover image URL
- `name`: Book title
- `publisher`: Publisher name
- `authors`: List of author dictionaries
- `year`: Publication year
- `language`: Book language
- `extension`: File format
- `size`: File size
- `rating`: User rating

## ZlibProfile Class

User profile and account management.

### Methods

#### `get_limits() -> dict`

Get download limits and usage.

**Returns:**
```python
{
    "daily_amount": int,      # Total daily downloads allowed
    "daily_allowed": int,     # Downloads allowed today
    "daily_remaining": int,   # Downloads remaining today
    "daily_reset": int        # Hours until reset
}
```

#### `download_history() -> DownloadsPaginator`

Get user's download history.

**Returns:**
- `DownloadsPaginator`: Paginated download history

#### `search_public_booklists(q: str, **kwargs) -> BooklistsPaginator`

Search public booklists.

**Parameters:**
- `q` (str): Search query
- `count` (int, optional): Results per page
- `order` (OrderOptions, optional): Sort order

#### `search_private_booklists(q: str, **kwargs) -> BooklistsPaginator`

Search user's private booklists.

## Enums and Constants

### Extension

Supported file formats:
- `PDF`, `EPUB`, `MOBI`, `AZW`, `AZW3`
- `TXT`, `RTF`, `FB2`, `LIT`
- `DJV`, `DJVU`

### Language

200+ supported languages including:
- `ENGLISH`, `SPANISH`, `FRENCH`, `GERMAN`
- `RUSSIAN`, `CHINESE`, `JAPANESE`, `KOREAN`
- `ARABIC`, `HINDI`, `PORTUGUESE`, `ITALIAN`

### OrderOptions

Result sorting options:
- `POPULAR`: Most popular first
- `NEWEST`: Newest publications first
- `RECENT`: Recently added first

## Error Handling

### Custom Exceptions

- `LoginFailed`: Authentication errors
- `ParseError`: HTML parsing failures
- `EmptyQueryError`: Invalid or empty search queries
- `ProxyNotMatchError`: Proxy configuration issues
- `NoProfileError`: Profile not available (need to login)
- `NoDomainError`: Domain resolution issues
- `NoIdError`: Missing required book ID

### Example Error Handling

```python
from zlibrary.exception import LoginFailed, ParseError

try:
    await lib.login(email, password)
except LoginFailed as e:
    print(f"Login failed: {e}")

try:
    results = await lib.search("python programming")
except ParseError as e:
    print(f"Search parsing error: {e}")
```