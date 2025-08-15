#!/bin/bash

# Quick test script for reliable Russian book extraction
# Tests the improved IUC05 system with fixed URLs

set -euo pipefail

echo "🎯 RELIABLE RUSSIAN BOOK EXTRACTION TEST"
echo "========================================"
echo "📅 $(TZ=Europe/Moscow date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

echo "🔧 Testing single extraction with fixed URL..."
CONSISTENCY_TEST=true timeout 60 bash -c '
    cd tests/IUC
    export SELECTED_BOOKSTORE="https://eksmo.ru/book/k-sebe-nezhno-ITD1083100/"
    export STORE_TYPE="publisher"
    source lib/iuc_patterns.sh
    source IUC05_russian_bookstore_extraction.sh
    
    echo "🤖 Testing Claude extraction..."
    if result=$(extract_with_claude "$SELECTED_BOOKSTORE" "$STORE_TYPE"); then
        echo "✅ Extraction successful!"
        echo "📥 Result: $result"
        
        echo ""
        echo "🔍 Testing validation..."
        if validate_metadata "$result"; then
            echo "✅ Validation successful!"
            echo "📚 Title: $EXTRACTED_TITLE"
            echo "✍️ Author: $EXTRACTED_AUTHOR"
            echo "📊 Confidence: $EXTRACTED_CONFIDENCE"
        else
            echo "❌ Validation failed"
        fi
    else
        echo "❌ Extraction failed"
    fi
' || echo "❌ Test timed out or failed"

echo ""
echo "📊 Checking success rate..."
if [[ -f "tests/IUC/extraction_success_$(date '+%Y-%m-%d').log" ]]; then
    cat "tests/IUC/extraction_success_$(date '+%Y-%m-%d').log"
else
    echo "No log file found"
fi

echo ""
echo "✅ Test completed!"