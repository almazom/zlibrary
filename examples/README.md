# Z-Library API Examples

This directory contains comprehensive examples demonstrating how to use the Z-Library Python API in various scenarios. The examples are organized by complexity and use case to help you get started quickly.

## Directory Structure

```
examples/
├── python/                     # Python API examples
│   ├── basic_usage.py         # Fundamental operations
│   ├── advanced_features.py   # Complex functionality
│   └── practical_applications.py # Real-world use cases
└── curl/                      # HTTP API examples
    ├── basic_auth.sh          # Authentication
    ├── search_examples.sh     # Search operations  
    ├── book_details.sh        # Book information
    ├── profile_operations.sh  # User profile
    └── README.md              # curl documentation
```

## Quick Start

### Prerequisites

1. **Install the library**
   ```bash
   pip install zlibrary
   ```

2. **Set up credentials**
   ```bash
   export ZLOGIN="your-email@example.com"
   export ZPASSW="your-password"
   ```

3. **Basic test**
   ```python
   import asyncio
   import zlibrary
   
   async def test():
       lib = zlibrary.AsyncZlib()
       await lib.login("email", "password")
       results = await lib.search("python programming")
       books = await results.next()
       print(f"Found {len(books)} books")
   
   asyncio.run(test())
   ```

## Python Examples

### 1. Basic Usage (`python/basic_usage.py`)

**What it covers:**
- Authentication and login
- Simple and advanced search
- Pagination navigation
- Book details retrieval
- Profile information access
- Error handling patterns

**Run it:**
```bash
cd examples/python
python basic_usage.py
```

**Key features demonstrated:**
```python
# Simple search
paginator = await lib.search(q="python programming", count=5)
books = await paginator.next()

# Advanced search with filters
paginator = await lib.search(
    q="machine learning",
    from_year=2020,
    to_year=2024,
    lang=[Language.ENGLISH],
    extensions=[Extension.PDF]
)

# Get book details
book = books[0]
details = await book.fetch()
print(f"Download URL: {details.get('download_url')}")

# Check download limits
limits = await lib.profile.get_limits()
print(f"Remaining: {limits['daily_remaining']}")
```

### 2. Advanced Features (`python/advanced_features.py`)

**What it covers:**
- Proxy configurations (HTTP, SOCKS, chains)
- Tor/onion domain access
- Batch and concurrent operations
- Performance optimization techniques
- Custom search strategies
- Error recovery patterns

**Run it:**
```bash
cd examples/python
python advanced_features.py
```

**Key features demonstrated:**
```python
# Tor access
lib = zlibrary.AsyncZlib(
    onion=True,
    proxy_list=['socks5://127.0.0.1:9050']
)

# Concurrent searches
tasks = [lib.search(q=query, count=5) for query in queries]
paginators = await asyncio.gather(*tasks)

# Performance optimization
# - Client reuse
# - Concurrent vs sequential execution
# - Pagination caching
```

### 3. Practical Applications (`python/practical_applications.py`)

**What it covers:**
- Book collection management
- Academic research tools
- Content analysis and trends
- Automated collection building
- Download monitoring
- Data export and reporting

**Run it:**
```bash
cd examples/python
python practical_applications.py
```

**Key features demonstrated:**
```python
# Collection management
class BookCollectionManager:
    async def add_book_to_collection(self, query: str):
        # Search, select, and save book metadata
        
    def export_collection_csv(self):
        # Export to structured format

# Research tool
async def academic_research_tool():
    # Multi-query research strategy
    # Bibliography generation
    # Source analysis

# Trend analysis
async def content_analysis_tool():
    # Analyze content trends over time
    # Generate reports
```

## curl Examples

The `curl/` directory contains shell scripts that demonstrate the underlying HTTP API calls. These are useful for:

- Understanding the raw API structure
- Integration with non-Python environments
- Debugging and troubleshooting
- Custom automation scripts

### Quick curl Usage

1. **Authenticate**
   ```bash
   cd examples/curl
   chmod +x *.sh
   ./basic_auth.sh
   ```

2. **Search**
   ```bash
   ./search_examples.sh
   ```

3. **Get book details**
   ```bash
   ./book_details.sh
   ```

See [`curl/README.md`](curl/README.md) for detailed curl documentation.

## Common Use Cases

### 1. Academic Research

```python
# Search for papers on a specific topic
results = await lib.search(
    q="machine learning ethics",
    from_year=2018,
    lang=[Language.ENGLISH],
    extensions=[Extension.PDF]
)

# Process results to build bibliography
for book in await results.next():
    details = await book.fetch()
    # Extract citation information
```

### 2. Personal Library Management

```python
# Build a collection of programming books
collections = {
    "Python": ["python programming", "django", "flask"],
    "JavaScript": ["javascript", "react", "node.js"],
    "Data Science": ["data science", "machine learning", "statistics"]
}

for category, queries in collections.items():
    for query in queries:
        results = await lib.search(q=query, count=10)
        # Add books to collection
```

