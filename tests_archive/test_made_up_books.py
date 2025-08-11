#!/usr/bin/env python3
"""
Comprehensive test with made-up book titles to test 'not found' responses
"""
import asyncio
import json
import time
import sys
sys.path.insert(0, 'src')

from zlibrary.libasync_enhanced import EnhancedAsyncZlib

async def test_made_up_books():
    print("🔬 Z-Library Service - Made-Up Books Edge Case Testing")
    print("=" * 70)
    print("Testing with completely fictional, non-existent books\n")
    
    # Initialize client
    client = EnhancedAsyncZlib(use_cookie_fallback=True)
    await client.login('almazomam@gmail.com', 'tataronrails78')
    
    # Made-up book titles - these definitely don't exist
    made_up_books = [
        # Absurd titles
        {
            "title": "The Quantum Mechanics of Unicorn Dreams",
            "author": "Dr. Sparkles McGillicuddy",
            "query": "The Quantum Mechanics of Unicorn Dreams by Dr. Sparkles McGillicuddy"
        },
        # Technical nonsense
        {
            "title": "Advanced PHP Programming for Toasters",
            "author": "Kitchen Appliance Institute",
            "query": "Advanced PHP Programming for Toasters"
        },
        # Impossible combinations
        {
            "title": "Shakespeare's Guide to JavaScript Frameworks",
            "author": "William Shakespeare",
            "query": "Shakespeare's Guide to JavaScript Frameworks"
        },
        # Random word salad
        {
            "title": "Purple Monkey Dishwasher Cookbook",
            "author": "Random Word Generator",
            "query": "Purple Monkey Dishwasher Cookbook"
        },
        # Future books that can't exist yet
        {
            "title": "The Complete History of the Year 2050",
            "author": "Time Traveler",
            "query": "The Complete History of the Year 2050"
        },
        # Contradictory titles
        {
            "title": "The Silent Symphony of Loud Quietness",
            "author": "Paradox Publishing",
            "query": "The Silent Symphony of Loud Quietness"
        },
        # Extremely specific nonsense
        {
            "title": "437 Ways to Train Your Pet Rock to Code Python",
            "author": "Geological Software Society",
            "query": "437 Ways to Train Your Pet Rock to Code Python"
        },
        # Mix of numbers and gibberish
        {
            "title": "XYZ123ABC: The Novel",
            "author": "Algorithm Author 9000",
            "query": "XYZ123ABC The Novel by Algorithm Author 9000"
        },
        # Impossible academic titles
        {
            "title": "PhD Thesis on the Psychology of Imaginary Numbers",
            "author": "Dr. i-squared",
            "query": "PhD Thesis on the Psychology of Imaginary Numbers"
        },
        # Pop culture mashup that doesn't exist
        {
            "title": "Harry Potter and the Linux Kernel",
            "author": "J.K. Torvalds",
            "query": "Harry Potter and the Linux Kernel"
        }
    ]
    
    print(f"Testing {len(made_up_books)} made-up book titles...\n")
    
    results = []
    response_times = []
    
    for i, book_info in enumerate(made_up_books, 1):
        print(f"{i}. Testing: \"{book_info['title']}\"")
        print(f"   Author: {book_info['author']}")
        
        start_time = time.time()
        
        try:
            # Search for the made-up book
            result = await client.search_with_fallback(book_info['query'], count=5)
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            # Analyze the response
            if result.get('status') == 'success':
                num_results = result.get('total_results', 0)
                
                if num_results == 0:
                    print(f"   ✅ Correctly returned: NOT FOUND")
                    print(f"   Response time: {response_time:.2f}s")
                    status = 'correct_not_found'
                else:
                    print(f"   ⚠️  Unexpected: Found {num_results} results!")
                    if result.get('results'):
                        print(f"      Found: {result['results'][0].get('title', 'Unknown')[:50]}...")
                    status = 'false_positive'
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')[:50]}")
                status = 'error'
            
            results.append({
                'book': book_info['title'],
                'status': status,
                'response_time': response_time,
                'num_results': result.get('total_results', 0) if result.get('status') == 'success' else None
            })
            
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:50]}")
            results.append({
                'book': book_info['title'],
                'status': 'exception',
                'response_time': None,
                'num_results': None
            })
        
        print()
    
    # Print detailed summary
    print("=" * 70)
    print("\n📊 DETAILED TEST RESULTS:\n")
    
    correct_not_found = sum(1 for r in results if r['status'] == 'correct_not_found')
    false_positives = sum(1 for r in results if r['status'] == 'false_positive')
    errors = sum(1 for r in results if r['status'] in ['error', 'exception'])
    
    print(f"✅ Correct 'Not Found': {correct_not_found}/{len(results)}")
    print(f"⚠️  False Positives: {false_positives}/{len(results)}")
    print(f"❌ Errors: {errors}/{len(results)}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"\n⏱️  Average Response Time: {avg_time:.2f}s")
        print(f"   Fastest: {min(response_times):.2f}s")
        print(f"   Slowest: {max(response_times):.2f}s")
    
    # Show any false positives
    if false_positives > 0:
        print("\n⚠️  FALSE POSITIVES (books that shouldn't exist but got results):")
        for r in results:
            if r['status'] == 'false_positive':
                print(f"   - {r['book']}: {r['num_results']} results")
    
    # Show example proper response
    print("\n" + "=" * 70)
    print("\n📋 EXAMPLE PROPER 'NOT FOUND' RESPONSE:")
    
    example_response = {
        "status": "success",
        "service": "zlibrary_api_module",
        "query": made_up_books[0]['query'],
        "total_results": 0,
        "page": 1,
        "total_pages": 0,
        "results": [],
        "message": "No books found matching your search criteria",
        "suggestions": [
            "The book might not exist in Z-Library",
            "Try searching with different keywords",
            "Check if the title is spelled correctly",
            "Try searching for similar books by the same author"
        ],
        "searched_for": {
            "title": made_up_books[0]['title'],
            "author": made_up_books[0]['author'],
            "type": "made_up_book_test"
        }
    }
    
    print(json.dumps(example_response, indent=2))
    
    # Final verdict
    print("\n" + "=" * 70)
    print("\n🏁 FINAL VERDICT:")
    
    if correct_not_found == len(results):
        print("✅ PERFECT! All made-up books correctly returned 'not found'")
    elif correct_not_found >= len(results) * 0.8:
        print("✅ GOOD! Most made-up books correctly identified as non-existent")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Too many false positives or errors")
    
    print(f"\nSuccess Rate: {(correct_not_found/len(results)*100):.1f}%")
    
    return results

async def test_with_bash_script():
    """Also test with bash script"""
    print("\n" + "=" * 70)
    print("\n🐚 Testing with Bash Script:\n")
    
    import subprocess
    
    test_queries = [
        "Quantum Unicorn Dreams",
        "Purple Monkey Dishwasher",
        "XYZ123ABC789"
    ]
    
    for query in test_queries:
        print(f"Query: \"{query}\"")
        
        result = subprocess.run([
            './scripts/zlib_book_search_fixed.sh',
            '--json',
            query
        ], capture_output=True, text=True, timeout=10)
        
        try:
            response = json.loads(result.stdout)
            if response.get('status') == 'error' and 'No books found' in response.get('message', ''):
                print(f"  ✅ Correctly returned 'No books found'")
            else:
                print(f"  Response: {json.dumps(response, indent=2)}")
        except:
            print(f"  Output: {result.stdout[:100]}")
            print(f"  Error: {result.stderr[:100] if result.stderr else 'None'}")
        print()

if __name__ == "__main__":
    # Run the main test
    results = asyncio.run(test_made_up_books())
    
    # Also test with bash script
    asyncio.run(test_with_bash_script())
    
    print("\n✨ Edge case testing complete!")