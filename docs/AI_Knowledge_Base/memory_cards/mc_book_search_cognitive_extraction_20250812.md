# Memory Card: Book Search Cognitive Extraction
**Date**: 2025-08-12  
**Project**: zlibrary_api_module
**Category**: URL Extraction, Book Search, Claude Integration

## Problem
Book search from URLs returns wrong books when multiple books have the same title but different authors (e.g., "Лунный камень" by Павич vs. Коллинз).

## Root Causes
1. **Z-Library database limitations** - doesn't have all books (especially new editions)
2. **Z-Library search prioritizes title** over author accuracy
3. **No clear "not available" message** when wrong book is found

## Solution: Mandatory Claude Cognitive Layer + Author Validation

### Always Use Claude Extraction for URLs
```bash
# MANDATORY for all URL inputs
CLAUDE_EXTRACT=true ./scripts/book_search.sh --claude-extract "URL"
```

### Extraction Prompt (config/extraction_prompts.yaml)
```yaml
eksmo:
  prompt: |
    Extract book title and author EXACTLY as written in ORIGINAL LANGUAGE
    CRITICAL: Keep title and author in the EXACT language shown on the page!
```

### WebFetch Integration
```bash
# In book_search.sh extract_query_from_url()
if [[ "$CLAUDE_EXTRACT" == "true" ]]; then
    # MUST use Claude WebFetch for cognitive extraction
    echo "CLAUDE_COGNITIVE_REQUIRED" >&2
fi
```

## Key Learnings

1. **Cognitive extraction is NON-NEGOTIABLE** for accurate book metadata
2. **Author validation is CRITICAL** for disambiguation
3. **Language context matters** - Russian sites → Russian books priority

## Implementation Status
- ✅ **Automatic Claude extraction for ALL URLs** (no flag needed!)
- ✅ Extraction prompts with language preservation  
- ✅ Author validation with `compare_authors()` function
- ✅ Confidence scoring with author matching (40% weight)
- ✅ Clear "NOT AVAILABLE" message when author mismatch detected
- ✅ Single entry point following KISS/DRY/SOLID principles

## Test Case
```bash
# URL automatically triggers Claude extraction - no flags needed!
./scripts/book_search.sh "https://eksmo.ru/book/lunnyy-kamen-ITD1334449/"

# Result: Correctly identifies book is NOT AVAILABLE
# - Extracts: "Лунный камень" by "Милорад Павич" ✓
# - Finds: "Лунный камень" by "Уилки Коллинз" ✗
# - Shows: "❌ Book NOT AVAILABLE in this service"
```

## Key Takeaway
**It's OK to say "NOT AVAILABLE"** - better than giving users the wrong book!

## Related Files
- `/scripts/book_search.sh` - Main search script
- `/config/extraction_prompts.yaml` - Extraction prompts
- `/scripts/book_search_feedback_loop.md` - Development roadmap