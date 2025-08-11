# UC13: Network Resilience and Recovery

## Feature: Network Failure Recovery
As a system user
I want the service to recover from network failures
So that temporary issues don't cause permanent failures

## Background
Given the Z-Library API is configured
And accounts are available

## Scenario 1: DNS Failure Recovery
```gherkin
Given DNS resolution is failing
When I search for "Clean Code"
Then the system should:
  - Detect DNS failure
  - Try alternative DNS servers (8.8.8.8, 1.1.1.1)
  - Cache resolved IPs for future use
  - Return result or graceful error
```

## Scenario 2: Connection Timeout Handling
```gherkin
Given Z-Library server is slow (>30s response)
When I search for a book
Then the system should:
  - Timeout after 10 seconds
  - Retry with exponential backoff (2s, 4s, 8s)
  - Try alternative mirrors
  - Return cached results if available
```

## Scenario 3: SSL Certificate Issues
```gherkin
Given SSL certificate verification fails
When connecting to Z-Library
Then the system should:
  - Log the SSL error
  - Try with relaxed SSL (dev only)
  - Fallback to cached session
  - Alert user about security issue
```

## Scenario 4: Network Partition Recovery
```gherkin
Given network is completely down
When user attempts search
Then the system should:
  - Detect network unavailability
  - Return cached results if <24h old
  - Queue request for when network returns
  - Provide offline mode indication
```

## Implementation Requirements

### 1. Retry Logic
```python
async def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except NetworkError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            await asyncio.sleep(wait_time)
```

### 2. DNS Fallback
```python
DNS_SERVERS = [
    '8.8.8.8',     # Google
    '1.1.1.1',     # Cloudflare
    '9.9.9.9',     # Quad9
    '208.67.222.222' # OpenDNS
]
```

### 3. Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
```

### 4. Cache Strategy
```python
CACHE_STRATEGY = {
    'search_results': 3600,    # 1 hour
    'book_details': 86400,     # 24 hours
    'account_status': 300,     # 5 minutes
    'dns_resolution': 3600     # 1 hour
}
```

## Success Criteria
- ✅ Recovers from DNS failures within 3 attempts
- ✅ Handles timeouts gracefully with backoff
- ✅ Maintains service during network issues via cache
- ✅ Circuit breaker prevents cascade failures
- ✅ User receives clear error messages

## Test Data
```python
test_scenarios = [
    {'type': 'dns_fail', 'duration': 10},
    {'type': 'timeout', 'duration': 35},
    {'type': 'ssl_error', 'duration': 5},
    {'type': 'network_down', 'duration': 60}
]
```

## Expected Behavior
1. **First failure**: Immediate retry
2. **Second failure**: 2s wait, then retry
3. **Third failure**: 4s wait, then retry
4. **Fourth failure**: Circuit opens, cache-only mode
5. **After 60s**: Circuit half-opens, test connection
6. **Success**: Circuit closes, normal operation

## Monitoring Metrics
- Network failure rate
- Average recovery time
- Cache hit ratio
- Circuit breaker state changes
- DNS resolution time