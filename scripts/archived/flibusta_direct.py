#!/usr/bin/env python3
"""
Direct Flibusta search when Z-Library accounts are exhausted
"""
import asyncio
import sys
import os
sys.path.insert(0, '/home/almaz/microservices/zlibrary_api_module/src')
from book_sources.flibusta_source import FlibustaSource

async def search_flibusta(query: str):
    """Direct search in Flibusta"""
    print(f"🔍 Searching Flibusta for: {query}")
    print("=" * 50)
    
    flibusta = FlibustaSource()
    result = await flibusta.search(query)
    
    if result.found:
        print(f"✅ Found: {result.title}")
        print(f"👤 Author: {result.author}")
        print(f"📄 File: {result.file_path}")
        print(f"🎯 Confidence: {result.confidence:.0%}")
    else:
        print(f"❌ Not found in Flibusta")
        if result.error:
            print(f"   Error: {result.error}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 flibusta_direct.py 'book query'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    asyncio.run(search_flibusta(query))