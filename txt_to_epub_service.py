#!/usr/bin/env python3
"""
Text to EPUB Service
Processes text input to find EPUB books with confidence scoring
"""

import asyncio
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

class TextToEPUBService:
    """Service to find EPUB books from text input"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent / "scripts" / "zlib_book_search_fixed.sh"
    
    def extract_query_from_text(self, text):
        """Extract search query from raw text input"""
        text = text.strip()
        
        # Clean and normalize text
        text = re.sub(r'[^\w\sа-яё\-]', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)
        
        # Limit to reasonable length
        words = text.split()[:10]  # Max 10 words
        
        return ' '.join(words) if words else "unknown"
    
    def calculate_confidence(self, original_text, search_result):
        """Calculate confidence that this book matches the text input"""
        original_words = set(re.findall(r'\w+', original_text.lower()))
        title_words = set(re.findall(r'\w+', search_result.get("name", "").lower()))
        
        # Calculate word overlap
        if original_words:
            overlap = len(original_words & title_words) / len(original_words)
        else:
            overlap = 0.0
        
        # Boost for exact phrase matches
        if len(original_text) > 3 and original_text.lower() in search_result.get("name", "").lower():
            overlap = min(overlap + 0.4, 1.0)
        
        # Check for author names in text
        authors = search_result.get("authors", [])
        for author_data in authors:
            if isinstance(author_data, dict):
                author = author_data.get("author", "")
            else:
                author = str(author_data)
            
            if len(author) > 3 and author.lower() in original_text.lower():
                overlap = min(overlap + 0.3, 1.0)
                break
        
        # Language consistency bonus
        has_cyrillic = bool(re.search('[а-яё]', search_result.get("name", ""), re.IGNORECASE))
        text_has_cyrillic = bool(re.search('[а-яё]', original_text, re.IGNORECASE))
        
        if has_cyrillic == text_has_cyrillic:
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
        
        for author_data in authors_list[:5]:
            if isinstance(author_data, dict):
                author = author_data.get("author", "")
            else:
                author = str(author_data)
            
            if not any(skip in author.lower() for skip in skip_words):
                if len(author) > 2 and not author.isdigit():
                    clean_authors.append(author)
                    if len(clean_authors) >= 3:
                        break
        
        return clean_authors or ["Unknown Author"]
    
    async def search_book_from_text(self, text_input):
        """
        Main function to search book from text input
        Always returns standardized JSON schema
        """
        timestamp = datetime.now().isoformat()
        extracted_query = self.extract_query_from_text(text_input)
        
        # Base response structure
        response = {
            "status": "error",
            "timestamp": timestamp,
            "input_format": "txt",
            "query_info": {
                "original_input": text_input,
                "extracted_query": extracted_query
            },
            "result": {
                "error": "unknown_error",
                "message": "An unknown error occurred"
            }
        }
        
        try:
            # Execute search using zlib script
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
                    confidence = self.calculate_confidence(text_input, book)
                    
                    # For now, epub_download_url is null (would need actual download implementation)
                    epub_url = None
                    
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
                    # No results found
                    response.update({
                        "status": "not_found",
                        "result": {
                            "found": False,
                            "message": f"No EPUB books found for text: '{extracted_query}'"
                        }
                    })
            else:
                # Search command failed
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
    """Test the TXT to EPUB service"""
    
    service = TextToEPUBService()
    
    test_texts = [
        "Maniac Benjamin Labatut",
        "Новалис мистический мир философия поэтика",
        "Harry Potter philosopher stone",
        "Гарри Поттер философский камень",
        "Clean Code Robert Martin programming",
        "хьбиуфвбиу некая несуществующая книга 12345"
    ]
    
    print("🚀 Text to EPUB Service Testing")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: '{text}'")
        print("=" * 40)
        
        result = await service.search_book_from_text(text)
        
        # Pretty print JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Summary
        if result["status"] == "success":
            book_info = result["result"]["book_info"]
            confidence = result["result"]["confidence"]
            print(f"\n✅ FOUND: {book_info['title'][:50]}")
            print(f"   Authors: {', '.join(book_info['authors'][:2])}")
            print(f"   Confidence: {confidence['level']} ({confidence['score']:.1%})")
            print(f"   Recommended: {'YES' if confidence['recommended'] else 'NO'}")
        elif result["status"] == "not_found":
            print(f"\n❌ NOT FOUND: {result['result']['message']}")
        else:
            print(f"\n💥 ERROR: {result['result']['error']}")

if __name__ == "__main__":
    asyncio.run(main())