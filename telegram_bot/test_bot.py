#!/usr/bin/env python3
"""
TDD Test Suite for Simple Book Search Telegram Bot
RED-GREEN-REFACTOR approach
"""

import pytest
import asyncio
import json
import os
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path
from dotenv import load_dotenv

# Load test environment
load_dotenv()

from aiogram import types
from aiogram.types import User, Chat, Message


class TestBotMessageReception:
    """Test 1: Bot must receive and acknowledge messages"""
    
    @pytest.mark.asyncio
    async def test_bot_receives_message_and_logs_it(self):
        """FAILING TEST: Bot should receive message and log it"""
        # Arrange
        from simple_bot import handle_message
        
        # Create mock message
        user = User(id=123, is_bot=False, first_name="Test")
        chat = Chat(id=456, type="private")
        message = Message(
            message_id=1,
            date=123456789,
            chat=chat,
            from_user=user,
            content_type="text",
            text="Test message"
        )
        
        # Act & Assert
        with patch('simple_bot.logger') as mock_logger:
            await handle_message(message)
            
            # Must log message reception
            mock_logger.info.assert_called_with(
                "📨 Received message from user 123: 'Test message'"
            )


class TestBookSearchIntegration:
    """Test 2: Bot must call scripts/book_search.sh correctly"""
    
    @pytest.mark.asyncio 
    async def test_bot_calls_book_search_script(self):
        """FAILING TEST: Bot should call book_search.sh --download 'text'"""
        # Arrange
        from simple_bot import search_book
        
        # Act & Assert
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = '{"status": "success", "result": {"found": true, "epub_download_url": "/path/to/book.epub"}}'
            mock_run.return_value.returncode = 0
            
            result = await search_book("Clean Code programming")
            
            # Must call correct script with correct args
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]  # First positional arg (the command list)
            
            assert "/scripts/book_search.sh" in call_args[0]
            assert "--download" in call_args
            assert "Clean Code programming" in call_args
            
            # Must return parsed result
            assert result["status"] == "success"
            assert result["result"]["found"] is True


class TestEpubFileSending:
    """Test 3: Bot must send EPUB files when book found"""
    
    @pytest.mark.asyncio
    async def test_bot_sends_epub_when_book_found(self):
        """FAILING TEST: Bot should send EPUB file when book search succeeds"""
        # Arrange
        from simple_bot import send_epub_file
        
        # Create mock message with proper mocking
        message_mock = AsyncMock()
        message_mock.answer_document = AsyncMock()
        message_mock.answer = AsyncMock()
        
        # Create test EPUB file
        test_epub_path = "/tmp/test_book.epub"
        Path(test_epub_path).touch()
        
        # Act & Assert
        try:
            await send_epub_file(message_mock, test_epub_path, "Test Book")
            
            # Must send document
            message_mock.answer_document.assert_called_once()
            
            # Check that FSInputFile was used with correct path  
            call_args = message_mock.answer_document.call_args
            assert "Test Book" in str(call_args)
            
        finally:
            # Cleanup
            Path(test_epub_path).unlink(missing_ok=True)


class TestEndToEndPipeline:
    """Test 4: Complete E2E pipeline"""
    
    @pytest.mark.asyncio
    async def test_complete_message_to_epub_pipeline(self):
        """FAILING TEST: Complete pipeline from message to EPUB"""
        # Arrange
        from simple_bot import process_book_request
        
        # Create mock message
        message_mock = AsyncMock()
        message_mock.text = "Clean Code programming"
        message_mock.from_user.id = 123
        message_mock.answer = AsyncMock()
        
        # Mock successful book search
        mock_search_result = {
            "status": "success",
            "result": {
                "found": True,
                "epub_download_url": "/downloads/clean_code.epub",
                "book_info": {"title": "Clean Code"}
            }
        }
        
        # Act & Assert
        with patch('simple_bot.search_book', return_value=mock_search_result) as mock_search, \
             patch('simple_bot.send_epub_file') as mock_send_epub:
            
            await process_book_request(message_mock)
            
            # Must call search with correct query
            mock_search.assert_called_once_with("Clean Code programming")
            
            # Must send progress message
            message_mock.answer.assert_called_with("🔍 Searching for book...")
            
            # Must send EPUB
            mock_send_epub.assert_called_once_with(
                message_mock, 
                "/downloads/clean_code.epub",
                "Clean Code"
            )