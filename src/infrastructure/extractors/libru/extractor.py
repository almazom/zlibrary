#!/usr/bin/env python3
"""
Lib.ru Book Extractor Implementation
Concrete implementation of IBookExtractor for lib.ru source
"""

import asyncio
import aiohttp
import random
import re
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.core.interfaces.extractor import (
    IBookExtractor,
    ExtractionRequest,
    ExtractionResult,
    ExtractionStatus,
    BookEntity
)


class LibRuExtractor(IBookExtractor):
    """Lib.ru concrete implementation with clean separation of concerns"""
    
    CATEGORIES = {
        "RUFANT": "https://lib.ru/RUFANT",      # Russian Fantasy
        "INOFANT": "https://lib.ru/INOFANT",    # Foreign Fantasy  
        "RAZNOE": "https://lib.ru/RAZNOE"       # Miscellaneous
    }
    
    def __init__(self, 
                 http_client: Optional[aiohttp.ClientSession] = None,
                 cache_manager: Optional[Any] = None,
                 encoding: str = "koi8-r"):
        """
        Initialize LibRu extractor with injected dependencies.
        
        Args:
            http_client: Reusable HTTP client session
            cache_manager: Cache manager for deduplication
            encoding: Source encoding (default: koi8-r)
        """
        self._http_client = http_client
        self._cache = cache_manager
        self._encoding = encoding
        self._session_authors = set()  # Track used authors in session
        self._owns_http_client = False
        
        # If no HTTP client provided, we'll create our own
        if not self._http_client:
            self._owns_http_client = True
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self._owns_http_client:
            timeout = aiohttp.ClientTimeout(total=8)
            self._http_client = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._owns_http_client and self._http_client:
            await self._http_client.close()
    
    @property
    def source_id(self) -> str:
        """Unique identifier for this extractor"""
        return "libru"
    
    @property
    def priority(self) -> int:
        """High priority for Russian books"""
        return 90
    
    def get_source_info(self) -> Dict[str, Any]:
        """Return source metadata"""
        return {
            "name": "Lib.ru - Russian Literature Library",
            "url": "https://lib.ru",
            "categories": list(self.CATEGORIES.keys()),
            "languages": ["ru", "en"],
            "rate_limit": 10,  # Requests per second
            "capabilities": {
                "search": False,
                "random": True,
                "categories": True,
                "full_text": True
            }
        }
    
    def supports_category(self, category: str) -> bool:
        """Check if category is supported"""
        return category.upper() in self.CATEGORIES
    
    async def health_check(self) -> bool:
        """Check if lib.ru is accessible"""
        try:
            if not self._http_client:
                return False
                
            async with self._http_client.get("https://lib.ru") as response:
                return response.status == 200
        except Exception:
            return False
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract a random book from lib.ru"""
        start_time = datetime.now()
        
        try:
            # Check cache first if available
            if self._cache:
                cached = await self._check_cache(request)
                if cached:
                    return cached
            
            # Select category
            category = request.category or self._select_random_category()
            if not self.supports_category(category):
                return self._create_error_result(
                    f"Unsupported category: {category}",
                    start_time
                )
            
            # Extract book from category
            book = await self._extract_from_category(category)
            
            if not book:
                return self._create_error_result(
                    "No book found in category",
                    start_time
                )
            
            # Create successful result
            extraction_time = (datetime.now() - start_time).total_seconds()
            result = ExtractionResult(
                status=ExtractionStatus.SUCCESS,
                book=book,
                extraction_time=extraction_time,
                confidence=0.95,  # High confidence for static HTML
                source=self.source_id,
                metrics={
                    "category": category,
                    "encoding": self._encoding,
                    "session_authors_count": len(self._session_authors)
                }
            )
            
            # Cache result if available
            if self._cache:
                await self._cache_result(result)
            
            return result
            
        except asyncio.TimeoutError:
            return self._create_error_result(
                "Extraction timeout",
                start_time
            )
        except Exception as e:
            return self._create_error_result(
                f"Extraction failed: {str(e)}",
                start_time
            )
    
    async def _extract_from_category(self, category: str) -> Optional[BookEntity]:
        """Extract a random book from specific category"""
        category_url = self.CATEGORIES[category]
        
        # Get author list
        authors = await self._fetch_authors(category_url)
        if not authors:
            return None
        
        # Select random unused author
        unused_authors = [a for a in authors if a['name'] not in self._session_authors]
        if not unused_authors:
            # Reset session if all authors used
            self._session_authors.clear()
            unused_authors = authors
        
        author = random.choice(unused_authors)
        self._session_authors.add(author['name'])
        
        # Get books from author
        author_directory = author['url'].strip('/').split('/')[-1]  # Extract directory from URL
        author_url = f"{category_url}/{author_directory}/"
        books = await self._fetch_author_books(author_url)
        if not books:
            return None
        
        # Select random book
        book_data = random.choice(books)
        
        # Create book entity
        return BookEntity(
            title=book_data['title'],
            author=author['name'],
            source_url=book_data['url'],
            language="ru",
            metadata={
                "category": category,
                "author_url": author['url'],
                "extraction_method": "random"
            }
        )
    
    async def _fetch_authors(self, category_url: str) -> List[Dict[str, str]]:
        """Fetch author list from category page"""
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")
            
        async with self._http_client.get(category_url) as response:
            if response.status != 200:
                return []
            
            html = await response.text(encoding=self._encoding)
            
            # Parse author links
            authors = []
            # Use working pattern from original extractor
            pattern = r'<A HREF=([A-Z][A-Z_0-9]*)/><b>([^<]+)</b></A>'
            
            for match in re.finditer(pattern, html):
                directory, name = match.groups()
                authors.append({
                    'url': f'/{directory}/',
                    'name': name.strip()
                })
            
            return authors
    
    async def _fetch_author_books(self, author_url: str) -> List[Dict[str, str]]:
        """Fetch book list from author page"""
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")
            
        async with self._http_client.get(author_url) as response:
            if response.status != 200:
                return []
            
            html = await response.text(encoding=self._encoding)
            
            # Parse book links
            books = []
            # Use working pattern from original extractor
            pattern = r'<A HREF=([^>]+\.txt)><b>([^<]+)</b></A>'
            
            for match in re.finditer(pattern, html):
                filename, title = match.groups()
                # Clean up title (remove numbering, extra spaces)
                clean_title = re.sub(r'^\d+\.\s*', '', title.strip())
                clean_title = re.sub(r'\s+', ' ', clean_title)
                
                books.append({
                    'url': f"{author_url}/{filename}",
                    'title': clean_title
                })
            
            return books
    
    def _select_random_category(self) -> str:
        """Select random category with weighted distribution"""
        # Weight towards variety
        weights = {
            "RUFANT": 0.4,   # 40% Russian Fantasy
            "INOFANT": 0.4,  # 40% Foreign Fantasy
            "RAZNOE": 0.2    # 20% Miscellaneous
        }
        
        categories = list(weights.keys())
        probabilities = list(weights.values())
        
        return random.choices(categories, weights=probabilities)[0]
    
    def _create_error_result(self, error_msg: str, start_time: datetime) -> ExtractionResult:
        """Create error extraction result"""
        extraction_time = (datetime.now() - start_time).total_seconds()
        
        return ExtractionResult(
            status=ExtractionStatus.FAILURE,
            book=None,
            extraction_time=extraction_time,
            confidence=0.0,
            source=self.source_id,
            error=error_msg,
            metrics={
                "session_authors_count": len(self._session_authors)
            }
        )
    
    async def _check_cache(self, request: ExtractionRequest) -> Optional[ExtractionResult]:
        """Check cache for existing extraction"""
        if not self._cache:
            return None
        
        # Generate cache key from request
        cache_key = self._generate_cache_key(request)
        
        # Check cache
        cached = await self._cache.get(cache_key)
        if cached:
            # Update status to indicate cached result
            cached.status = ExtractionStatus.CACHED
            return cached
        
        return None
    
    async def _cache_result(self, result: ExtractionResult):
        """Cache extraction result"""
        if not self._cache or not result.is_successful:
            return
        
        # Generate cache key
        cache_key = f"{self.source_id}:{result.book.title}:{result.book.author}"
        
        # Store in cache
        await self._cache.set(cache_key, result, ttl=3600)  # 1 hour TTL
    
    def _generate_cache_key(self, request: ExtractionRequest) -> str:
        """Generate cache key from request"""
        key_parts = [
            self.source_id,
            request.category or "any",
            request.session_id or "default"
        ]
        
        # Add filters if present
        if request.filters:
            filter_str = ":".join(f"{k}={v}" for k, v in sorted(request.filters.items()))
            key_parts.append(filter_str)
        
        # Create hash for consistent key
        key_str = ":".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()