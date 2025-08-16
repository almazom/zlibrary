#!/usr/bin/env python3
"""
Simple, DRY book extraction using Claude's cognitive layer
KISS principle: Just ask Claude to extract the book info
"""

import json
import sys

def extract_book_from_url(url):
    """
    In production, this would use Claude SDK:
    
    from anthropic import Anthropic
    client = Anthropic()
    
    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{
            "role": "user",
            "content": f"Extract book info from {url}. Return JSON with title and author."
        }]
    )
    
    For now, we return a note about using Claude properly.
    """
    
    return {
        "note": "Use Claude SDK WebFetch or API for real extraction",
        "url": url,
        "method": "claude.messages.create() or WebFetch()",
        "example_usage": "WebFetch(url, 'Extract book title and author')"
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "URL required"}))
        sys.exit(1)
    
    url = sys.argv[1]
    
    # In Claude Code, we can use WebFetch directly:
    # result = WebFetch(url, "Extract book title, author as JSON")
    
    result = extract_book_from_url(url)
    print(json.dumps(result, ensure_ascii=False))