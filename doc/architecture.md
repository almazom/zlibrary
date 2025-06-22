# Architecture Documentation

## Overview

The Z-Library Python API is designed as an asynchronous library that provides a clean interface to the Z-Library book repository. The architecture emphasizes performance, reliability, and ease of use through careful separation of concerns and robust error handling.

## Core Architecture Components

### 1. Network Layer (`util.py`)

The foundation of the library handles all HTTP communications:

- **Request Functions**: `GET_request()`, `POST_request()`, `GET_request_cookies()`
- **Proxy Support**: Chains multiple proxy types (HTTP, SOCKS4, SOCKS5)
- **Session Management**: Cookie handling and persistence
- **Rate Limiting**: Semaphore-based concurrency control

### 2. Authentication Layer (`libasync.py` - login methods)

Manages Z-Library authentication flow:

1. **Initial Login**: POST to `/rpc.php` with credentials
2. **Domain Resolution**: Extract user-specific mirror domain
3. **Session Establishment**: Store authentication cookies
4. **Mirror Switching**: Support for clearnet/onion domains

### 3. Data Access Layer

#### Search Engine (`abs.py` - SearchPaginator)
- **Pagination Logic**: Efficient result set navigation
- **Caching Strategy**: Store multiple pages in memory
- **Result Parsing**: HTML to structured data conversion
- **Lazy Loading**: Fetch detailed book info on demand

#### Profile Management (`profile.py` - ZlibProfile)
- **Usage Tracking**: Download limits and history
- **Account Features**: Booklist management
- **Statistics**: User activity and preferences

#### Book Management (`abs.py` - BookItem)
- **Metadata Handling**: Standard bibliographic fields
- **Content Access**: Download URL generation
- **Detail Fetching**: On-demand full book information

### 4. Domain Management

The library supports multiple access methods:

```
┌─────────────────┐    ┌──────────────────┐
│   Clearnet      │    │    Tor/Onion     │
│ z-library.sk    │◄──►│   .onion domains │
└─────────────────┘    └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌─────────────┐
              │   Proxies   │
              │ HTTP/SOCKS  │
              └─────────────┘
```

## Request Flow Architecture

### 1. Authentication Flow

```
Client → login(email, pass) → POST /rpc.php → Extract cookies & mirror → Store session
```

### 2. Search Flow

```
Client → search(query) → GET /s/{query} → Parse HTML → Return SearchPaginator
       → next() → Fetch next page → Cache results → Return BookItems
```

### 3. Book Detail Flow

```
Client → book.fetch() → GET /book/{id} → Parse metadata → Return book dict
```

## Data Flow Patterns

### Pagination Strategy

The library implements a sophisticated pagination system:

```python
SearchPaginator {
    storage: {1: [results], 2: [results], ...}  # Page cache
    position: current_index_in_page
    page: current_page_number
    result: current_visible_results
}
```

**Navigation Logic:**
- `next()`: Move position forward, fetch new page if needed
- `prev()`: Move position backward, use cached data
- `next_page()`/`prev_page()`: Direct page navigation

### Error Propagation

```
Network Error → Utility Layer → Business Logic → Custom Exception → Client
```

**Exception Hierarchy:**
- `LoginFailed`: Authentication issues
- `ParseError`: Data extraction problems  
- `ProxyNotMatchError`: Connection issues
- `NoProfileError`/`NoDomainError`/`NoIdError`: State issues

## Concurrency Model

### Semaphore-Based Rate Limiting

```python
__semaphore = asyncio.Semaphore(64)  # Max 64 concurrent requests
```

**Benefits:**
- Prevents server overload
- Maintains responsive performance
- Reduces chance of IP blocking

### Async/Await Throughout

All I/O operations use `async/await`:
- Network requests
- HTML parsing (where beneficial)
- Data transformation

## State Management

### Session State

```python
AsyncZlib {
    cookies: session_cookies
    domain: user_mirror_domain  
    profile: ZlibProfile_instance
    _jar: aiohttp.CookieJar
}
```

### Search State

```python
SearchPaginator {
    storage: page_cache
    __url: base_search_url
    __pos: current_position
    page: current_page
    total: total_results
}
```

## Security Considerations

### Credential Handling
- No credential storage after login
- Session-based authentication via cookies
- Support for environment variable injection

### Proxy Security
- Multiple proxy chain support
- No proxy credential logging
- Tor support for anonymity

### Request Security
- User-agent rotation capabilities
- Rate limiting to avoid detection
- Domain switching for redundancy

## Performance Optimizations

### Caching Strategy
- **Page Cache**: Store multiple search result pages
- **Session Persistence**: Reuse HTTP connections
- **Lazy Loading**: Fetch book details only when needed

### Network Optimization
- **Connection Pooling**: Reuse aiohttp sessions
- **Compression Support**: Accept gzip/brotli encoding
- **Keep-Alive**: Maintain persistent connections

### Memory Management
- **Bounded Cache**: Limit stored pages to prevent memory bloat
- **Weak References**: Allow garbage collection of unused objects
- **Stream Processing**: Handle large result sets efficiently

## Extension Points

### Custom Parsers
The parsing logic in `abs.py` can be extended for new data fields or formats.

### Proxy Providers
The `util.py` module supports adding new proxy types or authentication methods.

### Domain Providers
New mirror domains can be added to the domain resolution logic.

### Search Filters
Additional search parameters can be added to the search methods.

## Testing Architecture

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Mock Support**: Network request mocking for reliable testing

### Test Data
- Environment-based credentials
- Reproducible search queries
- Known book IDs for consistency