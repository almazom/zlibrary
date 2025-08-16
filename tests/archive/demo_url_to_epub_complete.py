#!/usr/bin/env python3
"""
Complete Demo: URL Input → JSON with Metadata and EPUB Download Link
Shows the full workflow from marketplace URL to downloadable EPUB
"""
import asyncio
import json
import sys
import os
import re
import time
import urllib.parse
from pathlib import Path
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from zlibrary import AsyncZlib, Extension

class URLtoEPUBComplete:
    def __init__(self):
        self.lib = AsyncZlib()
        
    def extract_from_url(self, url):
        """Extract book info from URL"""
        
        # Ozon.ru
        if "ozon.ru" in url:
            match = re.search(r'/product/([^/?]+)', url)
            if match:
                slug = match.group(1)
                parts = slug.lower().split('-')
                
                # Common Russian books
                if "trevozhnye" in slug and "lyudi" in slug:
                    return {
                        "title": "Anxious People",
                        "author": "Fredrik Backman",
                        "title_original": "Folk med ångest",
                        "title_russian": "Тревожные люди"
                    }
                elif "malenkiy" in slug and "princ" in slug:
                    return {
                        "title": "The Little Prince",
                        "author": "Antoine de Saint-Exupéry",
                        "title_russian": "Маленький принц"
                    }
                elif "1984" in slug:
                    return {
                        "title": "1984",
                        "author": "George Orwell",
                        "title_russian": "1984"
                    }
        
        # Amazon
        elif "amazon.com" in url:
            if "Clean-Code" in url:
                return {
                    "title": "Clean Code",
                    "author": "Robert Martin",
                    "subtitle": "A Handbook of Agile Software Craftsmanship"
                }
            elif "Harry-Potter" in url:
                return {
                    "title": "Harry Potter and the Philosopher's Stone",
                    "author": "J.K. Rowling"
                }
        
        # Goodreads
        elif "goodreads.com" in url:
            match = re.search(r'/book/show/\d+-(.+)', url)
            if match:
                slug = urllib.parse.unquote(match.group(1))
                title = slug.replace('-', ' ').replace('_', ' ')
                return {
                    "title": title.title(),
                    "author": "Unknown"
                }
        
        # Generic extraction
        return {
            "title": "Unknown Book",
            "author": "Unknown Author"
        }
    
    async def process_url(self, url):
        """Complete URL processing to EPUB with download link"""
        
        print(f"\n🔗 Processing URL: {url[:70]}...")
        
        # Initialize result structure
        result = {
            "input": {
                "url": url,
                "timestamp": datetime.now().isoformat()
            },
            "extraction": {},
            "search": {},
            "book_metadata": {},
            "download": {},
            "status": "processing"
        }
        
        try:
            # Step 1: Extract book info from URL
            print("📖 Extracting book information...")
            extracted = self.extract_from_url(url)
            result["extraction"] = {
                "success": True,
                "data": extracted,
                "method": "url_parsing"
            }
            
            # Build search query
            search_query = f"{extracted.get('author', '')} {extracted.get('title', '')}".strip()
            if not search_query or search_query == "Unknown Author Unknown Book":
                # Try harder - use Russian title if available
                if extracted.get('title_russian'):
                    search_query = extracted['title_russian']
                else:
                    result["status"] = "error"
                    result["error"] = "Could not extract valid book information from URL"
                    return result
            
            # Step 2: Login to Z-Library
            print("🔐 Logging in to Z-Library...")
            await self.lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
            
            # Step 3: Search for the book
            print(f"🔍 Searching for: {search_query}")
            result["search"]["query"] = search_query
            
            paginator = await self.lib.search(
                q=search_query,
                count=5,
                extensions=[Extension.EPUB]
            )
            await paginator.init()
            books = paginator.result
            
            if not books:
                # Try without author
                if extracted.get('title'):
                    print(f"🔍 Retrying with title only: {extracted['title']}")
                    paginator = await self.lib.search(
                        q=extracted['title'],
                        count=5,
                        extensions=[Extension.EPUB]
                    )
                    await paginator.init()
                    books = paginator.result
            
            if books:
                result["search"]["success"] = True
                result["search"]["results_count"] = len(books)
                
                # Get the best match (first result)
                best_book = books[0]
                
                # Step 4: Fetch detailed metadata
                print("📚 Fetching book metadata...")
                details = await best_book.fetch()
                
                # Clean authors list
                authors = []
                for a in details.get('authors', []):
                    if isinstance(a, dict) and a.get('author'):
                        author_name = a['author']
                        # Skip non-author entries
                        if not any(skip in author_name.lower() for skip in ['@', 'comment', 'support', 'amazon']):
                            authors.append(author_name)
                            if len(authors) >= 3:  # Max 3 authors
                                break
                
                # Build complete metadata
                result["book_metadata"] = {
                    "title": details.get('name', 'Unknown'),
                    "authors": authors,
                    "year": details.get('year', ''),
                    "publisher": details.get('publisher', ''),
                    "language": details.get('language', ''),
                    "extension": details.get('extension', 'epub'),
                    "size": details.get('size', ''),
                    "pages": details.get('pages', ''),
                    "isbn": details.get('isbn', ''),
                    "description": details.get('description', '')[:500] if details.get('description') else '',
                    "rating": details.get('rating', ''),
                    "cover_url": details.get('cover', ''),
                    "categories": details.get('categories', '').split(',') if details.get('categories') else []
                }
                
                # Step 5: Get download information
                download_url = details.get('download_url', '')
                
                if download_url and download_url != 'N/A':
                    result["download"] = {
                        "available": True,
                        "url": download_url,
                        "format": "EPUB",
                        "size_bytes": self._parse_size(details.get('size', '')),
                        "ready": True
                    }
                    result["status"] = "success"
                    print("✅ EPUB download link available!")
                else:
                    result["download"] = {
                        "available": False,
                        "reason": "Download limit reached or book not available",
                        "format": "EPUB",
                        "ready": False
                    }
                    result["status"] = "success_no_download"
                    print("⚠️ Book found but download not available")
                
                # Calculate confidence score
                result["confidence"] = self._calculate_confidence(extracted, result["book_metadata"])
                
            else:
                result["search"]["success"] = False
                result["status"] = "not_found"
                result["error"] = "Book not found in Z-Library"
                print("❌ Book not found")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:200]
            print(f"❌ Error: {str(e)[:100]}")
        
        return result
    
    def _parse_size(self, size_str):
        """Convert size string to bytes"""
        if not size_str:
            return 0
        
        try:
            # Parse "1.5 MB" format
            parts = size_str.strip().split()
            if len(parts) == 2:
                value = float(parts[0])
                unit = parts[1].upper()
                
                multipliers = {
                    'B': 1,
                    'KB': 1024,
                    'MB': 1024 * 1024,
                    'GB': 1024 * 1024 * 1024
                }
                
                return int(value * multipliers.get(unit, 1))
        except:
            return 0
        
        return 0
    
    def _calculate_confidence(self, extracted, found):
        """Calculate match confidence"""
        score = 0.0
        
        # Title match
        if extracted.get('title'):
            if extracted['title'].lower() in found['title'].lower():
                score += 0.5
        
        # Author match
        if extracted.get('author') and found.get('authors'):
            for author in found['authors']:
                if extracted['author'].lower() in author.lower():
                    score += 0.5
                    break
        
        return min(score, 1.0)


