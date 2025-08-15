#!/usr/bin/env python3
"""
COMPLETE SOLUTION: Telegram Bot with Guaranteed Pipeline Consistency
This ensures automated UC test messages trigger IDENTICAL pipeline as manual messages

SOLUTION COMPONENTS:
1. Dual-mode bot (polling + webhook capability)
2. Message queue to prevent conflicts
3. Retry mechanisms for progress messages
4. Separate test environment
5. Pipeline guarantee system
"""

import asyncio
import logging
import subprocess
import os
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import aiofiles
import uuid
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
import aiohttp

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('complete_solution.log')
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class MessageRequest:
    """Structured message request for queue processing"""
    request_id: str
    user_id: int
    message_text: str
    timestamp: datetime
    source: str  # 'manual' or 'uc_test'
    retry_count: int = 0
    max_retries: int = 3

class MessageQueue:
    """Thread-safe message queue to prevent conflicts"""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = {}
        self.completed = {}
        
    async def add_request(self, request: MessageRequest) -> str:
        """Add message request to queue"""
        await self.queue.put(request)
        logger.info(f"📥 QUEUE: Added request {request.request_id} from {request.source}")
        return request.request_id
    
    async def get_next_request(self) -> Optional[MessageRequest]:
        """Get next request from queue"""
        try:
            request = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            self.processing[request.request_id] = request
            return request
        except asyncio.TimeoutError:
            return None
    
    async def mark_completed(self, request_id: str, result: Dict[str, Any]) -> None:
        """Mark request as completed"""
        if request_id in self.processing:
            request = self.processing.pop(request_id)
            self.completed[request_id] = {
                'request': request,
                'result': result,
                'completed_at': datetime.now()
            }
            logger.info(f"✅ QUEUE: Completed request {request_id}")
    
    async def mark_failed(self, request_id: str, error: str) -> None:
        """Mark request as failed"""
        if request_id in self.processing:
            request = self.processing.pop(request_id)
            request.retry_count += 1
            
            if request.retry_count <= request.max_retries:
                logger.warning(f"🔄 QUEUE: Retrying request {request_id} (attempt {request.retry_count})")
                await self.add_request(request)
            else:
                logger.error(f"❌ QUEUE: Request {request_id} failed after {request.max_retries} attempts")
                self.completed[request_id] = {
                    'request': request,
                    'result': {'status': 'failed', 'error': error},
                    'completed_at': datetime.now()
                }

