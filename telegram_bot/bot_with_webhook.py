#!/usr/bin/env python3
"""
Conflict-free Telegram Bot using webhooks instead of polling
This eliminates polling conflicts with UC test scripts
"""

import asyncio
import logging
import subprocess
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
import time

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web, ClientTimeout
import aiohttp

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_webhook.log')
    ]
)

logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SCRIPT_PATH = os.getenv('SCRIPT_PATH', '/home/almaz/microservices/zlibrary_api_module/scripts/book_search.sh')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 8443))
WEBHOOK_PATH = f"/bot{TOKEN}"
WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

class ConflictFreeBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN, default=aiohttp.ClientTimeout(total=30))
        self.dp = Dispatcher()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup message handlers"""
        self.dp.message.register(self.start_handler, Command(commands=['start']))
        self.dp.message.register(self.message_handler)

    async def start_handler(self, message: types.Message):
        """Handle /start command"""
        logger.info(f"🚀 /start from user {message.from_user.id}")
        await self.safe_send(message, (
            "📚 Welcome to Book Search Bot!\n\n"
            "Send me a book title and I'll search for it and send you the EPUB file.\n\n"
            "Example: 'Clean Code programming'"
        ))

    async def message_handler(self, message: types.Message):
        """Handle all text messages with retry mechanism"""
        logger.info(f"📝 Processing message from user {message.from_user.id}: '{message.text}'")
        await self.process_book_request(message)

    async def safe_send(self, message: types.Message, text: str, max_retries: int = 3) -> Optional[types.Message]:
        """Send message with retry mechanism to handle conflicts"""
        for attempt in range(max_retries):
            try:
                result = await message.answer(text)
                logger.info(f"✅ Message sent successfully (attempt {attempt + 1})")
                return result
            except Exception as e:
                logger.warning(f"⚠️ Send attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    # Exponential backoff: 0.5s, 1s, 2s
                    await asyncio.sleep(0.5 * (2 ** attempt))
                else:
                    logger.error(f"❌ Failed to send after {max_retries} attempts")
                    return None

    async def safe_send_document(self, message: types.Message, document: FSInputFile, caption: str, max_retries: int = 3) -> Optional[types.Message]:
        """Send document with retry mechanism"""
        for attempt in range(max_retries):
            try:
                result = await message.answer_document(document=document, caption=caption)
                logger.info(f"✅ Document sent successfully (attempt {attempt + 1})")
                return result
            except Exception as e:
                logger.warning(f"⚠️ Document send attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                else:
                    logger.error(f"❌ Failed to send document after {max_retries} attempts")
                    return None

    async def search_book(self, query: str) -> dict:
        """Search for book using scripts/book_search.sh"""
        logger.info(f"🔍 Searching for book: '{query}'")
        
        cmd = [SCRIPT_PATH, "--download", query]
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(SCRIPT_PATH).parent.parent,
            timeout=90
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

    async def process_book_request(self, message: types.Message):
        """Complete pipeline with guaranteed progress messages"""
        logger.info(f"🚀 Processing book request from user {message.from_user.id}: '{message.text}'")
        
        # Step 1: Send progress message with retry
        progress_msg = await self.safe_send(message, "🔍 Searching for book...")
        if not progress_msg:
            logger.error("❌ Failed to send progress message - aborting request")
            return
        
        # Step 2: Search for book
        start_time = time.time()
        result = await self.search_book(message.text)
        search_duration = time.time() - start_time
        
        logger.info(f"🔍 Search completed in {search_duration:.2f}s")
        
        # Step 3: Process result
        if result.get("status") != "success":
            await self.safe_send(message, f"❌ Search failed: {result.get('message', 'Unknown error')}")
            return
        
        book_result = result.get("result", {})
        if not book_result.get("found"):
            await self.safe_send(message, "❌ Book not found")
            return
        
        # Step 4: Extract book info and send EPUB
        epub_path = book_result.get("epub_download_url")
        book_info = book_result.get("book_info", {})
        title = book_info.get("title", "Unknown Book")
        
        if not epub_path or not Path(epub_path).exists():
            await self.safe_send(message, "❌ No EPUB file available")
            return
        
        # Step 5: Send EPUB file
        document = FSInputFile(epub_path, filename=f"{title}.epub")
        result = await self.safe_send_document(message, document, f"📖 {title}")
        
        if result:
            logger.info(f"✅ Complete pipeline success for user {message.from_user.id} in {time.time() - start_time:.2f}s")
        else:
            logger.error(f"❌ Pipeline failed at file delivery for user {message.from_user.id}")

    async def start_webhook(self):
        """Start webhook server"""
        logger.info("🔗 Starting webhook mode...")
        
        # Set webhook
        webhook_set = await self.bot.set_webhook(
            WEBHOOK_URL,
            drop_pending_updates=True
        )
        
        if webhook_set:
            logger.info(f"✅ Webhook set to: {WEBHOOK_URL}")
        else:
            logger.error("❌ Failed to set webhook")
            return
        
        # Setup aiohttp application
        app = web.Application()
        
        # Setup webhook handler
        SimpleRequestHandler(
            dispatcher=self.dp,
            bot=self.bot
        ).register(app, path=WEBHOOK_PATH)
        
        # Setup application
        setup_application(app, self.dp, bot=self.bot)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, WEBHOOK_HOST, WEBHOOK_PORT)
        await site.start()
        
        logger.info(f"🚀 Webhook server started on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
        logger.info(f"📡 Listening on path: {WEBHOOK_PATH}")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("👋 Stopping webhook server...")
        finally:
            await self.bot.delete_webhook()
            await self.bot.session.close()

    async def start_polling(self):
        """Start polling mode (fallback)"""
        logger.info("🔄 Starting polling mode...")
        
        try:
            # Clear webhooks first
            await self.bot.delete_webhook(drop_pending_updates=True)
            logger.info("🧹 Webhooks cleared")
            
            # Start polling
            await self.dp.start_polling(self.bot, skip_updates=False)
            
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Polling error: {e}", exc_info=True)
        finally:
            await self.bot.session.close()
            logger.info("🔌 Bot session closed")

async def main():
    """Main function - choose webhook or polling based on environment"""
    logger.info("🤖 Starting Conflict-Free Bot...")
    
    bot = ConflictFreeBot()
    
    # Test connection
    try:
        me = await bot.bot.get_me()
        logger.info(f"✅ Bot connected: {me.first_name} (@{me.username})")
    except Exception as e:
        logger.error(f"❌ Bot connection failed: {e}")
        return
    
    # Choose mode based on environment
    use_webhook = os.getenv('USE_WEBHOOK', 'false').lower() == 'true'
    
    if use_webhook:
        await bot.start_webhook()
    else:
        logger.info("📝 Running in polling mode (webhook disabled)")
        await bot.start_polling()

if __name__ == '__main__':
    asyncio.run(main())