#!/bin/bash
# Quick URL extraction with strict timeout

URL="${1:-}"
if [[ -z "$URL" ]]; then
    echo "Usage: $0 'URL'"
    exit 1
fi

echo "🔗 Extracting from URL (max 5 seconds)..."

# Use curl with timeout instead of WebFetch
timeout 5 curl -s "$URL" | python3 -c "
import sys
import re
from html.parser import HTMLParser

html = sys.stdin.read()

# Quick extraction patterns
title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
author_match = re.search(r'(?:Автор|Author)[^>]*>([^<]+)<', html)

if 'ozon.ru' in '$URL':
    # Ozon specific
    title_match = re.search(r'kurort-([^-]+)', '$URL') or title_match
    
if 'alpinabook.ru' in '$URL':
    # Alpina specific
    title_match = re.search(r'book-([^/]+)', '$URL') or title_match

if title_match:
    print(f'Title extracted from URL')
else:
    print('Could not extract in 5 seconds')
"