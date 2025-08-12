#!/usr/bin/env python3
"""
Simple TDD Telegram Bot for Book Search
Built step-by-step with test-first approach
"""

import asyncio
import logging
import subprocess
import os
import json
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command

# Load environment
load_dotenv()

# Configure logging with DEEP debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_tdd.log')
    ]
)

logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SCRIPT_PATH = os.getenv('SCRIPT_PATH', '/home/almaz/microservices/zlibrary_api_module/scripts/book_search_engine.py')

logger.info(f"🔧 Bot configured - Token: {TOKEN[:20]}..., Script: {SCRIPT_PATH}")


async def handle_message(message: types.Message):
    """Handle incoming message - TEST 1"""
    logger.info(f"📨 Received message from user {message.from_user.id}: '{message.text}'")


async def search_book(query: str) -> dict:
    """Search for book using scripts/book_search.sh - TEST 2"""
    logger.info(f"🔍 Searching for book: '{query}'")
    
    # Build command
    cmd = ["bash", SCRIPT_PATH, "--download", query]
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    # Execute subprocess
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(SCRIPT_PATH).parent.parent  # Go to project root
    )
    
    logger.debug(f"Script returncode: {result.returncode}")
    logger.debug(f"Script stdout: {result.stdout[:500]}...")
    
    if result.returncode != 0:
        logger.error(f"Script failed: {result.stderr}")
        return {"status": "error", "message": "Script execution failed"}
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode failed: {e}")
        return {"status": "error", "message": "Invalid JSON response"}


async def send_epub_file(message: types.Message, epub_path: str, title: str):
    """Send EPUB file to user - TEST 3"""
    logger.info(f"📚 Sending EPUB file: {epub_path} with title: '{title}'")
    
    if not Path(epub_path).exists():
        logger.error(f"EPUB file not found: {epub_path}")
        await message.answer(f"❌ File not found: {epub_path}")
        return
    
    # Send file
    document = FSInputFile(epub_path, filename=f"{title}.epub")
    await message.answer_document(
        document=document,
        caption=f"📖 {title}"
    )
    
    logger.info(f"✅ EPUB file sent successfully: {title}")


async def process_book_request(message: types.Message):
    """Complete pipeline: message -> search -> send EPUB - TEST 4"""
    logger.info(f"🚀 Processing book request from user {message.from_user.id}: '{message.text}'")
    
    # Send progress message
    await message.answer("🔍 Searching for book...")
    
    # Search for book
    result = await search_book(message.text)
    
    if result.get("status") != "success":
        await message.answer(f"❌ Search failed: {result.get('message', 'Unknown error')}")
        return
    
    book_result = result.get("result", {})
    if not book_result.get("found"):
        await message.answer("❌ Book not found")
        return
    
    # Extract book info
    epub_path = book_result.get("epub_download_url")
    book_info = book_result.get("book_info", {})
    title = book_info.get("title", "Unknown Book")
    
    if not epub_path:
        await message.answer("❌ No EPUB file available")
        return
    
    # Send EPUB
    await send_epub_file(message, epub_path, title)


# Bot handlers
async def start_handler(message: types.Message):
    """Handle /start command"""
    logger.info(f"🚀 /start from user {message.from_user.id}")
    await message.answer(
        "📚 Welcome to Book Search Bot!\n\n"
        "Send me a book title and I'll search for it and send you the EPUB file.\n\n"
        "Example: 'Clean Code programming'"
    )


async def message_handler(message: types.Message):
    """Handle all text messages"""
    logger.info(f"📝 Text message from user {message.from_user.id}: '{message.text}'")
    
    # Log message (for TEST 1)
    await handle_message(message)
    
    # Process book request (for TEST 4)
    await process_book_request(message)


async def main():
    """Main bot function"""
    logger.info("🤖 Starting TDD Bot...")
    
    # Create bot and dispatcher
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Test API connection
    try:
        me = await bot.get_me()
        logger.info(f"✅ Bot connected: {me.first_name} (@{me.username})")
    except Exception as e:
        logger.error(f"❌ Bot connection failed: {e}")
        return
    
    # Register handlers
    logger.info("📝 Registering handlers...")
    dp.message.register(start_handler, Command(commands=['start']))
    dp.message.register(message_handler)  # All other text messages
    
    # Clear webhooks
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🧹 Webhooks cleared")
    
    # Start polling
    logger.info("🔄 Starting polling...")
    try:
        await dp.start_polling(bot, skip_updates=False)
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Polling error: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("🔌 Bot session closed")


if __name__ == '__main__':
    asyncio.run(main())