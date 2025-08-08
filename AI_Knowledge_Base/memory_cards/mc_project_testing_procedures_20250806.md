# Memory Card: Z-Library Testing Procedures
---
id: mc_project_testing_procedures_20250806
type: memory_card
category: project
created: 2025-08-06
status: active
---

## Test Environment Setup

### Required Environment Variables
```bash
export ZLOGIN="your_email@example.com"
export ZPASSW="your_password"
```

### Test File Locations
- Unit tests: `tests/`
- Integration tests: `src/test.py`
- Example tests: `examples/python/`
- Edge case tests: `test_penguin_books.py`

## Basic Functionality Tests

### 1. Authentication Test
```python
# tests/test_auth_only.py
async def test_login():
    client = AsyncZlib()
    profile = await client.login(email, password)
    assert profile is not None
    await client.logout()
```

### 2. Search Test
```python
async def test_search():
    client = AsyncZlib()
    await client.login(email, password)
    
    results = await client.search(q="python", count=5)
    await results.init()
    
    assert results.total > 0
    assert len(results.result) <= 5
    
    await client.logout()
```

### 3. Book Fetch Test
```python
async def test_book_fetch():
    client = AsyncZlib()
    await client.login(email, password)
    
    results = await client.search(q="python", count=1)
    await results.init()
    
    if results.result:
        book = results.result[0]
        details = await book.fetch()
        
        assert 'name' in details
        assert 'download_url' in details
    
    await client.logout()
```

## Edge Case Testing

### Penguin Books Test
```bash
python3 test_penguin_books.py
```
Tests:
- Publisher-specific search
- Sequential download (no batching)
- EPUB format filtering
- Rate limiting handling

### Empty Query Test
```python
try:
    await client.search(q="")
    assert False, "Should raise EmptyQueryError"
except EmptyQueryError:
    pass  # Expected
```

### Invalid ID Test
```python
try:
    await client.get_by_id("")
    assert False, "Should raise NoIdError"
except NoIdError:
    pass  # Expected
```

### Special Characters Test
```python
results = await client.search(
    q="Python & Machine Learning @ 2024",
    count=1
)
await results.init()
# Should handle special characters gracefully
```

## Performance Testing

### Concurrent Requests Test
```python
async def test_concurrent():
    client = AsyncZlib()
    await client.login(email, password)
    
    # Test semaphore limiting (max 64)
    tasks = []
    for i in range(100):
        task = client.search(f"test{i}", count=1)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Should handle without overwhelming the server
```

### Sequential vs Batch Processing
```python
# Sequential (recommended for downloads)
for book in books:
    details = await book.fetch()
    await asyncio.sleep(1)  # Rate limiting

# Batch (for metadata only)
tasks = [book.fetch() for book in books[:5]]
details_list = await asyncio.gather(*tasks)
```

## Integration Testing

### Full Workflow Test
```python
async def test_full_workflow():
    client = AsyncZlib()
    
    # 1. Login
    profile = await client.login(email, password)
    
    # 2. Check limits
    limits = await profile.get_limits()
    print(f"Remaining: {limits['daily_remaining']}")
    
    # 3. Search
    results = await client.search(
        q="python programming",
        extensions=[Extension.EPUB],
        lang=[Language.ENGLISH],
        count=10
    )
    await results.init()
    
    # 4. Navigate pages
    if results.total > 1:
        await results.next_page()
        await results.prev_page()
    
    # 5. Fetch book details
    if results.result:
        book = results.result[0]
        details = await book.fetch()
        print(f"Download URL: {details['download_url']}")
    
    # 6. Check history
    history = await profile.download_history()
    
    # 7. Logout
    await client.logout()
```

## Proxy/Tor Testing

### Tor Connection Test
```python
client = AsyncZlib(
    onion=True,
    proxy_list=['socks5://127.0.0.1:9050']
)
await client.login(email, password)
# Should connect through Tor
```

### Proxy Chain Test
```python
client = AsyncZlib(
    proxy_list=[
        'http://proxy1:8080',
        'socks5://proxy2:1080'
    ]
)
# Should route through proxy chain
```

## Run All Tests

### Using Script
```bash
# Run all tests
python3 src/test.py

# With logging
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import src.test
"
```

### Manual Test Suite
```bash
# Basic tests
python3 tests/test_auth_only.py

# Real download test
python3 tests/test_real_download.py

# Example scripts
python3 examples/python/basic_usage.py
python3 examples/python/advanced_features.py

# Edge cases
python3 test_penguin_books.py
```

## Expected Results

### Successful Test Output
```
✅ Login successful
✅ Search returned X results
✅ Book details fetched
✅ Download URL available
✅ Logout successful
```

### Common Failures
- `LoginFailed`: Invalid credentials
- `NoProfileError`: Not logged in
- `EmptyQueryError`: Empty search query
- `ParseError`: HTML structure changed
- `NoDomainError`: No working domain found