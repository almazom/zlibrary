# Troubleshooting Guide

This guide covers common issues and their solutions when using the Z-Library Python API.

## Common Authentication Issues

### Login Failed Error

**Symptoms:**
- `LoginFailed` exception when calling `login()`
- "Invalid credentials" messages
- Authentication timeouts

**Solutions:**

1. **Verify Credentials**
   ```python
   # Double-check your credentials
   email = "your-correct-email@example.com"
   password = "your-correct-password"
   await lib.login(email, password)
   ```

2. **Check Account Status**
   - Ensure your account is active
   - Verify you have singlelogin access
   - Check if account is temporarily locked

3. **Network Issues**
   ```python
   # Try with different domain
   lib = zlibrary.AsyncZlib(onion=False)  # Use clearnet
   # or
   lib = zlibrary.AsyncZlib(onion=True, proxy_list=['socks5://127.0.0.1:9050'])  # Use Tor
   ```

4. **Rate Limiting**
   ```python
   # Add delay between attempts
   import asyncio
   
   for attempt in range(3):
       try:
           await lib.login(email, password)
           break
       except zlibrary.exception.LoginFailed:
           if attempt < 2:
               await asyncio.sleep(5)  # Wait 5 seconds
           else:
               raise
   ```

### Cookie/Session Issues

**Symptoms:**
- Login succeeds but subsequent requests fail
- "No profile" errors after login
- Session expires quickly

**Solutions:**

1. **Check Cookie Persistence**
   ```python
   # Verify cookies are set after login
   await lib.login(email, password)
   print(f"Cookies: {lib.cookies}")
   
   # Ensure mirror domain is set
   print(f"Mirror: {lib.mirror}")
   ```

2. **Domain Resolution Problems**
   ```python
   # Manually set mirror if auto-detection fails
   await lib.login(email, password)
   if not lib.mirror:
       lib.mirror = "https://z-library.sk"
   ```

## Search and Data Issues

### Empty Search Results

**Symptoms:**
- `EmptyQueryError` exceptions
- No results for valid queries
- Unexpected empty result sets

**Solutions:**

1. **Query Validation**
   ```python
   # Ensure query is not empty
   query = "python programming"
   if not query.strip():
       raise ValueError("Query cannot be empty")
   
   await lib.search(q=query)
   ```

2. **Filter Conflicts**
   ```python
   # Check if filters are too restrictive
   try:
       results = await lib.search(
           q="programming",
           from_year=2023,
           to_year=2024,
           lang=[Language.ENGLISH],
           extensions=[Extension.PDF]
       )
   except Exception:
       # Try with fewer filters
       results = await lib.search(q="programming")
   ```

3. **Encoding Issues**
   ```python
   # Handle special characters properly
   import urllib.parse
   
   query = "C++ programming"  # Plus signs can cause issues
   # The library handles encoding, but be aware of special chars
   ```

### Parse Errors

**Symptoms:**
- `ParseError` exceptions
- Incorrect data extraction
- Missing book information

**Solutions:**

1. **HTML Structure Changes**
   ```python
   # Enable debug logging to see raw HTML
   import logging
   logging.getLogger("zlibrary").setLevel(logging.DEBUG)
   
   try:
       results = await lib.search(q="test")
   except zlibrary.exception.ParseError as e:
       print(f"Parse error: {e}")
       # Check if Z-Library changed their HTML structure
   ```

2. **Regional Differences**
   ```python
   # Some regions may have different page layouts
   # Try different domains or proxy locations
   lib = zlibrary.AsyncZlib(
       proxy_list=['http://proxy-in-different-region.com:8080']
   )
   ```

## Network and Connectivity Issues

### Timeout Errors

**Symptoms:**
- Requests timing out
- Slow response times
- Connection failures

**Solutions:**

1. **Adjust Timeouts**
   ```python
   # Modify timeout in util.py if needed
   # Default is 180 seconds total, 120 seconds for socket connect
   ```

2. **Network Optimization**
   ```python
   # Reduce concurrent requests
   lib = zlibrary.AsyncZlib(disable_semaphore=True)
   
   # Add delays between requests
   await asyncio.sleep(1)
   ```

