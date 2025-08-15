#!/usr/bin/env python3
"""
Test-Driven Development for Author-Based Fallback Search
Test cases for improved author search logic
"""

import pytest
import json
import asyncio
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

class TestAuthorFallbackSearch:
    """Test cases for author-based fallback search functionality"""
    
    def test_author_only_query_detection(self):
        """Test: Detect when user searches by author name only"""
        test_cases = [
            ("Умберто эко", True, "umberto eco"),
            ("Платон", True, "plato"), 
            ("Robert Martin", True, "robert martin"),
            ("Clean Code", False, "clean code"),  # Book title, not author
            ("Имя розы, Эко", False, "name of rose eco"),  # Book + author
            ("Python Programming", False, "python programming"),  # Subject
        ]
        
        for query, expected_is_author_only, expected_normalized in test_cases:
            is_author, normalized = detect_author_only_query(query)
            assert is_author == expected_is_author_only, f"Failed for: {query}"
            if expected_is_author_only:
                assert normalized is not None, f"Should return normalized author for: {query}"
    
    def test_author_book_matching(self):
        """Test: Match books to authors correctly"""
        # Test cases with known author-book pairs
        test_cases = [
            ("умберто эко", ["Имя розы", "Маятник Фуко", "Остров накануне"]),
            ("роберт мартин", ["Clean Code", "Clean Architecture"]),
            ("платон", ["Государство", "Федр", "Собрание сочинений"]),
        ]
        
        for author_query, expected_books in test_cases:
            books = find_books_by_author(author_query)
            # At least one book should be found
            assert len(books) > 0, f"No books found for author: {author_query}"
            # Should contain at least one expected book (partial match OK)
            found_titles = [book['title'].lower() for book in books]
            has_expected = any(
                any(expected.lower() in title for title in found_titles)
                for expected in expected_books
            )
            assert has_expected, f"Expected books not found for {author_query}: {found_titles}"
    
    def test_popular_book_selection(self):
        """Test: Select most popular/available EPUB from author's works"""
        # Mock book results for an author
        mock_books = [
            {"title": "Book A", "format": "pdf", "available": True, "popularity": 100},
            {"title": "Book B", "format": "epub", "available": True, "popularity": 200},
            {"title": "Book C", "format": "epub", "available": False, "popularity": 300},
            {"title": "Book D", "format": "epub", "available": True, "popularity": 150},
        ]
        
        # Should select Book B (highest popularity + epub + available)
        selected = select_best_epub_from_author_books(mock_books)
        assert selected['title'] == "Book B"
        assert selected['format'] == "epub"
        assert selected['available'] == True
    
    def test_confidence_boost_for_author_match(self):
        """Test: Boost confidence when found book matches author correctly"""
        # When we search for "Умберто эко" and find "Имя розы" by "Умберто Эко"
        # Confidence should be boosted significantly
        
        query = "умберто эко"
        found_title = "Имя розы"
        found_author = "Умберто Эко"
        
        # Original confidence would be very low (0.0) due to no title overlap
        base_confidence = calculate_base_confidence(query, found_title)
        assert base_confidence < 0.3  # Would normally be rejected
        
        # With author boost, should be acceptable
        boosted_confidence = calculate_confidence_with_author_boost(
            query, found_title, found_author
        )
        assert boosted_confidence >= 0.5  # Should be acceptable
    
    def test_integration_author_fallback_workflow(self):
        """Test: Full integration of author fallback search workflow"""
        # Test the complete workflow for author-only queries
        
        test_query = "умберто эко"
        
        # 1. Should detect as author-only query
        is_author_only = detect_author_only_query(test_query)[0]
        assert is_author_only == True
        
        # 2. Should find books by this author
        author_books = find_books_by_author(test_query)
        assert len(author_books) > 0
        
        # 3. Should select best EPUB
        best_book = select_best_epub_from_author_books(author_books)
        assert best_book is not None
        assert best_book.get('format') == 'epub'
        
        # 4. Should have sufficient confidence for download
        confidence = calculate_confidence_with_author_boost(
            test_query, best_book['title'], best_book.get('author', '')
        )
        assert confidence >= 0.5

# Mock functions to be implemented
def detect_author_only_query(query):
    """Detect if query is author name only vs book title + author"""
    # TODO: Implement author detection logic
    pass

def find_books_by_author(author_query):
    """Find books by specific author"""
    # TODO: Implement author-specific search
    pass

def select_best_epub_from_author_books(books):
    """Select best EPUB from author's book list"""
    # TODO: Implement selection logic based on popularity, availability, format
    pass

def calculate_base_confidence(query, title):
    """Calculate base confidence without author boost"""
    # TODO: Implement base confidence calculation
    pass

def calculate_confidence_with_author_boost(query, title, author):
    """Calculate confidence with author matching boost"""
    # TODO: Implement confidence with author boost
    pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])