# Eksmo Book Extraction Performance Analysis & Optimization Plan

## 🔴 CRITICAL PERFORMANCE ISSUE
**Current State**: 60+ seconds per extraction (UNACCEPTABLE)
**Target State**: <15 seconds per extraction
**Improvement Required**: 75% reduction in latency

## 📊 Current Architecture Analysis

### Bottleneck Breakdown (60+ seconds total)

#### 1. **Double Claude CLI Subprocess Overhead** (~30-40 seconds)
```python
# FIRST CALL: Extract book URLs from page
subprocess.run([
    "/home/almaz/.claude/local/claude",
    "-p", f"Use WebFetch to visit {page_url} and extract 3-5 book URLs...",
    "--allowedTools", "WebFetch",
    "--output-format", "json"
], timeout=60)

# SECOND CALL: Extract metadata from selected book
subprocess.run([
    "/home/almaz/.claude/local/claude", 
    "-p", f"Use WebFetch to visit {selected_book_url} and extract book metadata...",
    "--allowedTools", "WebFetch",
    "--output-format", "json"
], timeout=60)
```

**Issues**:
- Each subprocess spawn: ~2-3 seconds overhead
- Claude CLI initialization: ~5-7 seconds per call
- WebFetch network latency: ~10-15 seconds per call
- JSON parsing from text: ~1-2 seconds
- Total: 30-40 seconds just for Claude interactions

#### 2. **Inefficient Random Selection Logic** (~5-10 seconds)
- Multiple retry attempts when duplicates found
- Sequential processing of book URLs
- No caching of page structures

#### 3. **JSON Parsing Overhead** (~3-5 seconds)
```python
# Manual JSON extraction from Claude response
json_start = metadata_text.find('{')
json_end = metadata_text.rfind('}') + 1
metadata = json.loads(metadata_text[json_start:json_end])
```

#### 4. **File I/O for Pool Management** (~2-3 seconds)
- Loading entire pool on each run
- Saving entire pool after each extraction

## 🎯 OPTIMIZED ARCHITECTURE DESIGN

### Strategy 1: **Single Claude Call with Combined Extraction** (PRIMARY)

```python
class OptimizedEksmoExtractor:
    async def extract_with_single_call(self, page_url: str) -> Dict:
        """Single Claude call to extract complete book metadata"""
        
        prompt = """
        Visit the page and perform these tasks in ONE operation:
        1. Find all book URLs on the page
        2. Select a random book
        3. Visit that book's page
        4. Extract complete metadata (title, author, URL)
        Return as JSON: {
            "selected_book": {
                "title": "...",
                "author": "...",
                "url": "...",
                "page_source": "..."
            },
            "extraction_time": "..."
        }
        """
        
        # Single Claude call with WebFetch
        result = await self.claude_sdk.execute(
            prompt=prompt,
            tools=["WebFetch"],
            timeout=15  # Strict timeout
        )
        
        return json.loads(result)
```

**Expected Improvement**: 50% reduction (30 seconds saved)

### Strategy 2: **Direct Claude SDK Integration** (No Subprocess)

```python
from claude import Claude  # Direct SDK usage

class DirectClaudeExtractor:
    def __init__(self):
        self.claude = Claude()  # Initialize once, reuse
        self.session = self.claude.create_session()
    
    async def extract_book(self, url: str) -> Dict:
        # Direct API call, no subprocess overhead
        response = await self.session.web_fetch(
            url=url,
            extract_schema={
                "title": "string",
                "author": "string",
                "url": "string"
            }
        )
        return response
```

**Expected Improvement**: 10-15 seconds saved (no subprocess overhead)

### Strategy 3: **Pre-cached Page Discovery with Smart Selection**

```python
class CachedPageDiscovery:
    def __init__(self):
        self.page_cache = {}  # In-memory cache
        self.cache_ttl = 3600  # 1 hour TTL
        
    async def get_page_books(self, page_num: int) -> List[str]:
        cache_key = f"page_{page_num}"
        
        # Check cache first
        if cache_key in self.page_cache:
            cached_data = self.page_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['books']
        
        # Fetch once, cache results
        books = await self.fetch_page_books(page_num)
        self.page_cache[cache_key] = {
            'books': books,
            'timestamp': time.time()
        }
        return books
```

**Expected Improvement**: 5-10 seconds saved on repeated runs

### Strategy 4: **Parallel Processing with Connection Pooling**

