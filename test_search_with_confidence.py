#!/usr/bin/env python3
"""
Test Z-Library search with different input types showing normalization and confidence
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from zlibrary import AsyncZlib, Extension
from pipeline.cognitive_validator import CognitiveValidator
from claude_sdk_normalizer import ClaudeSDKNormalizer

class SearchWithConfidence:
    def __init__(self):
        self.lib = AsyncZlib()
        self.validator = CognitiveValidator()
        self.normalizer = ClaudeSDKNormalizer()
        
    async def search_with_normalization(self, query, query_type="text"):
        """Search with normalization and confidence scoring"""
        
        result = {
            "original_query": query,
            "query_type": query_type,
            "normalization": {},
            "search_results": {},
            "confidence": {}
        }
        
        # Step 1: Normalize the query
        print(f"\n🔍 Processing {query_type} query: {query}")
        
        if query_type == "url":
            # Extract from URL
            import re
            # Simple URL extraction (can be enhanced)
            if "amazon.com" in query or "goodreads.com" in query:
                # Extract title from URL
                parts = query.split('/')
                for part in parts:
                    if len(part) > 10 and not part.startswith('http'):
                        # Clean up URL encoding
                        import urllib.parse
                        decoded = urllib.parse.unquote(part)
                        # Remove dashes and clean
                        normalized = decoded.replace('-', ' ').replace('_', ' ')
                        result["normalization"]["extracted"] = normalized
                        query = normalized
                        break
        
        # Try Claude normalization
        try:
            norm_result = self.normalizer.normalize_book_title(query)
            if norm_result.get("success"):
                result["normalization"]["claude_normalized"] = norm_result.get("normalized_title", query)
                result["normalization"]["language_detected"] = norm_result.get("language", "unknown")
                result["normalization"]["confidence"] = norm_result.get("confidence", 0)
                
                # Use normalized query if available
                if norm_result.get("normalized_title"):
                    query = norm_result["normalized_title"]
            else:
                result["normalization"]["claude_normalized"] = query
                result["normalization"]["error"] = norm_result.get("error", "Normalization failed")
        except Exception as e:
            result["normalization"]["claude_normalized"] = query
            result["normalization"]["error"] = str(e)
        
        result["normalized_query"] = query
        
        # Step 2: Login and search
        try:
            await self.lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
            
            # Search with normalized query
            paginator = await self.lib.search(q=query, count=3, extensions=[Extension.EPUB])
            await paginator.init()
            books = paginator.result
            
            if books:
                result["search_results"]["found"] = True
                result["search_results"]["count"] = len(books)
                result["search_results"]["books"] = []
                
                for book in books[:3]:  # Top 3 results
                    try:
                        details = await book.fetch()
                        book_info = {
                            "title": details.get('name', 'Unknown'),
                            "authors": [a.get('author') for a in details.get('authors', []) 
                                       if isinstance(a, dict) and a.get('author')][:3],
                            "year": details.get('year', ''),
                            "extension": details.get('extension', ''),
                            "size": details.get('size', ''),
                            "rating": details.get('rating', '')
                        }
                        
                        # Calculate confidence for this match
                        confidence = self.calculate_confidence(
                            result["original_query"],
                            book_info["title"],
                            query
                        )
                        book_info["match_confidence"] = confidence
                        
                        result["search_results"]["books"].append(book_info)
                    except:
                        pass
                
                # Overall confidence calculation
                if result["search_results"]["books"]:
                    best_match = max(result["search_results"]["books"], 
                                   key=lambda x: x.get("match_confidence", 0))
                    result["confidence"]["best_match_score"] = best_match["match_confidence"]
                    result["confidence"]["best_match_title"] = best_match["title"]
                    
                    # Determine quality
                    score = best_match["match_confidence"]
                    if score >= 0.8:
                        result["confidence"]["quality"] = "excellent"
                    elif score >= 0.6:
                        result["confidence"]["quality"] = "good"
                    elif score >= 0.4:
                        result["confidence"]["quality"] = "fair"
                    else:
                        result["confidence"]["quality"] = "poor"
                    
                    result["confidence"]["recommendation"] = (
                        "High confidence match" if score >= 0.7 else
                        "Moderate confidence - review results" if score >= 0.5 else
                        "Low confidence - may not be what you're looking for"
                    )
            else:
                result["search_results"]["found"] = False
                result["search_results"]["message"] = "No books found"
                result["confidence"]["quality"] = "no_match"
                
        except Exception as e:
            result["search_results"]["error"] = str(e)
            result["confidence"]["quality"] = "error"
        
        return result
    
    def calculate_confidence(self, original_query, book_title, normalized_query):
        """Calculate match confidence score"""
        # Simple word-based matching (can be enhanced)
        original_words = set(w.lower() for w in original_query.split() if len(w) > 2)
        normalized_words = set(w.lower() for w in normalized_query.split() if len(w) > 2)
        title_words = set(w.lower() for w in book_title.split() if len(w) > 2)
        
        # Check how many query words appear in title
        original_match = len(original_words & title_words) / max(len(original_words), 1)
        normalized_match = len(normalized_words & title_words) / max(len(normalized_words), 1)
        
        # Take the better score
        return max(original_match, normalized_match)

async def main():
    """Test different input types"""
    searcher = SearchWithConfidence()
    
    # Test cases
    test_cases = [
        # Text searches
        ("Clean Code Robert Martin", "text"),
        ("harry poter filosofer stone", "text"),  # Misspelled
        ("1984 orwell", "text"),
        
        # URL searches  
        ("https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882", "url"),
        ("https://www.goodreads.com/book/show/3735293-clean-code", "url"),
        
        # Mixed/fuzzy
        ("teh grate gatsby", "text"),  # Very misspelled
        ("python programing for beginers", "text"),  # Common misspelling
    ]
    
    print("=" * 80)
    print("Z-LIBRARY SEARCH WITH NORMALIZATION AND CONFIDENCE")
    print("=" * 80)
    
    for query, query_type in test_cases[:3]:  # Test first 3 for demo
        result = await searcher.search_with_normalization(query, query_type)
        
        # Pretty print JSON result
        print("\n" + "=" * 80)
        print(f"Query Type: {query_type}")
        print(f"Original: {result['original_query']}")
        print(f"Normalized: {result.get('normalized_query', 'N/A')}")
        print("-" * 40)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("=" * 80)
        
        # Brief summary
        if result.get("confidence"):
            quality = result["confidence"].get("quality", "unknown")
            score = result["confidence"].get("best_match_score", 0)
            print(f"\n📊 Confidence: {score:.1%} ({quality})")
            print(f"💡 {result['confidence'].get('recommendation', 'No recommendation')}")
        
        await asyncio.sleep(1)  # Rate limiting

if __name__ == "__main__":
    # Check credentials
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("❌ Error: Set ZLOGIN and ZPASSW environment variables")
        sys.exit(1)
    
    asyncio.run(main())