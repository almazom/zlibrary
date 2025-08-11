# UC18: Mirror Failover Strategy

## Feature: Automatic Mirror Switching
As a user accessing Z-Library
I want automatic failover to working mirrors
So that service remains available despite mirror blocks

## Background
Given multiple Z-Library mirrors exist
And mirrors can be blocked or slow

## Scenario 1: Primary Mirror Failure
```gherkin
Given primary mirror z-library.sk is blocked
When user attempts to search
Then system should:
  - Detect failure (timeout/403/451)
  - Switch to mirror z-library.se
  - Retry request automatically
  - Complete within 5 seconds total
```

## Scenario 2: Geographic Optimization
```gherkin
Given user is in Europe
And mirrors available:
  | Mirror | Location | Latency |
  | z-library.se | Sweden | 20ms |
  | z-library.asia | Singapore | 180ms |
  | z-library.is | Iceland | 45ms |
When selecting mirror
Then prioritize by latency: .se → .is → .asia
```

## Scenario 3: Response Time Monitoring
```gherkin
Given active mirror response times:
  | Mirror | Avg Response | Status |
  | mirror1 | 500ms | healthy |
  | mirror2 | 5000ms | slow |
  | mirror3 | timeout | dead |
When mirror2 becomes slow (>3s)
Then mark as degraded
And switch to mirror1
```

## Scenario 4: Cascading Failover
```gherkin
Given mirror1 is primary
When mirror1 fails
Then try mirror2
When mirror2 also fails
Then try mirror3
When all mirrors fail
Then return cached results if available
And notify user of service disruption
```

## Implementation Strategy

### 1. Mirror Configuration
```python
MIRRORS = [
    {
        'domain': 'z-library.sk',
        'region': 'eu-central',
        'priority': 1,
        'type': 'clearnet'
    },
    {
        'domain': 'z-library.se', 
        'region': 'eu-north',
        'priority': 2,
        'type': 'clearnet'
    },
    {
        'domain': 'z-library.is',
        'region': 'eu-north',
        'priority': 3,
        'type': 'clearnet'
    },
    {
        'domain': 'zlibrary-asia.se',
        'region': 'asia',
        'priority': 4,
        'type': 'clearnet'
    },
    {
        'domain': 'bookszlibb74ugqojhzhg2a63w5i2atv5bqarulgczawnbmsb6s6qead.onion',
        'region': 'tor',
        'priority': 5,
        'type': 'onion'
    }
]
```

### 2. Health Check System
```python
class MirrorHealthCheck:
    async def check_mirror(self, mirror):
        try:
            start = time.time()
            response = await session.get(
                f"https://{mirror}/", 
                timeout=3
            )
            latency = time.time() - start
            
            return {
                'mirror': mirror,
                'status': 'healthy' if response.status == 200 else 'degraded',
                'latency': latency,
                'status_code': response.status
            }
        except:
            return {
                'mirror': mirror,
                'status': 'dead',
                'latency': float('inf')
            }
```

### 3. Failover Logic
```python
class MirrorFailover:
    def __init__(self):
        self.current_mirror = None
        self.mirror_stats = {}
        self.failover_count = 0
        
    async def get_best_mirror(self):
        # Sort by: status (healthy first), then latency
        mirrors = sorted(
            self.mirror_stats.items(),
            key=lambda x: (
                x[1]['status'] != 'healthy',
                x[1]['latency']
            )
        )
        return mirrors[0][0] if mirrors else None
    
    async def execute_with_failover(self, request_func):
        for mirror in self.get_mirror_sequence():
            try:
                result = await request_func(mirror)
                self.record_success(mirror)
                return result
            except:
                self.record_failure(mirror)
                continue
        raise Exception("All mirrors failed")
```

### 4. Geographic Detection
```python
async def detect_user_region():
    # Use IP geolocation or latency testing
    test_regions = {
        'eu': 'z-library.se',
        'us': 'z-library.is',
        'asia': 'zlibrary-asia.se'
    }
    
    best_region = None
    best_latency = float('inf')
    
    for region, mirror in test_regions.items():
        latency = await measure_latency(mirror)
        if latency < best_latency:
            best_latency = latency
            best_region = region
    
    return best_region
```

## Success Criteria
- ✅ Failover completes within 5 seconds
- ✅ Geographic optimization reduces latency >30%
- ✅ Dead mirrors detected within 3 attempts
- ✅ Service availability >99.5%
- ✅ Smooth user experience during switches

## Monitoring Metrics
- Mirror response times (p50, p95, p99)
- Failover frequency per hour
- Success rate per mirror
- Geographic distribution of requests
- Cache hit rate during outages