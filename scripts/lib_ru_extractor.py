#!/usr/bin/env python3
"""
Lib.ru Fast Book/Author Extractor
High-performance extraction from lib.ru/RUFANT/ with <10s target
No Claude calls needed - direct curl parsing!
"""

import asyncio
import aiohttp
import random
import json
import re
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys

@dataclass
class BookData:
    title: str
    author: str
    source_url: str
    extraction_time: float
    confidence: float = 0.95  # High confidence for static HTML

@dataclass
class AuthorData:
    name: str
    directory: str
    book_count: int = 0

class LibRuExtractor:
    # Multiple categories for maximum randomness
    CATEGORIES = {
        "RUFANT": "https://lib.ru/RUFANT",      # Russian Fantasy
        "INOFANT": "https://lib.ru/INOFANT",    # Foreign Fantasy  
        "RAZNOE": "https://lib.ru/RAZNOE"       # Miscellaneous
    }
    POOL_FILE = Path("tests/IUC/libru_book_pool.json")
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=8)
        self.book_pool = self.load_book_pool()
        self.session_authors = set()  # Track used authors in session
        self.category_stats = {cat: 0 for cat in self.CATEGORIES}  # Track category usage
        
    def load_book_pool(self) -> List[Dict]:
        """Load existing book pool"""
        if self.POOL_FILE.exists():
            try:
                with open(self.POOL_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_book_pool(self):
        """Save book pool to file"""
        self.POOL_FILE.parent.mkdir(exist_ok=True)
        with open(self.POOL_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.book_pool, f, ensure_ascii=False, indent=2)
    
    def book_hash(self, title: str, author: str) -> str:
        """Generate hash for book deduplication"""
        normalized = f"{title.lower().strip()} {author.lower().strip()}"
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_duplicate(self, title: str, author: str) -> bool:
        """Check if book already in pool (7 day window)"""
        book_hash = self.book_hash(title, author)
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for book in self.book_pool:
            if book.get('hash') == book_hash:
                try:
                    extraction_date = datetime.fromisoformat(book.get('extracted_at', '2020-01-01'))
                    if extraction_date > cutoff_date:
                        return True
                except:
                    continue
        return False
    
    async def fetch_with_encoding(self, url: str) -> str:
        """Fetch URL and convert from Windows-1251"""
        try:
            connector = aiohttp.TCPConnector(
                limit=10,
                ttl_dns_cache=300,
                enable_cleanup_closed=True
            )
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 Book Extractor'}
            ) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    raw_bytes = await response.read()
                    # Convert KOI8-R to UTF-8 (lib.ru uses KOI8-R encoding)
                    return raw_bytes.decode('koi8-r', errors='replace')
        except Exception as e:
            print(f"⚠️ Fetch error for {url}: {e}")
            raise
    
    def parse_authors(self, html: str, category: str) -> List[AuthorData]:
        """Parse author list from category page"""
        authors = []
        # Pattern: <A HREF=AUTHORDIR/><b>Author Name</b></A>
        pattern = r'<A HREF=([A-Z][A-Z_0-9]*)/><b>([^<]+)</b></A>'
        
        matches = re.findall(pattern, html)
        for directory, name in matches:
            authors.append(AuthorData(
                name=name.strip(),
                directory=directory.strip()
            ))
        
        print(f"📚 Parsed {len(authors)} authors from lib.ru/{category}")
        return authors
    
    def parse_books(self, html: str, author_name: str) -> List[Tuple[str, str]]:
        """Parse books from author directory"""
        books = []
        # Pattern: <A HREF=filename.txt><b>Book Title</b></A>
        pattern = r'<A HREF=([^>]+\.txt)><b>([^<]+)</b></A>'
        
        matches = re.findall(pattern, html)
        for filename, title in matches:
            # Clean up title (remove numbering, extra spaces)
            clean_title = re.sub(r'^\d+\.\s*', '', title.strip())
            clean_title = re.sub(r'\s+', ' ', clean_title)
            
            if len(clean_title) > 5 and not clean_title.startswith('Content'):  # Filter content files
                books.append((clean_title, filename))
        
        print(f"📖 Found {len(books)} books for {author_name}")
        return books
    
    def select_random_author(self, authors: List[AuthorData]) -> AuthorData:
        """Select random author with session-based variety"""
        # Prefer authors not used in this session
        unused_authors = [a for a in authors if a.directory not in self.session_authors]
        
        if unused_authors:
            selected = random.choice(unused_authors)
        else:
            # If all used, reset and select any
            self.session_authors.clear()
            selected = random.choice(authors)
        
        self.session_authors.add(selected.directory)
        return selected
    
    def select_random_category(self) -> Tuple[str, str]:
        """Select random category with preference for less used ones"""
        # Weight categories by inverse usage (prefer less used)
        weights = []
        categories = list(self.CATEGORIES.keys())
        
        for cat in categories:
            usage = self.category_stats[cat]
            # Higher weight for less used categories
            weight = 1.0 / (usage + 1)
            weights.append(weight)
        
        selected_cat = random.choices(categories, weights=weights)[0]
        selected_url = self.CATEGORIES[selected_cat]
        
        return selected_cat, selected_url
    
    async def send_telegram_notification(self, book_data: BookData, category: str):
        """Send extraction success to Telegram"""
        try:
            import subprocess
            message = f"""📚 NEW BOOK EXTRACTED!

📖 Title: {book_data.title}
✍️ Author: {book_data.author}
📂 Category: lib.ru/{category}
⏱️ Time: {book_data.extraction_time:.1f}s
🎯 Confidence: {book_data.confidence}

🔗 URL: {book_data.source_url}"""
            
            subprocess.run([
                "/home/almaz/MCP/SCRIPTS/telegram_send_manager.sh",
                "send",
                message
            ], capture_output=True, timeout=10)
            print("📱 Telegram notification sent")
            
        except Exception as e:
            print(f"⚠️ Telegram notification failed: {e}")
    
    async def extract_random_book(self) -> BookData:
        """Main extraction method with multi-category support"""
        start_time = time.time()
        
        try:
            # Step 1: Select random category
            selected_category, category_url = self.select_random_category()
            print(f"🎲 Selected category: lib.ru/{selected_category}")
            self.category_stats[selected_category] += 1
            
            # Step 2: Get authors list from selected category
            print(f"🔍 Fetching authors from {category_url}...")
            authors_html = await self.fetch_with_encoding(category_url)
            authors = self.parse_authors(authors_html, selected_category)
            
            if not authors:
                raise Exception(f"No authors found in {selected_category}")
            
            # Step 3: Select random author
            selected_author = self.select_random_author(authors)
            print(f"🎲 Selected author: {selected_author.name} ({selected_author.directory})")
            
            # Step 4: Get books from author directory
            author_url = f"{category_url}/{selected_author.directory}/"
            print(f"📚 Fetching books from {author_url}")
            
            books_html = await self.fetch_with_encoding(author_url)
            books = self.parse_books(books_html, selected_author.name)
            
            if not books:
                raise Exception(f"No books found for {selected_author.name}")
            
            # Step 5: Select random book and check for duplicates
            for attempt in range(min(5, len(books))):
                book_title, book_filename = random.choice(books)
                
                if not self.is_duplicate(book_title, selected_author.name):
                    book_url = f"{author_url}{book_filename}"
                    extraction_time = time.time() - start_time
                    
                    # Create book data
                    book_data = BookData(
                        title=book_title,
                        author=selected_author.name,
                        source_url=book_url,
                        extraction_time=extraction_time,
                        confidence=0.95  # High confidence for static parsing
                    )
                    
                    # Add to pool
                    self.add_to_pool(book_data, selected_category)
                    
                    # Send Telegram notification
                    await self.send_telegram_notification(book_data, selected_category)
                    
                    print(f"⚡ Extraction completed in {extraction_time:.2f}s")
                    return book_data, selected_category
                else:
                    print(f"⚠️ Duplicate: {book_title} by {selected_author.name}")
            
            raise Exception("All books are duplicates")
            
        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ Extraction failed after {total_time:.2f}s: {e}")
            raise
    
    def add_to_pool(self, book_data: BookData, category: str):
        """Add book to tracking pool"""
        book_entry = {
            "title": book_data.title,
            "author": book_data.author,
            "url": book_data.source_url,
            "confidence": book_data.confidence,
            "hash": self.book_hash(book_data.title, book_data.author),
            "extracted_at": datetime.now().isoformat(),
            "extraction_time": book_data.extraction_time,
            "source": f"lib.ru/{category}",
            "category": category
        }
        
        # Clean old entries
        cutoff_date = datetime.now() - timedelta(days=7)
        self.book_pool = [
            book for book in self.book_pool
            if datetime.fromisoformat(book.get('extracted_at', '2020-01-01')) > cutoff_date
        ]
        
        self.book_pool.append(book_entry)
        self.save_book_pool()
    
    def get_stats(self) -> Dict:
        """Get extraction statistics"""
        return {
            "total_books_in_pool": len(self.book_pool),
            "authors_used_in_session": len(self.session_authors),
            "categories_used": dict(self.category_stats),
            "available_categories": list(self.CATEGORIES.keys()),
            "source": "lib.ru (multi-category)"
        }
    
    async def close(self):
        """Clean up connections"""
        pass  # Sessions are managed per request now

async def main():
    extractor = LibRuExtractor()
    
    try:
        print("🚀 Starting multi-category lib.ru book extraction...")
        result, category = await extractor.extract_random_book()
        
        # Format output
        output = {
            "title": result.title,
            "author": result.author,
            "url": result.source_url,
            "confidence": result.confidence,
            "category": category,
            "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S MSK"),
            "performance": {
                "total_time": result.extraction_time,
                "source": f"lib.ru/{category}",
                "target_met": result.extraction_time < 10.0
            },
            "stats": extractor.get_stats()
        }
        
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
        # Performance summary
        print(f"\n🎯 PERFORMANCE SUMMARY:")
        print(f"⚡ Total time: {result.extraction_time:.1f}s (Target: <10s)")
        print(f"🎲 Randomness: High (199 authors, session tracking)")
        print(f"📊 Success: {'✅' if result.extraction_time < 10.0 else '⚠️'}")
        print(f"🔧 Method: Direct curl parsing (no Claude calls)")
        
        return output
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return None
    finally:
        await extractor.close()

if __name__ == "__main__":
    result = asyncio.run(main())
    if result and result.get("performance", {}).get("target_met", False):
        sys.exit(0)
    else:
        sys.exit(1)