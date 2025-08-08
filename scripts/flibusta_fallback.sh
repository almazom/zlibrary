#!/bin/bash
# Flibusta Fallback Search - Use when Z-Library accounts exhausted

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

QUERY="${1:-}"
if [[ -z "$QUERY" ]]; then
    echo "Usage: $0 'book query'"
    exit 1
fi

echo "🔍 Direct Flibusta Search (No authentication needed)"
echo "=================================================="

python3 -c "
import asyncio
import sys
import os
sys.path.insert(0, '$PROJECT_ROOT/src')

from book_sources.flibusta_source import FlibustaSource
from pipeline.epub_diagnostics import EPUBDiagnostics

async def main():
    query = '$QUERY'
    print(f'Query: {query}')
    
    # Direct Flibusta search
    flibusta = FlibustaSource()
    result = await flibusta.search(query)
    
    if result.found:
        print(f'✅ Found: {result.title}')
        print(f'👤 Author: {result.author}')
        print(f'📄 File: {result.file_path}')
        print(f'🎯 Confidence: {result.confidence:.0%}')
        
        # Run diagnostics
        if result.file_path and os.path.exists(result.file_path):
            diagnostics = EPUBDiagnostics()
            diag = diagnostics.validate_epub(result.file_path)
            if diag['valid']:
                print(f'✅ Valid EPUB - Quality: {diag[\"quality_score\"]:.0%}')
            else:
                print(f'⚠️ Invalid EPUB: {diag.get(\"error\", \"Unknown\")}')
    else:
        print('❌ Not found in Flibusta')
        print('   Note: Flibusta specializes in Russian literature')

asyncio.run(main())
"