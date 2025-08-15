#!/usr/bin/env python3
"""
Book Extraction Service
Orchestrates extraction across multiple sources with fallback and quality control
"""

import asyncio
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.interfaces.extractor import (
    IBookExtractor,
    ExtractionRequest,
    ExtractionResult,
    ExtractionStatus
)


class ExtractionService:
    """
    Orchestrates book extraction across multiple sources.
    Implements fallback strategies and quality control.
    """
    
    def __init__(self,
                 extractors: Dict[str, IBookExtractor],
                 quality_threshold: float = 0.85,
                 max_retries: int = 3,
                 enable_fallback: bool = True):
        """
        Initialize extraction service.
        
        Args:
            extractors: Dictionary of source_id -> extractor instances
            quality_threshold: Minimum confidence score for acceptance
            max_retries: Maximum extraction attempts per source
            enable_fallback: Enable fallback to other sources on failure
        """
        self._extractors = extractors
        self._quality_threshold = quality_threshold
        self._max_retries = max_retries
        self._enable_fallback = enable_fallback
        self._metrics = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "fallback_used": 0,
            "source_stats": {}
        }
    
    async def extract_book(self,
                          source: Optional[str] = None,
                          category: Optional[str] = None,
                          session_id: Optional[str] = None,
                          timeout: float = 10.0) -> ExtractionResult:
        """
        Extract a book with automatic source selection and fallback.
        
        Args:
            source: Specific source to use (optional)
            category: Category filter (optional)
            session_id: Session identifier for tracking
            timeout: Maximum time for extraction
            
        Returns:
            ExtractionResult with book or error information
        """
        start_time = datetime.now()
        self._metrics["total_extractions"] += 1
        
        # Create extraction request
        request = ExtractionRequest(
            source_id=source or "auto",
            category=category,
            session_id=session_id,
            timeout=timeout
        )
        
        # Determine extraction order
        if source and source in self._extractors:
            # Use specific source
            extractors_to_try = [(source, self._extractors[source])]
        else:
            # Auto-select based on priority
            extractors_to_try = self._get_prioritized_extractors(category)
        
        # Try extraction with each source
        last_error = None
        for source_id, extractor in extractors_to_try:
            # Check if source is healthy
            if not await self._is_source_healthy(extractor):
                continue
            
            # Attempt extraction with retries
            result = await self._extract_with_retries(
                extractor, request, source_id
            )
            
            # Check if result meets quality threshold
            if result.is_successful and result.confidence >= self._quality_threshold:
                self._metrics["successful_extractions"] += 1
                self._update_source_stats(source_id, True)
                return result
            
            # Store error for potential return
            last_error = result.error or "Quality threshold not met"
            
            # If fallback disabled, return first result
            if not self._enable_fallback:
                break
        
        # All sources failed
        self._metrics["failed_extractions"] += 1
        
        extraction_time = (datetime.now() - start_time).total_seconds()
        return ExtractionResult(
            status=ExtractionStatus.FAILURE,
            book=None,
            extraction_time=extraction_time,
            confidence=0.0,
            source="multi",
            error=last_error or "All extraction sources failed",
            metrics={
                "attempted_sources": len(extractors_to_try),
                "session_id": session_id
            }
        )
    
    async def extract_batch(self,
                           requests: List[Dict[str, Any]],
                           concurrency: int = 5) -> List[ExtractionResult]:
        """
        Extract multiple books concurrently.
        
        Args:
            requests: List of extraction request parameters
            concurrency: Maximum concurrent extractions
            
        Returns:
            List of extraction results
        """
        semaphore = asyncio.Semaphore(concurrency)
        
        async def extract_with_semaphore(req_params):
            async with semaphore:
                return await self.extract_book(**req_params)
        
        tasks = [extract_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for result in results:
            if isinstance(result, Exception):
                final_results.append(
                    ExtractionResult(
                        status=ExtractionStatus.FAILURE,
                        book=None,
                        extraction_time=0.0,
                        confidence=0.0,
                        source="batch",
                        error=str(result)
                    )
                )
            else:
                final_results.append(result)
        
        return final_results
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics.
        
        Returns:
            Dictionary with extraction statistics
        """
        return {
            **self._metrics,
            "success_rate": (
                self._metrics["successful_extractions"] / 
                max(self._metrics["total_extractions"], 1)
            ),
            "available_sources": list(self._extractors.keys()),
            "quality_threshold": self._quality_threshold
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all extraction sources.
        
        Returns:
            Dictionary of source_id -> health status
        """
        health_status = {}
        
        for source_id, extractor in self._extractors.items():
            try:
                health_status[source_id] = await extractor.health_check()
            except Exception:
                health_status[source_id] = False
        
        return health_status
    
    def _get_prioritized_extractors(self, 
                                   category: Optional[str] = None) -> List[tuple]:
        """
        Get extractors sorted by priority and category support.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of (source_id, extractor) tuples sorted by priority
        """
        extractors = []
        
        for source_id, extractor in self._extractors.items():
            # Skip if category not supported
            if category and not extractor.supports_category(category):
                continue
            
            extractors.append((source_id, extractor, extractor.priority))
        
        # Sort by priority (higher first)
        extractors.sort(key=lambda x: x[2], reverse=True)
        
        # Return without priority value
        return [(s, e) for s, e, _ in extractors]
    
    async def _extract_with_retries(self,
                                   extractor: IBookExtractor,
                                   request: ExtractionRequest,
                                   source_id: str) -> ExtractionResult:
        """
        Attempt extraction with retries on failure.
        
        Args:
            extractor: Extractor instance
            request: Extraction request
            source_id: Source identifier for metrics
            
        Returns:
            ExtractionResult from successful attempt or last failure
        """
        last_result = None
        
        for attempt in range(self._max_retries):
            try:
                # Add timeout enforcement
                result = await asyncio.wait_for(
                    extractor.extract(request),
                    timeout=request.timeout
                )
                
                # Return if successful
                if result.is_successful:
                    return result
                
                last_result = result
                
                # Exponential backoff for retries
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    
            except asyncio.TimeoutError:
                last_result = ExtractionResult(
                    status=ExtractionStatus.FAILURE,
                    book=None,
                    extraction_time=request.timeout,
                    confidence=0.0,
                    source=source_id,
                    error=f"Timeout after {request.timeout}s"
                )
            except Exception as e:
                last_result = ExtractionResult(
                    status=ExtractionStatus.FAILURE,
                    book=None,
                    extraction_time=0.0,
                    confidence=0.0,
                    source=source_id,
                    error=f"Extraction error: {str(e)}"
                )
        
        return last_result or ExtractionResult(
            status=ExtractionStatus.FAILURE,
            book=None,
            extraction_time=0.0,
            confidence=0.0,
            source=source_id,
            error="Maximum retries exceeded"
        )
    
    async def _is_source_healthy(self, extractor: IBookExtractor) -> bool:
        """
        Check if source is healthy with timeout.
        
        Args:
            extractor: Extractor instance
            
        Returns:
            True if source is healthy
        """
        try:
            return await asyncio.wait_for(
                extractor.health_check(),
                timeout=2.0
            )
        except (asyncio.TimeoutError, Exception):
            return False
    
    def _update_source_stats(self, source_id: str, success: bool):
        """
        Update source-specific statistics.
        
        Args:
            source_id: Source identifier
            success: Whether extraction was successful
        """
        if source_id not in self._metrics["source_stats"]:
            self._metrics["source_stats"][source_id] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0
            }
        
        stats = self._metrics["source_stats"][source_id]
        stats["attempts"] += 1
        
        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1