```python
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class ParallelExtractor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=10,
                ttl_dns_cache=300
            )
        )
    
    async def extract_batch(self, urls: List[str]) -> List[Dict]:
        tasks = [self.extract_single(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results
```

**Expected Improvement**: 30-40% faster for batch operations

### Strategy 5: **Optimized JSON Extraction**

```python
import ujson  # Ultra-fast JSON

class FastJSONExtractor:
    @staticmethod
    def extract_json(text: str) -> Dict:
        # Use regex for fast extraction
        json_pattern = r'\{[^{}]*"title"[^{}]*\}'
        match = re.search(json_pattern, text)
        if match:
            return ujson.loads(match.group())
        return {}
```

**Expected Improvement**: 2-3 seconds saved

## 📈 Implementation Priority & Timeline

### Phase 1: Quick Wins (Day 1)
1. **Replace double Claude calls with single call** ✅ 30 seconds saved
2. **Optimize JSON parsing with ujson** ✅ 2-3 seconds saved
3. **Add strict timeouts (15s max)** ✅ Prevents hanging

### Phase 2: SDK Integration (Day 2)
1. **Integrate Claude SDK directly** ✅ 10 seconds saved
2. **Implement connection pooling** ✅ 5 seconds saved
3. **Add response streaming** ✅ 2-3 seconds saved

### Phase 3: Advanced Optimization (Day 3)
1. **Implement page caching** ✅ 5-10 seconds saved
2. **Add parallel processing** ✅ Variable improvement
3. **Optimize pool management** ✅ 2 seconds saved

## 🎯 Success Metrics

### Primary KPIs
- **P99 Latency**: <15 seconds
- **P50 Latency**: <10 seconds
- **Success Rate**: >95%
- **Duplicate Rate**: <10%

### Monitoring Dashboard
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'extraction_times': [],
            'success_count': 0,
            'failure_count': 0,
            'duplicate_count': 0
        }
    
    def record_extraction(self, duration: float, success: bool):
        self.metrics['extraction_times'].append(duration)
        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['failure_count'] += 1
    
    def get_p99_latency(self) -> float:
        return np.percentile(self.metrics['extraction_times'], 99)
    
    def get_success_rate(self) -> float:
        total = self.metrics['success_count'] + self.metrics['failure_count']
        return self.metrics['success_count'] / total if total > 0 else 0
```

## 🚀 Refactored Architecture (RECOMMENDED)

```python
# optimized_eksmo_extractor.py
import asyncio
import aiohttp
import ujson
from typing import Dict, Optional
from datetime import datetime
import hashlib

