#!/usr/bin/env python3
"""
Enhanced Author-Based Search Logic
Implements author fallback search for better user experience
"""

import re
import json
import asyncio
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import os
import sys
from difflib import SequenceMatcher

# Add src to path for zlibrary import
sys.path.insert(0, str(Path(__file__).parent / "src"))
from zlibrary import AsyncZlib, Extension, Language

class AuthorSearchEnhancer:
    """Enhanced search logic for author-based queries"""
    
    def __init__(self):
        self.author_patterns = self._load_author_patterns()
        self.book_popularity_cache = {}
        
    def _load_author_patterns(self) -> Dict:
        """Load known author patterns and translations"""
        return {
            # Russian authors
            'умберто эко': {
                'normalized': 'umberto eco',
                'variations': ['умберто эко', 'эко', 'umberto eco'],
                'known_books': ['имя розы', 'маятник фуко', 'остров накануне']
            },
            'платон': {
                'normalized': 'plato',
                'variations': ['платон', 'plato'],
                'known_books': ['государство', 'федр', 'собрание сочинений']
            },
            'роберт мартин': {
                'normalized': 'robert martin',
                'variations': ['роберт мартин', 'роберт с мартин', 'robert martin', 'martin'],
                'known_books': ['clean code', 'clean architecture', 'чистый код']
            },
            'джеймс клир': {
                'normalized': 'james clear',
                'variations': ['джеймс клир', 'james clear', 'клир'],
                'known_books': ['atomic habits', 'атомные привычки']
            }
        }
    
    def detect_author_only_query(self, query: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Detect if query is author name only
        Returns: (is_author_only, normalized_author, author_info)
        """
        query_lower = query.lower().strip()
        
        # Remove common noise words
        noise_words = ['книга', 'книги', 'автор', 'книга от', 'от автора', 'произведения']
        for noise in noise_words:
            query_lower = query_lower.replace(noise, '').strip()
        
        # Check against known authors
        for author_key, author_info in self.author_patterns.items():
            for variation in author_info['variations']:
                if variation.lower() in query_lower or query_lower in variation.lower():
                    # High confidence author match
                    if len(query_lower.split()) <= 3:  # Author names are typically 1-3 words
                        return True, author_info['normalized'], author_info
        
        # Heuristic detection for unknown authors
        # Check if query looks like a person name (2-3 words, proper case patterns)
        words = query.split()
        if 2 <= len(words) <= 3:
            # Check for Cyrillic author pattern (Russian names)
            if re.search('[а-яё]', query, re.IGNORECASE):
                # Common Russian name endings
                if any(query.lower().endswith(ending) for ending in ['ов', 'ев', 'ин', 'он', 'ич', 'енко']):
                    return True, query_lower, None
            
            # Check for Latin author pattern
            else:
                # Simple heuristic: if all words start with capital letters
                if all(word[0].isupper() for word in words if word):
                    return True, query_lower, None
        
        return False, None, None
    
    async def find_books_by_author(self, client: AsyncZlib, author_query: str, 
                                 limit: int = 5) -> List[Dict]:
        """
        Find books by specific author with multiple search strategies
        """
        books_found = []
        
        # Strategy 1: Direct author search
        try:
            search_results = await client.search(
                q=author_query,
                extensions=[Extension.EPUB],
                count=limit
            )
            await search_results.init()
            
            for book in search_results.result:
                book_info = await book.fetch()
                books_found.append({
                    'title': book_info.get('name', ''),
                    'authors': book_info.get('authors', []),
                    'download_url': book_info.get('download_url', ''),
                    'year': book_info.get('year', ''),
                    'size': book_info.get('size', ''),
                    'format': 'epub',
                    'available': 'download' in book_info.get('download_url', '').lower(),
                    'search_strategy': 'direct_author'
                })
        except Exception as e:
            print(f"Direct author search failed: {e}")
        
        # Strategy 2: Search with known book titles if author is recognized
        author_info = self._get_author_info(author_query)
        if author_info and len(books_found) < limit:
            for known_book in author_info.get('known_books', []):
                try:
                    search_results = await client.search(
                        q=f"{known_book} {author_query}",
                        extensions=[Extension.EPUB],
                        count=2
                    )
                    await search_results.init()
                    
                    for book in search_results.result:
                        book_info = await book.fetch()
                        # Verify author match
                        if self._author_matches(author_query, book_info.get('authors', [])):
                            books_found.append({
                                'title': book_info.get('name', ''),
                                'authors': book_info.get('authors', []),
                                'download_url': book_info.get('download_url', ''),
                                'year': book_info.get('year', ''),
                                'size': book_info.get('size', ''),
                                'format': 'epub',
                                'available': 'download' in book_info.get('download_url', '').lower(),
                                'search_strategy': 'known_book_title'
                            })
                            if len(books_found) >= limit:
                                break
                except Exception as e:
                    print(f"Known book search failed for {known_book}: {e}")
                    continue
        
        return books_found[:limit]
    
    def _get_author_info(self, author_query: str) -> Optional[Dict]:
        """Get author info from patterns if available"""
        author_lower = author_query.lower().strip()
        for author_key, author_info in self.author_patterns.items():
            for variation in author_info['variations']:
                if variation.lower() in author_lower or author_lower in variation.lower():
                    return author_info
        return None
    
    def _author_matches(self, query_author: str, found_authors: List[Dict]) -> bool:
        """Check if found authors match query author"""
        if not found_authors:
            return False
        
        query_lower = query_author.lower()
        
        for author_dict in found_authors:
            author_name = author_dict.get('author', '').lower()
            if not author_name:
                continue
            
            # Direct match
            if query_lower in author_name or author_name in query_lower:
                return True
            
            # Fuzzy match
            similarity = SequenceMatcher(None, query_lower, author_name).ratio()
            if similarity > 0.6:
                return True
        
        return False
    
    def select_best_epub_from_author_books(self, books: List[Dict]) -> Optional[Dict]:
        """
        Select the best EPUB from author's books based on:
        1. Availability (download URL exists)
        2. Format (prefer EPUB)
        3. Popularity/recency (year)
        4. Size (reasonable size)
        """
        if not books:
            return None
        
        # Filter for available EPUBs
        epub_books = [
            book for book in books 
            if book.get('format') == 'epub' and book.get('available', False)
        ]
        
        if not epub_books:
            # Fallback to any available book
            available_books = [book for book in books if book.get('available', False)]
            if not available_books:
                return None
            epub_books = available_books
        
        # Score books
        scored_books = []
        for book in epub_books:
            score = 0
            
            # Availability bonus
            if book.get('available', False):
                score += 100
            
            # Format bonus
            if book.get('format') == 'epub':
                score += 50
            
            # Recency bonus (prefer newer books, but not too heavily)
            try:
                year = int(book.get('year', '0'))
                if year > 2000:
                    score += min(year - 2000, 20)  # Max 20 points for recency
            except (ValueError, TypeError):
                pass
            
            # Size bonus (prefer reasonable sizes, 1-50MB)
            try:
                size_str = book.get('size', '0 MB')
                size_mb = float(re.search(r'(\d+\.?\d*)', size_str).group(1))
                if 1 <= size_mb <= 50:
                    score += 30
                elif 0.1 <= size_mb <= 100:
                    score += 10
            except (AttributeError, ValueError, TypeError):
                pass
            
            # Known book bonus
            title_lower = book.get('title', '').lower()
            author_info = self._get_author_info_from_book(book)
            if author_info:
                for known_book in author_info.get('known_books', []):
                    if known_book.lower() in title_lower:
                        score += 40
                        break
            
            scored_books.append((score, book))
        
        # Return highest scoring book
        if scored_books:
            scored_books.sort(key=lambda x: x[0], reverse=True)
            return scored_books[0][1]
        
        return None
    
    def _get_author_info_from_book(self, book: Dict) -> Optional[Dict]:
        """Extract author info from book if matches known patterns"""
        authors = book.get('authors', [])
        if not authors:
            return None
        
        main_author = authors[0].get('author', '').lower()
        return self._get_author_info(main_author)
    
    def calculate_confidence_with_author_boost(self, query: str, found_title: str, 
                                             found_authors: List[Dict]) -> float:
        """
        Calculate confidence with author boost for author-only queries
        """
        # Base confidence from title-query overlap (will be low for author queries)
        base_confidence = self._calculate_base_confidence(query, found_title)
        
        # Author matching boost
        author_boost = 0.0
        if self._author_matches(query, found_authors):
            author_boost = 0.6  # Strong boost for author match
        
        # Known author-book combination boost
        author_info = self._get_author_info(query)
        if author_info:
            title_lower = found_title.lower()
            for known_book in author_info.get('known_books', []):
                if known_book.lower() in title_lower:
                    author_boost += 0.2  # Additional boost for known combination
                    break
        
        # Language consistency boost
        lang_boost = 0.0
        query_cyrillic = bool(re.search('[а-яё]', query, re.IGNORECASE))
        title_cyrillic = bool(re.search('[а-яё]', found_title, re.IGNORECASE))
        if (query_cyrillic and title_cyrillic) or (not query_cyrillic and not title_cyrillic):
            lang_boost = 0.1
        
        final_confidence = min(base_confidence + author_boost + lang_boost, 1.0)
        return final_confidence
    
    def _calculate_base_confidence(self, query: str, title: str) -> float:
        """Calculate base confidence from title-query word overlap"""
        query_words = set(query.lower().split())
        title_words = set(title.lower().split())
        
        if not query_words or not title_words:
            return 0.0
        
        overlap = len(query_words.intersection(title_words))
        total = len(query_words)
        
        return min(overlap / total * 0.5, 0.5)  # Max 0.5 from base overlap

# Usage example/test
async def test_author_search():
    """Test the author search enhancement"""
    enhancer = AuthorSearchEnhancer()
    
    # Test author detection
    test_queries = ["Умберто эко", "Имя розы, Эко", "Python Programming"]
    
    for query in test_queries:
        is_author, normalized, info = enhancer.detect_author_only_query(query)
        print(f"Query: '{query}' -> Author only: {is_author}, Normalized: {normalized}")
    
    # Test with real search (requires authentication)
    # client = AsyncZlib()
    # profile = await client.login("email", "password")
    # books = await enhancer.find_books_by_author(client, "умберто эко")
    # best_book = enhancer.select_best_epub_from_author_books(books)
    # print(f"Best book: {best_book}")

if __name__ == "__main__":
    asyncio.run(test_author_search())