#!/usr/bin/env python3
"""
Search for "Полночная библиотека" (The Midnight Library) by Matt Haig
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from zlibrary import AsyncZlib, Extension

async def search_midnight_library():
    """Search for The Midnight Library book"""
    
    # Book information from URL
    url = "https://www.ozon.ru/product/polnochnaya-biblioteka-heyg-mett-215999534/"
    
    # Extract from URL slug
    book_info = {
        "title_ru": "Полночная библиотека",
        "title_en": "The Midnight Library",
        "author": "Matt Haig",
        "author_ru": "Мэтт Хейг"
    }
    
    print("=" * 80)
    print("📚 SEARCHING FOR BOOK FROM OZON URL")
    print("=" * 80)
    print(f"🔗 URL: {url}")
    print(f"📖 Title (RU): {book_info['title_ru']}")
    print(f"📖 Title (EN): {book_info['title_en']}")
    print(f"✍️ Author: {book_info['author']}")
    print("=" * 80)
    
    result = {
        "input": {
            "url": url,
            "timestamp": datetime.now().isoformat()
        },
        "extraction": {
            "success": True,
            "data": book_info,
            "marketplace": "ozon"
        },
        "search_results": [],
        "status": "searching"
    }
    
    try:
        # Initialize Z-Library
        lib = AsyncZlib()
        
        # Load credentials
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
            print("❌ Error: Set ZLOGIN and ZPASSW in .env file")
            result["status"] = "error"
            result["error"] = "Missing credentials"
            return result
        
        print("\n🔐 Logging in to Z-Library...")
        await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
        
        # Try different search queries
        search_queries = [
            f"{book_info['author']} {book_info['title_en']}",
            book_info['title_en'],
            f"{book_info['author_ru']} {book_info['title_ru']}",
            book_info['title_ru']
        ]
        
        books_found = []
        
        for query in search_queries:
            print(f"\n🔍 Searching: {query}")
            
            try:
                paginator = await lib.search(
                    q=query,
                    count=5,
                    extensions=[Extension.EPUB]
                )
                await paginator.init()
                
                if paginator.result:
                    print(f"✅ Found {len(paginator.result)} results")
                    
                    for book in paginator.result[:3]:
                        try:
                            # Fetch detailed info
                            details = await book.fetch()
                            
                            # Extract clean authors
                            authors = []
                            for a in details.get('authors', [])[:3]:
                                if isinstance(a, dict) and a.get('author'):
                                    author_name = a['author']
                                    if not any(skip in author_name.lower() for skip in ['@', 'comment', 'support']):
                                        authors.append(author_name)
                            
                            book_data = {
                                "title": details.get('name', 'Unknown'),
                                "authors": authors,
                                "year": details.get('year', ''),
                                "publisher": details.get('publisher', ''),
                                "language": details.get('language', ''),
                                "extension": details.get('extension', ''),
                                "size": details.get('size', ''),
                                "pages": details.get('pages', ''),
                                "isbn": details.get('isbn', ''),
                                "rating": details.get('rating', ''),
                                "download_url": details.get('download_url', ''),
                                "description": details.get('description', '')[:200] if details.get('description') else '',
                                "cover_url": details.get('cover', ''),
                                "search_query": query
                            }
                            
                            # Check if it's likely the right book
                            title_lower = book_data['title'].lower()
                            is_match = False
                            confidence = 0.0
                            
                            # Check for title match
                            if 'midnight' in title_lower and 'library' in title_lower:
                                is_match = True
                                confidence = 0.9
                            elif 'полночная' in title_lower and 'библиотека' in title_lower:
                                is_match = True
                                confidence = 0.9
                            elif 'midnight' in title_lower:
                                confidence = 0.6
                            
                            # Check for author match
                            for author in authors:
                                if 'haig' in author.lower() or 'хейг' in author.lower():
                                    confidence += 0.1
                                    is_match = True
                                    break
                            
                            book_data['confidence'] = min(confidence, 1.0)
                            book_data['is_likely_match'] = is_match
                            
                            books_found.append(book_data)
                            
                            if is_match:
                                print(f"  📚 {book_data['title']}")
                                print(f"     Authors: {', '.join(authors)}")
                                print(f"     Year: {book_data['year']}, Language: {book_data['language']}")
                                print(f"     Size: {book_data['size']}, Format: {book_data['extension'].upper()}")
                                print(f"     Confidence: {confidence:.0%}")
                                
                        except Exception as e:
                            print(f"  ⚠️ Error fetching book details: {e}")
                    
                    # If we found a good match, stop searching
                    if any(b['is_likely_match'] for b in books_found):
                        break
                        
            except Exception as e:
                print(f"  ❌ Search error: {e}")
        
        # Sort by confidence
        books_found.sort(key=lambda x: x['confidence'], reverse=True)
        
        result["search_results"] = books_found[:5]  # Top 5 matches
        
        if books_found and books_found[0]['confidence'] >= 0.8:
            best_match = books_found[0]
            result["status"] = "success"
            result["best_match"] = {
                "title": best_match["title"],
                "authors": best_match["authors"],
                "year": best_match["year"],
                "language": best_match["language"],
                "extension": best_match["extension"],
                "size": best_match["size"],
                "download_url": best_match["download_url"],
                "confidence": best_match["confidence"]
            }
            
            print("\n" + "=" * 80)
            print("🎯 BEST MATCH FOUND:")
            print(f"📖 Title: {best_match['title']}")
            print(f"✍️ Authors: {', '.join(best_match['authors'])}")
            print(f"📅 Year: {best_match['year']}")
            print(f"🌍 Language: {best_match['language']}")
            print(f"📄 Format: {best_match['extension'].upper()}")
            print(f"📦 Size: {best_match['size']}")
            print(f"🎯 Confidence: {best_match['confidence']:.0%}")
            
            if best_match['download_url'] and best_match['download_url'] != 'N/A':
                print(f"\n✅ EPUB DOWNLOAD AVAILABLE:")
                print(f"🔗 {best_match['download_url']}")
                result["download"] = {
                    "available": True,
                    "url": best_match['download_url'],
                    "format": best_match['extension'].upper()
                }
            else:
                print("\n⚠️ Download link not available (daily limit may be reached)")
                result["download"] = {
                    "available": False,
                    "reason": "Daily download limit reached or book not available"
                }
        else:
            result["status"] = "not_found"
            print("\n❌ No confident match found for 'The Midnight Library'")
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"\n❌ Error: {e}")
    
    return result

async def main():
    result = await search_midnight_library()
    
    # Save result to JSON
    output_file = "midnight_library_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Full results saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("📊 COMPLETE JSON RESULT:")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())