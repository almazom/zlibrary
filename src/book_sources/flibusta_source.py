#!/usr/bin/env python3
"""
FLIBUSTA SOURCE ADAPTER - Fallback book source with AI normalization
TDD Implementation: AI-powered, Telegram-based book search
"""
import time
import asyncio
import aiohttp
import json
from typing import List, Optional, Dict, Any
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

from book_sources.base import BookSourceInterface, SearchResult

class FlibustaSource(BookSourceInterface):
    """
    Flibusta book source adapter
    
    Characteristics:
    - Lower priority (fallback source)
    - Slower response (25-35 seconds due to AI processing)
    - EPUB format only
    - Built-in AI normalization
    - Telegram-based search
    - Strong Russian language support
    """
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize Flibusta source
        
        Args:
            api_key: Flibusta API key
            base_url: Flibusta service URL
        """
        self.api_key = api_key or os.getenv("FLIBUSTA_API_KEY", "6fa3604591174567a249db854492489d")
        self.base_url = base_url or os.getenv("FLIBUSTA_BASE_URL", "http://localhost:8001")
        self._priority = 2  # Lower priority (fallback)
        self._timeout = 40  # Longer timeout for AI processing
        
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def search(self, query: str, **kwargs) -> SearchResult:
        """
        Search Flibusta for books with AI normalization
        
        Args:
            query: Search query (can be fuzzy, will be normalized by AI)
            **kwargs: Additional parameters
            
        Returns:
            SearchResult: Standardized search result
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            
            if len(query.strip()) < 1:
                raise ValueError("Query too short")
                
            if len(query.strip()) > 500:
                raise ValueError("Query too long (maximum 500 characters)")
            
            # Prepare request payload
            payload = {"query": query.strip()}
            
            # Make async HTTP request to Flibusta service
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/v1/books/find-epub",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        return SearchResult(
                            found=True,
                            title=self._extract_title_from_filename(data.get('file_name', '')),
                            author=self._extract_author_from_response(data),
                            source=self.get_source_name(),
                            download_url=data.get('download_url', ''),
                            file_id=data.get('file_id', ''),
                            confidence=0.8,  # Good confidence for AI-processed results
                            response_time=response_time,
                            metadata={
                                "query": query,
                                "file_name": data.get('file_name', ''),
                                "created_at": data.get('created_at', ''),
                                "ai_processed": True,
                                "format": "epub"
                            }
                        )
                    
                    elif response.status == 404:
                        # Book not found
                        return SearchResult(
                            found=False,
                            source=self.get_source_name(),
                            response_time=response_time,
                            metadata={
                                "query": query,
                                "error": "Book not found",
                                "ai_processed": True
                            }
                        )
                    
                    elif response.status == 401:
                        return SearchResult(
                            found=False,
                            source=self.get_source_name(),
                            response_time=response_time,
                            metadata={
                                "query": query,
                                "error": "Authentication failed - invalid API key"
                            }
                        )
                    
                    elif response.status == 422:
                        error_data = await response.json()
                        return SearchResult(
                            found=False,
                            source=self.get_source_name(),
                            response_time=response_time,
                            metadata={
                                "query": query,
                                "error": f"Invalid query: {error_data.get('detail', 'Unknown validation error')}"
                            }
                        )
                    
                    else:
                        # Other HTTP errors
                        error_text = await response.text()
                        return SearchResult(
                            found=False,
                            source=self.get_source_name(),
                            response_time=response_time,
                            metadata={
                                "query": query,
                                "error": f"HTTP {response.status}: {error_text}"
                            }
                        )
        
        except asyncio.TimeoutError:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={
                    "query": query,
                    "error": f"Timeout after {self._timeout} seconds"
                }
            )
        
        except aiohttp.ClientError as e:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={
                    "query": query,
                    "error": f"Network error: {e}"
                }
            )
        
        except json.JSONDecodeError as e:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={
                    "query": query,
                    "error": f"Invalid JSON response: {e}"
                }
            )
        
        except Exception as e:
            return SearchResult(
                found=False,
                source=self.get_source_name(),
                response_time=time.time() - start_time,
                metadata={
                    "query": query,
                    "error": f"Unexpected error: {e}"
                }
            )
    
    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract clean title from EPUB filename"""
        if not filename:
            return ""
        
        # Remove .epub extension
        title = filename.replace('.epub', '')
        
        # Handle common patterns in Flibusta filenames
        # Example: "dzhordzh_oruell-1984-64eeef25b643b.epub" -> "1984"
        if '-' in title:
            parts = title.split('-')
            # Usually title is in the second part
            if len(parts) >= 2:
                return parts[1].replace('_', ' ').title()
        
        # Fallback: clean up underscores and capitalize
        return title.replace('_', ' ').title()
    
    def _extract_author_from_response(self, data: Dict[str, Any]) -> str:
        """Extract author information from Flibusta response"""
        filename = data.get('file_name', '')
        
        if not filename:
            return ""
        
        # Extract author from filename pattern
        # Example: "dzhordzh_oruell-1984-64eeef25b643b.epub" -> "George Orwell"
        base_name = filename.replace('.epub', '')
        
        if '-' in base_name:
            parts = base_name.split('-')
            author_part = parts[0]
            
            # Convert from transliterated form
            author_mapping = {
                'dzhordzh_oruell': 'George Orwell',
                'lev_tolstoy': 'Leo Tolstoy',
                'fyodor_dostoevsky': 'Fyodor Dostoevsky',
                'aleksandr_pushkin': 'Alexander Pushkin',
                'anton_chekhov': 'Anton Chekhov',
                'mikhail_bulgakov': 'Mikhail Bulgakov',
                'ivan_turgenev': 'Ivan Turgenev',
                'nikolay_gogol': 'Nikolay Gogol'
            }
            
            return author_mapping.get(author_part, author_part.replace('_', ' ').title())
        
        return ""
    
    def get_priority(self) -> int:
        """Flibusta has lower priority (fallback source)"""
        return self._priority
    
    def get_timeout(self) -> int:
        """Flibusta needs longer timeout for AI processing"""
        return self._timeout
    
    def supports_language(self, language: str) -> bool:
        """Flibusta supports Russian and English primarily"""
        supported = ['ru', 'en', 'uk', 'be', 'kk', 'ky', 'tg', 'uz', 'hy', 'ka', 'az']
        return language.lower() in supported
    
    def get_source_name(self) -> str:
        """Source identifier"""
        return "flibusta"
    
    def get_supported_formats(self) -> List[str]:
        """Flibusta provides EPUB format only"""
        return ['epub']
    
    def get_supported_languages(self) -> List[str]:
        """Flibusta focuses on Russian and related languages"""
        return ['ru', 'en', 'uk', 'be', 'kk', 'ky', 'tg', 'uz', 'hy', 'ga', 'az']
    
    def supports_format(self, format_type: str) -> bool:
        """Flibusta only supports EPUB"""
        return format_type.lower() == 'epub'
    
    async def health_check(self) -> bool:
        """Check Flibusta service availability"""
        try:
            timeout = aiohttp.ClientTimeout(total=5.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('status') == 'OK'
                    return False
        except:
            return False
    
    async def download_file(self, file_id: str, save_path: str) -> bool:
        """
        Download EPUB file from Flibusta
        
        Args:
            file_id: File identifier from search result
            save_path: Local path to save the file
            
        Returns:
            bool: True if download successful
        """
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    f"{self.base_url}/api/v1/downloads/{file_id}",
                    headers={"X-API-Key": self.api_key}
                ) as response:
                    if response.status == 200:
                        with open(save_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return True
                    return False
        except:
            return False