3. **Proxy Issues**
   ```python
   # Test without proxy first
   lib = zlibrary.AsyncZlib()  # No proxy
   
   # Then test with proxy
   lib = zlibrary.AsyncZlib(proxy_list=['socks5://127.0.0.1:9050'])
   ```

### Proxy Configuration Problems

**Symptoms:**
- `ProxyNotMatchError` exceptions
- Connection refused errors
- Slow proxy connections

**Solutions:**

1. **Verify Proxy Availability**
   ```bash
   # Test proxy manually
   curl --proxy socks5://127.0.0.1:9050 https://httpbin.org/ip
   ```

2. **Proxy Chain Issues**
   ```python
   # Test with single proxy first
   lib = zlibrary.AsyncZlib(proxy_list=['socks5://127.0.0.1:9050'])
   
   # Then add chain if needed
   lib = zlibrary.AsyncZlib(proxy_list=[
       'http://proxy1.com:8080',
       'socks5://127.0.0.1:9050'
   ])
   ```

3. **Tor-Specific Issues**
   ```bash
   # Ensure Tor is running
   sudo systemctl status tor
   
   # Check Tor log for errors
   sudo journalctl -u tor -f
   
   # Test Tor connection
   curl --socks5 127.0.0.1:9050 https://check.torproject.org/
   ```

## Performance Issues

### Slow Search Performance

**Symptoms:**
- Long delays for search results
- Timeouts on large result sets
- Memory usage issues

**Solutions:**

1. **Optimize Search Parameters**
   ```python
   # Use smaller page sizes
   paginator = await lib.search(q="programming", count=10)  # Instead of 50
   
   # Add specific filters to reduce result set
   paginator = await lib.search(
       q="programming",
       from_year=2020,
       extensions=[Extension.PDF]
   )
   ```

2. **Batch Processing**
   ```python
   # Process results in batches
   async def process_search_batches(query, batch_size=5):
       paginator = await lib.search(q=query, count=batch_size)
       
       while True:
           try:
               books = await paginator.next()
               if not books:
                   break
               
               # Process batch
               for book in books:
                   details = await book.fetch()
                   # Process book details
               
               # Rate limiting
               await asyncio.sleep(1)
               
           except Exception as e:
               print(f"Batch error: {e}")
               break
   ```

3. **Memory Management**
   ```python
   # Clear paginator storage periodically
   paginator.storage.clear()
   
   # Limit stored pages
   if len(paginator.storage) > 10:
       # Keep only recent pages
       recent_pages = dict(list(paginator.storage.items())[-5:])
       paginator.storage = recent_pages
   ```

### Rate Limiting Issues

**Symptoms:**
- Sudden request failures
- Blocked IP addresses
- Temporary access restrictions

**Solutions:**

1. **Implement Exponential Backoff**
   ```python
   import random
   
   async def robust_request(func, *args, **kwargs):
       for attempt in range(5):
           try:
               return await func(*args, **kwargs)
           except Exception as e:
               if attempt == 4:
                   raise
               
               # Exponential backoff with jitter
               delay = (2 ** attempt) + random.uniform(0, 1)
               await asyncio.sleep(delay)
   ```

2. **Request Spacing**
   ```python
   # Add consistent delays
   class RateLimitedZlib(zlibrary.AsyncZlib):
       async def _r(self, url: str):
           result = await super()._r(url)
           await asyncio.sleep(0.5)  # 500ms delay
           return result
   ```

## Download and Access Issues

### Download Limit Reached

**Symptoms:**
- Cannot download books
- "Limit exceeded" messages
- Download buttons not available

**Solutions:**

1. **Check Download Limits**
   ```python
   limits = await lib.profile.get_limits()
   print(f"Remaining downloads: {limits['daily_remaining']}")
   print(f"Reset in: {limits['daily_reset']} hours")
   
   if limits['daily_remaining'] <= 0:
       print("Daily limit reached, waiting for reset...")
   ```

2. **Monitor Usage**
   ```python
   async def check_limits_before_download():
       limits = await lib.profile.get_limits()
       if limits['daily_remaining'] <= 0:
           reset_hours = limits['daily_reset']
           raise Exception(f"Download limit reached. Reset in {reset_hours} hours.")
       return limits
   ```

### Access Denied Errors

**Symptoms:**
- Cannot access certain books
- Premium content restrictions
- Geographic limitations

