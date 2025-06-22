#!/usr/bin/env python3
"""
Advanced Features Examples for Z-Library API

This script demonstrates advanced usage patterns including:
- Proxy configurations
- Tor/onion access
- Batch operations
- Custom search strategies
- Performance optimization
"""

import asyncio
import os
import time
import logging
from typing import List, Dict, Any
import zlibrary
from zlibrary import Language, Extension, OrderOptions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def proxy_configuration_example():
    """Demonstrate various proxy configurations."""
    print("=== Proxy Configuration Examples ===")
    
    # Example 1: Single HTTP proxy
    print("1. HTTP Proxy Configuration")
    lib_http = zlibrary.AsyncZlib(
        proxy_list=['http://proxy.example.com:8080']
    )
    
    # Example 2: SOCKS5 proxy (common for Tor)
    print("2. SOCKS5 Proxy Configuration")
    lib_socks = zlibrary.AsyncZlib(
        proxy_list=['socks5://127.0.0.1:9050']
    )
    
    # Example 3: Proxy chain
    print("3. Proxy Chain Configuration")
    lib_chain = zlibrary.AsyncZlib(
        proxy_list=[
            'http://first-proxy.com:8080',
            'socks5://second-proxy.com:1080',
            'socks4://third-proxy.com:9050'
        ]
    )
    
    # Example 4: Authenticated proxy
    print("4. Authenticated Proxy Configuration")
    lib_auth = zlibrary.AsyncZlib(
        proxy_list=['http://username:password@proxy.example.com:8080']
    )
    
    print("✓ Proxy configurations created (not tested - would need real proxies)")


async def tor_onion_example():
    """Access Z-Library through Tor onion domains."""
    print("=== Tor/Onion Access Example ===")
    
    # Note: Requires Tor to be running on default port 9050
    lib = zlibrary.AsyncZlib(
        onion=True,
        proxy_list=['socks5://127.0.0.1:9050']
    )
    
    email = os.getenv('ZLOGIN')
    password = os.getenv('ZPASSW')
    
    if not email or not password:
        print("❌ Credentials required for this example")
        return
    
    try:
        print("Connecting through Tor...")
        await lib.login(email, password)
        print("✓ Connected via Tor onion domain")
        
        # Test search through Tor
        paginator = await lib.search(q="cryptography", count=3)
        books = await paginator.next()
        
        print(f"Found {len(books)} books through Tor:")
        for book in books:
            print(f"  • {book.name}")
            
    except Exception as e:
        print(f"❌ Tor connection failed: {e}")
        print("   Make sure Tor is running on 127.0.0.1:9050")


