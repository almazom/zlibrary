# IUC05 Clean Architecture Implementation Guide

**Created**: 2025-08-14
**Status**: Ready for Implementation
**Priority**: HIGH

## Quick Summary

Your IUC05 book extraction system has excellent performance (4-5s extraction, 90% success) but needs architectural refactoring to scale beyond prototype stage. The current monolithic design violates SOLID principles and will become unmaintainable as you add more sources.

## Critical Issues to Address

### 1. 🔴 No Separation of Concerns
**Problem**: `LibRuExtractor` class does everything - HTTP, parsing, caching, statistics
**Impact**: Can't test components in isolation, hard to modify
**Solution**: Split into interfaces (core), services (application), and implementations (infrastructure)

### 2. 🔴 No Plugin Architecture  
**Problem**: Adding new sources requires modifying core code
**Impact**: Risk of breaking existing extractors when adding new ones
**Solution**: `IBookExtractor` interface with pluggable implementations

### 3. 🔴 No Resilience Patterns
**Problem**: No retry logic, circuit breakers, or fallback mechanisms
**Impact**: Single failure crashes entire extraction
**Solution**: Service layer with retry, circuit breaker, and fallback strategies

## Immediate Actions (Do Today)

### Step 1: Create Core Interfaces (1 hour)
```bash
# Already created for you - review and adjust if needed
cat src/core/interfaces/extractor.py
```

### Step 2: Refactor LibRu Extractor (2 hours)
```bash
# Already created example - adapt your existing code
cat src/infrastructure/extractors/libru/extractor.py
```

### Step 3: Add Service Layer (1 hour)
```bash
# Already created - implements orchestration
cat src/application/services/extraction_service.py
```

### Step 4: Test New Architecture (30 min)
```bash
# Run the demonstration
python3 demo_clean_architecture.py
```

## Performance Improvements Available

### Current: 4-5 seconds per extraction
### Target: <3 seconds with these optimizations:

1. **Connection Pooling** (-0.5s)
   - Reuse HTTP connections instead of creating new ones
   - Implementation provided in architecture doc

2. **Memory Caching** (-1s for repeated categories)
   - Cache author lists in memory for 1 hour
   - Hybrid cache implementation provided

3. **Concurrent Requests** (-0.5s)
   - Fetch author and book lists in parallel
   - Use asyncio.gather for parallel operations

4. **Smart Category Selection** (-0.5s)
   - Track which categories have fresh content
   - Avoid repeatedly hitting same category

## File Organization (Implement This Structure)

```
/src
├── core/                    # Protected - Architect approval needed
│   ├── interfaces/         # Abstract interfaces
│   │   ├── extractor.py    ✅ Created
│   │   ├── cache.py        🔄 TODO
│   │   └── tracker.py      🔄 TODO
│   └── entities/           # Domain models
│       └── book.py         ✅ In extractor.py
│
├── application/             # Service layer
│   └── services/
│       ├── extraction_service.py  ✅ Created
│       ├── quality_service.py     🔄 TODO
│       └── cache_service.py       🔄 TODO
│
└── infrastructure/          # Concrete implementations
    └── extractors/
        ├── libru/
        │   └── extractor.py  ✅ Created
        ├── eksmo/            🔄 TODO - Refactor existing
        └── gutenberg/        🔄 Future
```

## Migration Path (Minimal Disruption)

### Week 1: Foundation
```python
# 1. Keep existing scripts working
# 2. Create new architecture in /src
# 3. Gradually migrate extractors

# Old way (keep working):
python3 scripts/lib_ru_extractor_engine.py

# New way (implement gradually):
python3 -m src.presentation.cli extract --source libru
```

### Week 2: Integration
```python
# Update book_search.sh to use new service
from src.application.services.extraction_service import ExtractionService

# Backward compatibility wrapper
def legacy_extract(source="auto"):
    service = ExtractionService(get_extractors())
    result = await service.extract_book(source=source)
    return convert_to_legacy_format(result)
```

### Week 3: Production
- Switch all IUC tests to new architecture
- Deprecate old extractors
- Enable monitoring and metrics

## Quality Checklist

### Before (Current State) ❌
- [ ] Testable in isolation
- [ ] Plugin architecture
- [ ] Retry mechanisms
- [ ] Circuit breakers
- [ ] Metrics collection
- [ ] Health monitoring
- [ ] Concurrent support
- [ ] Rate limiting

### After (Target State) ✅
- [x] Testable in isolation
- [x] Plugin architecture  
- [x] Retry mechanisms
- [x] Circuit breakers
- [x] Metrics collection
- [x] Health monitoring
- [x] Concurrent support
- [ ] Rate limiting (TODO)

## Database vs File Storage Decision

