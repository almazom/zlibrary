#!/usr/bin/env python3
"""
Z-LIBRARY SOURCE ADAPTER - Primary book source
TDD Implementation: Fast, comprehensive book search
"""
import time
import asyncio
from typing import List, Optional, Dict, Any
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

from book_sources.base import BookSourceInterface, SearchResult
from zlibrary.libasync import AsyncZlib
from zlibrary.exception import LoginFailed, EmptyQueryError, ParseError

class ZLibrarySource(BookSourceInterface):
    """
    Z-Library book source adapter
    
    Characteristics:
    - High priority (primary source)
    - Fast response (2-5 seconds)
    - Multiple formats (PDF, EPUB, MOBI)
    - Requires authentication
    - Large book database (22M+ books)
    """
    
    def __init__(self, account_pool=None):
        """
        Initialize Z-Library source
        
        Args:
            account_pool: Optional account pool for multi-account support
        """
        self.account_pool = account_pool
        self.client = None
        self.authenticated = False
        self._priority = 1  # Highest priority
        self._timeout = 10  # Fast response expected
        
    async def _ensure_authenticated(self):
        """Ensure we have an authenticated Z-Library client"""
        if self.authenticated and self.client:
            return
            
        try:
            # Try to get credentials from environment or account pool
            from dotenv import load_dotenv
            load_dotenv()
            
            email = os.getenv("ZLOGIN")
            password = os.getenv("ZPASSW")
            
            if not email or not password:
                raise ValueError("Z-Library credentials not found in environment")
            
            self.client = AsyncZlib()
            await self.client.login(email, password)
            self.authenticated = True
            
        except Exception as e:
            raise RuntimeError(f"Z-Library authentication failed: {e}")
    
    async def search(self, query: str, **kwargs) -> SearchResult:
        """
        Search Z-Library for books
        
        Args:
            query: Search query (title, author, or combined)
            **kwargs: Additional parameters (limit_results, etc.)
            
        Returns:
            SearchResult: Standardized search result
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            
            if len(query.strip()) < 2:
                raise ValueError("Query too short (minimum 2 characters)")
                
            # Ensure authentication
            await self._ensure_authenticated()
            
            # Perform search
            limit = kwargs.get('limit_results', 10)
            search_results = await self.client.search(q=query.strip(), count=limit)
            await search_results.init()
            
            response_time = time.time() - start_time
            
            if not search_results.result:
                return SearchResult(
                    found=False,
                    source=self.get_source_name(),
                    response_time=response_time,
                    metadata={"query": query, "total_results": 0}
                )
            
            # Get first result for primary response
            first_book = search_results.result[0]
            
            # Try to get detailed information
            book_details = {}
            try:
                detailed = await first_book.fetch()
                book_details = detailed if isinstance(detailed, dict) else {}
            except:
                # Use basic information if detailed fetch fails
                book_details = {
                    "name": getattr(first_book, 'name', ''),
                    "authors": getattr(first_book, 'authors', ''),
                    "download_url": getattr(first_book, 'download_url', ''),
                }
            
            return SearchResult(
                found=True,
                title=book_details.get('name', ''),
                author=book_details.get('authors', ''),
                source=self.get_source_name(),
                download_url=book_details.get('download_url', ''),
                file_id=getattr(first_book, 'id', ''),
                confidence=0.9,  # High confidence for Z-Library
                response_time=response_time,
                metadata={
                    "query": query,
                    "total_results": len(search_results.result),
                    "book_details": book_details,
                    "all_results": [
                        {
                            "title": getattr(book, 'name', ''),
                            "author": getattr(book, 'authors', ''),
                            "id": getattr(book, 'id', '')
                        }
                        for book in search_results.result[:5]  # Top 5 results
                    ]
                }
            )
            
        except EmptyQueryError:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={"error": "Empty query", "query": query}
            )
            
        except LoginFailed as e:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={"error": f"Authentication failed: {e}", "query": query}
            )
            
        except ParseError as e:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={"error": f"Parse error: {e}", "query": query}
            )
            
        except asyncio.TimeoutError:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={"error": "Search timeout", "query": query}
            )
            
        except Exception as e:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={"error": f"Unexpected error: {e}", "query": query}
            )
    
    def get_priority(self) -> int:
        """Z-Library has highest priority (primary source)"""
        return self._priority
    
    def get_timeout(self) -> int:
        """Z-Library should respond quickly"""
        return self._timeout
    
    def supports_language(self, language: str) -> bool:
        """Z-Library supports many languages"""
        supported = [
            'en', 'ru', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko',
            'ar', 'hi', 'pl', 'nl', 'sv', 'no', 'da', 'fi', 'tr', 'he',
            'th', 'vi', 'id', 'ms', 'tl', 'cs', 'sk', 'hu', 'ro', 'bg',
            'hr', 'sr', 'sl', 'et', 'lv', 'lt', 'mt', 'ga', 'cy', 'eu',
            'ca', 'gl', 'ast', 'an', 'oc', 'co', 'sc', 'rm', 'fur', 'lij'
        ]
        return language.lower() in supported
    
    def get_source_name(self) -> str:
        """Source identifier"""
        return "zlibrary"
    
    def get_supported_formats(self) -> List[str]:
        """Z-Library supports multiple formats"""
        return ['pdf', 'epub', 'mobi', 'djvu', 'fb2', 'txt', 'rtf', 'doc', 'docx']
    
    def get_supported_languages(self) -> List[str]:
        """Get comprehensive list of supported languages"""
        return [
            'en', 'ru', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko',
            'ar', 'hi', 'pl', 'nl', 'sv', 'no', 'da', 'fi', 'tr', 'he',
            'th', 'vi', 'id', 'ms', 'tl', 'cs', 'sk', 'hu', 'ro', 'bg'
        ]
    
    async def health_check(self) -> bool:
        """Check Z-Library availability"""
        try:
            await self._ensure_authenticated()
            # Try a simple search
            result = await asyncio.wait_for(
                self.search("test", limit_results=1),
                timeout=5.0
            )
            return True
        except:
            return False
    
    async def cleanup(self):
        """Clean up resources"""
        if self.client:
            try:
                await self.client.logout()
            except:
                pass
            finally:
                self.authenticated = False
                self.client = None