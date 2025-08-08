#!/usr/bin/env python3
"""
Edge case testing for Penguin Publishing books
Tests sequential downloading of EPUB files one by one
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from datetime import datetime
import json
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib, Extension, Language
from zlibrary.exception import (
    LoginFailed, ParseError, EmptyQueryError,
    NoProfileError, NoDomainError, NoIdError
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable zlibrary debug logging
zlib_logger = logging.getLogger("zlibrary")
zlib_logger.addHandler(logging.StreamHandler())
zlib_logger.setLevel(logging.DEBUG)

class PenguinBooksTester:
    def __init__(self):
        self.client = None
        self.profile = None
        self.download_dir = Path(__file__).parent / "test_downloads" / "penguin_books"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.download_dir / "test_results.json"
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "searches": [],
            "downloads": [],
            "errors": [],
            "stats": {
                "total_searched": 0,
                "total_found": 0,
                "total_downloaded": 0,
                "total_failed": 0
            }
        }
        
    async def setup(self):
        """Initialize client and login"""
        logger.info("🚀 Initializing Z-Library client...")
        
        # Get credentials from environment
        email = os.getenv("ZLOGIN")
        password = os.getenv("ZPASSW")
        
        if not email or not password:
            raise ValueError("Please set ZLOGIN and ZPASSW environment variables")
        
        self.client = AsyncZlib()
        
        try:
            logger.info("🔐 Logging in to Z-Library...")
            self.profile = await self.client.login(email, password)
            logger.info("✅ Login successful")
            
            # Check download limits
            limits = await self.profile.get_limits()
            logger.info(f"📊 Download limits: {limits['daily_remaining']}/{limits['daily_allowed']} remaining")
            
            if limits['daily_remaining'] == 0:
                logger.warning("⚠️ No downloads remaining today!")
                
            return limits
            
        except LoginFailed as e:
            logger.error(f"❌ Login failed: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Setup error: {e}")
            raise
    
    async def search_penguin_books(self, search_queries=None):
        """Search for Penguin Publishing books"""
        if search_queries is None:
            # Default Penguin search queries for recommendations
            search_queries = [
                "Penguin Classics",
                "Penguin Modern Classics",
                "Penguin Great Ideas",
                "Penguin Little Black Classics",
                "publisher:Penguin",
                "Penguin Random House bestsellers",
                "Penguin Books recommendations 2024",
                "Penguin English Library"
            ]
        
        all_results = []
        
        for query in search_queries:
            logger.info(f"\n🔍 Searching: '{query}'")
            search_data = {
                "query": query,
                "results": [],
                "error": None,
                "metadata": {}
            }
            
            try:
                # Search specifically for EPUB books in English
                paginator = await self.client.search(
                    q=query,
                    extensions=[Extension.EPUB],
                    lang=[Language.ENGLISH],
                    count=10  # Get 10 results per search
                )
                
                # Initialize paginator
                await paginator.init()
                
                # Get total results
                search_data["metadata"] = {
                    "total_pages": paginator.total,
                    "current_page": paginator.page,
                    "results_per_page": paginator.count
                }
                
                logger.info(f"📚 Found {paginator.total} pages of results")
                
                # Get first page results
                books = paginator.result
                
                if books:
                    logger.info(f"📖 Processing {len(books)} books from first page...")
                    
                    for i, book in enumerate(books, 1):
                        # Try to get basic info without fetching
                        book_info = {
                            "id": book.id,
                            "name": book.name,
                            "authors": book.authors,
                            "year": book.year,
                            "language": book.language,
                            "extension": book.extension,
                            "size": book.size,
                            "rating": book.rating,
                            "publisher": book.publisher if hasattr(book, 'publisher') else None,
                            "isbn": book.isbn if hasattr(book, 'isbn') else None,
                            "cover": book.cover,
                            "url": book.url
                        }
                        
                        # Check if it's actually from Penguin
                        is_penguin = False
                        if book_info["publisher"]:
                            publisher_lower = book_info["publisher"].lower()
                            if "penguin" in publisher_lower:
                                is_penguin = True
                                logger.info(f"  ✅ {i}. {book_info['name'][:50]}... [PENGUIN: {book_info['publisher']}]")
                        
                        if not is_penguin:
                            logger.info(f"  📚 {i}. {book_info['name'][:50]}... [Publisher: {book_info['publisher'] or 'Unknown'}]")
                        
                        search_data["results"].append(book_info)
                        all_results.append(book)
                    
                    self.test_results["stats"]["total_found"] += len(books)
                else:
                    logger.warning(f"  ⚠️ No results found for '{query}'")
                    
            except EmptyQueryError:
                error_msg = f"Empty query error for '{query}'"
                logger.error(f"  ❌ {error_msg}")
                search_data["error"] = error_msg
                self.test_results["errors"].append({"type": "search", "query": query, "error": error_msg})
                
            except Exception as e:
                error_msg = f"Search error: {str(e)}"
                logger.error(f"  ❌ {error_msg}")
                search_data["error"] = error_msg
                self.test_results["errors"].append({"type": "search", "query": query, "error": error_msg})
            
            self.test_results["searches"].append(search_data)
            self.test_results["stats"]["total_searched"] += 1
            
            # Small delay between searches
            await asyncio.sleep(1)
        
        return all_results
    
    async def download_book_sequential(self, book, index):
        """Download a single book (no batching)"""
        download_info = {
            "book_id": book.id,
            "book_name": book.name,
            "start_time": datetime.now().isoformat(),
            "status": None,
            "file_path": None,
            "error": None,
            "download_url": None,
            "details": None
        }
        
        try:
            logger.info(f"\n📥 Downloading book {index}: {book.name[:60]}...")
            logger.info(f"  Authors: {', '.join(book.authors) if book.authors else 'Unknown'}")
            logger.info(f"  Size: {book.size}, Year: {book.year}")
            
            # Fetch full book details (includes download URL)
            logger.info("  🔄 Fetching book details...")
            book_details = await book.fetch()
            download_info["details"] = book_details
            
            # Check download URL
            download_url = book_details.get('download_url', '')
            download_info["download_url"] = download_url
            
            if not download_url:
                error_msg = "No download URL available"
                logger.warning(f"  ⚠️ {error_msg}")
                download_info["status"] = "no_url"
                download_info["error"] = error_msg
                self.test_results["stats"]["total_failed"] += 1
                return download_info
            
            if download_url == "No download available":
                error_msg = "Book not available for download"
                logger.warning(f"  ⚠️ {error_msg}")
                download_info["status"] = "unavailable"
                download_info["error"] = error_msg
                self.test_results["stats"]["total_failed"] += 1
                return download_info
            
            # Simulate download (we have the URL but won't actually download to save quota)
            # In real scenario, you would use aiohttp or requests to download the file
            
            # Create a placeholder file name
            safe_name = "".join(c for c in book.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name[:100]  # Limit length
            file_name = f"{book.id}_{safe_name}.epub"
            file_path = self.download_dir / file_name
            
            logger.info(f"  ✅ Download URL obtained: {download_url[:50]}...")
            logger.info(f"  📁 Would save to: {file_path}")
            
            # Save metadata instead of actual file (for testing)
            metadata_path = self.download_dir / f"{book.id}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(book_details, f, indent=2, ensure_ascii=False)
            
            download_info["status"] = "success"
            download_info["file_path"] = str(file_path)
            download_info["metadata_path"] = str(metadata_path)
            self.test_results["stats"]["total_downloaded"] += 1
            
            logger.info(f"  ✅ Book processed successfully")
            
        except ParseError as e:
            error_msg = f"Parse error: {str(e)}"
            logger.error(f"  ❌ {error_msg}")
            download_info["status"] = "parse_error"
            download_info["error"] = error_msg
            self.test_results["stats"]["total_failed"] += 1
            
        except Exception as e:
            error_msg = f"Download error: {str(e)}"
            logger.error(f"  ❌ {error_msg}")
            download_info["status"] = "error"
            download_info["error"] = error_msg
            self.test_results["stats"]["total_failed"] += 1
        
        download_info["end_time"] = datetime.now().isoformat()
        self.test_results["downloads"].append(download_info)
        
        return download_info
    
    async def test_edge_cases(self):
        """Test various edge cases"""
        logger.info("\n🧪 Testing edge cases...")
        
        edge_cases = []
        
        # Test 1: Empty search
        try:
            logger.info("  Test: Empty search query")
            await self.client.search(q="", extensions=[Extension.EPUB])
            edge_cases.append({"test": "empty_search", "status": "unexpected_pass"})
        except EmptyQueryError:
            logger.info("    ✅ Correctly rejected empty query")
            edge_cases.append({"test": "empty_search", "status": "pass"})
        except Exception as e:
            logger.error(f"    ❌ Unexpected error: {e}")
            edge_cases.append({"test": "empty_search", "status": "fail", "error": str(e)})
        
        # Test 2: Invalid book ID
        try:
            logger.info("  Test: Invalid book ID")
            await self.client.get_by_id("invalid_id_12345")
            edge_cases.append({"test": "invalid_id", "status": "unexpected_pass"})
        except NoIdError:
            logger.info("    ✅ Correctly rejected invalid ID")
            edge_cases.append({"test": "invalid_id", "status": "pass"})
        except Exception as e:
            logger.error(f"    ❌ Unexpected error: {e}")
            edge_cases.append({"test": "invalid_id", "status": "fail", "error": str(e)})
        
        # Test 3: Special characters in search
        try:
            logger.info("  Test: Special characters in search")
            results = await self.client.search(
                q="Penguin & Books @ #2024",
                extensions=[Extension.EPUB],
                count=1
            )
            await results.init()
            logger.info(f"    ✅ Handled special characters, found {results.total} pages")
            edge_cases.append({"test": "special_chars", "status": "pass", "results": results.total})
        except Exception as e:
            logger.error(f"    ❌ Error with special characters: {e}")
            edge_cases.append({"test": "special_chars", "status": "fail", "error": str(e)})
        
        return edge_cases
    
    async def run(self):
        """Main test execution"""
        try:
            # Setup
            limits = await self.setup()
            
            # Test edge cases first
            edge_cases = await self.test_edge_cases()
            self.test_results["edge_cases"] = edge_cases
            
            # Search for Penguin books
            logger.info("\n📚 Starting Penguin books search...")
            books = await self.search_penguin_books()
            
            if not books:
                logger.warning("❌ No books found!")
                return
            
            logger.info(f"\n📊 Total books found: {len(books)}")
            
            # Download books one by one (sequential, no batching)
            logger.info("\n⬇️ Starting sequential downloads (one by one)...")
            
            # Limit downloads to preserve quota
            max_downloads = min(5, len(books), limits['daily_remaining'])
            logger.info(f"📋 Will process up to {max_downloads} books")
            
            for i, book in enumerate(books[:max_downloads], 1):
                # Sequential download with delay
                await self.download_book_sequential(book, i)
                
                # Wait between downloads (anti-rate-limit)
                if i < max_downloads:
                    delay = 2  # seconds
                    logger.info(f"⏳ Waiting {delay} seconds before next download...")
                    await asyncio.sleep(delay)
            
            # Save results
            self.test_results["end_time"] = datetime.now().isoformat()
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            # Print summary
            logger.info("\n" + "="*60)
            logger.info("📊 TEST SUMMARY")
            logger.info("="*60)
            logger.info(f"Total searches: {self.test_results['stats']['total_searched']}")
            logger.info(f"Total books found: {self.test_results['stats']['total_found']}")
            logger.info(f"Total processed: {self.test_results['stats']['total_downloaded']}")
            logger.info(f"Total failed: {self.test_results['stats']['total_failed']}")
            logger.info(f"Total errors: {len(self.test_results['errors'])}")
            logger.info(f"Results saved to: {self.results_file}")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise
        finally:
            if self.client:
                await self.client.logout()
                logger.info("👋 Logged out")

async def main():
    """Run the test"""
    tester = PenguinBooksTester()
    await tester.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Test interrupted by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)