#!/usr/bin/env python3
"""
Simple URL extractor that simulates Claude extraction using web scraping
For testing purposes when Claude CLI is not available
"""

import json
import sys
import re
from urllib.parse import urlparse

def extract_from_goodreads_url(url):
    """Extract book ID from Goodreads URL"""
    # Pattern: https://www.goodreads.com/book/show/6483624-book-title
    match = re.search(r'/book/show/(\d+)(?:-([^/?]+))?', url)
    if match:
        book_id = match.group(1)
        slug = match.group(2) if match.group(2) else ""
        
        # If we have a slug, use it as title
        if slug:
            title = slug.replace('-', ' ')
        else:
            # For now, just return a generic search
            # In production, this would call the actual Claude API or web fetch
            title = f"goodreads book {book_id}"
        
        return {
            "title": title,
            "author": "",
            "source": "goodreads",
            "book_id": book_id
        }
    return {}

def extract_from_amazon_url(url):
    """Extract ASIN from Amazon URL"""
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        asin = match.group(1)
        return {
            "title": f"book_{asin}",
            "author": "",
            "needs_fetch": True,
            "source": "amazon",
            "asin": asin
        }
    return {}

def extract_from_podpisnie_url(url):
    """Extract book slug from Podpisnie URL"""
    match = re.search(r'/books/([^/]+)', url)
    if match:
        slug = match.group(1)
        # Convert slug to search query
        title = slug.replace('-', ' ')
        return {
            "title": title,
            "author": "",
            "source": "podpisnie",
            "slug": slug
        }
    return {}

def extract_from_any_url(url):
    """Generic extraction for any URL - returns a basic query"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    # Try to extract meaningful parts from the URL path
    # Remove common prefixes and extensions
    path = path.replace('/books/', ' ').replace('/book/', ' ')
    path = path.replace('.html', '').replace('.htm', '').replace('.php', '')
    path = path.replace('-', ' ').replace('_', ' ').replace('/', ' ')
    
    # Get last meaningful part (usually the book identifier)
    parts = [p for p in path.split() if len(p) > 2]
    
    if parts:
        # Use the most meaningful parts as search query
        query = ' '.join(parts[-5:])  # Last 5 parts
        return {
            "title": query,
            "author": "",
            "source": parsed.netloc,
            "needs_manual_extraction": True
        }
    
    return {
        "title": f"book from {parsed.netloc}",
        "author": "",
        "source": parsed.netloc
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "no_url"}))
        sys.exit(1)
    
    url = sys.argv[1]
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    result = {}
    
    if 'goodreads' in domain:
        result = extract_from_goodreads_url(url)
    elif 'amazon' in domain:
        result = extract_from_amazon_url(url)
    elif 'podpisnie' in domain:
        result = extract_from_podpisnie_url(url)
    else:
        # Handle ANY URL with generic extraction
        result = extract_from_any_url(url)
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()