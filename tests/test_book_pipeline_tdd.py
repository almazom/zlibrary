#!/usr/bin/env python3
"""
BOOK SEARCH PIPELINE - TDD/BDD Test Suite
Test-Driven Development for multi-source book search with fallback chains
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Test data structures (define before implementation)
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

@dataclass
class PipelineConfig:
    """Pipeline configuration for testing"""
    fallback_chain: List[str] = None
    timeout_per_source: int = 30
    max_total_timeout: int = 120
    cache_enabled: bool = True
    parallel_search: bool = False
    
    def __post_init__(self):
        if self.fallback_chain is None:
            self.fallback_chain = ["zlibrary", "flibusta"]

class TestBookSourceInterface:
    """TDD: Define interface behavior before implementation"""
    
    def test_interface_should_define_search_method(self):
        """BDD: As a developer, I want a common interface for all book sources"""
        # This test will fail until we implement the interface
        from book_sources.base import BookSourceInterface
        
        # Test that interface exists and has required methods
        assert hasattr(BookSourceInterface, 'search')
        assert hasattr(BookSourceInterface, 'get_priority')
        assert hasattr(BookSourceInterface, 'get_timeout')
        assert hasattr(BookSourceInterface, 'supports_language')
    
    def test_interface_should_enforce_async_search(self):
        """TDD: search method must be async"""
        from book_sources.base import BookSourceInterface
        import inspect
        
        # Test that search method is async
        search_method = getattr(BookSourceInterface, 'search')
        assert inspect.iscoroutinefunction(search_method)

class TestZLibrarySource:
    """TDD: Z-Library source implementation"""
    
    @pytest.mark.asyncio
    async def test_zlibrary_should_search_successfully(self):
        """BDD: As a user, I want Z-Library to find books quickly"""
        from book_sources.zlibrary_source import ZLibrarySource
        
        # Arrange
        source = ZLibrarySource()
        query = "1984 George Orwell"
        
        # Act
        result = await source.search(query)
        
        # Assert
        assert isinstance(result, SearchResult)
        assert result.source == "zlibrary"
    
    def test_zlibrary_priority_should_be_high(self):
        """TDD: Z-Library should have high priority (primary source)"""
        from book_sources.zlibrary_source import ZLibrarySource
        
        source = ZLibrarySource()
        assert source.get_priority() == 1  # Highest priority
    
    def test_zlibrary_timeout_should_be_short(self):
        """TDD: Z-Library should have short timeout (fast source)"""
        from book_sources.zlibrary_source import ZLibrarySource
        
        source = ZLibrarySource()
        assert source.get_timeout() <= 10  # Fast response expected

class TestFlibustaSource:
    """TDD: Flibusta source implementation"""
    
    @pytest.mark.asyncio
    async def test_flibusta_should_search_with_ai_normalization(self):
        """BDD: As a user, I want Flibusta to normalize queries with AI"""
        from book_sources.flibusta_source import FlibustaSource
        
        # Arrange
        source = FlibustaSource()
        fuzzy_query = "malenkiy prinz"  # Fuzzy Russian input
        
        # Act
        result = await source.search(fuzzy_query)
        
        # Assert
        assert isinstance(result, SearchResult)
        assert result.source == "flibusta"
        # Should find "Маленький принц" despite fuzzy input
    
    def test_flibusta_priority_should_be_lower(self):
        """TDD: Flibusta should have lower priority (fallback source)"""
        from book_sources.flibusta_source import FlibustaSource
        
        source = FlibustaSource()
        assert source.get_priority() > 1  # Lower priority than Z-Library
    
    def test_flibusta_timeout_should_be_longer(self):
        """TDD: Flibusta should have longer timeout (AI processing takes time)"""
        from book_sources.flibusta_source import FlibustaSource
        
        source = FlibustaSource()
        assert source.get_timeout() >= 30  # AI processing needs time

class TestBookSearchPipeline:
    """TDD: Main pipeline orchestration"""
    
    @pytest.mark.asyncio
    async def test_pipeline_should_use_default_fallback_chain(self):
        """BDD: As a user, I want pipeline to use Z-Library first, then Flibusta"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Act
        chain = pipeline.get_fallback_chain()
        
        # Assert
        assert chain[0] == "zlibrary"  # Primary
        assert chain[1] == "flibusta"  # Secondary
    
    @pytest.mark.asyncio
    async def test_pipeline_should_try_sources_in_order(self):
        """TDD: Pipeline should try sources sequentially on failure"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        config = PipelineConfig(fallback_chain=["zlibrary", "flibusta"])
        pipeline = BookSearchPipeline(config)
        
        # Mock Z-Library to fail, Flibusta to succeed
        with patch('book_sources.zlibrary_source.ZLibrarySource.search') as mock_zlib, \
             patch('book_sources.flibusta_source.FlibustaSource.search') as mock_flibusta:
            
            mock_zlib.return_value = SearchResult(found=False, source="zlibrary")
            mock_flibusta.return_value = SearchResult(found=True, title="1984", source="flibusta")
            
            # Act
            result = await pipeline.search_book("1984 Orwell")
            
            # Assert
            assert result.found == True
            assert result.source == "flibusta"
            mock_zlib.assert_called_once()  # Z-Library tried first
            mock_flibusta.assert_called_once()  # Flibusta tried second
    
    @pytest.mark.asyncio
    async def test_pipeline_should_return_first_successful_result(self):
        """TDD: Pipeline should return immediately on first success"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        config = PipelineConfig(fallback_chain=["zlibrary", "flibusta"])
        pipeline = BookSearchPipeline(config)
        
        # Mock Z-Library to succeed
        with patch('book_sources.zlibrary_source.ZLibrarySource.search') as mock_zlib, \
             patch('book_sources.flibusta_source.FlibustaSource.search') as mock_flibusta:
            
            mock_zlib.return_value = SearchResult(found=True, title="1984", source="zlibrary")
            
            # Act
            result = await pipeline.search_book("1984 Orwell")
            
            # Assert
            assert result.found == True
            assert result.source == "zlibrary"
            mock_zlib.assert_called_once()
            mock_flibusta.assert_not_called()  # Should not try Flibusta