async def batch_search_example():
    """Perform multiple searches efficiently."""
    print("=== Batch Search Example ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Define multiple search queries
    queries = [
        "machine learning",
        "data science", 
        "artificial intelligence",
        "deep learning",
        "neural networks"
    ]
    
    print(f"Performing {len(queries)} searches concurrently...")
    start_time = time.time()
    
    # Create search tasks
    search_tasks = []
    for query in queries:
        task = lib.search(q=query, count=5)
        search_tasks.append(task)
    
    # Execute all searches concurrently
    paginators = await asyncio.gather(*search_tasks)
    
    # Get results from all searches
    result_tasks = []
    for paginator in paginators:
        task = paginator.next()
        result_tasks.append(task)
    
    all_results = await asyncio.gather(*result_tasks)
    
    end_time = time.time()
    
    # Display results
    for i, (query, books) in enumerate(zip(queries, all_results)):
        print(f"\n{i+1}. '{query}': {len(books)} books found")
        if books:
            print(f"   Top result: {books[0].name}")
    
    print(f"\n⏱️  Completed {len(queries)} searches in {end_time - start_time:.2f} seconds")


async def booklist_management_example():
    """Demonstrate booklist functionality."""
    print("=== Booklist Management Example ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Search public booklists
    print("1. Searching public booklists for 'programming'")
    try:
        booklist_paginator = await lib.profile.search_public_booklists(
            q="programming",
            count=5,
            order=OrderOptions.POPULAR
        )
        
        booklists = await booklist_paginator.next()
        
        print(f"Found {len(booklists)} public booklists:")
        for i, booklist in enumerate(booklists, 1):
            print(f"  {i}. Booklist found")
            
            # Get booklist details
            try:
                booklist_data = await booklist.fetch()
                print(f"     Name: {booklist_data.get('name', 'Unknown')}")
            except Exception as e:
                print(f"     Could not fetch details: {e}")
        
        # Get books from first booklist
        if booklists:
            print(f"\n2. Getting books from first booklist...")
            try:
                books = await booklists[0].next()
                print(f"   Found {len(books)} books in the booklist")
                for book in books[:3]:  # Show first 3
                    print(f"   • {book.name}")
            except Exception as e:
                print(f"   Could not fetch books: {e}")
                
    except Exception as e:
        print(f"❌ Booklist search failed: {e}")
    
    # Search private booklists
    print("\n3. Searching private booklists")
    try:
        private_lists = await lib.profile.search_private_booklists(q="")
        private_results = private_lists.result if hasattr(private_lists, 'result') else []
        print(f"Found {len(private_results)} private booklists")
    except Exception as e:
        print(f"Could not access private booklists: {e}")


async def advanced_search_strategies():
    """Demonstrate sophisticated search strategies."""
    print("=== Advanced Search Strategies ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Strategy 1: Year-by-year search for trending topics
    print("1. Year-by-year search for 'blockchain'")
    years = [2020, 2021, 2022, 2023, 2024]
    
    for year in years:
        try:
            paginator = await lib.search(
                q="blockchain",
                from_year=year,
                to_year=year,
                lang=[Language.ENGLISH],
                extensions=[Extension.PDF],
                count=3
            )
            books = await paginator.next()
            print(f"   {year}: {len(books)} books found")
        except Exception as e:
            print(f"   {year}: Error - {e}")
    
    # Strategy 2: Multi-language search
    print("\n2. Multi-language search for 'mathematics'")
    languages = [Language.ENGLISH, Language.SPANISH, Language.FRENCH, Language.GERMAN]
    
    for lang in languages:
        try:
            paginator = await lib.search(
                q="mathematics",
                lang=[lang],
                count=2
            )
            books = await paginator.next()
            print(f"   {lang.value}: {len(books)} books found")
        except Exception as e:
            print(f"   {lang.value}: Error - {e}")
    
    # Strategy 3: Format comparison
    print("\n3. Format availability for 'python programming'")
    formats = [Extension.PDF, Extension.EPUB, Extension.MOBI]
    
    for fmt in formats:
        try:
            paginator = await lib.search(
                q="python programming",
                extensions=[fmt],
                count=5
            )
            books = await paginator.next()
            print(f"   {fmt.value}: {len(books)} books available")
        except Exception as e:
            print(f"   {fmt.value}: Error - {e}")


async def performance_optimization_example():
    """Demonstrate performance optimization techniques."""
    print("=== Performance Optimization Example ===")
    
    # Technique 1: Reuse client instance
    print("1. Client reuse vs new instances")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Reused client - faster
    start_time = time.time()
    for i in range(3):
        paginator = await lib.search(q=f"test query {i}", count=2)
        await paginator.next()
    reused_time = time.time() - start_time
    
    print(f"   Reused client: {reused_time:.2f} seconds for 3 searches")
    
    # Technique 2: Concurrent vs sequential searches
    print("\n2. Concurrent vs sequential execution")
    
    queries = ["python", "java", "javascript"]
    
    # Sequential
    start_time = time.time()
    for query in queries:
        paginator = await lib.search(q=query, count=2)
        await paginator.next()
    sequential_time = time.time() - start_time
    
    # Concurrent
    start_time = time.time()
    tasks = [lib.search(q=query, count=2) for query in queries]
    paginators = await asyncio.gather(*tasks)
    
    result_tasks = [p.next() for p in paginators]
    await asyncio.gather(*result_tasks)
    concurrent_time = time.time() - start_time
    
    print(f"   Sequential: {sequential_time:.2f} seconds")
    print(f"   Concurrent: {concurrent_time:.2f} seconds")
    print(f"   Speedup: {sequential_time/concurrent_time:.1f}x")
    
    # Technique 3: Pagination caching
    print("\n3. Pagination caching demonstration")
    
    paginator = await lib.search(q="data structures", count=5)
    
    # First access - fetches from server
    start_time = time.time()
    page1_first = await paginator.next()
    first_access_time = time.time() - start_time
    
    # Move to next page
    page2 = await paginator.next()
    
    # Return to first page - uses cache
    start_time = time.time()
    page1_cached = await paginator.prev()
    cached_access_time = time.time() - start_time
    
    print(f"   First access: {first_access_time:.3f} seconds")
    print(f"   Cached access: {cached_access_time:.3f} seconds")
    print(f"   Cache speedup: {first_access_time/cached_access_time:.1f}x")


async def error_recovery_example():
    """Demonstrate robust error handling and recovery."""
    print("=== Error Recovery Example ===")
    
    lib = zlibrary.AsyncZlib()
    
    # Retry mechanism for login
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
            print(f"✓ Login successful on attempt {attempt + 1}")
            break
        except Exception as e:
            print(f"❌ Login attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("   Retrying in 2 seconds...")
                await asyncio.sleep(2)
            else:
                print("   Max retries reached")
                return
    
    # Graceful degradation for searches
    search_queries = ["valid query", "", "another valid query"]
    successful_searches = 0
    
    for i, query in enumerate(search_queries, 1):
        try:
            if not query.strip():
                raise zlibrary.exception.EmptyQueryError("Empty query")
            
            paginator = await lib.search(q=query, count=3)
            books = await paginator.next()
            print(f"✓ Search {i}: Found {len(books)} books")
            successful_searches += 1
            
        except zlibrary.exception.EmptyQueryError:
            print(f"⚠️  Search {i}: Skipped empty query")
        except Exception as e:
            print(f"❌ Search {i}: Failed - {e}")
    
    print(f"\nCompleted {successful_searches}/{len(search_queries)} searches successfully")


async def custom_search_filters():
    """Demonstrate creating custom search filter combinations."""
    print("=== Custom Search Filters Example ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Filter 1: Recent technical books
    print("1. Recent technical books (2023-2024, English, PDF)")
    try:
        paginator = await lib.search(
            q="software engineering OR programming OR algorithms",
            from_year=2023,
            to_year=2024,
            lang=[Language.ENGLISH],
            extensions=[Extension.PDF],
            count=5
        )
        books = await paginator.next()
        print(f"   Found {len(books)} recent technical books")
        for book in books[:2]:
            print(f"   • {book.name} ({book.year})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Filter 2: Classic literature in multiple formats
    print("\n2. Classic literature (before 1950, multiple formats)")
    try:
        paginator = await lib.search(
            q="shakespeare OR dickens OR austen",
            to_year=1950,
            lang=[Language.ENGLISH],
            extensions=[Extension.PDF, Extension.EPUB, Extension.TXT],
            count=5
        )
        books = await paginator.next()
        print(f"   Found {len(books)} classic literature books")
        for book in books[:2]:
            print(f"   • {book.name} ({book.year}) - {book.extension}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Filter 3: Scientific papers and journals
    print("\n3. Scientific content (PDF only, recent)")
    try:
        paginator = await lib.search(
            q="journal OR research OR paper OR study",
            from_year=2020,
            lang=[Language.ENGLISH],
            extensions=[Extension.PDF],
            count=5
        )
        books = await paginator.next()
        print(f"   Found {len(books)} scientific publications")
        for book in books[:2]:
            print(f"   • {book.name}")
    except Exception as e:
        print(f"   Error: {e}")


async def main():
    """Run all advanced examples."""
    print("Z-Library Advanced Features Examples")
    print("=" * 50)
    
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("⚠️  Set ZLOGIN and ZPASSW environment variables")
        print("   Some examples will be skipped")
        print()
    
    examples = [
        proxy_configuration_example,
        tor_onion_example,
        batch_search_example,
        booklist_management_example,
        advanced_search_strategies,
        performance_optimization_example,
        error_recovery_example,
        custom_search_filters
    ]
    
    for example in examples:
        try:
            await example()
            print()
        except Exception as e:
            print(f"❌ Example failed: {e}")
            print()


if __name__ == "__main__":
    asyncio.run(main())