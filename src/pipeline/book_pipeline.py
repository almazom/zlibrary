#!/usr/bin/env python3
"""
BOOK SEARCH PIPELINE - Multi-source orchestrator with intelligent fallback
TDD Implementation: Configurable fallback chains with Claude normalization
"""
import asyncio
import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

from book_sources.base import BookSourceInterface, SearchResult
from book_sources.zlibrary_source import ZLibrarySource
from book_sources.flibusta_source import FlibustaSource
from claude_sdk_normalizer import ClaudeSDKNormalizer

@dataclass
class PipelineConfig:
    """Configuration for the book search pipeline"""
    fallback_chain: List[str] = field(default_factory=lambda: ["zlibrary", "flibusta"])
    timeout_per_source: int = 30
    max_total_timeout: int = 120
    cache_enabled: bool = True
    parallel_search: bool = False
    enable_claude_normalization: bool = True
    language_aware_routing: bool = True

class BookSearchPipeline:
    """
    Multi-source book search pipeline with intelligent fallback
    
    Features:
    - Configurable source chains
    - Claude SDK normalization
    - Language-aware routing
    - Performance monitoring
    - Graceful error handling
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the book search pipeline
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        self.sources: Dict[str, BookSourceInterface] = {}
        self.normalizer = None
        self.stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "source_stats": {},
            "average_response_time": 0.0
        }
        
        # Initialize components
        self._initialize_sources()
        self._initialize_normalizer()
    
    def _initialize_sources(self):
        """Initialize all available book sources"""
        # Initialize Z-Library
        if "zlibrary" in self.config.fallback_chain:
            try:
                self.sources["zlibrary"] = ZLibrarySource()
            except Exception as e:
                print(f"Warning: Failed to initialize Z-Library: {e}")
        
        # Initialize Flibusta
        if "flibusta" in self.config.fallback_chain:
            try:
                self.sources["flibusta"] = FlibustaSource()
            except Exception as e:
                print(f"Warning: Failed to initialize Flibusta: {e}")
    
    def _initialize_normalizer(self):
        """Initialize Claude SDK normalizer if enabled"""
        if self.config.enable_claude_normalization:
            try:
                self.normalizer = ClaudeSDKNormalizer()
            except Exception as e:
                print(f"Warning: Failed to initialize Claude normalizer: {e}")
                self.normalizer = None
    
    async def search_book(self, query: str, **kwargs) -> SearchResult:
        """
        Main search method with full pipeline
        
        Args:
            query: Book search query (can be fuzzy)
            **kwargs: Additional parameters
            
        Returns:
            SearchResult: Best result from available sources
        """
        start_time = time.time()
        self.stats["total_searches"] += 1
        
        try:
            # Validate input
            self._validate_query(query)
            
            # Step 1: Normalize query with Claude if enabled
            normalized_queries = await self._normalize_query(query)
            
            # Step 2: Determine optimal fallback chain
            optimal_chain = self._get_optimal_chain(query, **kwargs)
            
            # Step 3: Search through sources in order
            for source_name in optimal_chain:
                if source_name not in self.sources:
                    continue
                
                source = self.sources[source_name]
                
                # Try each normalized query
                for norm_query in normalized_queries:
                    try:
                        result = await self._search_with_timeout(source, norm_query, **kwargs)
                        
                        if result.found:
                            # Success! Update stats and return
                            self._update_stats(source_name, result, time.time() - start_time)
                            return result
                        
                    except Exception as e:
                        print(f"Source {source_name} failed for query '{norm_query}': {e}")
                        continue
            
            # No sources found the book
            total_time = time.time() - start_time
            return SearchResult(
                found=False,
                source="pipeline",
                response_time=total_time,
                metadata={
                    "original_query": query,
                    "normalized_queries": normalized_queries,
                    "sources_tried": optimal_chain,
                    "total_time": total_time
                }
            )
            
        except ValueError as e:
            # Input validation error
            return SearchResult(
                found=False,
                source="pipeline",
                response_time=time.time() - start_time,
                metadata={
                    "error": f"Invalid input: {e}",
                    "original_query": query
                }
            )
        
        except Exception as e:
            # Unexpected error
            return SearchResult(
                found=False,
                source="pipeline",
                response_time=time.time() - start_time,
                metadata={
                    "error": f"Pipeline error: {e}",
                    "original_query": query
                }
            )
    
    def _validate_query(self, query: str):
        """Validate search query"""
        if not query:
            raise ValueError("Query cannot be empty")
        
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty or whitespace only")
        
        if len(query) < 2:
            raise ValueError("Query too short (minimum 2 characters)")
        
        if len(query) > 500:
            raise ValueError("Query too long (maximum 500 characters)")
        
        # Check for potentially invalid patterns
        if re.match(r'^[!@#$%^&*()_+\-=\[\]{}|;\':",./<>?`~]+$', query):
            raise ValueError("Query contains only special characters")
    
    async def _normalize_query(self, query: str) -> List[str]:
        """
        Normalize query using Claude SDK
        
        Returns:
            List[str]: List of normalized queries to try
        """
        queries = [query]  # Always include original
        
        if not self.normalizer:
            return queries
        
        try:
            result = self.normalizer.normalize_book_title(query)
            
            if result.get("success"):
                search_strings = result.get("search_strings", {})
                
                # Add normalized strings
                if "original" in search_strings and search_strings["original"]:
                    queries.append(search_strings["original"])
                
                if "russian" in search_strings and search_strings["russian"]:
                    queries.append(search_strings["russian"])
                
                # Add main normalized query if available
                if "normalized_query" in result and result["normalized_query"]:
                    queries.append(result["normalized_query"])
        
        except Exception as e:
            print(f"Query normalization failed: {e}")
        
        # Remove duplicates while preserving order
        unique_queries = []
        seen = set()
        for q in queries:
            if q and q.lower() not in seen:
                unique_queries.append(q)
                seen.add(q.lower())
        
        return unique_queries
    
    def _get_optimal_chain(self, query: str, **kwargs) -> List[str]:
        """
        Determine optimal fallback chain based on query and context
        
        Args:
            query: Search query
            **kwargs: Additional context (language_hint, time_limit, etc.)
            
        Returns:
            List[str]: Ordered list of source names to try
        """
        # Start with configured chain
        chain = self.config.fallback_chain.copy()
        
        if not self.config.language_aware_routing:
            return chain
        
        # Language-aware routing
        detected_language = self._detect_language(query)
        
        if detected_language == "ru" and "flibusta" in chain and "zlibrary" in chain:
            # Russian text - prioritize Flibusta
            chain = ["flibusta", "zlibrary"]
        
        # Time constraint routing
        time_limit = kwargs.get("max_time", 0)
        if time_limit > 0 and time_limit < 15:
            # Fast search - only fast sources
            chain = [s for s in chain if s == "zlibrary"]
        
        return [s for s in chain if s in self.sources]
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Count Cyrillic vs Latin characters
        cyrillic_chars = len(re.findall(r'[а-яёА-ЯЁ]', text))
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if cyrillic_chars > latin_chars:
            return "ru"
        elif latin_chars > cyrillic_chars:
            return "en"
        else:
            return "mixed"
    
    async def _search_with_timeout(self, source: BookSourceInterface, query: str, **kwargs) -> SearchResult:
        """Search with source-specific timeout"""
        timeout = min(source.get_timeout(), self.config.timeout_per_source)
        
        try:
            return await asyncio.wait_for(source.search(query, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            return SearchResult(
                found=False,
                source=source.get_source_name(),
                response_time=timeout,
                metadata={
                    "error": f"Timeout after {timeout} seconds",
                    "query": query
                }
            )
    
    def _update_stats(self, source_name: str, result: SearchResult, total_time: float):
        """Update pipeline statistics"""
        if result.found:
            self.stats["successful_searches"] += 1
        
        if source_name not in self.stats["source_stats"]:
            self.stats["source_stats"][source_name] = {
                "attempts": 0,
                "successes": 0,
                "total_time": 0.0
            }
        
        stats = self.stats["source_stats"][source_name]
        stats["attempts"] += 1
        if result.found:
            stats["successes"] += 1
        stats["total_time"] += result.response_time
        
        # Update average response time
        total_searches = self.stats["total_searches"]
        if total_searches > 1:
            prev_avg = self.stats["average_response_time"]
            self.stats["average_response_time"] = (prev_avg * (total_searches - 1) + total_time) / total_searches
        else:
            self.stats["average_response_time"] = total_time
    
    def get_fallback_chain(self) -> List[str]:
        """Get current fallback chain configuration"""
        return self.config.fallback_chain.copy()
    
    def get_optimal_chain_for_query(self, query: str) -> List[str]:
        """Get optimal chain for specific query (for testing)"""
        return self._get_optimal_chain(query)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        stats = self.stats.copy()
        
        # Calculate success rates
        for source_name, source_stats in stats["source_stats"].items():
            if source_stats["attempts"] > 0:
                source_stats["success_rate"] = source_stats["successes"] / source_stats["attempts"]
                source_stats["average_response_time"] = source_stats["total_time"] / source_stats["attempts"]
            else:
                source_stats["success_rate"] = 0.0
                source_stats["average_response_time"] = 0.0
        
        # Overall success rate
        if stats["total_searches"] > 0:
            stats["overall_success_rate"] = stats["successful_searches"] / stats["total_searches"]
        else:
            stats["overall_success_rate"] = 0.0
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all sources"""
        health_status = {"pipeline": "healthy", "sources": {}}
        
        for source_name, source in self.sources.items():
            try:
                is_healthy = await source.health_check()
                health_status["sources"][source_name] = "healthy" if is_healthy else "unhealthy"
            except Exception as e:
                health_status["sources"][source_name] = f"error: {e}"
        
        # Check if normalizer is working
        if self.normalizer:
            try:
                test_result = self.normalizer.normalize_book_title("test")
                health_status["claude_normalizer"] = "healthy" if test_result else "unhealthy"
            except:
                health_status["claude_normalizer"] = "unhealthy"
        else:
            health_status["claude_normalizer"] = "disabled"
        
        return health_status
    
    async def cleanup(self):
        """Clean up resources"""
        for source in self.sources.values():
            if hasattr(source, 'cleanup'):
                try:
                    await source.cleanup()
                except:
                    pass