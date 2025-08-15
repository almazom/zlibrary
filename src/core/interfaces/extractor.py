#!/usr/bin/env python3
"""
Core Book Extractor Interface
Defines the contract all extraction engines must implement
Part of the trunk - changes require architectural review
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ExtractionStatus(Enum):
    """Extraction result status"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CACHED = "cached"


@dataclass(frozen=True)
class BookEntity:
    """Immutable book domain entity"""
    title: str
    author: str
    source_url: str
    language: str = "unknown"
    isbn: Optional[str] = None
    year: Optional[int] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate book entity"""
        if not self.title:
            raise ValueError("Book title cannot be empty")
        if not self.source_url:
            raise ValueError("Source URL cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "title": self.title,
            "author": self.author,
            "source_url": self.source_url,
            "language": self.language,
            "isbn": self.isbn,
            "year": self.year,
            "publisher": self.publisher,
            "description": self.description,
            "metadata": self.metadata
        }


@dataclass(frozen=True)
class ExtractionRequest:
    """Immutable extraction request"""
    source_id: str
    category: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    priority: int = 0  # Higher priority requests processed first
    timeout: float = 10.0  # Maximum extraction time in seconds
    
    def __post_init__(self):
        """Validate request"""
        if not self.source_id:
            raise ValueError("Source ID cannot be empty")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")


@dataclass(frozen=True)
class ExtractionResult:
    """Immutable extraction result"""
    status: ExtractionStatus
    book: Optional[BookEntity]
    extraction_time: float
    confidence: float
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate result"""
        if self.status == ExtractionStatus.SUCCESS and not self.book:
            raise ValueError("Successful extraction must include book entity")
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("Confidence must be between 0 and 1")
        if self.extraction_time < 0:
            raise ValueError("Extraction time cannot be negative")
    
    @property
    def is_successful(self) -> bool:
        """Check if extraction was successful"""
        return self.status in [ExtractionStatus.SUCCESS, ExtractionStatus.CACHED]
    
    @property
    def is_high_confidence(self, threshold: float = 0.85) -> bool:
        """Check if result meets confidence threshold"""
        return self.confidence >= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "status": self.status.value,
            "book": self.book.to_dict() if self.book else None,
            "extraction_time": self.extraction_time,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "metrics": self.metrics
        }


class IBookExtractor(ABC):
    """Core extraction interface - all extractors must implement"""
    
    @abstractmethod
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
        Extract a book from the source.
        
        Args:
            request: Extraction request with source and filters
            
        Returns:
            ExtractionResult with book entity or error
            
        Raises:
            Should not raise exceptions - errors go in ExtractionResult
        """
        pass
    
    @abstractmethod
    def get_source_info(self) -> Dict[str, Any]:
        """
        Return source metadata.
        
        Returns:
            Dictionary with source information:
            - name: Source display name
            - url: Base URL
            - categories: List of supported categories
            - languages: List of supported languages
            - rate_limit: Requests per second limit
            - capabilities: Feature support flags
        """
        pass
    
    @abstractmethod
    def supports_category(self, category: str) -> bool:
        """
        Check if category is supported.
        
        Args:
            category: Category identifier
            
        Returns:
            True if category is supported
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the source is accessible.
        
        Returns:
            True if source is healthy and accessible
        """
        pass
    
    @property
    @abstractmethod
    def source_id(self) -> str:
        """
        Unique identifier for this extractor.
        
        Returns:
            Source identifier string
        """
        pass
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Extractor priority for fallback ordering.
        
        Returns:
            Priority value (higher = preferred)
        """
        pass