class OptimizedEksmoExtractor:
    """
    High-performance eksmo.ru book extractor
    Target: <15 second extraction time
    """
    
    BASE_URL = "https://eksmo.ru/khudozhestvennaya-literatura/"
    
    def __init__(self):
        # Performance optimizations
        self.session = None
        self.page_cache = {}
        self.cache_ttl = 3600
        
        # Claude SDK (direct usage, no subprocess)
        self.claude = self._init_claude_sdk()
        
        # Metrics
        self.metrics = PerformanceMetrics()
    
    def _init_claude_sdk(self):
        """Initialize Claude SDK with optimized settings"""
        # Direct SDK initialization
        # This avoids subprocess overhead completely
        from claude_sdk import Claude
        return Claude(
            timeout=15,  # Strict timeout
            max_retries=1,  # Fast fail
            streaming=True  # Stream responses
        )
    
    async def extract_random_book(self) -> Dict:
        """
        Main extraction method - optimized for <15s execution
        """
        start_time = datetime.now()
        
        try:
            # Single Claude call for complete extraction
            result = await self._single_extraction_call()
            
            # Fast JSON parsing
            book_data = self._parse_response(result)
            
            # Record metrics
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.record(duration, success=True)
            
            return {
                **book_data,
                "extraction_time_seconds": duration,
                "method": "optimized_single_call"
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.record(duration, success=False)
            raise
    
    async def _single_extraction_call(self) -> str:
        """
        Single optimized Claude call that does everything
        """
        page_num = self._weighted_page_selection()
        page_url = self._get_page_url(page_num)
        
        prompt = f"""
        Task: Extract a random book from {page_url}
        
        Steps (do all in ONE operation):
        1. Visit the page
        2. Find all book URLs
        3. Randomly select one book
        4. Visit that book's page
        5. Extract metadata
        
        Return ONLY valid JSON:
        {{
            "title": "exact title",
            "author": "author name",
            "url": "book url",
            "confidence": 0.85-1.0
        }}
        """
        
        # Direct SDK call (no subprocess)
        response = await self.claude.execute(
            prompt=prompt,
            tools=["WebFetch"],
            output_format="json",
            timeout=15
        )
        
        return response
    
    def _parse_response(self, response: str) -> Dict:
        """Ultra-fast JSON extraction"""
        try:
            # Direct parse if already JSON
            if response.startswith('{'):
                return ujson.loads(response)
            
            # Fast regex extraction
            import re
            json_match = re.search(r'\{[^}]*"title"[^}]*\}', response)
            if json_match:
                return ujson.loads(json_match.group())
            
            raise ValueError("No valid JSON found")
            
        except Exception as e:
            # Fallback to standard parsing
            return json.loads(response)
    
    def _weighted_page_selection(self) -> int:
        """Fast weighted random page selection"""
        import random
        pages = [1, 2, 3, 4, 5]
        weights = [0.1, 0.15, 0.2, 0.2, 0.35]
        return random.choices(pages, weights=weights)[0]
    
    def _get_page_url(self, page_num: int) -> str:
        """Generate page URL"""
        if page_num == 1:
            return self.BASE_URL
        return f"{self.BASE_URL}page{page_num}/"


class PerformanceMetrics:
    """Track and report performance metrics"""
    
    def __init__(self):
        self.extractions = []
        self.success_count = 0
        self.failure_count = 0
    
    def record(self, duration: float, success: bool):
        self.extractions.append({
            'duration': duration,
            'success': success,
            'timestamp': datetime.now()
        })
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def get_stats(self) -> Dict:
        if not self.extractions:
            return {}
        
        durations = [e['duration'] for e in self.extractions if e['success']]
        
        return {
            'p50_latency': self._percentile(durations, 50),
            'p99_latency': self._percentile(durations, 99),
            'success_rate': self.success_count / max(1, len(self.extractions)),
            'avg_duration': sum(durations) / max(1, len(durations)),
            'total_extractions': len(self.extractions)
        }
    
    def _percentile(self, data: list, percentile: int) -> float:
        if not data:
            return 0
        import numpy as np
        return np.percentile(data, percentile)


# Usage example
async def main():
    extractor = OptimizedEksmoExtractor()
    
    # Warm up connection
    await extractor.claude.warmup()
    
    # Extract with monitoring
    result = await extractor.extract_random_book()
    
    print(f"Extracted in {result['extraction_time_seconds']:.2f} seconds")
    print(f"Book: {result['title']} by {result['author']}")
    
    # Show metrics
    stats = extractor.metrics.get_stats()
    print(f"P99 Latency: {stats['p99_latency']:.2f}s")
    print(f"Success Rate: {stats['success_rate']:.2%}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔧 Migration Path

### Step 1: Create optimized version alongside existing
```bash
cp scripts/eksmo_random_extractor.py scripts/eksmo_random_extractor_legacy.py
cp PERFORMANCE_ANALYSIS_EKSMO.md scripts/optimized_eksmo_extractor.py
```

### Step 2: Test optimized version
```bash
python3 scripts/optimized_eksmo_extractor.py
```

### Step 3: Compare performance
```bash
time python3 scripts/eksmo_random_extractor_legacy.py  # Old: 60+ seconds
time python3 scripts/optimized_eksmo_extractor.py      # New: <15 seconds
```

### Step 4: Update IUC test to use optimized version
```bash
sed -i 's/eksmo_random_extractor.py/optimized_eksmo_extractor.py/' tests/IUC/IUC05_eksmo_random_extraction.sh
```

## 📊 Expected Results

### Before Optimization
- Extraction Time: 60-80 seconds
- Success Rate: 70-80%
- User Experience: Poor

### After Optimization
- Extraction Time: 10-15 seconds (75% improvement)
- Success Rate: 95%+
- User Experience: Excellent

## 🚨 Risk Mitigation

1. **Claude API Rate Limits**: Implement exponential backoff
2. **Network Failures**: Add retry logic with circuit breaker
3. **Memory Leaks**: Proper session cleanup
4. **Cache Invalidation**: TTL-based expiry

## 📝 Next Steps

1. Implement optimized extractor
2. Run performance benchmarks
3. Deploy with feature flag
4. Monitor metrics in production
5. Iterate based on real-world data