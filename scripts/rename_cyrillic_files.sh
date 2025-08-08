#!/bin/bash

# =============================================================================
# Batch Rename Cyrillic Files to Linux-Safe Names
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default directory
TARGET_DIR="${1:-$PROJECT_ROOT/downloads}"

echo -e "${BLUE}📝 Smart Rename Utility${NC}"
echo -e "${BLUE}Target: $TARGET_DIR${NC}"
echo "================================"

python3 -c "
import sys
import os
from pathlib import Path

sys.path.insert(0, '$PROJECT_ROOT/src')
from pipeline.epub_diagnostics import EPUBDiagnostics

diagnostics = EPUBDiagnostics(verbose=True)

target_dir = Path('$TARGET_DIR')
if not target_dir.exists():
    print('❌ Directory not found')
    sys.exit(1)

renamed_count = 0
checked_count = 0

for file in target_dir.glob('*.epub'):
    checked_count += 1
    original_name = file.name
    
    # Check if has Cyrillic
    if any(ord(c) > 127 for c in original_name):
        print(f'\\n📂 File: {original_name}')
        
        # Run diagnostics first
        diag = diagnostics.validate_epub(str(file))
        if diag['valid']:
            print('   ✅ Valid EPUB')
        else:
            print(f'   ⚠️  {diag.get(\"error\", \"Invalid EPUB\")}')
        
        # Rename
        new_path = diagnostics.rename_if_needed(str(file), force=False)
        if new_path:
            renamed_count += 1
            print(f'   📝 → {Path(new_path).name}')

print(f'\\n✅ Complete: {renamed_count}/{checked_count} files renamed')
"

echo -e "\n${GREEN}✅ Renaming complete!${NC}"