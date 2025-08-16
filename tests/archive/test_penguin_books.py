#!/usr/bin/env python3
"""
Penguin 2025 Best Books - Z-Library Testing Script
Tests our Z-Library microservice with each book from the list
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

try:
    import zlibrary
    from zlibrary import AsyncZlib, Extension, Language
except ImportError as e:
    print(f"❌ Failed to import zlibrary: {e}")
    print("Make sure you're running from the project root directory")
    exit(1)

# Book list from Penguin Random House 2025
PENGUIN_2025_BOOKS = [
    {"title": "The Emperor of Gladness", "author": "Ocean Vuong"},
    {"title": "Murderland", "author": "Caroline Fraser"},
    {"title": "One Golden Summer", "author": "Carley Fortune"},
    {"title": "Beyond Anxiety", "author": "Martha Beck"},
    {"title": "We Can Do Hard Things", "author": "Glennon Doyle"},
    {"title": "The Note", "author": "Alafair Burke"},
    {"title": "The Stolen Queen", "author": "Fiona Davis"},
    {"title": "We Do Not Part", "author": "Han Kang"},
    {"title": "Dream Count", "author": "Chimamanda Ngozi Adichie"},
    {"title": "Problematic Summer Romance", "author": "Ali Hazelwood"},
    {"title": "All the Other Mothers Hate Me", "author": "Sarah Harman"},
    {"title": "Witchcraft for Wayward Girls", "author": "Grady Hendrix"},
    {"title": "Water Moon", "author": "Samantha Sotto Yambao"},
    {"title": "Mask of the Deer Woman", "author": "Laurie L. Dove"},
    {"title": "Theft", "author": "Abdulrazak Gurnah"},
    {"title": "The Missing Half", "author": "Ashley Flowers"},
    {"title": "The Listeners", "author": "Maggie Stiefvater"},
    {"title": "Let's Call Her Barbie", "author": "Renée Rosen"},
    {"title": "The Favorites", "author": "Layne Fargo"},
    {"title": "All That Life Can Afford", "author": "Emily Everett"},
    {"title": "Good Dirt", "author": "Charmaine Wilkerson"},
    {"title": "One Good Thing", "author": "Georgia Hunter"},
    {"title": "Great Big Beautiful Life", "author": "Emily Henry"},
    {"title": "Stag Dance", "author": "Torrey Peters"},
    {"title": "Dream State", "author": "Eric Puchner"},
    {"title": "The Dream Hotel", "author": "Laila Lalami"},
    {"title": "No More Tears", "author": "Gardiner Harris"},
    {"title": "The Girls Who Grew Big", "author": "Leila Mottley"},
    {"title": "Memorial Days", "author": "Geraldine Brooks"},
    {"title": "Dead Money", "author": "Jakob Kerr"},
    {"title": "Atmosphere", "author": "Taylor Jenkins Reid"},
]

class PenguinBooksTest:
    def __init__(self):
        self.client = None
        self.results = []
        self.downloads_dir = Path("downloads/penguin_2025")
        self.downloads_dir.mkdir(exist_ok=True, parents=True)
        
    async def setup_client(self):
        """Initialize Z-Library client with authentication"""
        print("🔑 Setting up Z-Library client...")
        
        # Get credentials from environment
        email = os.getenv('ZLOGIN')
        password = os.getenv('ZPASSW')
        
        if not email or not password:
            print("❌ Z-Library credentials not found!")
            print("Set ZLOGIN and ZPASSW environment variables")
            return False
            
        try:
            self.client = AsyncZlib()
            profile = await self.client.login(email, password)
            
            # Check download limits
            limits = await profile.get_limits()
            print(f"✅ Logged in successfully!")
            print(f"📊 Download limits: {limits['daily_remaining']}/{limits['daily_allowed']} remaining")
            
            return True
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    async def search_book(self, book, book_num, total):
        """Search for a single book"""
        title = book["title"]
        author = book["author"]
        search_query = f"{title} {author}"
        
        print(f"\n📚 [{book_num}/{total}] Searching: {title} by {author}")
        print(f"🔍 Query: {search_query}")
        
        result = {
            "book": book,
            "query": search_query,
            "found": False,
            "results_count": 0,
            "best_match": None,
            "download_attempted": False,
            "download_successful": False,
            "error": None
        }
        
        try:
            # Search with EPUB preference and English filter
            search_results = await self.client.search(
                q=search_query,
                extensions=[Extension.EPUB],
                lang=[Language.ENGLISH],
                count=10
            )
            
            await search_results.init()
            results = search_results.result
            
            result["results_count"] = len(results)
            result["found"] = len(results) > 0
            
            if results:
                print(f"✅ Found {len(results)} results")
                
                # Get details for best match
                best_match = results[0]
                book_details = await best_match.fetch()
                
                result["best_match"] = {
                    "title": book_details.get("name", "Unknown"),
                    "authors": book_details.get("authors", []),
                    "year": book_details.get("year", "Unknown"),
                    "extension": book_details.get("extension", "Unknown"),
                    "size": book_details.get("size", "Unknown"),
                    "rating": book_details.get("rating", "Unknown"),
                    "download_url": book_details.get("download_url", "")
                }
                
                print(f"📖 Best match: {book_details.get('name', 'Unknown')}")
                print(f"👤 Authors: {', '.join([a.get('name', '') for a in book_details.get('authors', [])])}")
                print(f"📅 Year: {book_details.get('year', 'Unknown')}")
                print(f"📄 Format: {book_details.get('extension', 'Unknown')}")
                print(f"💾 Size: {book_details.get('size', 'Unknown')}")
                print(f"⭐ Rating: {book_details.get('rating', 'Unknown')}")
                
                # Check if download is available
                download_url = book_details.get("download_url", "")
                if download_url and "Download" in download_url:
                    print("✅ Download available")
                    result["download_attempted"] = True
                    # Note: Actual download would happen here in a real scenario
                    # For testing, we just mark it as attempted
                else:
                    print("❌ Download not available")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            result["error"] = str(e)
        
        self.results.append(result)
        return result
    
    async def test_all_books(self):
        """Test searching for all books in the list"""
        print("🚀 Starting Penguin 2025 Books Test")
        print(f"📋 Testing {len(PENGUIN_2025_BOOKS)} books")
        print("="*60)
        
        if not await self.setup_client():
            return False
        
        # Test each book
        for i, book in enumerate(PENGUIN_2025_BOOKS, 1):
            await self.search_book(book, i, len(PENGUIN_2025_BOOKS))
            
            # Small delay between searches to be respectful
            await asyncio.sleep(1)
        
        # Generate summary report
        self.generate_report()
        return True
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 PENGUIN 2025 BOOKS TEST REPORT")
        print("="*60)
        
        found_count = sum(1 for r in self.results if r["found"])
        downloadable_count = sum(1 for r in self.results if r["download_attempted"])
        error_count = sum(1 for r in self.results if r["error"])
        
        print(f"📚 Total books tested: {len(self.results)}")
        print(f"✅ Books found: {found_count}")
        print(f"📥 Books with downloads: {downloadable_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📈 Success rate: {(found_count/len(self.results)*100):.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 60)
        
        for i, result in enumerate(self.results, 1):
            book = result["book"]
            status = "✅" if result["found"] else "❌"
            download = "📥" if result["download_attempted"] else "❌"
            
            print(f"{i:2d}. {status} {book['title']} by {book['author']}")
            print(f"    Results: {result['results_count']} | Download: {download}")
            
            if result["best_match"]:
                match = result["best_match"]
                print(f"    Best match: {match['title']} ({match['year']}, {match['extension']})")
            
            if result["error"]:
                print(f"    Error: {result['error']}")
            print()
        
        # Save detailed report to JSON
        report_file = self.downloads_dir / "penguin_2025_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        print("\n🎯 SUCCESS CRITERIA ANALYSIS:")
        print("-" * 40)
        print(f"• Z-Library microservice connection: {'✅ Working' if found_count > 0 else '❌ Failed'}")
        print(f"• Book search functionality: {'✅ Working' if found_count > 0 else '❌ Failed'}")
        print(f"• Search result parsing: {'✅ Working' if found_count > 0 else '❌ Failed'}")
        print(f"• Download availability check: {'✅ Working' if downloadable_count > 0 else '❌ Limited'}")

async def main():
    """Main test function"""
    tester = PenguinBooksTest()
    
    try:
        success = await tester.test_all_books()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    finally:
        if tester.client:
            await tester.client.logout()
            print("🔓 Logged out from Z-Library")

if __name__ == "__main__":
    exit(asyncio.run(main()))