### Current: JSON files
- ✅ Simple, no dependencies
- ✅ Good for <10K records
- ❌ No concurrent access
- ❌ No query capabilities

### Recommendation: Stay with files for now, prepare for DB
```python
# Design tracker interface to support both
class ITracker(ABC):
    @abstractmethod
    async def check_duplicate(self, book_hash: str) -> bool:
        pass

# File implementation (current)
class JsonFileTracker(ITracker):
    pass

# Database implementation (future)
class PostgresTracker(ITracker):
    pass
```

## CLI Improvements

### Current Issues:
- Inconsistent argument parsing
- No unified error handling
- Mixed concerns in scripts

### Recommended: Click-based CLI
```python
# src/presentation/cli/commands.py
import click

@click.group()
def cli():
    """IUC05 Book Extraction System"""
    pass

@cli.command()
@click.option('--source', default='auto')
@click.option('--category')
@click.option('--format', type=click.Choice(['json', 'text']))
async def extract(source, category, format):
    """Extract a book from specified source"""
    service = get_extraction_service()
    result = await service.extract_book(source, category)
    output_result(result, format)

@cli.command()
async def health():
    """Check health of all sources"""
    service = get_extraction_service()
    status = await service.health_check()
    display_health(status)
```

## Monitoring & Observability

### Add These Metrics:
1. **Extraction latency** (P50, P95, P99)
2. **Success rate** by source
3. **Cache hit ratio**
4. **Concurrent requests**
5. **Error types** distribution

### Simple Implementation:
```python
# Use prometheus_client
from prometheus_client import start_http_server, Counter, Histogram

extraction_duration = Histogram(
    'extraction_duration_seconds',
    'Book extraction duration',
    ['source']
)

@extraction_duration.time()
async def extract_with_metrics(source):
    return await extract_book(source)
```

## Testing Strategy

### Unit Tests (New)
```python
# tests/unit/test_libru_extractor.py
async def test_libru_extraction():
    # Mock HTTP client
    mock_http = MockHttpClient()
    extractor = LibRuExtractor(http_client=mock_http)
    
    result = await extractor.extract(request)
    assert result.is_successful
```

### Integration Tests (Existing)
```bash
# Keep existing IUC tests
./tests/IUC/IUC05_*.sh

# Add new architecture tests
./tests/integration/test_extraction_service.py
```

### Load Tests (New)
```python
# tests/load/test_concurrent_extraction.py
async def test_100_concurrent_extractions():
    service = ExtractionService(extractors)
    requests = [create_request() for _ in range(100)]
    
    start = time.time()
    results = await service.extract_batch(requests)
    duration = time.time() - start
    
    assert duration < 60  # 100 books in under 1 minute
    assert success_rate(results) > 0.95
```

## Common Pitfalls to Avoid

1. **Don't refactor everything at once**
   - Keep existing system running
   - Migrate incrementally

2. **Don't over-engineer**
   - Start with provided examples
   - Add complexity only when needed

3. **Don't skip tests**
   - Test each component in isolation
   - Maintain existing IUC tests

4. **Don't ignore monitoring**
   - Add metrics from day 1
   - Track refactoring impact

## Questions Answered

**Q: Should we implement a plugin architecture?**
A: Yes, the `IBookExtractor` interface enables this. New sources just implement the interface.

**Q: Is file-based tracking adequate?**
A: Yes for now (<10K books). Design with `ITracker` interface for future DB migration.

**Q: How to improve CLI interface?**
A: Use Click for consistent argument parsing and help text.

**Q: What design patterns to use?**
A: Repository (data access), Service Layer (orchestration), Factory (extractor creation)

**Q: Should we separate extraction from formatting?**
A: Yes, extraction returns `ExtractionResult`, formatting is presentation layer concern.

**Q: How to handle rate limiting?**
A: Per-source rate limiters in service layer, configured in `get_source_info()`.

## Next Steps

1. **Today**: Review provided code examples
2. **Tomorrow**: Implement core interfaces
3. **This Week**: Migrate LibRu extractor
4. **Next Week**: Add service layer and tests
5. **Month End**: Production deployment

## Success Metrics

- ✅ Extraction time <3 seconds (from 4-5s)
- ✅ Success rate >95% (from 90%)
- ✅ Support 100+ concurrent requests
- ✅ Add new source in <1 hour
- ✅ 80% test coverage
- ✅ Zero downtime migration

---

**Remember**: The goal is not perfection but sustainable, maintainable growth. Start with the provided examples, test thoroughly, and iterate based on real usage.

**Your existing system works** - this refactoring makes it production-ready and maintainable for the long term.

🚀 You're 80% there with performance. This architecture gets you the last 20% plus maintainability!