#!/usr/bin/env python3
"""
URL to EPUB: Extract book info from marketplace URLs and search Z-Library
Shows full JSON result with normalization and confidence scores
"""
import asyncio
import json
import sys
import os
import re
import time
import urllib.parse
from pathlib import Path

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from zlibrary import AsyncZlib, Extension
from claude_sdk_normalizer_fast import SimpleNormalizer

class URLToEPUB:
    def __init__(self):
        self.lib = AsyncZlib()
        
    def extract_from_url(self, url):
        """Extract book info from various marketplace URLs"""
        
        result = {
            "url": url,
            "marketplace": "unknown",
            "extracted": {},
            "method": "none"
        }
        
        # Ozon.ru extraction
        if "ozon.ru" in url:
            result["marketplace"] = "ozon"
            
            # Extract from URL slug
            match = re.search(r'/product/([^/?]+)', url)
            if match:
                slug = match.group(1)
                result["extracted"]["slug"] = slug
                
                # Parse slug parts
                parts = slug.lower().split('-')
                
                # Known patterns for Russian books
                title_mapping = {
                    "trevozhnye-lyudi": ("Тревожные люди", "Anxious People"),
                    "malenkiy-princ": ("Маленький принц", "The Little Prince"),
                    "vedmak": ("Ведьмак", "The Witcher"),
                }
                
                # Check for known patterns
                for pattern, (ru_title, en_title) in title_mapping.items():
                    if pattern in slug:
                        result["extracted"]["title_ru"] = ru_title
                        result["extracted"]["title_en"] = en_title
                        break
                
                # Extract author
                if "bakman" in parts or "backman" in parts:
                    result["extracted"]["author"] = "Fredrik Backman"
                elif "fredrik" in parts:
                    result["extracted"]["author"] = "Fredrik Backman"
                elif "sapkovski" in parts or "sapkowski" in parts:
                    result["extracted"]["author"] = "Andrzej Sapkowski"
                
                # Generic extraction
                if not result["extracted"].get("title_ru"):
                    # Use first 2-3 parts as title
                    title_parts = []
                    for part in parts[:3]:
                        if not part.isdigit() and len(part) > 2:
                            title_parts.append(part)
                    if title_parts:
                        result["extracted"]["title_generic"] = ' '.join(title_parts).title()
                
                result["method"] = "slug_parsing"
        
        # Amazon extraction
        elif "amazon.com" in url:
            result["marketplace"] = "amazon"
            
            # Extract from URL path
            match = re.search(r'/([^/]+)/dp/', url)
            if match:
                title_slug = urllib.parse.unquote(match.group(1))
                result["extracted"]["title_en"] = title_slug.replace('-', ' ').title()
                result["method"] = "url_path"
        
        # Goodreads extraction
        elif "goodreads.com" in url:
            result["marketplace"] = "goodreads"
            
            # Extract from book/show path
            match = re.search(r'/book/show/\d+-(.+)', url)
            if match:
                title_slug = urllib.parse.unquote(match.group(1))
                result["extracted"]["title_en"] = title_slug.replace('-', ' ').replace('_', ' ').title()
                result["method"] = "url_path"
        
        # Generic extraction
        else:
            # Try to extract from URL path
            parts = url.split('/')
            for part in parts:
                if len(part) > 15 and not part.startswith('http'):
                    decoded = urllib.parse.unquote(part)
                    result["extracted"]["title_generic"] = decoded.replace('-', ' ').replace('_', ' ')
                    result["method"] = "generic_path"
                    break
        
        return result
    
    async def search_book(self, url):
        """Complete URL to EPUB search with confidence scoring"""
        
        start_time = time.time()
        
        # Initialize result
        result = {
            "input_url": url,
            "extraction": {},
            "search_queries": [],
            "search_results": {},
            "confidence": {},
            "timing": {}
        }
        
        # Step 1: Extract from URL
        extract_start = time.time()
        extraction = self.extract_from_url(url)
        result["extraction"] = extraction
        result["timing"]["extraction"] = time.time() - extract_start
        
        # Step 2: Build search queries
        queries = []
        
        # Priority 1: Author + Title
        if extraction["extracted"].get("author"):
            author = extraction["extracted"]["author"]
            
            # Try Russian title first
            if extraction["extracted"].get("title_ru"):
                queries.append({
                    "query": f"{author} {extraction['extracted']['title_ru']}",
                    "type": "author_title_ru",
                    "priority": 1
                })
            
            # Then English title
            if extraction["extracted"].get("title_en"):
                queries.append({
                    "query": f"{author} {extraction['extracted']['title_en']}",
                    "type": "author_title_en",
                    "priority": 2
                })
        
        # Priority 2: Title only
        if extraction["extracted"].get("title_ru"):
            queries.append({
                "query": extraction["extracted"]["title_ru"],
                "type": "title_ru",
                "priority": 3
            })
        
        if extraction["extracted"].get("title_en"):
            queries.append({
                "query": extraction["extracted"]["title_en"],
                "type": "title_en",
                "priority": 4
            })
        
        # Priority 3: Generic title
        if extraction["extracted"].get("title_generic"):
            queries.append({
                "query": extraction["extracted"]["title_generic"],
                "type": "title_generic",
                "priority": 5
            })
        
        # Fallback: Raw slug
        if extraction["extracted"].get("slug"):
            queries.append({
                "query": extraction["extracted"]["slug"].replace('-', ' '),
                "type": "slug_raw",
                "priority": 6
            })
        
        result["search_queries"] = queries
        
        # Step 3: Try searches in priority order
        if not queries:
            result["error"] = "Could not extract searchable information from URL"
            return result
        
        try:
            # Login to Z-Library
            await self.lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
            
            # Try each query
            for query_info in queries[:3]:  # Try top 3 queries
                query = query_info["query"]
                
                # Normalize query
                normalized = SimpleNormalizer.normalize(query)
                search_query = normalized.get("normalized", query)
                
                print(f"🔍 Trying: {search_query} (type: {query_info['type']})")
                
                # Search
                search_start = time.time()
                try:
                    paginator = await self.lib.search(
                        q=search_query, 
                        count=3, 
                        extensions=[Extension.EPUB]
                    )
                    await paginator.init()
                    books = paginator.result
                    
                    if books:
                        # Found results!
                        result["search_results"]["found"] = True
                        result["search_results"]["query_used"] = search_query
                        result["search_results"]["query_type"] = query_info["type"]
                        result["search_results"]["count"] = len(books)
                        result["search_results"]["books"] = []
                        
                        # Process results
                        for book in books[:3]:
                            try:
                                details = await asyncio.wait_for(book.fetch(), timeout=5.0)
                                
                                # Extract clean authors
                                authors = []
                                for a in details.get('authors', [])[:3]:
                                    if isinstance(a, dict) and a.get('author'):
                                        author_name = a['author']
                                        if not any(skip in author_name.lower() 
                                                  for skip in ['@', 'support', 'comment']):
                                            authors.append(author_name)
                                
                                book_info = {
                                    "title": details.get('name', 'Unknown'),
                                    "authors": authors,
                                    "year": details.get('year', ''),
                                    "extension": details.get('extension', ''),
                                    "size": details.get('size', ''),
                                    "rating": details.get('rating', ''),
                                    "download_url": details.get('download_url', '')
                                }
                                
                                # Calculate confidence
                                confidence = self._calculate_confidence(
                                    extraction["extracted"],
                                    book_info
                                )
                                book_info["confidence"] = confidence
                                
                                result["search_results"]["books"].append(book_info)
                                
                            except Exception as e:
                                pass
                        
                        # Calculate overall confidence
                        if result["search_results"]["books"]:
                            confidences = [b["confidence"] for b in result["search_results"]["books"]]
                            result["confidence"]["best_match"] = max(confidences)
                            result["confidence"]["average"] = sum(confidences) / len(confidences)
                            
                            # Quality assessment
                            best = result["confidence"]["best_match"]
                            if best >= 0.8:
                                result["confidence"]["quality"] = "excellent"
                                result["confidence"]["recommendation"] = "✅ High confidence match"
                            elif best >= 0.6:
                                result["confidence"]["quality"] = "good"
                                result["confidence"]["recommendation"] = "👍 Good match found"
                            elif best >= 0.4:
                                result["confidence"]["quality"] = "fair"
                                result["confidence"]["recommendation"] = "🤔 Moderate confidence"
                            else:
                                result["confidence"]["quality"] = "poor"
                                result["confidence"]["recommendation"] = "⚠️ Low confidence match"
                        
                        result["timing"]["search"] = time.time() - search_start
                        break  # Found results, stop trying
                        
                except Exception as e:
                    # This query failed, try next
                    continue
            
            # No results found with any query
            if not result["search_results"].get("found"):
                result["search_results"]["found"] = False
                result["search_results"]["message"] = "No books found with any extracted query"
                result["confidence"]["quality"] = "no_match"
                
        except Exception as e:
            result["error"] = str(e)[:200]
        
        result["timing"]["total"] = time.time() - start_time
        
        return result
    
    def _calculate_confidence(self, extracted, book_info):
        """Calculate match confidence between extracted and found book"""
        
        score = 0.0
        factors = 0
        
        # Check title match
        book_title_lower = book_info["title"].lower()
        
        if extracted.get("title_ru"):
            if extracted["title_ru"].lower() in book_title_lower:
                score += 0.4
            factors += 0.4
            
        if extracted.get("title_en"):
            if extracted["title_en"].lower() in book_title_lower:
                score += 0.4
            factors += 0.4
        
        # Check author match
        if extracted.get("author") and book_info.get("authors"):
            author_lower = extracted["author"].lower()
            for book_author in book_info["authors"]:
                if author_lower in book_author.lower() or book_author.lower() in author_lower:
                    score += 0.2
                    break
            factors += 0.2
        
        # Normalize to 0-1
        if factors > 0:
            return score / factors
        else:
            # Basic word matching
            if extracted.get("title_generic"):
                words = set(extracted["title_generic"].lower().split())
                title_words = set(book_title_lower.split())
                if words and title_words:
                    return len(words & title_words) / len(words)
        
        return 0.0


