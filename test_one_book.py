#!/usr/bin/env python3
"""
Simple one-book normalization test
"""
import asyncio
import sys
sys.path.insert(0, '.')
from book_normalization_system import UnifiedBookNormalizer

async def test_one_book(book_title):
    normalizer = UnifiedBookNormalizer()
    
    print(f"\n📚 Testing: '{book_title}'")
    print("-" * 50)
    
    result = await normalizer.normalize_book_query(book_title)
    
    normalized = result['final_result']['result']
    confidence = result['final_result']['confidence']
    method = result['final_result']['method']
    
    print(f"✅ Result: '{normalized}'")
    print(f"Confidence: {confidence}")
    print(f"Method: {method}")
    
    if normalized != book_title:
        print(f"\n🔄 Changed from: '{book_title}'")
        print(f"           to: '{normalized}'")
    else:
        print("\n📌 No change needed")

# Test with a misspelled book
asyncio.run(test_one_book("hary poter"))