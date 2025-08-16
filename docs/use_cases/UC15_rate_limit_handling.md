# UC15: Rate Limit Detection and Handling

## Feature: Intelligent Rate Limiting
As a system user
I want the service to respect rate limits
So that accounts don't get banned or throttled

## Background
Given multiple Z-Library accounts
And API rate limits exist

## Scenario 1: Rate Limit Detection
```gherkin
Given an account is making requests
When the response indicates rate limiting (429 status)
Then the system should:
  - Detect the rate limit immediately
  - Extract retry-after header if present
  - Switch to another account
  - Queue the request for later
```

## Scenario 2: Adaptive Throttling
```gherkin
Given request rate is 10 requests/second
When rate limit warnings appear
Then the system should:
  - Reduce rate to 5 requests/second
  - Monitor for improvements
  - Gradually increase rate if stable
  - Maintain optimal throughput
```

## Scenario 3: Per-Account Rate Tracking
```gherkin
Given 3 accounts with different limits:
  | Account | Limit | Period |
  | 1 | 100 | 1 hour |
  | 2 | 50 | 1 hour |
  | 3 | 200 | 1 hour |
When requests are distributed
Then each account should stay within limits
And load balancing should be proportional
```

## Scenario 4: Burst Protection
```gherkin
Given a burst of 50 simultaneous requests
When the system processes them
Then requests should be:
  - Queued and throttled
  - Distributed across accounts
  - Delayed to prevent triggering limits
  - Completed without any 429 errors
```

## Implementation Strategy

### 1. Rate Limiter Design
```python
class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        
    async def acquire(self):
        """Wait if necessary to respect rate limit"""
        now = time.time()
        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
            
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            wait_time = self.requests[0] + self.time_window - now
            await asyncio.sleep(wait_time)
            
        self.requests.append(now)
```

### 2. Adaptive Throttling
```python
class AdaptiveThrottler:
    def __init__(self):
        self.current_rate = 10  # requests/second
        self.min_rate = 1
        self.max_rate = 20
        self.success_count = 0
        self.limit_count = 0
        
    def adjust_rate(self, was_limited: bool):
        if was_limited:
            # Reduce rate by 50%
            self.current_rate = max(self.min_rate, self.current_rate * 0.5)
            self.limit_count += 1
        else:
            self.success_count += 1
            # Increase rate by 10% after 10 successes
            if self.success_count >= 10:
                self.current_rate = min(self.max_rate, self.current_rate * 1.1)
                self.success_count = 0
```

### 3. Account-Specific Limits
```python
ACCOUNT_LIMITS = {
    'account1': {'requests': 100, 'period': 3600},
    'account2': {'requests': 50, 'period': 3600},
    'account3': {'requests': 200, 'period': 3600}
}
```

### 4. Request Queue Management
```python
class RequestQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = False
        
    async def add(self, request):
        await self.queue.put(request)
        if not self.processing:
            asyncio.create_task(self.process())
            
    async def process(self):
        self.processing = True
        while not self.queue.empty():
            request = await self.queue.get()
            await self.rate_limiter.acquire()
            await self.execute(request)
        self.processing = False
```

## Rate Limit Indicators
- HTTP 429 Too Many Requests
- Headers: X-RateLimit-Limit, X-RateLimit-Remaining
- Response body: "rate limit exceeded"
- Slow response times (>5s)
- Connection refused

## Recovery Strategies
1. **Immediate**: Switch account
2. **Short-term**: Reduce rate by 50%
3. **Medium-term**: Implement exponential backoff
4. **Long-term**: Analyze patterns and optimize

## Success Criteria
- ✅ Zero 429 errors during normal operation
- ✅ Automatic rate adjustment within 10 seconds
- ✅ Maintain 80% of optimal throughput
- ✅ No account bans or suspensions
- ✅ Request completion rate >99%

## Monitoring Metrics
- Requests per second per account
- Rate limit hits per hour
- Average queue depth
- Response time percentiles
- Throttle adjustment frequency