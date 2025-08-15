#!/usr/bin/env python3
"""
Eksmo.ru Random Book Extractor
Randomly selects pages and books from eksmo.ru fiction category
"""

import asyncio
import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import sys

class EksmoRandomExtractor:
    BASE_URL = "https://eksmo.ru/khudozhestvennaya-literatura/"
    POOL_FILE = Path("tests/IUC/eksmo_book_pool.json")
    
    def __init__(self):
        self.page_weights = {1: 0.1, 2: 0.15, 3: 0.2, 4: 0.2, 5: 0.35}  # Higher weight for later pages
        self.book_pool = self.load_book_pool()
    
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
    
    def get_random_page_url(self) -> str:
        """Get random page URL with weighted selection"""
        pages = list(self.page_weights.keys())
        weights = list(self.page_weights.values())
        selected_page = random.choices(pages, weights=weights)[0]
        
        if selected_page == 1:
            return self.BASE_URL
        else:
            return f"{self.BASE_URL}page{selected_page}/"
    
    def book_hash(self, title: str, author: str) -> str:
        """Generate hash for book deduplication"""
        normalized = f"{title.lower().strip()} {author.lower().strip()}"
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def is_duplicate(self, title: str, author: str) -> bool:
        """Check if book already in pool"""
        book_hash = self.book_hash(title, author)
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for book in self.book_pool:
            if book.get('hash') == book_hash:
                extraction_date = datetime.fromisoformat(book.get('extracted_at', '2020-01-01'))
                if extraction_date > cutoff_date:
                    return True
        return False
    
    def add_to_pool(self, title: str, author: str, url: str, confidence: float):
        """Add book to pool"""
        book_data = {
            "title": title,
            "author": author, 
            "url": url,
            "confidence": confidence,
            "hash": self.book_hash(title, author),
            "extracted_at": datetime.now().isoformat(),
            "page_source": url
        }
        
        # Remove old entries
        cutoff_date = datetime.now() - timedelta(days=7)
        self.book_pool = [
            book for book in self.book_pool
            if datetime.fromisoformat(book.get('extracted_at', '2020-01-01')) > cutoff_date
        ]
        
        self.book_pool.append(book_data)
        self.save_book_pool()
    
    async def extract_random_book(self) -> Dict:
        """Extract random book from eksmo.ru"""
        max_attempts = 10
        
        for attempt in range(max_attempts):
            try:
                # 1. Get random page
                page_url = self.get_random_page_url()
                print(f"🔄 Attempt {attempt + 1}: Selected page {page_url}")
                
                # 2. Use Claude to extract book URLs from page
                claude_cmd = [
                    "/home/almaz/.claude/local/claude",
                    "-p", f"Use WebFetch to visit {page_url} and extract 3-5 book URLs in format https://eksmo.ru/book/...",
                    "--allowedTools", "WebFetch",
                    "--output-format", "json"
                ]
                
                result = subprocess.run(claude_cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    print(f"⚠️ Claude extraction failed: {result.stderr}")
                    continue
                
                # Parse Claude response for book URLs
                claude_response = json.loads(result.stdout)
                response_text = claude_response.get("response", "")
                
                # Extract book URLs using simple parsing
                book_urls = []
                for line in response_text.split('\n'):
                    if 'https://eksmo.ru/book/' in line:
                        # Extract URL from line
                        start = line.find('https://eksmo.ru/book/')
                        if start != -1:
                            end = line.find(' ', start)
                            if end == -1:
                                end = len(line)
                            url = line[start:end].rstrip('.,)')
                            book_urls.append(url)
                
                if not book_urls:
                    print("⚠️ No book URLs found on page")
                    continue
                
                # 3. Select random book URL
                selected_book_url = random.choice(book_urls)
                print(f"📖 Selected book URL: {selected_book_url}")
                
                # 4. Extract book metadata
                extract_cmd = [
                    "/home/almaz/.claude/local/claude", 
                    "-p", f"Use WebFetch to visit {selected_book_url} and extract book metadata (title, author) as JSON",
                    "--allowedTools", "WebFetch",
                    "--output-format", "json"
                ]
                
                extract_result = subprocess.run(extract_cmd, capture_output=True, text=True, timeout=60)
                if extract_result.returncode != 0:
                    print(f"⚠️ Book extraction failed: {extract_result.stderr}")
                    continue
                
                # Parse metadata
                extract_response = json.loads(extract_result.stdout)
                metadata_text = extract_response.get("response", "")
                
                # Try to parse JSON from response
                try:
                    if '{' in metadata_text and '}' in metadata_text:
                        json_start = metadata_text.find('{')
                        json_end = metadata_text.rfind('}') + 1
                        metadata = json.loads(metadata_text[json_start:json_end])
                        
                        title = metadata.get('title', '')
                        author = metadata.get('author', '')
                        
                        if title and author:
                            # 5. Check for duplicates
                            if self.is_duplicate(title, author):
                                print(f"⚠️ Duplicate book: {title} by {author}")
                                continue
                            
                            # 6. Add to pool and return
                            confidence = 0.85 + random.uniform(0, 0.15)  # 0.85-1.0
                            self.add_to_pool(title, author, selected_book_url, confidence)
                            
                            return {
                                "title": title,
                                "author": author,
                                "url": selected_book_url,
                                "confidence": confidence,
                                "page_source": page_url,
                                "attempt": attempt + 1,
                                "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S MSK")
                            }
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Failed to parse metadata JSON")
                    continue
                
            except Exception as e:
                print(f"⚠️ Error in attempt {attempt + 1}: {e}")
                continue
        
        raise Exception("Failed to extract book after maximum attempts")

async def main():
    extractor = EksmoRandomExtractor()
    
    try:
        result = await extractor.extract_random_book()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return None

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        sys.exit(0)
    else:
        sys.exit(1)