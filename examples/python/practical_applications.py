#!/usr/bin/env python3
"""
Practical Applications for Z-Library API

Real-world usage scenarios including:
- Academic research tools
- Book collection management
- Content analysis
- Automated workflows
"""

import asyncio
import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import zlibrary
from zlibrary import Language, Extension

# Setup data directory
DATA_DIR = Path("zlibrary_data")
DATA_DIR.mkdir(exist_ok=True)


class BookCollectionManager:
    """Manage a personal book collection with Z-Library integration."""
    
    def __init__(self):
        self.lib = None
        self.collection_file = DATA_DIR / "my_collection.json"
        self.wishlist_file = DATA_DIR / "wishlist.json"
    
    async def initialize(self, email: str, password: str):
        """Initialize Z-Library connection."""
        self.lib = zlibrary.AsyncZlib()
        await self.lib.login(email, password)
        print("✓ Connected to Z-Library")
    
    def load_collection(self) -> List[Dict]:
        """Load existing collection from file."""
        if self.collection_file.exists():
            with open(self.collection_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_collection(self, collection: List[Dict]):
        """Save collection to file."""
        with open(self.collection_file, 'w') as f:
            json.dump(collection, f, indent=2)
    
    async def add_book_to_collection(self, query: str) -> bool:
        """Search for a book and add it to collection."""
        try:
            paginator = await self.lib.search(q=query, count=5)
            books = await paginator.next()
            
            if not books:
                print(f"No books found for '{query}'")
                return False
            
            # Show options to user
            print(f"\nFound {len(books)} books for '{query}':")
            for i, book in enumerate(books, 1):
                authors = ", ".join([a['author'] for a in book.authors])
                print(f"{i}. {book.name} by {authors} ({book.year})")
            
            # For demo, automatically select first book
            selected_book = books[0]
            
            # Get detailed information
            details = await selected_book.fetch()
            
            # Create collection entry
            book_entry = {
                'id': details.get('id', selected_book.id),
                'title': details['name'],
                'authors': [a['author'] for a in selected_book.authors],
                'year': selected_book.year,
                'publisher': selected_book.publisher,
                'extension': selected_book.extension,
                'size': selected_book.size,
                'rating': selected_book.rating,
                'description': details.get('description', ''),
                'categories': details.get('categories', ''),
                'date_added': datetime.now().isoformat(),
                'download_url': details.get('download_url', ''),
                'cover_url': selected_book.cover
            }
            
            # Add to collection
            collection = self.load_collection()
            
            # Check if already exists
            if any(book['id'] == book_entry['id'] for book in collection):
                print(f"Book '{book_entry['title']}' already in collection")
                return False
            
            collection.append(book_entry)
            self.save_collection(collection)
            
            print(f"✓ Added '{book_entry['title']}' to collection")
            return True
            
        except Exception as e:
            print(f"❌ Error adding book: {e}")
            return False
    
    def export_collection_csv(self):
        """Export collection to CSV file."""
        collection = self.load_collection()
        if not collection:
            print("No books in collection")
            return
        
        csv_file = DATA_DIR / "collection_export.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'title', 'authors', 'year', 'publisher', 'extension', 
                'size', 'rating', 'categories', 'date_added'
            ])
            writer.writeheader()
            
            for book in collection:
                row = {
                    'title': book['title'],
                    'authors': '; '.join(book['authors']),
                    'year': book['year'],
                    'publisher': book['publisher'],
                    'extension': book['extension'],
                    'size': book['size'],
                    'rating': book['rating'],
                    'categories': book['categories'],
                    'date_added': book['date_added']
                }
                writer.writerow(row)
        
        print(f"✓ Collection exported to {csv_file}")
    
    def get_statistics(self):
        """Get collection statistics."""
        collection = self.load_collection()
        if not collection:
            print("No books in collection")
            return
        
        # Basic stats
        total_books = len(collection)
        extensions = {}
        years = []
        publishers = {}
        
        for book in collection:
            # Count extensions
            ext = book['extension']
            extensions[ext] = extensions.get(ext, 0) + 1
            
            # Collect years
            if book['year'] and book['year'].isdigit():
                years.append(int(book['year']))
            
            # Count publishers
            pub = book['publisher']
            if pub:
                publishers[pub] = publishers.get(pub, 0) + 1
        
        print(f"\n=== Collection Statistics ===")
        print(f"Total books: {total_books}")
        
        if extensions:
            print(f"\nFormats:")
            for ext, count in sorted(extensions.items()):
                print(f"  {ext}: {count}")
        
        if years:
            print(f"\nYear range: {min(years)} - {max(years)}")
            print(f"Average year: {sum(years) / len(years):.0f}")
        
        if publishers:
            top_publishers = sorted(publishers.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"\nTop publishers:")
            for pub, count in top_publishers:
                print(f"  {pub}: {count} books")


