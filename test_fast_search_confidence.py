#!/usr/bin/env python3
"""
Fast Z-Library search with normalization and confidence (no timeouts!)
"""
import asyncio
import json
import sys
import os
import time
import re
from pathlib import Path

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from zlibrary import AsyncZlib, Extension
from claude_sdk_normalizer_fast import ClaudeSDKNormalizerFast, SimpleNormalizer

class FastSearchWithConfidence:
    def __init__(self, use_cognitive=True):
        self.lib = AsyncZlib()
        self.normalizer = ClaudeSDKNormalizerFast(use_cognitive=use_cognitive, timeout=3)
        
    async def search_with_confidence(self, query, query_type="text"):
        """Fast search with normalization and confidence scoring"""
        
        start_time = time.time()
        
        result = {
            "original_query": query,
            "query_type": query_type,
            "normalization": {},
            "search_results": {},
            "confidence": {},
            "timing": {}
        }
        
        # Step 1: Handle URL extraction
        if query_type == "url":
            query = self._extract_from_url(query)
            result["normalization"]["url_extracted"] = query
        
        # Step 2: Fast normalization
        norm_start = time.time()
        norm_result = self.normalizer.normalize_book_title(query)
        result["normalization"]["time"] = time.time() - norm_start
        
        if norm_result.get("success"):
            result["normalization"]["normalized"] = norm_result.get("normalized_title", query)
            result["normalization"]["method"] = norm_result.get("method", "unknown")
            result["normalization"]["fixes"] = norm_result.get("problems_found", [])
            result["normalization"]["confidence"] = norm_result.get("confidence", 0)
            
            # Use normalized query
            search_query = norm_result.get("search_string", norm_result.get("normalized_title", query))
        else:
            # Fallback to simple normalization
            simple_result = SimpleNormalizer.normalize(query)
            result["normalization"]["normalized"] = simple_result.get("normalized", query)
            result["normalization"]["method"] = "simple_fallback"
            result["normalization"]["confidence"] = simple_result.get("confidence", 0.5)
            search_query = simple_result.get("normalized", query)
        
        result["search_query"] = search_query
        
        # Step 3: Search Z-Library
        search_start = time.time()
        try:
            await self.lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
            
            # Search with normalized query
            paginator = await self.lib.search(q=search_query, count=3, extensions=[Extension.EPUB])
            await paginator.init()
            books = paginator.result
            
            result["search_results"]["time"] = time.time() - search_start
            
            if books:
                result["search_results"]["found"] = True
                result["search_results"]["count"] = len(books)
                result["search_results"]["books"] = []
                
                for i, book in enumerate(books[:3]):
                    try:
                        # Fast fetch without timeout
                        details = await asyncio.wait_for(book.fetch(), timeout=5.0)
                        
                        book_info = {
                            "title": details.get('name', 'Unknown'),
                            "authors": self._extract_authors(details.get('authors', [])),
                            "year": details.get('year', ''),
                            "extension": details.get('extension', ''),
                            "size": details.get('size', ''),
                            "rating": details.get('rating', ''),
                            "match_confidence": self._calculate_confidence(
                                query, 
                                details.get('name', ''),
                                search_query
                            )
                        }
                        
                        result["search_results"]["books"].append(book_info)
                    except asyncio.TimeoutError:
                        # Skip books that timeout
                        pass
                    except Exception as e:
                        # Skip failed books
                        pass
                
                # Calculate overall confidence
                if result["search_results"]["books"]:
                    confidences = [b["match_confidence"] for b in result["search_results"]["books"]]
                    best_confidence = max(confidences)
                    avg_confidence = sum(confidences) / len(confidences)
                    
                    result["confidence"]["best_match"] = best_confidence
                    result["confidence"]["average"] = avg_confidence
                    result["confidence"]["quality"] = self._get_quality_label(best_confidence)
                    result["confidence"]["recommendation"] = self._get_recommendation(best_confidence)
                    
                    # Find best match
                    best_book = max(result["search_results"]["books"], 
                                  key=lambda x: x["match_confidence"])
                    result["confidence"]["best_book"] = best_book["title"]
            else:
                result["search_results"]["found"] = False
                result["confidence"]["quality"] = "no_match"
                result["confidence"]["recommendation"] = "No books found - try different search terms"
                
        except Exception as e:
            result["search_results"]["error"] = str(e)[:100]  # Truncate long errors
            result["confidence"]["quality"] = "error"
        
        result["timing"]["total"] = time.time() - start_time
        
        return result
    
    def _extract_from_url(self, url):
        """Extract book info from URL"""
        import urllib.parse
        
        # Amazon pattern
        if "amazon.com" in url:
            match = re.search(r'/([^/]+)/dp/', url)
            if match:
                title = urllib.parse.unquote(match.group(1))
                return title.replace('-', ' ')
        
        # Goodreads pattern  
        if "goodreads.com" in url:
            match = re.search(r'/book/show/[0-9]+-(.+)', url)
            if match:
                title = urllib.parse.unquote(match.group(1))
                return title.replace('-', ' ').replace('_', ' ')
        
        # Generic extraction
        parts = url.split('/')
        for part in parts:
            if len(part) > 15 and not part.startswith('http'):
                return urllib.parse.unquote(part).replace('-', ' ')
        
        return url
    
    def _extract_authors(self, authors_data):
        """Extract clean author names"""
        authors = []
        for item in authors_data[:3]:  # Max 3 authors
            if isinstance(item, dict) and item.get('author'):
                author = item['author']
                # Skip non-author entries
                if not any(skip in author.lower() for skip in ['comments', '@', 'support', '&']):
                    authors.append(author)
        return authors
    
    def _calculate_confidence(self, original, book_title, normalized):
        """Fast confidence calculation"""
        # Clean and split into words
        orig_words = set(w.lower() for w in re.findall(r'\w+', original) if len(w) > 2)
        norm_words = set(w.lower() for w in re.findall(r'\w+', normalized) if len(w) > 2)
        title_words = set(w.lower() for w in re.findall(r'\w+', book_title) if len(w) > 2)
        
        if not orig_words:
            return 0.5
        
        # Calculate overlaps
        orig_match = len(orig_words & title_words) / len(orig_words)
        norm_match = len(norm_words & title_words) / len(norm_words) if norm_words else 0
        
        return max(orig_match, norm_match)
    
    def _get_quality_label(self, confidence):
        """Get quality label from confidence score"""
        if confidence >= 0.8:
            return "excellent"
        elif confidence >= 0.6:
            return "good"
        elif confidence >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _get_recommendation(self, confidence):
        """Get recommendation based on confidence"""
        if confidence >= 0.8:
            return "✅ High confidence - this is likely what you're looking for"
        elif confidence >= 0.6:
            return "👍 Good match - probably correct"
        elif confidence >= 0.4:
            return "🤔 Moderate confidence - please verify"
        else:
            return "⚠️ Low confidence - may not be the right book"


