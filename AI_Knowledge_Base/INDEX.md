# Z-Library API Module - Knowledge Base Index

## Memory Cards
| File | Category | Topic | Created | Status |
|------|----------|-------|---------|--------|
| mc_project_zlibrary_overview_20250806.md | Project | Z-Library API Module Overview | 2025-08-06 | Active |
| mc_project_setup_instructions_20250806.md | Project | Installation and Setup Guide | 2025-08-06 | Active |
| mc_technical_api_reference_20250806.md | Technical | Complete API Reference | 2025-08-06 | Updated 2025-08-07 |
| mc_project_testing_procedures_20250806.md | Project | Testing Procedures and Examples | 2025-08-06 | Active |
| mc_technical_authentication_flow_20250806.md | Technical | Authentication and Session Management | 2025-08-06 | Active |
| mc_project_edge_cases_20250806.md | Project | Edge Cases and Error Handling | 2025-08-06 | Active |
| **mc_technical_multi_account_system_20250806.md** | **Technical** | **Multi-Account Pool System** | **2025-08-06** | **Active** |
| **mc_zlibrary_service_implementation_20250807.md** | **Implementation** | **Service Mode CLI & JSON API** | **2025-08-07** | **Active** |
| **mc_pipeline_implementation_tdd_20250807.md** | **Implementation** | **Multi-Source Pipeline TDD** | **2025-08-07** | **Active** |
| **mc_visual_pipeline_complete_20250807.md** | **Visual** | **Complete Visual Pipeline System** | **2025-08-07** | **Active** |
| **mc_book_downloads_20250808.md** | **Operations** | **Book Downloads & Service Tracking** | **2025-08-08** | **Active** |
| **mc_dual_confidence_json_schema_20250808.md** | **Schema** | **Dual Confidence JSON Schema System** | **2025-08-08** | **Active** |
| **mc_scripts_reorganization_20250808.md** | **Operations** | **Scripts Folder Reorganization & Naming** | **2025-08-08** | **Active** |

## Deep Research Archives
| File | Topic | Created | Status |
|------|-------|---------|--------|
| dr_zlibrary_api_architecture_20250806.md | Z-Library API Architecture Analysis | 2025-08-06 | Comprehensive |
| dr_penguin_books_testing_20250806.md | Penguin Books Search and Download Testing | 2025-08-06 | Research |
| dr_epub_sequential_download_20250806.md | EPUB Sequential Download Strategy | 2025-08-06 | Analysis |

## Documentation
| File | Type | Description | Created |
|------|------|-------------|---------|
| quick_start.md | Guide | Quick start guide for developers | 2025-08-06 |
| api_examples.md | Examples | Working code examples | 2025-08-06 |
| troubleshooting.md | Guide | Common issues and solutions | 2025-08-06 |

## Quick Reference

### Latest Script (2025-08-07)
```bash
# Search books (with service selection - 2025-08-08)
./scripts/zlib_book_search_fixed.sh --json "book title"              # Auto-fallback
./scripts/zlib_book_search_fixed.sh --force-zlib --json "book"        # Z-Library only
./scripts/zlib_book_search_fixed.sh --force-flibusta --json "книга"   # Flibusta only

# Download EPUB
./scripts/zlib_book_search_fixed.sh -o /tmp/books -f epub --download "book"

# Service mode (API integration)
./scripts/zlib_book_search_fixed.sh --service --json -o /path --download "book"

# Multi-source pipeline (2025-08-07)
python3 -c "
from pipeline.book_pipeline import BookSearchPipeline
import asyncio
pipeline = BookSearchPipeline()
result = asyncio.run(pipeline.search_book('1984 Orwell'))
print(f'Found: {result.found} via {result.source}')
"

# Visual pipeline system (2025-08-07) 
./search/visual_search.sh "hary poter filosofer stone"
./search/fuzzy_search.sh english_fuzzy
./search/quick_search.sh --json --format epub "book title"

# Complete end-to-end with EPUB download
./scripts/zlib_book_search_fixed.sh --service --json -f epub --download "Harry Potter"

# Enhanced dual confidence system (2025-08-08) - renamed for simplicity
./scripts/book_search.sh "1984 George Orwell"                           # Search only
./scripts/book_search.sh --download "1984 George Orwell"                # With download
python3 service_simulation_demo.py                                       # Full simulation
```

### Dual Confidence JSON Schema (2025-08-08)
- **Book Matching Confidence**: How well search matched user's intent
- **EPUB Quality Confidence**: How readable and high-quality the EPUB is  
- **Russian Descriptions**: User-friendly explanations
- **Actual Download URLs**: Real file paths when downloads succeed
- **Main Script**: `scripts/book_search.sh` (renamed for simplicity)
- **Schema File**: `schemas/book_search_response_schema.json`

---
*Auto-updated: 2025-08-08*- [Book Search Cognitive Extraction](memory_cards/mc_book_search_cognitive_extraction_20250812.md) - Mandatory Claude cognitive layer for URL book extraction
