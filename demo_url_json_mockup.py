#!/usr/bin/env python3
"""
URL to EPUB Demo with Complete JSON Response
Shows the expected JSON structure with metadata and download links
"""
import json
import re
import urllib.parse
from datetime import datetime

def extract_from_url(url):
    """Extract book info from marketplace URLs"""
    
    result = {
        "url": url,
        "marketplace": "unknown",
        "extracted": {}
    }
    
    # Ozon.ru extraction
    if "ozon.ru" in url:
        result["marketplace"] = "ozon"
        match = re.search(r'/product/([^/?]+)', url)
        if match:
            slug = match.group(1)
            
            # Parse Ozon URL patterns
            if "trevozhnye-lyudi" in slug:
                result["extracted"] = {
                    "title_ru": "Тревожные люди",
                    "title_en": "Anxious People",
                    "author": "Fredrik Backman",
                    "author_ru": "Фредрик Бакман"
                }
            elif "1984" in slug:
                result["extracted"] = {
                    "title": "1984",
                    "author": "George Orwell",
                    "author_ru": "Джордж Оруэлл"
                }
    
    # Amazon extraction
    elif "amazon.com" in url:
        result["marketplace"] = "amazon"
        if "Harry-Potter" in url:
            result["extracted"] = {
                "title": "Harry Potter and the Philosopher's Stone",
                "author": "J.K. Rowling"
            }
    
    return result

def generate_mockup_response(url):
    """Generate complete JSON response showing the expected structure"""
    
    # Extract info from URL
    extraction = extract_from_url(url)
    
    # Build complete response based on extraction
    if "trevozhnye-lyudi" in url:
        # Anxious People example
        return {
            "input": {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "type": "marketplace_url"
            },
            "extraction": {
                "success": True,
                "marketplace": extraction["marketplace"],
                "data": extraction["extracted"],
                "method": "url_slug_parsing",
                "confidence": 0.95
            },
            "normalization": {
                "original": "trevozhnye lyudi bakman",
                "normalized": "Anxious People Fredrik Backman",
                "variants": [
                    "Тревожные люди Фредрик Бакман",
                    "Anxious People Backman",
                    "Folk med ångest"  # Original Swedish
                ],
                "language_routing": "multilingual"
            },
            "search": {
                "query_used": "Fredrik Backman Anxious People",
                "service": "zlibrary",
                "results_count": 3,
                "search_time": 2.34
            },
            "book_metadata": {
                "title": "Anxious People",
                "authors": ["Fredrik Backman"],
                "year": "2019",
                "publisher": "Atria Books",
                "language": "English",
                "extension": "epub",
                "size": "1.2 MB",
                "size_bytes": 1258291,
                "pages": "352",
                "isbn": "9781501160837",
                "description": "A poignant, charming novel about a crime that never took place, a would-be bank robber who disappears into thin air...",
                "rating": "4.5/5",
                "cover_url": "https://covers.zlibcdn.com/covers299/books/12/34/56/123456.jpg",
                "categories": ["Fiction", "Contemporary", "Humor"]
            },
            "download": {
                "available": True,
                "url": "https://usa1lib.org/dl/123456/abcdef",
                "format": "EPUB",
                "size_bytes": 1258291,
                "ready": True,
                "limits": {
                    "daily_remaining": 9,
                    "daily_total": 10
                }
            },
            "confidence": {
                "extraction": 0.95,
                "normalization": 0.90,
                "match": 0.98,
                "overall": 0.94,
                "quality": "excellent"
            },
            "status": "success",
            "processing_time": 3.45
        }
    
    elif "1984" in url:
        # 1984 example
        return {
            "input": {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "type": "marketplace_url"
            },
            "extraction": {
                "success": True,
                "marketplace": extraction["marketplace"],
                "data": extraction["extracted"],
                "method": "url_parsing",
                "confidence": 1.0
            },
            "search": {
                "query_used": "George Orwell 1984",
                "service": "zlibrary",
                "results_count": 15
            },
            "book_metadata": {
                "title": "1984",
                "authors": ["George Orwell"],
                "year": "1949",
                "publisher": "Signet Classic",
                "language": "English",
                "extension": "epub",
                "size": "563 KB",
                "size_bytes": 576921,
                "pages": "328",
                "isbn": "9780451524935",
                "description": "Winston Smith toes the Party line, rewriting history to satisfy the demands of the Ministry of Truth...",
                "rating": "4.7/5",
                "categories": ["Fiction", "Dystopian", "Classic"]
            },
            "download": {
                "available": True,
                "url": "https://usa1lib.org/dl/789012/xyz123",
                "format": "EPUB",
                "size_bytes": 576921,
                "ready": True
            },
            "confidence": {
                "overall": 1.0,
                "quality": "excellent"
            },
            "status": "success"
        }
    
    else:
        # Generic response
        return {
            "input": {
                "url": url,
                "timestamp": datetime.now().isoformat()
            },
            "extraction": extraction,
            "status": "partial",
            "message": "Extraction successful but book not found in library"
        }

def main():
    """Demonstrate URL to EPUB JSON workflow"""
    
    print("=" * 80)
    print("🎯 URL TO EPUB - COMPLETE JSON WORKFLOW DEMONSTRATION")
    print("=" * 80)
    print("\nShowing complete URL → JSON with metadata → EPUB download link")
    print("=" * 80)
    
    # Test URLs
    test_urls = [
        "https://www.ozon.ru/product/trevozhnye-lyudi-bakman-fredrik-202912464/",
        "https://www.ozon.ru/product/1984-orwell-george-138516846/"
    ]
    
    for url in test_urls:
        print(f"\n{'=' * 70}")
        print(f"🔗 INPUT URL:")
        print(f"   {url}")
        print("-" * 70)
        
        # Generate complete response
        response = generate_mockup_response(url)
        
        # Display formatted JSON
        print("\n📊 COMPLETE JSON RESPONSE:")
        print("-" * 70)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Highlight key information
        print("\n✨ KEY INFORMATION:")
        print("-" * 70)
        
        if response.get("status") == "success":
            metadata = response.get("book_metadata", {})
            download = response.get("download", {})
            
            print(f"📖 Title: {metadata.get('title')}")
            print(f"✍️  Authors: {', '.join(metadata.get('authors', []))}")
            print(f"📅 Year: {metadata.get('year')}")
            print(f"📏 Size: {metadata.get('size')} ({metadata.get('size_bytes', 0):,} bytes)")
            print(f"📄 Format: {metadata.get('extension', '').upper()}")
            
            if download.get("available"):
                print(f"\n🔗 EPUB DOWNLOAD URL:")
                print(f"   {download.get('url')}")
                print(f"   Status: ✅ Ready for download")
                if download.get("limits"):
                    limits = download["limits"]
                    print(f"   Daily limit: {limits.get('daily_remaining')}/{limits.get('daily_total')} downloads remaining")
            
            confidence = response.get("confidence", {})
            print(f"\n🎯 Confidence: {confidence.get('overall', 0):.0%} ({confidence.get('quality', 'unknown')})")
    
    print("\n" + "=" * 70)
    print("📌 This demonstrates the complete JSON structure returned when:")
    print("   1. URL is provided as input")
    print("   2. Book information is extracted from the URL")
    print("   3. Book is found in Z-Library")
    print("   4. Metadata is retrieved")
    print("   5. Download link is generated")
    print("=" * 70)

if __name__ == "__main__":
    main()