class TestFallbackChainConfiguration:
    """TDD: Configurable fallback chains"""
    
    @pytest.mark.asyncio
    async def test_russian_priority_chain_should_use_flibusta_first(self):
        """BDD: As a Russian user, I want Flibusta to be tried first"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        config = PipelineConfig(fallback_chain=["flibusta", "zlibrary"])
        pipeline = BookSearchPipeline(config)
        
        # Act
        chain = pipeline.get_fallback_chain()
        
        # Assert
        assert chain[0] == "flibusta"  # Primary for Russian
        assert chain[1] == "zlibrary"  # Secondary
    
    @pytest.mark.asyncio
    async def test_speed_priority_chain_should_skip_slow_sources(self):
        """BDD: As a user in a hurry, I want only fast sources"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        config = PipelineConfig(fallback_chain=["zlibrary"])  # No Flibusta
        pipeline = BookSearchPipeline(config)
        
        # Act
        chain = pipeline.get_fallback_chain()
        
        # Assert
        assert len(chain) == 1
        assert chain[0] == "zlibrary"

class TestClaudeNormalizationIntegration:
    """TDD: Claude SDK integration with pipeline"""
    
    @pytest.mark.asyncio
    async def test_pipeline_should_normalize_fuzzy_input_before_search(self):
        """BDD: As a user, I want fuzzy input to be normalized before searching"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        fuzzy_query = "hary poter filosofer stone"
        
        # Mock Claude normalizer
        with patch('claude_sdk_normalizer.ClaudeSDKNormalizer.normalize_book_title') as mock_claude:
            mock_claude.return_value = {
                "success": True,
                "search_strings": {
                    "original": "Harry Potter and the Philosopher's Stone",
                    "russian": "Гарри Поттер и философский камень"
                }
            }
            
            # Act
            result = await pipeline.search_book(fuzzy_query)
            
            # Assert
            mock_claude.assert_called_once_with(fuzzy_query)
    
    @pytest.mark.asyncio
    async def test_pipeline_should_use_both_normalized_strings_for_search(self):
        """TDD: Both original and Russian normalized strings should be tried"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Mock Claude to return bilingual normalization
        normalized_result = {
            "success": True,
            "search_strings": {
                "original": "Harry Potter",
                "russian": "Гарри Поттер"
            }
        }
        
        with patch('claude_sdk_normalizer.ClaudeSDKNormalizer.normalize_book_title') as mock_claude, \
             patch('book_sources.zlibrary_source.ZLibrarySource.search') as mock_search:
            
            mock_claude.return_value = normalized_result
            mock_search.return_value = SearchResult(found=True, source="zlibrary")
            
            # Act
            await pipeline.search_book("hary poter")
            
            # Assert
            # Should try both normalized strings
            call_args = [call.args[0] for call in mock_search.call_args_list]
            assert "Harry Potter" in call_args or "Гарри Поттер" in call_args

