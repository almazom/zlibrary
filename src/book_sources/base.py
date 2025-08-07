#!/usr/bin/env python3
"""
BOOK SOURCE INTERFACE - Base class for all book sources
TDD Implementation: Define interface that all tests expect
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import asyncio

@dataclass
class SearchResult:
    """Standard search result across all sources"""
    found: bool
    title: str = ""
    author: str = ""
    source: str = ""
    download_url: str = ""
    file_id: str = ""
    confidence: float = 0.0
    response_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BookSourceInterface(ABC):
    """
    Common interface for all book sources
    
    This interface ensures consistency across Z-Library, Flibusta, 
    and any future book sources we may add to the pipeline.
    """
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> SearchResult:
        """
        Search for a book using the provided query
        
        Args:
            query: Book search query (title, author, or combined)
            **kwargs: Source-specific parameters
            
        Returns:
            SearchResult: Standardized search result
            
        Raises:
            ValueError: If query is invalid
            TimeoutError: If search takes too long
        """
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """
        Get the priority level of this source
        
        Returns:
            int: Priority (1 = highest, lower numbers = higher priority)
        """
        pass
    
    @abstractmethod
    def get_timeout(self) -> int:
        """
        Get the timeout for this source in seconds
        
        Returns:
            int: Timeout in seconds
        """
        pass
    
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """
        Check if this source supports the given language
        
        Args:
            language: Language code (e.g., 'en', 'ru', 'fr')
            
        Returns:
            bool: True if language is supported
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name identifier of this source
        
        Returns:
            str: Source name (e.g., 'zlibrary', 'flibusta')
        """
        pass
    
    def supports_format(self, format_type: str) -> bool:
        """
        Check if this source supports the given file format
        
        Args:
            format_type: File format (e.g., 'pdf', 'epub', 'mobi')
            
        Returns:
            bool: True if format is supported
        """
        # Default implementation - sources can override
        return True
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of all supported languages
        
        Returns:
            List[str]: List of supported language codes
        """
        # Default implementation - sources should override
        return ['en', 'ru']
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of all supported file formats
        
        Returns:
            List[str]: List of supported formats
        """
        # Default implementation - sources should override
        return ['pdf', 'epub', 'mobi']
    
    async def health_check(self) -> bool:
        """
        Check if the source is available and healthy
        
        Returns:
            bool: True if source is healthy
        """
        try:
            # Basic health check - try a simple search with timeout
            result = await asyncio.wait_for(
                self.search("test health check", limit_results=1),
                timeout=5.0
            )
            return True
        except:
            return False
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(priority={self.get_priority()}, timeout={self.get_timeout()}s)"