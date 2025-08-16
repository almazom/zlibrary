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

def detect_error_type_with_confidence(result: dict) -> dict:
    """
    TDD-driven error type detection with high confidence scoring
    Returns: {
        'error_type': str,
        'confidence': float,
        'user_message': str,
        'technical_details': str
    }
    """
    status = result.get("status", "unknown")
    message = result.get("message", "Unknown error")
    result_data = result.get("result", {})
    
    # HIGH CONFIDENCE: Book Not Found (status = "not_found")
    if status == "not_found" and result_data.get("found") == False:
        return {
            'error_type': 'book_not_found',
            'confidence': 0.95,
            'user_message': f"""📚 Book not found
            
We searched our entire library but couldn't find: "{message.replace('No books found matching the search criteria', 'your requested book')}"

💡 Try these suggestions:
• Check spelling of title and author
• Use fewer, simpler keywords  
• Try alternative titles or author names
• Search by author name only""",
            'technical_details': f"Status: {status}, Found: {result_data.get('found', 'N/A')}"
        }
    
    error_lower = message.lower()
    
    # HIGH CONFIDENCE: Network/Connection Issues
    if any(word in error_lower for word in ['timeout', 'connection', 'network', 'unreachable', 'dns']):
        return {
            'error_type': 'network_error',
            'confidence': 0.90,
            'user_message': """🌐 Network connection issue
            
Our servers are having trouble connecting to the book database.

🔄 Please try again in 30-60 seconds""",
            'technical_details': f"Network error: {message}"
        }
    
    # HIGH CONFIDENCE: Authentication Issues  
    if any(word in error_lower for word in ['auth', 'login', 'credential', 'unauthorized', '401', '403']):
        return {
            'error_type': 'auth_error',
            'confidence': 0.90,
            'user_message': """🔐 Authentication issue
            
There's a temporary problem with our book search credentials.

📞 This should resolve automatically, but contact support if it continues""",
            'technical_details': f"Auth error: {message}"
        }
    
    # MEDIUM CONFIDENCE: Rate Limiting
    if any(word in error_lower for word in ['rate', 'limit', 'too many', 'throttle', '429']):
        return {
            'error_type': 'rate_limit',
            'confidence': 0.85,
            'user_message': """⏳ Too many requests
            
You've made several searches recently. Please wait a moment.

⏰ Try again in 1-2 minutes""",
            'technical_details': f"Rate limit: {message}"
        }
    
    # MEDIUM CONFIDENCE: Service Issues
    if any(word in error_lower for word in ['unavailable', 'maintenance', 'service', '500', '502', '503']):
        return {
            'error_type': 'service_error',
            'confidence': 0.80,
            'user_message': """⚠️ Service temporarily unavailable
            
The book search service is having temporary issues.

🔄 Please try again in a few minutes""",
            'technical_details': f"Service error: {message}"
        }
    
    # LOW CONFIDENCE: Unknown Error (fallback)
    return {
        'error_type': 'unknown_error',
        'confidence': 0.30,
        'user_message': f"""⚠️ Search temporarily unavailable

Something unexpected happened during your search.

🔄 Please try again, and contact support if this continues

📋 Error details: {message}""",
        'technical_details': f"Unknown error: {message}, Status: {status}"
    }

def get_user_friendly_error_message(error_msg: str) -> str:
    """Legacy function - kept for backward compatibility"""
    # Create a mock result for the new detection system
    mock_result = {"status": "error", "message": error_msg}
    error_info = detect_error_type_with_confidence(mock_result)
    return error_info['user_message']

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
    
    # Send progress message and store reference for editing
    progress_message = await message.answer("🔍 Searching for book...")
    logger.debug(f"📤 Progress message sent with ID: {progress_message.message_id}")
    
    # Search for book
    result = await search_book(message.text)
    
    if result.get("status") != "success":
        # Use TDD-driven error detection for high confidence error typing
        error_info = detect_error_type_with_confidence(result)
        
        logger.info(f"🔍 Error detected: {error_info['error_type']} (confidence: {error_info['confidence']:.2f})")
        logger.debug(f"🔧 Technical details: {error_info['technical_details']}")
        
        try:
            await progress_message.edit_text(error_info['user_message'])
            logger.info(f"✅ Progress message updated with {error_info['error_type']} message")
        except Exception as e:
            logger.error(f"❌ Failed to edit progress message: {e}")
            await message.answer(error_info['user_message'])
        return
    
    book_result = result.get("result", {})
    if not book_result.get("found"):
        # Use TDD-driven detection for "book not found" scenarios
        not_found_result = {
            "status": "not_found", 
            "result": {"found": False}, 
            "message": f"No books found matching: {message.text}"
        }
        error_info = detect_error_type_with_confidence(not_found_result)
        
        logger.info(f"📚 Book not found: {message.text} (confidence: {error_info['confidence']:.2f})")
        
        try:
            await progress_message.edit_text(error_info['user_message'])
            logger.info("✅ Progress message updated with book not found message")
        except Exception as e:
            logger.error(f"❌ Failed to edit progress message: {e}")
            await message.answer(error_info['user_message'])
        return
    
    # Extract book info
    epub_path = book_result.get("epub_download_url")
    book_info = book_result.get("book_info", {})
    title = book_info.get("title", "Unknown Book")
    
    if not epub_path:
        # Edit progress message to show no EPUB available
        try:
            await progress_message.edit_text("❌ No EPUB file available")
            logger.info("✅ Progress message updated with no EPUB status")
        except Exception as e:
            logger.error(f"❌ Failed to edit progress message: {e}")
            await message.answer("❌ No EPUB file available")
        return
    
    # Edit progress message to show book found
    try:
        await progress_message.edit_text(f"✅ Book found: {title}\n📄 Sending EPUB file...")
        logger.info("✅ Progress message updated with book found status")
    except Exception as e:
        logger.error(f"❌ Failed to edit progress message: {e}")
    
    # Send EPUB
    await send_epub_file(message, epub_path, title)
    
    # Clean up progress message after successful EPUB delivery
    try:
        await progress_message.delete()
        logger.info("🧹 Progress message cleaned up after successful EPUB delivery")
    except Exception as e:
        logger.error(f"❌ Failed to delete progress message: {e}")


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