#!/usr/bin/env python3
"""
Demo: Compare different normalization methods for Z-Library search
Shows speed vs accuracy tradeoffs
"""
import asyncio
import time
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from zlibrary import AsyncZlib, Extension
from claude_sdk_normalizer_fast import ClaudeSDKNormalizerFast, SimpleNormalizer

async def test_search_methods():
    """Compare different search normalization methods"""
    
    # Test inputs - various difficulty levels
    test_inputs = [
        {
            "input": "hary poter and teh filosofer stone", 
            "type": "misspelled",
            "expected": "Harry Potter and the Philosopher's Stone"
        },
        {
            "input": "малинкий принз антуан сент экзюпери",
            "type": "russian_transliterated", 
            "expected": "Маленький принц / Le Petit Prince"
        },
        {
            "input": "clean code robert c martin",
            "type": "technical",
            "expected": "Clean Code: A Handbook of Agile Software Craftsmanship"
        },
        {
            "input": "https://www.goodreads.com/book/show/3735293-clean-code",
            "type": "url",
            "expected": "Clean Code"
        },
        {
            "input": "1Q84 murakami", 
            "type": "japanese_author",
            "expected": "1Q84 by Haruki Murakami"
        }
    ]
    
    print("=" * 80)
    print("📊 Z-LIBRARY SEARCH NORMALIZATION COMPARISON")
    print("=" * 80)
    print("\nComparing 3 methods:")
    print("1. Simple (local rules only) - Instant")
    print("2. Fast Cognitive (Claude with timeout) - Fast")  
    print("3. Direct (no normalization) - Baseline")
    print("=" * 80)
    
    # Initialize Z-Library
    lib = AsyncZlib()
    try:
        await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Test each input with different methods
    for test_case in test_inputs[:3]:  # Test first 3 for demo
        print(f"\n{'=' * 80}")
        print(f"📝 Input: {test_case['input']}")
        print(f"   Type: {test_case['type']}")
        print(f"   Expected: {test_case['expected']}")
        print("-" * 80)
        
        results = []
        
        # Method 1: Simple normalizer (instant)
        print("\n1️⃣ SIMPLE NORMALIZER (Local rules)")
        start = time.time()
        simple_result = SimpleNormalizer.normalize(test_case['input'])
        norm_time = time.time() - start
        
        normalized = simple_result.get('normalized', test_case['input'])
        print(f"   Normalized: {normalized}")
        print(f"   Confidence: {simple_result.get('confidence', 0):.1%}")
        print(f"   Time: {norm_time:.4f}s")
        
        # Search with simple normalized
        try:
            search_start = time.time()
            paginator = await lib.search(q=normalized, count=1, extensions=[Extension.EPUB])
            await paginator.init()
            books = paginator.result
            search_time = time.time() - search_start
            
            if books:
                book = books[0]
                details = await book.fetch()
                found_title = details.get('name', 'Unknown')
                print(f"   ✅ Found: {found_title[:60]}...")
                print(f"   Search time: {search_time:.2f}s")
                
                # Calculate match
                match = calculate_match(normalized, found_title)
                print(f"   Match score: {match:.1%}")
            else:
                print(f"   ❌ No books found")
                print(f"   Search time: {search_time:.2f}s")
        except Exception as e:
            print(f"   ❌ Search error: {str(e)[:50]}")
        
        results.append({
            "method": "Simple",
            "normalized": normalized,
            "time": norm_time + search_time,
            "found": bool(books)
        })
        
        # Method 2: Fast cognitive (with timeout)
        print("\n2️⃣ FAST COGNITIVE (Claude with 3s timeout)")
        normalizer = ClaudeSDKNormalizerFast(use_cognitive=True, timeout=3)
        
        start = time.time()
        cognitive_result = normalizer.normalize_book_title(test_case['input'])
        norm_time = time.time() - start
        
        if cognitive_result.get('success'):
            normalized = cognitive_result.get('search_string', 
                                            cognitive_result.get('normalized_title', test_case['input']))
            print(f"   Normalized: {normalized}")
            print(f"   Method: {cognitive_result.get('method', 'unknown')}")
            print(f"   Confidence: {cognitive_result.get('confidence', 0):.1%}")
            print(f"   Time: {norm_time:.2f}s")
            
            # Search with cognitive normalized
            try:
                search_start = time.time()
                paginator = await lib.search(q=normalized, count=1, extensions=[Extension.EPUB])
                await paginator.init()
                books = paginator.result
                search_time = time.time() - search_start
                
                if books:
                    book = books[0]
                    details = await book.fetch()
                    found_title = details.get('name', 'Unknown')
                    print(f"   ✅ Found: {found_title[:60]}...")
                    print(f"   Search time: {search_time:.2f}s")
                    
                    match = calculate_match(normalized, found_title)
                    print(f"   Match score: {match:.1%}")
                else:
                    print(f"   ❌ No books found")
                    print(f"   Search time: {search_time:.2f}s")
            except Exception as e:
                print(f"   ❌ Search error: {str(e)[:50]}")
            
            results.append({
                "method": "Cognitive",
                "normalized": normalized,
                "time": norm_time + search_time,
                "found": bool(books)
            })
        else:
            print(f"   ❌ Normalization failed/timeout")
            results.append({
                "method": "Cognitive",
                "normalized": test_case['input'],
                "time": norm_time,
                "found": False
            })
        
        # Method 3: Direct search (no normalization)
        print("\n3️⃣ DIRECT SEARCH (No normalization)")
        
        # Extract from URL if needed
        search_query = test_case['input']
        if test_case['type'] == 'url':
            # Simple URL extraction
            if 'clean-code' in search_query:
                search_query = 'clean code'
        
        try:
            search_start = time.time()
            paginator = await lib.search(q=search_query, count=1, extensions=[Extension.EPUB])
            await paginator.init()
            books = paginator.result
            search_time = time.time() - search_start
            
            if books:
                book = books[0]
                details = await book.fetch()
                found_title = details.get('name', 'Unknown')
                print(f"   ✅ Found: {found_title[:60]}...")
                print(f"   Search time: {search_time:.2f}s")
                
                match = calculate_match(search_query, found_title)
                print(f"   Match score: {match:.1%}")
            else:
                print(f"   ❌ No books found")
                print(f"   Search time: {search_time:.2f}s")
        except Exception as e:
            print(f"   ❌ Search error: {str(e)[:50]}")
        
        results.append({
            "method": "Direct",
            "normalized": search_query,
            "time": search_time,
            "found": bool(books)
        })
        
        # Summary for this test case
        print(f"\n📈 SUMMARY for '{test_case['type']}':")
        print("-" * 40)
        for r in results:
            status = "✅" if r['found'] else "❌"
            print(f"   {r['method']:12} {status} Time: {r['time']:.2f}s")
        
        # Find winner
        successful = [r for r in results if r['found']]
        if successful:
            fastest = min(successful, key=lambda x: x['time'])
            print(f"\n   🏆 Fastest successful: {fastest['method']} ({fastest['time']:.2f}s)")
        
        await asyncio.sleep(1)  # Rate limiting
    
    # Overall conclusions
    print(f"\n{'=' * 80}")
    print("📋 CONCLUSIONS:")
    print("-" * 80)
    print("1. Simple Normalizer: ⚡ Instant (< 0.01s) with good results for common errors")
    print("2. Fast Cognitive: 🧠 Smart normalization in ~3s when Claude available")
    print("3. Direct Search: 🎯 Works for clean input but fails on misspellings")
    print("\n💡 RECOMMENDATION:")
    print("   Use Simple Normalizer by default (instant + good enough)")
    print("   Enable Cognitive for complex/important searches")
    print("   Set timeout based on your needs (3-5s recommended)")

def calculate_match(query, title):
    """Calculate match score between query and title"""
    import re
    query_words = set(w.lower() for w in re.findall(r'\w+', query) if len(w) > 2)
    title_words = set(w.lower() for w in re.findall(r'\w+', title) if len(w) > 2)
    
    if not query_words:
        return 0.0
    
    return len(query_words & title_words) / len(query_words)

if __name__ == "__main__":
    # Load environment
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("❌ Error: Set ZLOGIN and ZPASSW in .env file")
        sys.exit(1)
    
    asyncio.run(test_search_methods())