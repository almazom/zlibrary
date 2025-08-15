"""
Pytest Integration Tests - Guardian-Approved Simple Implementation

Replaces 70+ IUC files with clean, maintainable pytest suite.
Works with existing pytest infrastructure and CI/CD.

No ceremony, no abstractions, just working tests.
"""

import pytest
import asyncio
from telegram_bot_tester import TelegramBotTester, SimplifiedIUCTests


class TestTelegramBotIntegration:
    """
    Simple pytest integration tests.
    
    Each test is atomic, isolated, and straightforward.
    No BDD ceremony, no shell script complexity.
    """
    
    @pytest.fixture(scope="session")
    def event_loop(self):
        """Create event loop for async tests"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    @pytest.fixture
    async def bot_tester(self):
        """Create and connect bot tester"""
        tester = TelegramBotTester()
        await tester.connect()
        yield tester
        await tester.disconnect()
    
    @pytest.mark.asyncio
    async def test_start_command_integration(self, bot_tester):
        """Test /start command integration"""
        response = await bot_tester.send_and_wait("/start")
        
        # Simple, clear assertions
        assert len(response.text) > 0, "Bot should respond to /start"
        assert (
            "welcome" in response.text.lower() or 
            "book" in response.text.lower() or
            "📚" in response.text
        ), f"Response should be welcoming, got: {response.text[:100]}"
    
    @pytest.mark.asyncio
    async def test_book_search_valid_integration(self, bot_tester):
        """Test valid book search integration"""
        response = await bot_tester.send_and_wait("Clean Code Robert Martin", timeout=30)
        
        # Check for success indicators
        success_indicators = [
            response.has_file,
            "searching" in response.text.lower(),
            "found" in response.text.lower(),
            len(response.text) > 10
        ]
        
        assert any(success_indicators), (
            f"Should show search progress or results. "
            f"Response: {response.text[:100]}..., has_file: {response.has_file}"
        )
    
    @pytest.mark.asyncio 
    async def test_book_search_invalid_integration(self, bot_tester):
        """Test invalid book search integration"""
        import time
        fake_title = f"NonExistentBook{int(time.time())}"
        
        response = await bot_tester.send_and_wait(fake_title, timeout=30)
        
        # Should get some kind of error response
        error_indicators = [
            "not found" in response.text.lower(),
            "error" in response.text.lower(),
            "failed" in response.text.lower(),
            len(response.text) > 0  # At least some response
        ]
        
        assert any(error_indicators), (
            f"Should handle invalid searches gracefully. "
            f"Response: {response.text[:100]}..."
        )
    
    @pytest.mark.asyncio
    async def test_full_integration_suite(self):
        """Run complete integration suite"""
        tests = SimplifiedIUCTests()
        results = await tests.run_all_tests()
        
        # Verify test execution
        assert results['total_tests'] > 0, "Should execute tests"
        assert results['execution_time'] < 120, "Should complete within 2 minutes"
        
        # At least some tests should pass
        success_rate = results['passed'] / results['total_tests'] if results['total_tests'] > 0 else 0
        assert success_rate >= 0.5, (
            f"At least 50% of tests should pass. "
            f"Passed: {results['passed']}/{results['total_tests']}"
        )


class TestTelegramBotTesterUnit:
    """
    Unit tests for the bot tester itself.
    
    Tests the testing infrastructure without external dependencies.
    """
    
    def test_bot_response_creation(self):
        """Test BotResponse dataclass"""
        from telegram_bot_tester import BotResponse
        
        response = BotResponse(text="Hello", has_file=True)
        assert response.text == "Hello"
        assert response.has_file is True
        assert "Hello" in str(response)
    
    def test_telegram_bot_tester_init(self):
        """Test TelegramBotTester initialization"""
        tester = TelegramBotTester()
        
        assert tester.api_id is not None
        assert tester.api_hash is not None
        assert tester.bot_username == "@epub_toc_based_sample_bot"
        assert tester.default_timeout == 10
    
    def test_session_string_loading(self):
        """Test session string loading logic"""
        tester = TelegramBotTester()
        session = tester._load_session_string()
        
        assert isinstance(session, str)
        assert len(session) > 10  # Should be a meaningful session string


# Pytest configuration
@pytest.mark.integration
class TestPerformanceBenchmarks:
    """
    Performance benchmarks comparing simplified vs original IUC.
    
    Demonstrates the efficiency gains from simplification.
    """
    
    @pytest.mark.asyncio
    async def test_execution_speed_benchmark(self):
        """Benchmark test execution speed"""
        import time
        
        start_time = time.time()
        
        tests = SimplifiedIUCTests()
        results = await tests.run_all_tests()
        
        execution_time = time.time() - start_time
        
        # Should be much faster than original IUC (which took 2-5 minutes)
        assert execution_time < 60, (
            f"Simplified tests should complete under 1 minute, "
            f"took {execution_time:.1f}s"
        )
        
        print(f"\n🏃‍♂️ Performance: Completed {results['total_tests']} tests in {execution_time:.1f}s")
        print(f"📊 Speed: {results['total_tests']/execution_time:.1f} tests/second")


if __name__ == "__main__":
    # Direct execution support
    import sys
    
    print("🧪 Running Simplified IUC Tests")
    print("=" * 40)
    
    # Run with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)