**Solutions:**

1. **Account Level Check**
   ```python
   # Some content requires premium accounts
   # Check account status in profile
   try:
       limits = await lib.profile.get_limits()
       if limits['daily_allowed'] < 10:
           print("Consider upgrading account for better access")
   except Exception:
       print("Cannot access profile - check login status")
   ```

2. **Alternative Formats**
   ```python
   # Try different file formats
   formats = [Extension.PDF, Extension.EPUB, Extension.TXT]
   
   for fmt in formats:
       try:
           results = await lib.search(
               q="book title",
               extensions=[fmt]
           )
           if results.result:
               print(f"Found in {fmt} format")
               break
       except Exception:
           continue
   ```

## Development and Testing Issues

### Testing with Mock Data

**Symptoms:**
- Need to test without making real requests
- Development environment limitations
- API changes breaking tests

**Solutions:**

1. **Mock HTTP Requests**
   ```python
   import unittest.mock
   
   async def mock_test():
       with unittest.mock.patch('zlibrary.util.GET_request') as mock_get:
           mock_get.return_value = "<html>Mock response</html>"
           
           # Test your code here
           lib = zlibrary.AsyncZlib()
           # This will use mocked responses
   ```

2. **Environment-Specific Configuration**
   ```python
   import os
   
   if os.getenv('ENVIRONMENT') == 'test':
       # Use test credentials or mock data
       lib = MockZlibrary()
   else:
       lib = zlibrary.AsyncZlib()
   ```

### Debugging API Changes

**Symptoms:**
- Code suddenly stops working
- New error messages
- Changed response formats

**Solutions:**

1. **Enable Comprehensive Logging**
   ```python
   import logging
   
   # Enable all zlibrary logs
   logging.getLogger("zlibrary").setLevel(logging.DEBUG)
   
   # Enable aiohttp logs
   logging.getLogger("aiohttp").setLevel(logging.DEBUG)
   
   # Enable detailed error tracebacks
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Response Inspection**
   ```python
   # Intercept and log raw responses
   original_get = zlibrary.util.GET_request
   
   async def logging_get_request(*args, **kwargs):
       response = await original_get(*args, **kwargs)
       print(f"Response length: {len(response)}")
       print(f"First 500 chars: {response[:500]}")
       return response
   
   zlibrary.util.GET_request = logging_get_request
   ```

## Error Recovery Patterns

### Graceful Degradation

```python
async def robust_search(query, max_retries=3):
    """Search with fallback strategies."""
    strategies = [
        # Strategy 1: Full search with filters
        lambda: lib.search(
            q=query,
            lang=[Language.ENGLISH],
            extensions=[Extension.PDF]
        ),
        # Strategy 2: Basic search without filters  
        lambda: lib.search(q=query),
        # Strategy 3: Simplified query
        lambda: lib.search(q=query.split()[0])  # First word only
    ]
    
    for strategy in strategies:
        for attempt in range(max_retries):
            try:
                return await strategy()
            except Exception as e:
                print(f"Strategy failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                break  # Try next strategy
    
    raise Exception("All search strategies failed")
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'closed'  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
            
            raise e
```

## Getting Help

### Enable Debug Mode

```python
import logging
import zlibrary

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("zlibrary")
logger.setLevel(logging.DEBUG)
```

### Collect Diagnostic Information

```python
async def get_diagnostic_info():
    """Collect information for bug reports."""
    import sys
    import aiohttp
    
    info = {
        'python_version': sys.version,
        'aiohttp_version': aiohttp.__version__,
        'zlibrary_version': '1.0.2',  # Update as needed
        'platform': sys.platform,
    }
    
    try:
        lib = zlibrary.AsyncZlib()
        await lib.login(email, password)
        info['login_successful'] = True
        info['mirror'] = lib.mirror
        info['cookies_count'] = len(lib.cookies) if lib.cookies else 0
    except Exception as e:
        info['login_successful'] = False
        info['login_error'] = str(e)
    
    return info
```

### Community Resources

- GitHub Issues: Report bugs and request features
- Documentation: Check API reference and guides
- Examples: Review working code samples
- Logs: Always include relevant log output when reporting issues

Remember to never include credentials or personal information when sharing diagnostic information or requesting help.