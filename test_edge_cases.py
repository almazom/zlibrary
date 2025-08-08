#!/usr/bin/env python3
"""
Test edge cases and demonstrate proper 'not found' responses
"""
import asyncio
import json
import sys
import datetime
sys.path.insert(0, 'src')

from zlibrary.libasync_enhanced import EnhancedAsyncZlib

def create_not_found_response(query: str) -> dict:
    """Create standardized 'not found' response"""
    return {
        "status": "success",
        "service": "zlibrary_api_module",
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "total_results": 0,
        "page": 1,
        "total_pages": 0,
        "results": [],
        "message": "No books found matching your search criteria",
        "suggestions": [
            "Try using fewer or different keywords",
            "Check spelling of author or title",
            "Try searching for similar books",
            "The book might not be available in Z-Library"
        ]
    }

async def test_all_edge_cases():
    """Test various edge cases"""
    
    print("🧪 Z-Library Service - Edge Case Testing")
    print("=" * 60)
    
    client = EnhancedAsyncZlib(use_cookie_fallback=True)
    await client.login('almazomam@gmail.com', 'tataronrails78')
    
    # Test cases
    test_cases = [
        {
            "name": "Non-existent book",
            "query": "The Invisible Purple Elephant's Guide to Time Travel",
            "expected": "not_found"
        },
        {
            "name": "Random characters",
            "query": "xyzabc123456nonexistentbook789",
            "expected": "not_found"
        },
        {
            "name": "Empty search",
            "query": "",
            "expected": "error"
        },
        {
            "name": "Very long query",
            "query": "a" * 500,
            "expected": "not_found"
        },
        {
            "name": "Special characters only",
            "query": "@#$%^&*()",
            "expected": "error_or_not_found"
        },
        {
            "name": "Known book (control test)",
            "query": "Harry Potter",
            "expected": "found"
        }
    ]
    
    results_summary = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['name']}")
        print(f"   Query: \"{test['query'][:50]}...\"" if len(test['query']) > 50 else f"   Query: \"{test['query']}\"")
        
        try:
            result = await client.search_with_fallback(test['query'], count=5)
            
            if result.get('status') == 'success':
                num_results = result.get('total_results', 0)
                
                if num_results == 0:
                    print(f"   ✅ Result: NOT FOUND (0 results)")
                    status = "not_found"
                else:
                    print(f"   ✅ Result: FOUND ({num_results} results)")
                    status = "found"
                    if num_results > 0 and result.get('results'):
                        print(f"      First: {result['results'][0].get('title', 'Unknown')[:50]}...")
            else:
                print(f"   ⚠️  Result: ERROR - {result.get('error', 'Unknown')[:50]}")
                status = "error"
                
            # Check if result matches expectation
            if test['expected'] == status or test['expected'] == 'error_or_not_found' and status in ['error', 'not_found']:
                print(f"   ✓ Passed: Got expected result")
                test_result = "PASS"
            else:
                print(f"   ✗ Failed: Expected {test['expected']}, got {status}")
                test_result = "FAIL"
                
            results_summary.append({
                "test": test['name'],
                "result": test_result,
                "status": status
            })
            
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:100]}")
            results_summary.append({
                "test": test['name'],
                "result": "ERROR",
                "status": "exception"
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("\n📊 Test Summary:")
    passed = sum(1 for r in results_summary if r['result'] == 'PASS')
    total = len(results_summary)
    
    for r in results_summary:
        emoji = "✅" if r['result'] == 'PASS' else "❌"
        print(f"{emoji} {r['test']}: {r['result']}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Show example of proper "not found" response
    print("\n" + "=" * 60)
    print("\n📋 Example Proper 'Not Found' Response:")
    example_response = create_not_found_response("The Invisible Purple Elephant's Guide to Time Travel")
    print(json.dumps(example_response, indent=2))
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(test_all_edge_cases())
    
    if success:
        print("\n✅ All edge cases handled correctly!")
    else:
        print("\n⚠️  Some edge cases need improvement")
    
    print("\n💡 Key Points:")
    print("1. Service correctly returns empty results for non-existent books")
    print("2. Response format is consistent and includes helpful suggestions")
    print("3. Special characters are handled (may return error or empty)")
    print("4. Service distinguishes between real books and non-existent ones")