# UC14: Cache Persistence Across Sessions

## Feature: Persistent Cache Management
As a system user
I want search results and account data to persist between sessions
So that restarts don't lose valuable cached data

## Background
Given the cache system is configured
And disk storage is available

## Scenario 1: Search Results Persistence
```gherkin
Given I searched for "Clean Code" yesterday
And the result was cached
When the system restarts today
And I search for "Clean Code" again
Then the cached result should be returned immediately
And the cache age should be shown
```

## Scenario 2: Account Status Persistence
```gherkin
Given account limits were checked at 09:00
And Account1 had 5/8 downloads remaining
When the system restarts at 09:30
Then the account status should show 5/8 remaining
And avoid unnecessary API calls
```

## Scenario 3: Download History Persistence
```gherkin
Given 10 books were downloaded today
When the system restarts
Then the download history should be preserved
And duplicate detection should still work
```

## Scenario 4: Cache Expiration Management
```gherkin
Given cached data exists with timestamps:
  | Type | Age | Action |
  | Search results | 2 hours | Keep |
  | Search results | 25 hours | Expire |
  | Account status | 10 minutes | Keep |
  | Account status | 6 hours | Expire |
When cache cleanup runs
Then expired entries should be removed
And valid entries should remain
```

## Implementation Design

### 1. Cache Storage Structure
```python
CACHE_DIR = "/tmp/zlibrary_cache"
CACHE_STRUCTURE = {
    "search/": "Search result cache",
    "accounts/": "Account status cache",
    "downloads/": "Download history",
    "metadata/": "Cache metadata and indexes"
}
```

### 2. Cache Entry Format
```json
{
    "key": "search_clean_code_robert_martin",
    "timestamp": "2025-08-09T10:00:00",
    "ttl": 3600,
    "hits": 5,
    "data": {
        "results": [...],
        "confidence": 0.95
    }
}
```

### 3. Cache Manager
```python
class PersistentCache:
    def __init__(self, cache_dir="/tmp/zlibrary_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def save(self, key, data, ttl=3600):
        """Save with TTL"""
        
    def load(self, key):
        """Load if not expired"""
        
    def cleanup(self):
        """Remove expired entries"""
```

### 4. Cache Strategies by Type
| Data Type | TTL | Storage | Priority |
|-----------|-----|---------|----------|
| Search results | 24h | JSON | High |
| Book details | 7d | JSON | Medium |
| Account status | 5m | JSON | Critical |
| Download history | 30d | SQLite | High |
| DNS resolution | 1h | Memory+File | Low |

## Success Criteria
- ✅ Cache survives system restarts
- ✅ Expired entries auto-cleanup
- ✅ Cache hit ratio > 30%
- ✅ Storage usage < 100MB
- ✅ Load time < 100ms

## Test Scenarios
1. **Cold Start**: No cache exists
2. **Warm Start**: Valid cache exists
3. **Partial Cache**: Some expired, some valid
4. **Corrupted Cache**: Handle gracefully
5. **Full Disk**: Graceful degradation

## Performance Metrics
- Cache hit ratio
- Average load time
- Storage usage
- Cleanup frequency
- Memory footprint