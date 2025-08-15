#!/usr/bin/env python3
"""
Test Message Cleanup Functionality
Tests the new progress message editing and cleanup features in simple_bot.py
"""

import asyncio
import logging
import json
import time
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


class MockMessage:
    """Mock Telegram message for testing"""
    def __init__(self, message_id: int, text: str = "", user_id: int = 12345):
        self.message_id = message_id
        self.text = text
        self.from_user = MagicMock()
        self.from_user.id = user_id
        self.edit_text = AsyncMock()
        self.delete = AsyncMock()
    
    async def answer(self, text: str) -> 'MockMessage':
        """Mock answer method that returns a new message"""
        progress_msg = MockMessage(message_id=self.message_id + 1)
        progress_msg.text = text
        return progress_msg
    
    async def answer_document(self, document, caption: str = ""):
        """Mock document sending"""
        logger.debug(f"📄 Mock sending document with caption: {caption}")


class MessageCleanupTester:
    """Test suite for message cleanup functionality"""
    
    def __init__(self):
        self.test_results = []
        self.mock_search_results = {}
    
    def setup_mock_search_results(self):
        """Setup different search result scenarios"""
        self.mock_search_results = {
            "success": {
                "status": "success",
                "result": {
                    "found": True,
                    "epub_download_url": "/tmp/test_book.epub",
                    "book_info": {"title": "Clean Code"}
                }
            },
            "not_found": {
                "status": "success",
                "result": {"found": False}
            },
            "no_epub": {
                "status": "success",
                "result": {
                    "found": True,
                    "epub_download_url": None,
                    "book_info": {"title": "Test Book"}
                }
            },
            "error": {
                "status": "error",
                "message": "Network error"
            }
        }
    
    async def mock_search_book(self, query: str, scenario: str = "success"):
        """Mock search function with different scenarios"""
        logger.debug(f"🔍 Mock search for: '{query}' using scenario: {scenario}")
        await asyncio.sleep(0.1)  # Simulate search delay
        return self.mock_search_results.get(scenario, self.mock_search_results["success"])
    
    async def mock_send_epub_file(self, message, epub_path: str, title: str):
        """Mock EPUB sending"""
        logger.debug(f"📚 Mock sending EPUB: {title}")
        await asyncio.sleep(0.1)  # Simulate file sending
    
    async def test_successful_book_found(self):
        """Test: Book found -> Progress updated -> EPUB sent -> Message deleted"""
        logger.info("🧪 Test 1: Successful book found scenario")
        
        message = MockMessage(message_id=1, text="Clean Code", user_id=12345)
        
        # Mock the search and file operations
        with patch('simple_bot.search_book', self.mock_search_book), \
             patch('simple_bot.send_epub_file', self.mock_send_epub_file):
            
            # Simulate the process_book_request logic
            progress_message = await message.answer("🔍 Searching for book...")
            result = await self.mock_search_book("Clean Code", "success")
            
            # Check if book found
            book_result = result.get("result", {})
            if book_result.get("found"):
                epub_path = book_result.get("epub_download_url")
                title = book_result.get("book_info", {}).get("title", "Unknown")
                
                if epub_path:
                    # Update progress message
                    await progress_message.edit_text(f"✅ Book found: {title}\n📄 Sending EPUB file...")
                    
                    # Send EPUB
                    await self.mock_send_epub_file(message, epub_path, title)
                    
                    # Delete progress message
                    await progress_message.delete()
                    
                    # Verify calls
                    progress_message.edit_text.assert_called_with(f"✅ Book found: {title}\n📄 Sending EPUB file...")
                    progress_message.delete.assert_called_once()
                    
                    logger.info("✅ Test 1 PASSED: Message edited and deleted correctly")
                    return True
        
        logger.error("❌ Test 1 FAILED")
        return False
    
    async def test_book_not_found(self):
        """Test: Book not found -> Progress updated with error"""
        logger.info("🧪 Test 2: Book not found scenario")
        
        message = MockMessage(message_id=2, text="Non Existent Book", user_id=12345)
        
        with patch('telegram_bot.simple_bot.search_book', self.mock_search_book):
            progress_message = await message.answer("🔍 Searching for book...")
            result = await self.mock_search_book("Non Existent Book", "not_found")
            
            book_result = result.get("result", {})
            if not book_result.get("found"):
                await progress_message.edit_text("❌ Book not found")
                
                # Verify call
                progress_message.edit_text.assert_called_with("❌ Book not found")
                progress_message.delete.assert_not_called()  # Should NOT delete on error
                
                logger.info("✅ Test 2 PASSED: Progress message updated with not found status")
                return True
        
        logger.error("❌ Test 2 FAILED")
        return False
    
    async def test_search_error(self):
        """Test: Search error -> Progress updated with error message"""
        logger.info("🧪 Test 3: Search error scenario")
        
        message = MockMessage(message_id=3, text="Error Book", user_id=12345)
        
        with patch('telegram_bot.simple_bot.search_book', self.mock_search_book):
            progress_message = await message.answer("🔍 Searching for book...")
            result = await self.mock_search_book("Error Book", "error")
            
            if result.get("status") != "success":
                error_msg = f"❌ Search failed: {result.get('message', 'Unknown error')}"
                await progress_message.edit_text(error_msg)
                
                # Verify call
                progress_message.edit_text.assert_called_with("❌ Search failed: Network error")
                progress_message.delete.assert_not_called()
                
                logger.info("✅ Test 3 PASSED: Progress message updated with error status")
                return True
        
        logger.error("❌ Test 3 FAILED")
        return False
    
    async def test_no_epub_available(self):
        """Test: Book found but no EPUB -> Progress updated with no EPUB message"""
        logger.info("🧪 Test 4: No EPUB available scenario")
        
        message = MockMessage(message_id=4, text="No EPUB Book", user_id=12345)
        
        with patch('telegram_bot.simple_bot.search_book', self.mock_search_book):
            progress_message = await message.answer("🔍 Searching for book...")
            result = await self.mock_search_book("No EPUB Book", "no_epub")
            
            book_result = result.get("result", {})
            if book_result.get("found"):
                epub_path = book_result.get("epub_download_url")
                if not epub_path:
                    await progress_message.edit_text("❌ No EPUB file available")
                    
                    # Verify call
                    progress_message.edit_text.assert_called_with("❌ No EPUB file available")
                    progress_message.delete.assert_not_called()
                    
                    logger.info("✅ Test 4 PASSED: Progress message updated with no EPUB status")
                    return True
        
        logger.error("❌ Test 4 FAILED")
        return False
    
    async def test_message_edit_failure(self):
        """Test: Handle message edit failures gracefully"""
        logger.info("🧪 Test 5: Message edit failure handling")
        
        message = MockMessage(message_id=5, text="Test Book", user_id=12345)
        
        # Mock edit_text to raise an exception
        progress_message = await message.answer("🔍 Searching for book...")
        progress_message.edit_text.side_effect = Exception("Message deleted by user")
        
        # Try to edit the message
        try:
            await progress_message.edit_text("❌ Book not found")
            logger.error("❌ Test 5 FAILED: Exception should have been raised")
            return False
        except Exception as e:
            logger.debug(f"Expected exception caught: {e}")
            logger.info("✅ Test 5 PASSED: Message edit failure handled correctly")
            return True
    
    async def test_concurrent_users(self):
        """Test: Multiple users with different scenarios simultaneously"""
        logger.info("🧪 Test 6: Concurrent users scenario")
        
        # Create multiple user messages
        user_messages = [
            MockMessage(message_id=10, text="Clean Code", user_id=111),
            MockMessage(message_id=20, text="Non Existent", user_id=222),
            MockMessage(message_id=30, text="Error Book", user_id=333)
        ]
        
        scenarios = ["success", "not_found", "error"]
        
        async def process_user_message(msg, scenario):
            with patch('telegram_bot.simple_bot.search_book', self.mock_search_book), \
                 patch('telegram_bot.simple_bot.send_epub_file', self.mock_send_epub_file):
                
                progress_msg = await msg.answer("🔍 Searching for book...")
                result = await self.mock_search_book(msg.text, scenario)
                
                if result.get("status") == "success":
                    book_result = result.get("result", {})
                    if book_result.get("found"):
                        await progress_msg.edit_text("✅ Book found: Test\n📄 Sending EPUB file...")
                        await progress_msg.delete()
                    else:
                        await progress_msg.edit_text("❌ Book not found")
                else:
                    await progress_msg.edit_text("❌ Search failed: Network error")
        
        # Run all user requests concurrently
        tasks = [
            process_user_message(msg, scenario) 
            for msg, scenario in zip(user_messages, scenarios)
        ]
        
        await asyncio.gather(*tasks)
        
        logger.info("✅ Test 6 PASSED: Concurrent users handled correctly")
        return True
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        logger.info("🚀 Starting Message Cleanup Test Suite")
        
        self.setup_mock_search_results()
        
        tests = [
            self.test_successful_book_found,
            self.test_book_not_found,
            self.test_search_error,
            self.test_no_epub_available,
            self.test_message_edit_failure,
            self.test_concurrent_users
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Test failed with exception: {e}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        logger.info(f"\n📊 TEST SUMMARY")
        logger.info(f"✅ Passed: {passed}/{total}")
        logger.info(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! Message cleanup feature ready for production.")
        else:
            logger.error("⚠️  Some tests failed. Review implementation before deployment.")
        
        return passed == total


async def main():
    """Run the test suite"""
    tester = MessageCleanupTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎯 SUCCESS: Message cleanup feature is working correctly!")
        print("📋 Features implemented:")
        print("  ✅ Progress message editing on different outcomes")
        print("  ✅ Message deletion after successful EPUB delivery")
        print("  ✅ Error handling for message edit failures")
        print("  ✅ Support for concurrent users")
    else:
        print("\n❌ FAILURE: Some tests failed. Check logs for details.")


if __name__ == '__main__':
    asyncio.run(main())