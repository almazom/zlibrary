#!/usr/bin/env python3
"""
Search for 'Наследники. Экстравагантная история' by Конрад Дж. Форд Ф. М.
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

async def search_nasledniki():
    """Search for the Russian book"""
    
    # Book information
    book_info = {
        "title": "Наследники. Экстравагантная история",
        "title_short": "Наследники",
        "authors": "Конрад Дж. Форд Ф. М.",
        "author_variants": ["Конрад", "Форд", "Conrad", "Ford"]
    }
    
    print("🔍 SEARCHING FOR RUSSIAN BOOK")
    print("=" * 50)
    print(f"📖 Title: {book_info['title']}")
    print(f"✍️ Author: {book_info['authors']}")
    print("=" * 50)
    
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
        return
    
    try:
        # Initialize Z-Library
        lib = AsyncZlib()
        print("\n🔐 Logging in to Z-Library...")
        await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
        
        # Try different search queries
        search_queries = [
            # Full title + author
            f"{book_info['authors']} {book_info['title']}",
            # Short title + author
            f"{book_info['authors']} {book_info['title_short']}",
            # Just title
            book_info['title'],
            book_info['title_short'],
            # Author variants
            f"Конрад Форд {book_info['title_short']}",
            f"Conrad Ford наследники",
            # English variation
            "The Inheritors Conrad Ford"
        ]
        
        books_found = []
        
        for i, query in enumerate(search_queries, 1):
            print(f"\n🔍 Query {i}: {query}")
            
            try:
                paginator = await lib.search(
                    q=query,
                    count=5,
                    extensions=[Extension.EPUB]
                )
                await paginator.init()
                
                if paginator.result:
                    print(f"✅ Found {len(paginator.result)} results")
                    
                    for book in paginator.result:
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
                                "language": details.get('language', ''),
                                "extension": details.get('extension', ''),
                                "size": details.get('size', ''),
                                "download_url": details.get('download_url', ''),
                                "search_query": query
                            }
                            
                            # Check if it's likely the right book
                            title_lower = book_data['title'].lower()
                            is_match = False
                            confidence = 0.0
                            
                            # Check for title match
                            if 'наследник' in title_lower:
                                confidence += 0.6
                                is_match = True
                            elif 'inheritor' in title_lower:
                                confidence += 0.5
                                is_match = True
                            
                            # Check for author match
                            for author in authors:
                                author_lower = author.lower()
                                if any(name.lower() in author_lower for name in ['conrad', 'ford', 'конрад', 'форд']):
                                    confidence += 0.4
                                    is_match = True
                                    break
                            
                            book_data['confidence'] = min(confidence, 1.0)
                            book_data['is_likely_match'] = is_match
                            
                            if is_match:
                                books_found.append(book_data)
                                print(f"  📚 {book_data['title']}")
                                print(f"     Authors: {', '.join(authors[:2])}")
                                print(f"     Year: {book_data['year']}, Size: {book_data['size']}")
                                print(f"     Confidence: {confidence:.0%}")
                                
                                # Stop if we found a high confidence match
                                if confidence >= 0.8:
                                    print(f"  🎯 High confidence match found!")
                                    break
                            
                        except Exception as e:
                            print(f"  ⚠️ Error fetching book details: {e}")
                    
                    # If we found good matches, stop searching
                    if any(b['confidence'] >= 0.8 for b in books_found):
                        break
                        
                else:
                    print(f"❌ No results")
                    
            except Exception as e:
                print(f"❌ Search error: {e}")
        
        # Sort by confidence
        books_found.sort(key=lambda x: x['confidence'], reverse=True)
        
        print("\n" + "=" * 50)
        print("📊 SEARCH RESULTS SUMMARY")
        print("=" * 50)
        
        if books_found:
            print(f"✅ Found {len(books_found)} potential matches")
            
            for i, book in enumerate(books_found[:3], 1):
                print(f"\n{i}. {book['title']}")
                print(f"   Authors: {', '.join(book['authors'])}")
                print(f"   Year: {book['year']}, Language: {book['language']}")
                print(f"   Size: {book['size']}, Format: {book['extension'].upper()}")
                print(f"   Confidence: {book['confidence']:.0%}")
                print(f"   Query that found it: {book['search_query']}")
                
                if book['download_url'] and book['download_url'] != 'N/A':
                    print(f"   ✅ Download available")
                else:
                    print(f"   ⚠️ Download not available")
            
            # Show best match
            best = books_found[0]
            print(f"\n🎯 BEST MATCH:")
            print(f"📖 {best['title']}")
            print(f"✍️ {', '.join(best['authors'])}")
            print(f"🎯 {best['confidence']:.0%} confidence")
            
            if best['download_url'] and best['download_url'] != 'N/A':
                print(f"\n✅ EPUB DOWNLOAD AVAILABLE!")
                print(f"🔗 Ready to download")
                
                # Save result for terminal command
                result = {
                    "found": True,
                    "best_match": best,
                    "terminal_command": f"./scripts/zlib_book_search_fixed.sh --service --json -f epub --download \"{best['search_query']}\"",
                    "all_matches": books_found
                }
                
                with open("nasledniki_search_result.json", "w", encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"\n🎮 TERMINAL COMMAND TO DOWNLOAD:")
                print(f"./scripts/zlib_book_search_fixed.sh --service --json -f epub --download \"{best['search_query']}\"")
                
            else:
                print(f"\n⚠️ Download not available (daily limit or restrictions)")
                
        else:
            print("❌ No matching books found")
            print("\n💡 Try these terminal commands manually:")
            print("./scripts/zlib_book_search_fixed.sh --json \"наследники\"")
            print("./scripts/zlib_book_search_fixed.sh --json \"conrad ford\"")
            print("./scripts/zlib_book_search_fixed.sh --json \"inheritors\"")
            
        return books_found
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(search_nasledniki())