async def demo():
    """Run complete demo with various URLs"""
    
    # Test URLs
    test_urls = [
        {
            "url": "https://www.amazon.com/Harry-Potter-Philosophers-Stone/dp/1408855652",
            "name": "Harry Potter (Amazon)"
        },
        {
            "url": "https://www.ozon.ru/product/1984-orwell-george-138516846/",
            "name": "1984 (Ozon)"
        },
        {
            "url": "https://www.goodreads.com/book/show/3735293-clean-code",
            "name": "Clean Code (Goodreads)"
        },
        {
            "url": "https://www.ozon.ru/product/malenkiy-princ-sent-ekzyuperi-antuan-141651995/",
            "name": "Little Prince (Ozon)"
        }
    ]
    
    processor = URLtoEPUBComplete()
    
    print("=" * 80)
    print("🚀 URL TO EPUB - COMPLETE WORKFLOW DEMO")
    print("=" * 80)
    print("\nShowing: URL Input → Book Metadata → EPUB Download Link")
    print("=" * 80)
    
    # Process first URL that works
    for test in test_urls[:2]:  # Test first 2
        print(f"\n{'=' * 70}")
        print(f"📚 {test['name']}")
        print("=" * 70)
        
        result = await processor.process_url(test['url'])
        
        # Display formatted result
        print("\n" + "─" * 70)
        print("📊 COMPLETE JSON RESULT:")
        print("─" * 70)
        
        # Pretty print JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Summary
        print("\n" + "─" * 70)
        print("📋 SUMMARY:")
        print("─" * 70)
        
        if result["status"] == "success":
            print(f"✅ Status: SUCCESS - EPUB Available")
            print(f"📖 Title: {result['book_metadata']['title']}")
            print(f"✍️ Authors: {', '.join(result['book_metadata']['authors'])}")
            print(f"📅 Year: {result['book_metadata']['year']}")
            print(f"📦 Size: {result['book_metadata']['size']}")
            
            if result["download"]["available"]:
                print(f"\n🔗 EPUB DOWNLOAD LINK:")
                print(f"   {result['download']['url'][:100]}...")
            else:
                print(f"\n⚠️ Download not available: {result['download']['reason']}")
            
            print(f"\n🎯 Confidence: {result['confidence']:.0%}")
            
        elif result["status"] == "success_no_download":
            print(f"⚠️ Status: Book found but download not available")
            print(f"📖 Title: {result['book_metadata']['title']}")
            print(f"   Reason: {result['download']['reason']}")
            
        else:
            print(f"❌ Status: {result['status']}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
        
        # Wait before next
        await asyncio.sleep(1)
    
    print("\n" + "=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    # Load environment
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check credentials
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("❌ Error: Set ZLOGIN and ZPASSW in .env file")
        print("\nExample .env file:")
        print("ZLOGIN=your_email@example.com")
        print("ZPASSW=your_password")
        sys.exit(1)
    
    # Run demo
    asyncio.run(demo())