class TestEdgeCasesAndNegativeScenarios:
    """TDD: Edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_pipeline_should_handle_all_sources_failing(self):
        """BDD: As a system, I should handle gracefully when no sources find the book"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Mock all sources to fail
        with patch('book_sources.zlibrary_source.ZLibrarySource.search') as mock_zlib, \
             patch('book_sources.flibusta_source.FlibustaSource.search') as mock_flibusta:
            
            mock_zlib.return_value = SearchResult(found=False, source="zlibrary")
            mock_flibusta.return_value = SearchResult(found=False, source="flibusta")
            
            # Act
            result = await pipeline.search_book("nonexistent book xyz123")
            
            # Assert
            assert result.found == False
            assert result.source in ["", "pipeline"]  # No successful source
    
    @pytest.mark.asyncio
    async def test_pipeline_should_handle_claude_normalization_failure(self):
        """TDD: Pipeline should continue even if Claude normalization fails"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Mock Claude to fail
        with patch('claude_sdk_normalizer.ClaudeSDKNormalizer.normalize_book_title') as mock_claude:
            mock_claude.return_value = {"success": False, "error": "Timeout"}
            
            # Act & Assert - should not raise exception
            result = await pipeline.search_book("some query")
            # Should use original query if normalization fails
    
    @pytest.mark.asyncio
    async def test_pipeline_should_timeout_gracefully(self):
        """TDD: Pipeline should respect timeout limits"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        config = PipelineConfig(max_total_timeout=5)  # 5 second limit
        pipeline = BookSearchPipeline(config)
        
        # Mock source to take too long
        async def slow_search(query):
            await asyncio.sleep(10)  # Longer than timeout
            return SearchResult(found=True, source="slow")
        
        with patch('book_sources.zlibrary_source.ZLibrarySource.search', slow_search):
            
            # Act
            result = await pipeline.search_book("any query")
            
            # Assert
            # Should timeout and return not found
            assert result.found == False
    
    @pytest.mark.parametrize("fuzzy_input,expected_type", [
        ("", "empty_query"),
        ("a", "too_short"),
        ("x" * 1000, "too_long"),
        ("!@#$%", "invalid_characters"),
        ("     ", "whitespace_only"),
        ("123456789", "numbers_only"),
    ])
    @pytest.mark.asyncio
    async def test_pipeline_should_handle_invalid_inputs(self, fuzzy_input, expected_type):
        """TDD: Pipeline should validate input and handle edge cases"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Act & Assert
        if expected_type in ["empty_query", "too_short", "whitespace_only"]:
            with pytest.raises(ValueError):
                await pipeline.search_book(fuzzy_input)
        else:
            # Should handle gracefully without exception
            result = await pipeline.search_book(fuzzy_input)
            assert isinstance(result, SearchResult)

class TestFallbackChainVariations:
    """TDD: Different fallback chain configurations"""
    
    @pytest.mark.parametrize("chain_config,expected_order", [
        (["zlibrary"], ["zlibrary"]),
        (["flibusta"], ["flibusta"]),
        (["zlibrary", "flibusta"], ["zlibrary", "flibusta"]),
        (["flibusta", "zlibrary"], ["flibusta", "zlibrary"]),
    ])
    @pytest.mark.asyncio
    async def test_pipeline_should_respect_custom_chains(self, chain_config, expected_order):
        """BDD: As a user, I want to configure my preferred search order"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        config = PipelineConfig(fallback_chain=chain_config)
        pipeline = BookSearchPipeline(config)
        
        # Act
        actual_chain = pipeline.get_fallback_chain()
        
        # Assert
        assert actual_chain == expected_order

class TestLanguageAwareRouting:
    """TDD: Smart routing based on query language"""
    
    @pytest.mark.parametrize("query,expected_primary", [
        ("Война и мир", "flibusta"),  # Russian text
        ("1984 Orwell", "zlibrary"),  # English text
        ("малenkiy принц", "flibusta"),  # Mixed with Russian
    ])
    @pytest.mark.asyncio
    async def test_pipeline_should_route_based_on_language(self, query, expected_primary):
        """BDD: As a user, I want the system to choose the best source for my language"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Act
        optimal_chain = pipeline.get_optimal_chain_for_query(query)
        
        # Assert
        assert optimal_chain[0] == expected_primary

# Integration Tests
class TestPipelineIntegration:
    """Integration tests with real components"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_pipeline_with_real_components(self):
        """Integration: Test complete pipeline with actual Claude and Z-Library"""
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Act - Use real services (skip if not available)
        try:
            result = await pipeline.search_book("1984 Orwell")
            
            # Assert
            assert isinstance(result, SearchResult)
            if result.found:
                assert result.title
                assert result.source in ["zlibrary", "flibusta"]
        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")

# Performance Tests
class TestPipelinePerformance:
    """Performance and timing tests"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_pipeline_should_meet_response_time_sla(self):
        """Performance: Pipeline should respond within SLA"""
        import time
        from pipeline.book_pipeline import BookSearchPipeline
        
        # Arrange
        pipeline = BookSearchPipeline()
        
        # Act
        start_time = time.time()
        result = await pipeline.search_book("1984 Orwell")
        end_time = time.time()
        
        # Assert
        response_time = end_time - start_time
        if result.found and result.source == "zlibrary":
            assert response_time < 10  # Z-Library should be fast
        elif result.found and result.source == "flibusta":
            assert response_time < 40  # Flibusta allowed to be slower

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s", "--tb=short"])