async def main():
    """Test different input types with fast processing"""
    
    # Initialize searchers
    cognitive_searcher = FastSearchWithConfidence(use_cognitive=True)
    simple_searcher = FastSearchWithConfidence(use_cognitive=False)
    
    # Test cases
    test_cases = [
        ("hary poter filosofer stone", "text", "Misspelled popular book"),
        ("Clean Code Robert Martin", "text", "Technical book"),
        ("1984 orwell", "text", "Classic with author"),
        ("https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882", "url", "Amazon URL"),
        ("teh grate gatsby", "text", "Very misspelled classic"),
        ("python programing for beginers", "text", "Common misspellings"),
    ]
    
    print("=" * 80)
    print("🚀 FAST Z-LIBRARY SEARCH WITH CONFIDENCE")
    print("=" * 80)
    
    for query, query_type, description in test_cases[:4]:  # Test first 4
        print(f"\n{'=' * 80}")
        print(f"📚 {description}")
        print(f"Input: {query}")
        print(f"Type: {query_type}")
        print("-" * 80)
        
        # Test with cognitive layer (if available)
        print("\n🧠 WITH COGNITIVE LAYER:")
        try:
            result = await cognitive_searcher.search_with_confidence(query, query_type)
            
            print(f"  Normalized: {result.get('search_query', 'N/A')}")
            print(f"  Method: {result['normalization'].get('method', 'unknown')}")
            print(f"  Norm Time: {result['normalization'].get('time', 0):.2f}s")
            
            if result["search_results"].get("found"):
                print(f"  Books Found: {result['search_results']['count']}")
                print(f"  Search Time: {result['search_results'].get('time', 0):.2f}s")
                
                conf = result.get("confidence", {})
                print(f"\n  📊 Confidence: {conf.get('best_match', 0):.1%} ({conf.get('quality', 'unknown')})")
                print(f"  Best Match: {conf.get('best_book', 'N/A')}")
                print(f"  {conf.get('recommendation', '')}")
                
                # Show top results
                if result["search_results"].get("books"):
                    print("\n  Top Results:")
                    for i, book in enumerate(result["search_results"]["books"][:2], 1):
                        print(f"    {i}. {book['title'][:60]}...")
                        if book.get('authors'):
                            print(f"       By: {', '.join(book['authors'][:2])}")
                        print(f"       Confidence: {book['match_confidence']:.1%}")
            else:
                print(f"  ❌ No books found")
            
            print(f"\n  ⏱️ Total Time: {result['timing'].get('total', 0):.2f}s")
            
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
        
        # Brief pause
        await asyncio.sleep(0.5)
    
    # Show speed comparison
    print(f"\n{'=' * 80}")
    print("⚡ SPEED TEST: Simple Normalizer (no Claude)")
    print("-" * 80)
    
    test = "hary poter and teh filosofer stone"
    print(f"Input: {test}")
    
    start = time.time()
    simple_result = SimpleNormalizer.normalize(test)
    elapsed = time.time() - start
    
    print(f"Output: {simple_result.get('normalized', test)}")
    print(f"Time: {elapsed:.6f}s (instant!)")
    print(f"Fixes: {', '.join(simple_result.get('fixes', []))}")

if __name__ == "__main__":
    # Load environment
    if not os.getenv('ZLOGIN'):
        # Try to load from .env file
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    # Check credentials
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("❌ Error: Set ZLOGIN and ZPASSW environment variables")
        print("   Or create a .env file with:")
        print("   ZLOGIN=your_email")
        print("   ZPASSW=your_password")
        sys.exit(1)
    
    asyncio.run(main())