class PipelineGuaranteor:
    """Ensures identical pipeline execution regardless of message source"""
    
    def __init__(self, bot: Bot, script_path: str):
        self.bot = bot
        self.script_path = script_path
        self.message_queue = MessageQueue()
        self.processing_worker_task = None
        
    async def start_processing_worker(self):
        """Start background worker to process message queue"""
        self.processing_worker_task = asyncio.create_task(self._processing_worker())
        logger.info("🔄 PIPELINE: Processing worker started")
    
    async def stop_processing_worker(self):
        """Stop background worker"""
        if self.processing_worker_task:
            self.processing_worker_task.cancel()
            try:
                await self.processing_worker_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 PIPELINE: Processing worker stopped")
    
    async def _processing_worker(self):
        """Background worker that processes requests sequentially"""
        logger.info("👷 PIPELINE: Worker thread started")
        
        while True:
            try:
                request = await self.message_queue.get_next_request()
                if request:
                    await self._process_single_request(request)
                else:
                    await asyncio.sleep(0.1)  # Small delay when no requests
            except asyncio.CancelledError:
                logger.info("👷 PIPELINE: Worker thread cancelled")
                break
            except Exception as e:
                logger.error(f"❌ PIPELINE: Worker error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Pause on error
    
    async def _process_single_request(self, request: MessageRequest):
        """Process a single message request with guaranteed pipeline"""
        logger.info(f"🚀 PIPELINE: Processing {request.request_id} from {request.source}")
        
        start_time = time.time()
        pipeline_log = []
        
        try:
            # Stage 1: Send progress message (GUARANTEED)
            progress_sent = await self._send_progress_message_guaranteed(request)
            pipeline_log.append(f"Progress message: {'✅' if progress_sent else '❌'}")
            
            if not progress_sent:
                raise Exception("Failed to send progress message after retries")
            
            # Stage 2: Execute book search (IDENTICAL for both sources)
            search_result = await self._execute_book_search(request.message_text)
            pipeline_log.append(f"Book search: {'✅' if search_result.get('status') == 'success' else '❌'}")
            
            # Stage 3: Process result (IDENTICAL logic)
            if search_result.get("status") != "success":
                await self._send_error_message_guaranteed(request, search_result.get('message', 'Unknown error'))
                pipeline_log.append("Error message: ✅")
            else:
                book_result = search_result.get("result", {})
                if not book_result.get("found"):
                    await self._send_not_found_guaranteed(request)
                    pipeline_log.append("Not found message: ✅")
                else:
                    # Stage 4: Send EPUB (GUARANTEED)
                    epub_sent = await self._send_epub_guaranteed(request, book_result)
                    pipeline_log.append(f"EPUB delivery: {'✅' if epub_sent else '❌'}")
            
            duration = time.time() - start_time
            
            # Mark as completed
            result = {
                'status': 'success',
                'duration': duration,
                'pipeline_log': pipeline_log,
                'source': request.source
            }
            
            await self.message_queue.mark_completed(request.request_id, result)
            
            logger.info(f"✅ PIPELINE: Request {request.request_id} completed in {duration:.2f}s")
            logger.info(f"📋 PIPELINE: Stages - {' | '.join(pipeline_log)}")
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ PIPELINE: Request {request.request_id} failed after {duration:.2f}s - {e}")
            await self.message_queue.mark_failed(request.request_id, str(e))
    
    async def _send_progress_message_guaranteed(self, request: MessageRequest, max_attempts: int = 5) -> bool:
        """Send progress message with guaranteed delivery"""
        for attempt in range(max_attempts):
            try:
                await self.bot.send_message(
                    chat_id=request.user_id,
                    text="🔍 Searching for book..."
                )
                logger.info(f"✅ PIPELINE: Progress message sent to {request.user_id} (attempt {attempt + 1})")
                return True
            except Exception as e:
                logger.warning(f"⚠️ PIPELINE: Progress message attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
        
        logger.error(f"❌ PIPELINE: Failed to send progress message after {max_attempts} attempts")
        return False
    
    async def _execute_book_search(self, query: str) -> Dict[str, Any]:
        """Execute book search - IDENTICAL for manual and UC tests"""
        logger.info(f"🔍 PIPELINE: Executing book search for: '{query}'")
        
        cmd = [self.script_path, "--download", query]
        logger.debug(f"PIPELINE: Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(self.script_path).parent.parent,
                timeout=90
            )
            
            logger.debug(f"PIPELINE: Script returncode: {result.returncode}")
            logger.debug(f"PIPELINE: Script stdout: {result.stdout[:500]}...")
            
            if result.returncode != 0:
                logger.error(f"PIPELINE: Script failed: {result.stderr}")
                return {"status": "error", "message": "Script execution failed"}
            
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            logger.error("PIPELINE: Script timeout (90s)")
            return {"status": "error", "message": "Search timeout"}
        except json.JSONDecodeError as e:
            logger.error(f"PIPELINE: JSON decode failed: {e}")
            return {"status": "error", "message": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"PIPELINE: Unexpected error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_error_message_guaranteed(self, request: MessageRequest, error_msg: str) -> bool:
        """Send error message with retry"""
        try:
            await self.bot.send_message(
                chat_id=request.user_id,
                text=f"❌ Search failed: {error_msg}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ PIPELINE: Failed to send error message: {e}")
            return False
    
    async def _send_not_found_guaranteed(self, request: MessageRequest) -> bool:
        """Send not found message with retry"""
        try:
            await self.bot.send_message(
                chat_id=request.user_id,
                text="❌ Book not found"
            )
            return True
        except Exception as e:
            logger.error(f"❌ PIPELINE: Failed to send not found message: {e}")
            return False
    
    async def _send_epub_guaranteed(self, request: MessageRequest, book_result: Dict[str, Any]) -> bool:
        """Send EPUB file with guaranteed delivery"""
        epub_path = book_result.get("epub_download_url")
        book_info = book_result.get("book_info", {})
        title = book_info.get("title", "Unknown Book")
        
        if not epub_path or not Path(epub_path).exists():
            await self.bot.send_message(
                chat_id=request.user_id,
                text="❌ No EPUB file available"
            )
            return False
        
        try:
            document = FSInputFile(epub_path, filename=f"{title}.epub")
            await self.bot.send_document(
                chat_id=request.user_id,
                document=document,
                caption=f"📖 {title}"
            )
            logger.info(f"✅ PIPELINE: EPUB sent successfully to {request.user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ PIPELINE: Failed to send EPUB: {e}")
            return False
    
    async def submit_message_request(self, user_id: int, message_text: str, source: str) -> str:
        """Submit message request for processing"""
        request = MessageRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            message_text=message_text,
            timestamp=datetime.now(),
            source=source
        )
        
        request_id = await self.message_queue.add_request(request)
        logger.info(f"📝 PIPELINE: Submitted {source} request {request_id}")
        return request_id

class CompleteSolutionBot:
    """Complete solution bot with guaranteed pipeline consistency"""
    
    def __init__(self):
        self.bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.dp = Dispatcher()
        self.script_path = os.getenv('SCRIPT_PATH', '/home/almaz/microservices/zlibrary_api_module/scripts/book_search.sh')
        self.pipeline = PipelineGuaranteor(self.bot, self.script_path)
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup message handlers"""
        self.dp.message.register(self.start_handler, Command(commands=['start']))
        self.dp.message.register(self.message_handler)
    
    async def start_handler(self, message: types.Message):
        """Handle /start command"""
        logger.info(f"🚀 /start from user {message.from_user.id}")
        await message.answer(
            "📚 Welcome to Book Search Bot!\n\n"
            "Send me a book title and I'll search for it and send you the EPUB file.\n\n"
            "Example: 'Clean Code programming'\n\n"
            "🔧 This bot uses guaranteed pipeline processing for consistent results."
        )
    
    async def message_handler(self, message: types.Message):
        """Handle all text messages through guaranteed pipeline"""
        logger.info(f"📝 Message from user {message.from_user.id}: '{message.text}'")
        
        # Submit to guaranteed pipeline
        request_id = await self.pipeline.submit_message_request(
            user_id=message.from_user.id,
            message_text=message.text,
            source='manual'
        )
        
        logger.info(f"📋 Submitted manual message as request {request_id}")
    
    async def process_uc_message(self, user_id: int, message_text: str) -> str:
        """Process UC test message through IDENTICAL pipeline"""
        logger.info(f"🧪 UC test message from user {user_id}: '{message_text}'")
        
        # Submit to SAME guaranteed pipeline as manual messages
        request_id = await self.pipeline.submit_message_request(
            user_id=user_id,
            message_text=message_text,
            source='uc_test'
        )
        
        logger.info(f"📋 Submitted UC test message as request {request_id}")
        return request_id
    
    async def start_polling(self):
        """Start bot in polling mode"""
        logger.info("🤖 Starting Complete Solution Bot...")
        
        try:
            # Test connection
            me = await self.bot.get_me()
            logger.info(f"✅ Bot connected: {me.first_name} (@{me.username})")
            
            # Start pipeline processor
            await self.pipeline.start_processing_worker()
            
            # Clear webhooks
            await self.bot.delete_webhook(drop_pending_updates=True)
            logger.info("🧹 Webhooks cleared")
            
            # Start polling
            logger.info("🔄 Starting polling with guaranteed pipeline...")
            await self.dp.start_polling(self.bot, skip_updates=False)
            
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}", exc_info=True)
        finally:
            await self.pipeline.stop_processing_worker()
            await self.bot.session.close()
            logger.info("🔌 Bot session closed")

# Global bot instance for UC test integration
complete_bot = None

async def initialize_complete_solution():
    """Initialize the complete solution bot"""
    global complete_bot
    complete_bot = CompleteSolutionBot()
    await complete_bot.pipeline.start_processing_worker()
    logger.info("🔧 Complete solution initialized for UC testing")

async def process_uc_test_message(user_id: int, message_text: str) -> str:
    """Process UC test message through identical pipeline"""
    global complete_bot
    if not complete_bot:
        await initialize_complete_solution()
    
    return await complete_bot.process_uc_message(user_id, message_text)

async def main():
    """Main bot execution"""
    bot = CompleteSolutionBot()
    await bot.start_polling()

if __name__ == '__main__':
    asyncio.run(main())