async def academic_research_tool():
    """Tool for academic research and literature review."""
    print("=== Academic Research Tool ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Research topic
    research_topic = "machine learning ethics"
    print(f"Researching: {research_topic}")
    
    # Comprehensive search strategy
    search_variations = [
        "machine learning ethics",
        "AI ethics artificial intelligence",
        "algorithmic bias fairness",
        "responsible AI development",
        "ethical artificial intelligence"
    ]
    
    all_results = []
    
    for variation in search_variations:
        try:
            print(f"Searching: {variation}")
            
            # Search recent academic content
            paginator = await lib.search(
                q=variation,
                from_year=2018,
                lang=[Language.ENGLISH],
                extensions=[Extension.PDF],
                count=10
            )
            
            books = await paginator.next()
            
            for book in books:
                # Get detailed information
                try:
                    details = await book.fetch()
                    
                    result = {
                        'search_term': variation,
                        'title': details['name'],
                        'authors': [a['author'] for a in book.authors],
                        'year': book.year,
                        'publisher': book.publisher,
                        'description': details.get('description', '')[:500],
                        'categories': details.get('categories', ''),
                        'rating': book.rating,
                        'url': details.get('url', ''),
                        'relevance_score': 0  # Could implement relevance scoring
                    }
                    
                    all_results.append(result)
                    
                except Exception as e:
                    print(f"Could not fetch details for {book.name}: {e}")
            
            # Rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error searching '{variation}': {e}")
    
    # Save research results
    research_file = DATA_DIR / f"research_{research_topic.replace(' ', '_')}.json"
    with open(research_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✓ Found {len(all_results)} relevant sources")
    print(f"✓ Results saved to {research_file}")
    
    # Generate bibliography
    bib_file = DATA_DIR / f"bibliography_{research_topic.replace(' ', '_')}.txt"
    with open(bib_file, 'w') as f:
        f.write(f"Bibliography: {research_topic.title()}\n")
        f.write("=" * 50 + "\n\n")
        
        for i, result in enumerate(all_results[:20], 1):  # Top 20 results
            authors = ", ".join(result['authors'])
            f.write(f"{i}. {result['title']}\n")
            f.write(f"   Authors: {authors}\n")
            f.write(f"   Publisher: {result['publisher']} ({result['year']})\n")
            f.write(f"   Categories: {result['categories']}\n")
            f.write(f"   URL: {result['url']}\n\n")
    
    print(f"✓ Bibliography saved to {bib_file}")


async def content_analysis_tool():
    """Analyze content trends and patterns."""
    print("=== Content Analysis Tool ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Analyze trends in programming books over time
    programming_languages = ["python", "javascript", "java", "rust", "go"]
    years = [2020, 2021, 2022, 2023, 2024]
    
    trend_data = {}
    
    for lang in programming_languages:
        trend_data[lang] = {}
        
        for year in years:
            try:
                paginator = await lib.search(
                    q=f"{lang} programming",
                    from_year=year,
                    to_year=year,
                    lang=[Language.ENGLISH],
                    extensions=[Extension.PDF],
                    count=50  # Get larger sample
                )
                
                books = await paginator.next()
                trend_data[lang][year] = len(books)
                
                print(f"{lang} {year}: {len(books)} books")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error analyzing {lang} {year}: {e}")
                trend_data[lang][year] = 0
    
    # Save trend analysis
    trends_file = DATA_DIR / "programming_trends.json"
    with open(trends_file, 'w') as f:
        json.dump(trend_data, f, indent=2)
    
    # Generate trend report
    report_file = DATA_DIR / "trend_report.txt"
    with open(report_file, 'w') as f:
        f.write("Programming Language Book Trends (2020-2024)\n")
        f.write("=" * 50 + "\n\n")
        
        for lang, yearly_data in trend_data.items():
            f.write(f"{lang.upper()}:\n")
            total = sum(yearly_data.values())
            f.write(f"  Total books (2020-2024): {total}\n")
            
            if len(yearly_data) > 1:
                years_list = sorted(yearly_data.keys())
                growth = yearly_data[years_list[-1]] - yearly_data[years_list[0]]
                f.write(f"  Growth (2020-2024): {growth:+d}\n")
            
            f.write(f"  Yearly breakdown: {yearly_data}\n\n")
    
    print(f"✓ Trend analysis saved to {trends_file}")
    print(f"✓ Report saved to {report_file}")


async def automated_collection_builder():
    """Automatically build collections based on criteria."""
    print("=== Automated Collection Builder ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Define collection criteria
    collections = {
        "Classic Computer Science": {
            "queries": ["algorithms", "data structures", "computer science fundamentals"],
            "to_year": 2000,
            "languages": [Language.ENGLISH],
            "extensions": [Extension.PDF]
        },
        "Modern AI/ML": {
            "queries": ["machine learning", "deep learning", "artificial intelligence"],
            "from_year": 2018,
            "languages": [Language.ENGLISH],
            "extensions": [Extension.PDF, Extension.EPUB]
        },
        "Web Development": {
            "queries": ["javascript", "react", "node.js", "web development"],
            "from_year": 2020,
            "languages": [Language.ENGLISH],
            "extensions": [Extension.PDF]
        }
    }
    
    for collection_name, criteria in collections.items():
        print(f"\nBuilding collection: {collection_name}")
        collection_books = []
        
        for query in criteria["queries"]:
            try:
                search_params = {
                    "q": query,
                    "count": 10,
                    "lang": criteria["languages"],
                    "extensions": criteria["extensions"]
                }
                
                if "from_year" in criteria:
                    search_params["from_year"] = criteria["from_year"]
                if "to_year" in criteria:
                    search_params["to_year"] = criteria["to_year"]
                
                paginator = await lib.search(**search_params)
                books = await paginator.next()
                
                for book in books:
                    # Get book details
                    try:
                        details = await book.fetch()
                        
                        book_info = {
                            'id': book.id,
                            'title': details['name'],
                            'authors': [a['author'] for a in book.authors],
                            'year': book.year,
                            'publisher': book.publisher,
                            'extension': book.extension,
                            'rating': book.rating,
                            'description': details.get('description', ''),
                            'query_found': query
                        }
                        
                        # Avoid duplicates
                        if not any(b['id'] == book_info['id'] for b in collection_books):
                            collection_books.append(book_info)
                            print(f"  Added: {book_info['title']}")
                        
                    except Exception as e:
                        print(f"  Could not fetch details: {e}")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"  Error searching '{query}': {e}")
        
        # Save collection
        collection_file = DATA_DIR / f"collection_{collection_name.replace(' ', '_').lower()}.json"
        with open(collection_file, 'w') as f:
            json.dump({
                'name': collection_name,
                'criteria': criteria,
                'created': datetime.now().isoformat(),
                'books': collection_books
            }, f, indent=2)
        
        print(f"✓ Collection '{collection_name}' saved with {len(collection_books)} books")


async def download_monitor():
    """Monitor download limits and usage."""
    print("=== Download Monitor ===")
    
    lib = zlibrary.AsyncZlib()
    await lib.login(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Get current limits
    limits = await lib.profile.get_limits()
    
    # Create monitoring log
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'daily_allowed': limits['daily_allowed'],
        'daily_remaining': limits['daily_remaining'],
        'daily_amount': limits['daily_amount'],
        'daily_reset': limits['daily_reset']
    }
    
    # Save to log file
    log_file = DATA_DIR / "download_log.json"
    
    if log_file.exists():
        with open(log_file, 'r') as f:
            log_data = json.load(f)
    else:
        log_data = []
    
    log_data.append(log_entry)
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"Download Status:")
    print(f"  Daily allowed: {limits['daily_allowed']}")
    print(f"  Remaining today: {limits['daily_remaining']}")
    print(f"  Total daily amount: {limits['daily_amount']}")
    print(f"  Reset in: {limits['daily_reset']} hours")
    
    # Check usage pattern
    if len(log_data) > 1:
        previous = log_data[-2]
        current = log_data[-1]
        
        downloads_since_last = previous['daily_remaining'] - current['daily_remaining']
        if downloads_since_last > 0:
            print(f"  Downloads since last check: {downloads_since_last}")
    
    # Alert if running low
    usage_percentage = (limits['daily_allowed'] - limits['daily_remaining']) / limits['daily_allowed'] * 100
    if usage_percentage > 80:
        print(f"⚠️  Warning: {usage_percentage:.1f}% of daily downloads used")


async def main():
    """Run practical application examples."""
    print("Z-Library Practical Applications")
    print("=" * 40)
    
    if not os.getenv('ZLOGIN') or not os.getenv('ZPASSW'):
        print("❌ Set ZLOGIN and ZPASSW environment variables")
        return
    
    # Example 1: Book Collection Manager
    print("1. Book Collection Management")
    manager = BookCollectionManager()
    await manager.initialize(os.getenv('ZLOGIN'), os.getenv('ZPASSW'))
    
    # Add some books to collection
    await manager.add_book_to_collection("Clean Code")
    await manager.add_book_to_collection("Design Patterns")
    
    # Show statistics
    manager.get_statistics()
    manager.export_collection_csv()
    print()
    
    # Example 2: Academic Research Tool
    await academic_research_tool()
    print()
    
    # Example 3: Content Analysis
    await content_analysis_tool()
    print()
    
    # Example 4: Automated Collection Building
    await automated_collection_builder()
    print()
    
    # Example 5: Download Monitoring
    await download_monitor()
    
    print(f"\n✓ All data saved to {DATA_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())