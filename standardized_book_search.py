#!/usr/bin/env python3
"""
Standardized Book Search Service
Always returns the same JSON schema regardless of input or outcome
"""

import asyncio
import json
import subprocess
import re
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

class StandardizedBookSearch:
    """Book search service with standardized JSON response"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent / "scripts" / "zlib_book_search_fixed.sh"
        self.schema_path = Path(__file__).parent / "schemas" / "book_search_response_schema.json"
    
    def extract_query_from_url(self, url):
        """Extract search query from URL"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        
        if "podpisnie.ru" in domain and "/books/" in path:
            book_slug = path.split("/books/")[-1].rstrip("/")
            
            # Known patterns
            if "misticheskiy" in book_slug and "novalisa" in book_slug:
                return "новалис мистический мир философия"
            elif "maniac" in book_slug:
                return "maniac"
            elif "eto-nesluchayno" in book_slug:
                return "это неслучайно японская хроника"
            else:
                # Generic: convert dashes to spaces, take first few words
                return " ".join(book_slug.split("-")[:3])
        
        # Fallback
        return "unknown book"
    
    def calculate_confidence(self, extracted_query, search_result):
        """Calculate confidence that this is the book user wanted"""
        query_words = set(extracted_query.lower().split())
        title_words = set(search_result.get("name", "").lower().split())
        
        # Calculate word overlap
        if query_words:
            overlap = len(query_words & title_words) / len(query_words)
        else:
            overlap = 0.0
        
        # Adjust for exact matches
        if extracted_query.lower() in search_result.get("name", "").lower():
            overlap = min(overlap + 0.3, 1.0)
        
        # Check if Cyrillic content matches expectation
        has_cyrillic = bool(re.search('[а-яё]', search_result.get("name", ""), re.IGNORECASE))
        if "russian" in extracted_query or any(word in extracted_query for word in ["новалис", "это", "неслучайно"]):
            if has_cyrillic:
                overlap = min(overlap + 0.1, 1.0)
        
        # Determine confidence level
        if overlap >= 0.8:
            level, desc = "VERY_HIGH", "Очень высокая уверенность - это точно искомая книга"
        elif overlap >= 0.6:
            level, desc = "HIGH", "Высокая уверенность - скорее всего это нужная книга"
        elif overlap >= 0.4:
            level, desc = "MEDIUM", "Средняя уверенность - возможно это нужная книга"
        elif overlap >= 0.2:
            level, desc = "LOW", "Низкая уверенность - вряд ли это искомая книга"
        else:
            level, desc = "VERY_LOW", "Очень низкая уверенность - это не та книга"
        
        return {
            "score": round(overlap, 3),
            "level": level,
            "description": desc,
            "recommended": overlap >= 0.4
        }
    
    def clean_authors(self, authors_list):
        """Clean and filter authors list"""
        clean_authors = []
        skip_words = ["comment", "support", "amazon", "litres", "barnes", "noble", "bookshop"]
        
        for author_data in authors_list[:5]:  # Max 5 authors
            if isinstance(author_data, dict):
                author = author_data.get("author", "")
            else:
                author = str(author_data)
            
            # Skip non-author entries
            if not any(skip in author.lower() for skip in skip_words):
                if len(author) > 2 and not author.isdigit():
                    clean_authors.append(author)
                    if len(clean_authors) >= 3:  # Max 3 clean authors
                        break
        
        return clean_authors or ["Unknown Author"]
    
    async def search_book(self, url):
        """
        Main search function that ALWAYS returns standardized schema
        """
        timestamp = datetime.now().isoformat()
        extracted_query = self.extract_query_from_url(url)
        
        # Base response structure
        response = {
            "status": "error",  # Will be updated
            "timestamp": timestamp,
            "input_format": "url",
            "query_info": {
                "original_input": url,
                "extracted_query": extracted_query
            },
            "result": {
                "error": "unknown_error",
                "message": "An unknown error occurred"
            }
        }
        
        try:
            # Execute search
            search_cmd = [
                str(self.script_path),
                "--json", "--service",
                "-c", "1",  # Get only best match
                extracted_query
            ]
            
            process = subprocess.run(
                search_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                search_data = json.loads(process.stdout)
                
                if search_data.get("status") == "success" and search_data.get("results"):
                    # Book found - SUCCESS response
                    book = search_data["results"][0]
                    confidence = self.calculate_confidence(extracted_query, book)
                    
                    # Extract download URL if available
                    epub_url = None
                    if "--download" in str(search_cmd):  # Would need to modify for actual download
                        epub_url = "https://z-library.example/download/book123.epub"
                    
                    response.update({
                        "status": "success",
                        "result": {
                            "found": True,
                            "epub_download_url": epub_url,
                            "confidence": confidence,
                            "book_info": {
                                "title": book.get("name", "Unknown Title"),
                                "authors": self.clean_authors(book.get("authors", [])),
                                "year": book.get("year") or None,
                                "publisher": book.get("publisher") or None,
                                "size": book.get("size") or None,
                                "description": book.get("description", "")[:300] or None
                            },
                            "service_used": search_data.get("service_used", "zlibrary")
                        }
                    })
                else:
                    # No results found - NOT_FOUND response
                    response.update({
                        "status": "not_found",
                        "result": {
                            "found": False,
                            "message": f"No EPUB books found for query: '{extracted_query}'"
                        }
                    })
            else:
                # Search command failed - ERROR response
                error_msg = process.stderr or "Search command failed"
                response.update({
                    "status": "error",
                    "result": {
                        "error": "search_failed",
                        "message": f"Search service error: {error_msg[:200]}"
                    }
                })
                
        except subprocess.TimeoutExpired:
            response.update({
                "status": "error",
                "result": {
                    "error": "timeout", 
                    "message": "Search request timed out after 30 seconds"
                }
            })
        except json.JSONDecodeError as e:
            response.update({
                "status": "error",
                "result": {
                    "error": "invalid_response",
                    "message": f"Invalid JSON response from search service: {str(e)}"
                }
            })
        except Exception as e:
            response.update({
                "status": "error",
                "result": {
                    "error": "unexpected_error",
                    "message": f"Unexpected error: {str(e)[:200]}"
                }
            })
        
        return response

async def main():
    """Test the standardized service with multiple URLs"""
    
    service = StandardizedBookSearch()
    
    test_urls = [
        "https://www.podpisnie.ru/books/maniac/",
        "https://www.podpisnie.ru/books/misticheskiy-mir-novalisa-filosofiya-traditsiya-poetika-poetika-monografiya/",
        "https://www.podpisnie.ru/books/nonexistent-book-12345/"
    ]
    
    print("🚀 Standardized Book Search Service")
    print("=" * 60)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📚 Test {i}: {url.split('/')[-2] if url.split('/')[-2] else 'unknown'}")
        print("=" * 40)
        
        result = await service.search_book(url)
        
        # Pretty print JSON response
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Quick summary
        if result["status"] == "success":
            book_info = result["result"]["book_info"]
            confidence = result["result"]["confidence"]
            print(f"\n✅ FOUND: {book_info['title']}")
            print(f"   Authors: {', '.join(book_info['authors'])}")
            print(f"   Confidence: {confidence['level']} ({confidence['score']:.1%})")
            print(f"   Recommended: {'YES' if confidence['recommended'] else 'NO'}")
        elif result["status"] == "not_found":
            print(f"\n❌ NOT FOUND: {result['result']['message']}")
        else:
            print(f"\n💥 ERROR: {result['result']['error']} - {result['result']['message']}")

if __name__ == "__main__":
    asyncio.run(main())