async def main():
    """Test URL to EPUB extraction"""
    
    # Test URLs
    test_urls = [
        "https://www.ozon.ru/product/trevozhnye-lyudi-bakman-fredrik-202912464/",
        "https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882",
        "https://www.goodreads.com/book/show/3735293-clean-code",
    ]
    
    converter = URLToEPUB()
    
    print("=" * 80)
    print("📚 URL TO EPUB EXTRACTION AND SEARCH")
    print("=" * 80)
    
    for url in test_urls[:1]:  # Test Ozon URL
        print(f"\n{'=' * 80}")
        print(f"🔗 URL: {url[:60]}...")
        print("-" * 80)
        
        result = await converter.search_book(url)
        
        # Pretty print results
        print("\n📋 EXTRACTION:")
        print(f"  Marketplace: {result['extraction']['marketplace']}")
        print(f"  Method: {result['extraction']['method']}")
        
        if result['extraction']['extracted']:
            print("  Extracted:")
            for key, value in result['extraction']['extracted'].items():
                print(f"    {key}: {value}")
        
        print(f"\n🔍 SEARCH QUERIES ({len(result['search_queries'])} generated):")
        for q in result['search_queries'][:3]:
            print(f"  {q['priority']}. {q['query'][:50]}... ({q['type']})")
        
        if result.get('search_results', {}).get('found'):
            print(f"\n✅ RESULTS FOUND:")
            print(f"  Query used: {result['search_results']['query_used']}")
            print(f"  Query type: {result['search_results']['query_type']}")
            print(f"  Books found: {result['search_results']['count']}")
            
            print(f"\n📚 TOP MATCHES:")
            for i, book in enumerate(result['search_results']['books'][:3], 1):
                print(f"\n  {i}. {book['title'][:60]}...")
                if book['authors']:
                    print(f"     Authors: {', '.join(book['authors'][:2])}")
                print(f"     Year: {book['year']}, Format: {book['extension']}, Size: {book['size']}")
                print(f"     Confidence: {book['confidence']:.1%}")
                if book.get('download_url'):
                    print(f"     ✅ Download available")
            
            conf = result.get('confidence', {})
            print(f"\n📊 CONFIDENCE:")
            print(f"  Best match: {conf.get('best_match', 0):.1%}")
            print(f"  Quality: {conf.get('quality', 'unknown')}")
            print(f"  {conf.get('recommendation', '')}")
        else:
            print(f"\n❌ NO RESULTS FOUND")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        
        print(f"\n⏱️ TIMING:")
        print(f"  Extraction: {result['timing'].get('extraction', 0):.3f}s")
        if result['timing'].get('search'):
            print(f"  Search: {result['timing']['search']:.2f}s")
        print(f"  Total: {result['timing']['total']:.2f}s")
        
        # Full JSON output
        print(f"\n📄 FULL JSON RESULT:")
        print("-" * 40)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Load environment
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("❌ Error: Set ZLOGIN and ZPASSW in .env file")
        sys.exit(1)
    
    asyncio.run(main())