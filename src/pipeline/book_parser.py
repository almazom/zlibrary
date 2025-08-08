#!/usr/bin/env python3
"""
Book Parser - Intelligent extraction of book metadata from various formats
"""
import re
from typing import Dict, Optional, Tuple

class BookParser:
    """
    Parse various book input formats to extract metadata
    """
    
    @staticmethod
    def parse_numbered_list_format(text: str) -> Dict[str, str]:
        """
        Parse numbered list format like: "24. Секисов А. Курорт (Альпина. Проза)"
        
        Returns:
            Dict with title, author, publisher
        """
        # Pattern: number. Author Name. Title (Publisher)
        pattern = r'^\d+\.\s*([А-Яа-яA-Za-z]+\s+[А-ЯA-Z]\.)\s*(.+?)\s*\(([^)]+)\)?\s*$'
        match = re.match(pattern, text)
        
        if match:
            return {
                'author': match.group(1).strip() if match.group(1) else '',
                'title': match.group(2).strip() if match.group(2) else '',
                'publisher': match.group(3).strip() if match.group(3) else '',
                'format': 'numbered_list'
            }
        
        # Try without parentheses
        pattern2 = r'^\d+\.\s*([А-Яа-яA-Za-z]+\s+[А-ЯA-Z]\.)\s*(.+)$'
        match = re.match(pattern2, text)
        
        if match:
            return {
                'author': match.group(1).strip(),
                'title': match.group(2).strip(),
                'publisher': '',
                'format': 'numbered_list'
            }
        
        return {}
    
    @staticmethod
    def parse_author_title_format(text: str) -> Dict[str, str]:
        """
        Parse "Author. Title" or "Author Name. Book Title" format
        """
        # Pattern: Author Name. Title
        pattern = r'^([А-Яа-яA-Za-z]+(?:\s+[А-Яа-яA-Za-z]+)?(?:\s+[А-ЯA-Z]\.)?)\.\s*(.+)$'
        match = re.match(pattern, text)
        
        if match:
            return {
                'author': match.group(1).strip(),
                'title': match.group(2).strip(),
                'publisher': '',
                'format': 'author_title'
            }
        
        return {}
    
    @staticmethod
    def parse_title_by_author_format(text: str) -> Dict[str, str]:
        """
        Parse "Title by Author" format
        """
        # Pattern: Title by Author
        pattern = r'^(.+?)\s+(?:by|автор)\s+(.+)$'
        match = re.match(pattern, text, re.IGNORECASE)
        
        if match:
            return {
                'title': match.group(1).strip(),
                'author': match.group(2).strip(),
                'publisher': '',
                'format': 'title_by_author'
            }
        
        return {}
    
    @classmethod
    def parse(cls, text: str) -> Dict[str, str]:
        """
        Try all parsing patterns and return best match
        
        Args:
            text: Input text to parse
            
        Returns:
            Dict with extracted metadata
        """
        # Clean input
        text = text.strip()
        
        # Try different formats
        parsers = [
            cls.parse_numbered_list_format,
            cls.parse_author_title_format,
            cls.parse_title_by_author_format
        ]
        
        for parser in parsers:
            result = parser(text)
            if result:
                result['original'] = text
                # Create normalized query
                if result.get('author') and result.get('title'):
                    result['normalized_query'] = f"{result['author']} {result['title']}"
                elif result.get('title'):
                    result['normalized_query'] = result['title']
                else:
                    result['normalized_query'] = text
                return result
        
        # Fallback - return original
        return {
            'original': text,
            'normalized_query': text,
            'title': '',
            'author': '',
            'publisher': '',
            'format': 'unknown'
        }

if __name__ == "__main__":
    # Test cases
    test_cases = [
        "24. Секисов А. Курорт (Альпина. Проза)",
        "Достоевский Ф.М. Преступление и наказание",
        "The Great Gatsby by F. Scott Fitzgerald",
        "1. Иванов И. Книга",
        "Simple book title"
    ]
    
    parser = BookParser()
    for test in test_cases:
        result = parser.parse(test)
        print(f"\nInput: {test}")
        print(f"Parsed: {result}")