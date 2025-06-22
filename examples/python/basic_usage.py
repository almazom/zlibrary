#!/usr/bin/env python3
"""
Basic Usage Examples for Z-Library API

This script demonstrates the fundamental operations of the Z-Library Python API.
"""

import asyncio
import os
import logging
import zlibrary
from zlibrary import Language, Extension

# Enable logging to see what's happening
logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
logging.getLogger("zlibrary").setLevel(logging.INFO)


async def basic_search_example():
    """Basic search functionality demonstration."""
    print("=== Basic Search Example ===")
    
    # Initialize the client
    lib = zlibrary.AsyncZlib()
    
    # Login (use environment variables for credentials)
    email = os.getenv('ZLOGIN', 'your-email@example.com')
    password = os.getenv('ZPASSW', 'your-password')
    
    try:
        await lib.login(email, password)
        print("✓ Login successful")
        
        # Simple search
        print("\n1. Simple search for 'python programming'")
        paginator = await lib.search(q="python programming", count=5)
        
        # Get first set of results
        books = await paginator.next()
        print(f"Found {len(books)} books on page {paginator.page}")
        
        # Display results
        for i, book in enumerate(books, 1):
            print(f"{i}. {book.name}")
            print(f"   Authors: {[a['author'] for a in book.authors]}")
            print(f"   Year: {book.year}, Format: {book.extension}")
            print(f"   Size: {book.size}")
            print()
            
    except zlibrary.exception.LoginFailed:
        print("❌ Login failed. Check your credentials.")
    except Exception as e:
        print(f"❌ Error: {e}")


async def advanced_search_example():
    """Advanced search with filters."""
    print("=== Advanced Search Example ===")
    
    lib = zlibrary.AsyncZlib()
    
    email = os.getenv('ZLOGIN')
    password = os.getenv('ZPASSW')
    
    if not email or not password:
        print("❌ Please set ZLOGIN and ZPASSW environment variables")
        return
    
    await lib.login(email, password)
    
    # Advanced search with filters
    print("Searching for 'machine learning' books (PDF only, English, 2020-2024)")
    
    paginator = await lib.search(
        q="machine learning",
        count=10,
        from_year=2020,
        to_year=2024,
        lang=[Language.ENGLISH],
        extensions=[Extension.PDF]
    )
    
    books = await paginator.next()
    
    print(f"Found {len(books)} filtered results")
    for book in books[:3]:  # Show first 3
        print(f"• {book.name} ({book.year})")
        print(f"  Publisher: {book.publisher}")
        print()


async def pagination_example():
    """Demonstrate pagination navigation."""
    print("=== Pagination Example ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Search with pagination
    paginator = await lib.search(q="data science", count=5)
    
    # Get first page
    print("Page 1:")
    page1 = await paginator.next()
    for book in page1:
        print(f"  • {book.name}")
    
    # Get second page
    print("\nPage 2:")
    page2 = await paginator.next()
    for book in page2:
        print(f"  • {book.name}")
    
    # Go back to first page
    print("\nBack to Page 1:")
    back_to_page1 = await paginator.prev()
    for book in back_to_page1:
        print(f"  • {book.name}")
    
    print(f"\nTotal results available: {paginator.total}")
    print(f"Current page: {paginator.page}")


async def book_details_example():
    """Get detailed book information."""
    print("=== Book Details Example ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Search for a book
    paginator = await lib.search(q="python cookbook", count=3)
    books = await paginator.next()
    
    if books:
        # Get detailed information for first book
        book = books[0]
        print(f"Getting details for: {book.name}")
        
        # Fetch complete details
        details = await book.fetch()
        
        print("\n=== Complete Book Information ===")
        print(f"Title: {details['name']}")
        print(f"Description: {details.get('description', 'N/A')[:200]}...")
        print(f"Edition: {details.get('edition', 'N/A')}")
        print(f"Categories: {details.get('categories', 'N/A')}")
        print(f"Rating: {details.get('rating', 'N/A')}")
        print(f"Download URL: {details.get('download_url', 'N/A')}")


async def profile_example():
    """User profile and account information."""
    print("=== Profile Information Example ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Get download limits
    limits = await lib.profile.get_limits()
    
    print("=== Download Limits ===")
    print(f"Daily allowed: {limits['daily_allowed']}")
    print(f"Daily remaining: {limits['daily_remaining']}")
    print(f"Daily amount: {limits['daily_amount']}")
    print(f"Reset in: {limits['daily_reset']} hours")
    
    # Get download history (first few items)
    print("\n=== Recent Downloads ===")
    try:
        history = await lib.profile.download_history()
        recent = history.result[:5] if history.result else []
        
        if recent:
            for item in recent:
                print(f"• {item.name}")
        else:
            print("No download history found")
            
    except Exception as e:
        print(f"Could not fetch download history: {e}")


async def full_text_search_example():
    """Full-text search within book contents."""
    print("=== Full-Text Search Example ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Search for specific text within books
    query = "artificial neural networks"
    print(f"Searching for '{query}' within book contents...")
    
    paginator = await lib.full_text_search(
        q=query,
        lang=[Language.ENGLISH],
        extensions=[Extension.PDF],
        phrase=True,  # Search as exact phrase
        exact=True    # Exact word matching
    )
    
    books = await paginator.next()
    
    print(f"Found {len(books)} books containing '{query}'")
    for book in books[:3]:
        print(f"• {book.name}")
        print(f"  Authors: {[a['author'] for a in book.authors]}")
        print()


async def error_handling_example():
    """Demonstrate proper error handling."""
    print("=== Error Handling Example ===")
    
    lib = zlibrary.AsyncZlib()
    
    # Example 1: Login error
    try:
        await lib.login("invalid@email.com", "wrongpassword")
    except zlibrary.exception.LoginFailed as e:
        print(f"Login failed as expected: {e}")
    
    # Example 2: Empty query error
    try:
        await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
        await lib.search(q="")  # Empty query
    except zlibrary.exception.EmptyQueryError as e:
        print(f"Empty query error as expected: {e}")
    except Exception as e:
        print(f"Other error: {e}")
    
    # Example 3: Parse error handling
    try:
        # This would normally work, just demonstrating structure
        paginator = await lib.search(q="python")
        books = await paginator.next()
        print("✓ Search completed successfully")
    except zlibrary.exception.ParseError as e:
        print(f"Parse error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def main():
    """Run all examples."""
    print("Z-Library Python API Examples")
    print("=" * 40)
    
    # Check for credentials
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("⚠️  Set ZLOGIN and ZPASSW environment variables for full functionality")
        print("   export ZLOGIN='your-email@example.com'")
        print("   export ZPASSW='your-password'")
        print()
    
    examples = [
        basic_search_example,
        advanced_search_example,
        pagination_example,
        book_details_example,
        profile_example,
        full_text_search_example,
        error_handling_example
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