### 3. Content Analysis

```python
# Analyze publication trends
languages = ["python", "javascript", "rust", "go"]
years = range(2020, 2025)

for lang in languages:
    for year in years:
        results = await lib.search(
            q=f"{lang} programming",
            from_year=year,
            to_year=year
        )
        count = len(await results.next())
        print(f"{lang} {year}: {count} books")
```

### 4. Download Management

```python
# Monitor and manage download limits
async def smart_download_manager():
    limits = await lib.profile.get_limits()
    
    if limits['daily_remaining'] > 0:
        # Proceed with downloads
        pass
    else:
        # Wait for reset or prioritize downloads
        print(f"Limit reached. Reset in {limits['daily_reset']} hours")
```

## Configuration and Setup

### Environment Variables

```bash
# Required
export ZLOGIN="your-email@example.com"
export ZPASSW="your-password"

# Optional
export PROXY_URL="socks5://127.0.0.1:9050"  # For Tor
export ZLIBRARY_DEBUG="1"                    # Enable debug logging
```

### Proxy Setup for Tor

```bash
# Install and start Tor
sudo apt install tor
sudo systemctl start tor

# Test Tor connection
curl --socks5 127.0.0.1:9050 https://check.torproject.org/

# Use with zlibrary
export PROXY_URL="socks5://127.0.0.1:9050"
```

### Debug Mode

```python
import logging

# Enable comprehensive logging
logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
logging.getLogger("zlibrary").setLevel(logging.DEBUG)

# Also enable aiohttp logging for network debugging
logging.getLogger("aiohttp").setLevel(logging.INFO)
```

## Error Handling Patterns

### Robust Search

```python
async def robust_search(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await lib.search(q=query)
        except zlibrary.exception.EmptyQueryError:
            raise  # Don't retry on invalid input
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2 ** attempt)
```

### Graceful Degradation

```python
async def search_with_fallbacks(query):
    strategies = [
        # Try with all filters
        lambda: lib.search(q=query, lang=[Language.ENGLISH], extensions=[Extension.PDF]),
        # Try with fewer filters
        lambda: lib.search(q=query, lang=[Language.ENGLISH]),
        # Try basic search
        lambda: lib.search(q=query)
    ]
    
    for strategy in strategies:
        try:
            return await strategy()
        except Exception as e:
            print(f"Strategy failed: {e}")
            continue
    
    raise Exception("All search strategies failed")
```

## Performance Tips

1. **Reuse Client Instances**
   ```python
   # Good: One client for multiple operations
   lib = zlibrary.AsyncZlib()
   await lib.login(email, password)
   
   # Multiple searches with same client
   for query in queries:
       results = await lib.search(q=query)
   ```

2. **Use Concurrent Operations**
   ```python
   # Process multiple queries concurrently
   tasks = [lib.search(q=query) for query in queries]
   results = await asyncio.gather(*tasks)
   ```

3. **Implement Rate Limiting**
   ```python
   # Add delays between requests
   await asyncio.sleep(0.5)  # 500ms delay
   ```

4. **Cache Results**
   ```python
   # Use paginator caching
   paginator = await lib.search(q="query")
   page1 = await paginator.next()  # Fetches from server
   page1_again = await paginator.prev()  # Uses cache
   ```

## Troubleshooting

### Common Issues

1. **Login failures**: Check credentials and account status
2. **Empty results**: Verify query parameters and filters
3. **Timeouts**: Check network connection and proxy settings
4. **Rate limiting**: Add delays between requests

### Debug Information

```python
# Get diagnostic information
async def get_debug_info():
    info = {
        'login_successful': False,
        'mirror': None,
        'cookies_count': 0
    }
    
    try:
        lib = zlibrary.AsyncZlib()
        await lib.login(email, password)
        info['login_successful'] = True
        info['mirror'] = lib.mirror
        info['cookies_count'] = len(lib.cookies) if lib.cookies else 0
    except Exception as e:
        info['error'] = str(e)
    
    return info
```

## Contributing Examples

To contribute new examples:

1. **Follow the existing structure**
2. **Include comprehensive error handling**
3. **Add detailed comments**
4. **Test with different scenarios**
5. **Update this README**

See [`../doc/contributing.md`](../doc/contributing.md) for full contribution guidelines.

## Legal Notice

These examples are for educational purposes. Users must:
- Comply with Z-Library's terms of service
- Respect copyright laws
- Use the service responsibly
- Not abuse rate limits or overload servers

## Support

- **Documentation**: [`../doc/`](../doc/)
- **API Reference**: [`../doc/api-reference.md`](../doc/api-reference.md)
- **Troubleshooting**: [`../doc/troubleshooting.md`](../doc/troubleshooting.md)
- **GitHub Issues**: Report bugs and request features