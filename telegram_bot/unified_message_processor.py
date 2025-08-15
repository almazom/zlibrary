#!/usr/bin/env python3
"""
Unified Message Processor - Prevents Polling Conflicts
This ensures both manual and UC automated messages trigger IDENTICAL book search pipeline

SOLUTION APPROACH:
1. Single polling instance (eliminates conflicts)
2. Message source tagging (manual vs uc_test)
3. Identical pipeline processing regardless of source
4. External API for UC tests (no polling competition)
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
from dataclasses import dataclass, asdict
import aiohttp
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('unified_processor.log')
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class UnifiedMessageRequest:
    """Unified message request for both manual and UC test processing"""
    request_id: str
    user_id: int
    message_text: str
    timestamp: datetime
    source: str  # 'manual', 'uc_test', 'external_api'
    metadata: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class UnifiedPipelineProcessor:
    """Single processor that handles ALL message sources identically"""
    
    def __init__(self, bot: Bot, script_path: str):
        self.bot = bot
        self.script_path = script_path
        self.message_queue = asyncio.Queue()
        self.processing_worker_task = None
        self.request_registry = {}
        self.pipeline_stats = {
            'total_processed': 0,
            'manual_messages': 0,
            'uc_test_messages': 0,
            'external_api_messages': 0,
            'successful_pipelines': 0,
            'failed_pipelines': 0
        }
        
    async def start_processing_worker(self):
        """Start the unified processing worker"""
        self.processing_worker_task = asyncio.create_task(self._unified_processing_worker())
        logger.info("🔄 UNIFIED: Processing worker started")
    
    async def stop_processing_worker(self):
        """Stop the processing worker"""
        if self.processing_worker_task:
            self.processing_worker_task.cancel()
            try:
                await self.processing_worker_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 UNIFIED: Processing worker stopped")
    
    async def _unified_processing_worker(self):
        """Single worker that processes ALL messages identically"""
        logger.info("👷 UNIFIED: Worker thread started")
        
        while True:
            try:
                request = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._process_unified_request(request)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                logger.info("👷 UNIFIED: Worker thread cancelled")
                break
            except Exception as e:
                logger.error(f"❌ UNIFIED: Worker error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _process_unified_request(self, request: UnifiedMessageRequest):
        """Process request with IDENTICAL pipeline regardless of source"""
        logger.info(f"🚀 UNIFIED: Processing {request.source} message - ID: {request.request_id}")
        logger.info(f"📝 UNIFIED: Message: '{request.message_text}' from user {request.user_id}")
        
        start_time = time.time()
        pipeline_log = []
        
        try:
            # STAGE 1: Progress Message (IDENTICAL for all sources)
            progress_sent = await self._send_progress_message_unified(request)
            pipeline_log.append(f"Progress: {'✅' if progress_sent else '❌'}")
            
            if not progress_sent:
                raise Exception("Progress message failed")
            
            # STAGE 2: Book Search Execution (IDENTICAL logic)
            search_result = await self._execute_book_search_unified(request.message_text)
            pipeline_log.append(f"Search: {'✅' if search_result.get('status') == 'success' else '❌'}")
            
            # STAGE 3: Result Processing (IDENTICAL response handling)
            if search_result.get("status") != "success":
                await self._send_error_message_unified(request, search_result.get('message', 'Search failed'))
                pipeline_log.append("Error sent: ✅")
            else:
                book_result = search_result.get("result", {})
                if not book_result.get("found"):
                    await self._send_not_found_unified(request)
                    pipeline_log.append("Not found sent: ✅")
                else:
                    # STAGE 4: EPUB Delivery (IDENTICAL file handling)
                    epub_sent = await self._send_epub_unified(request, book_result)
                    pipeline_log.append(f"EPUB: {'✅' if epub_sent else '❌'}")
            
            duration = time.time() - start_time
            self.pipeline_stats['successful_pipelines'] += 1
            self.pipeline_stats[f'{request.source}_messages'] += 1
            
            # Store result in registry
            self.request_registry[request.request_id] = {
                'request': request,
                'status': 'completed',
                'duration': duration,
                'pipeline_log': pipeline_log,
                'completed_at': datetime.now()
            }
            
            logger.info(f"✅ UNIFIED: Request {request.request_id} completed in {duration:.2f}s")
            logger.info(f"📋 UNIFIED: Pipeline stages - {' | '.join(pipeline_log)}")
            
        except Exception as e:
            duration = time.time() - start_time
            self.pipeline_stats['failed_pipelines'] += 1
            
            self.request_registry[request.request_id] = {
                'request': request,
                'status': 'failed',
                'error': str(e),
                'duration': duration,
                'completed_at': datetime.now()
            }
            
            logger.error(f"❌ UNIFIED: Request {request.request_id} failed after {duration:.2f}s - {e}")
            
            # Send failure notification
            try:
                await self.bot.send_message(
                    chat_id=request.user_id,
                    text=f"❌ Request failed: {str(e)[:100]}..."
                )
            except Exception as notify_error:
                logger.error(f"❌ UNIFIED: Failed to send failure notification: {notify_error}")
        
        finally:
            self.pipeline_stats['total_processed'] += 1
    
    async def _send_progress_message_unified(self, request: UnifiedMessageRequest, max_attempts: int = 5) -> bool:
        """Send progress message with unified retry logic"""
        for attempt in range(max_attempts):
            try:
                await self.bot.send_message(
                    chat_id=request.user_id,
                    text=f"🔍 Searching for book... (via {request.source})"
                )
                logger.info(f"✅ UNIFIED: Progress sent to {request.user_id} (attempt {attempt + 1})")
                return True
            except Exception as e:
                logger.warning(f"⚠️ UNIFIED: Progress attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))
        
        return False
    
    async def _execute_book_search_unified(self, query: str) -> Dict[str, Any]:
        """Execute book search with IDENTICAL parameters for all sources"""
        logger.info(f"🔍 UNIFIED: Executing search for: '{query}'")
        
        cmd = [self.script_path, "--download", query]
        logger.debug(f"UNIFIED: Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(self.script_path).parent.parent,
                timeout=90
            )
            
            logger.debug(f"UNIFIED: Return code: {result.returncode}")
            logger.debug(f"UNIFIED: Output: {result.stdout[:200]}...")
            
            if result.returncode != 0:
                logger.error(f"UNIFIED: Script error: {result.stderr}")
                return {"status": "error", "message": "Script execution failed"}
            
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            logger.error("UNIFIED: Script timeout")
            return {"status": "error", "message": "Search timeout (90s)"}
        except json.JSONDecodeError as e:
            logger.error(f"UNIFIED: JSON decode error: {e}")
            return {"status": "error", "message": "Invalid response format"}
        except Exception as e:
            logger.error(f"UNIFIED: Unexpected error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_error_message_unified(self, request: UnifiedMessageRequest, error_msg: str) -> bool:
        """Send error message with unified formatting"""
        try:
            await self.bot.send_message(
                chat_id=request.user_id,
                text=f"❌ Search failed: {error_msg}\n\nSource: {request.source}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ UNIFIED: Error message failed: {e}")
            return False
    
    async def _send_not_found_unified(self, request: UnifiedMessageRequest) -> bool:
        """Send not found message with unified formatting"""
        try:
            await self.bot.send_message(
                chat_id=request.user_id,
                text=f"❌ Book not found: '{request.message_text}'\n\nSource: {request.source}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ UNIFIED: Not found message failed: {e}")
            return False
    
    async def _send_epub_unified(self, request: UnifiedMessageRequest, book_result: Dict[str, Any]) -> bool:
        """Send EPUB file with unified delivery logic"""
        epub_path = book_result.get("epub_download_url")
        book_info = book_result.get("book_info", {})
        title = book_info.get("title", "Unknown Book")
        
        if not epub_path or not Path(epub_path).exists():
            await self.bot.send_message(
                chat_id=request.user_id,
                text=f"❌ EPUB not available for: '{title}'"
            )
            return False
        
        try:
            document = FSInputFile(epub_path, filename=f"{title}.epub")
            await self.bot.send_document(
                chat_id=request.user_id,
                document=document,
                caption=f"📖 {title}\n\n🔧 Delivered via {request.source} pipeline"
            )
            logger.info(f"✅ UNIFIED: EPUB delivered to {request.user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ UNIFIED: EPUB delivery failed: {e}")
            return False
    
    async def submit_message_request(self, user_id: int, message_text: str, source: str, metadata: Dict[str, Any] = None) -> str:
        """Submit message request for unified processing"""
        request = UnifiedMessageRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            message_text=message_text,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {}
        )
        
        await self.message_queue.put(request)
        logger.info(f"📥 UNIFIED: Queued {source} request {request.request_id}")
        return request.request_id
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline processing statistics"""
        return {
            **self.pipeline_stats,
            'success_rate': (self.pipeline_stats['successful_pipelines'] / max(1, self.pipeline_stats['total_processed'])) * 100,
            'queue_size': self.message_queue.qsize(),
            'active_requests': len([r for r in self.request_registry.values() if r['status'] == 'processing'])
        }
    
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific request"""
        if request_id in self.request_registry:
            result = self.request_registry[request_id].copy()
            # Convert request object to dict for JSON serialization
            result['request'] = result['request'].to_dict()
            return result
        return None

class UnifiedTelegramBot:
    """Unified Telegram bot with single polling and external API"""
    
    def __init__(self):
        self.bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.dp = Dispatcher()
        self.script_path = os.getenv('SCRIPT_PATH', '/home/almaz/microservices/zlibrary_api_module/scripts/book_search.sh')
        self.processor = UnifiedPipelineProcessor(self.bot, self.script_path)
        self.api_server = None
        self.api_port = int(os.getenv('UNIFIED_API_PORT', '8765'))
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup Telegram message handlers"""
        self.dp.message.register(self.start_handler, Command(commands=['start']))
        self.dp.message.register(self.stats_handler, Command(commands=['stats']))
        self.dp.message.register(self.manual_message_handler)
    
    async def start_handler(self, message: types.Message):
        """Handle /start command"""
        logger.info(f"🚀 /start from user {message.from_user.id}")
        await message.answer(
            "📚 Unified Book Search Bot\n\n"
            "✨ Features:\n"
            "• Send book titles for EPUB search\n"
            "• Identical pipeline for manual & automated messages\n"
            "• Conflict-free processing\n\n"
            "🔧 Use /stats to see processing statistics"
        )
    
    async def stats_handler(self, message: types.Message):
        """Handle /stats command"""
        stats = self.processor.get_pipeline_stats()
        stats_text = f"""
📊 **Pipeline Statistics**

🔄 **Processing:**
• Total processed: {stats['total_processed']}
• Success rate: {stats['success_rate']:.1f}%
• Queue size: {stats['queue_size']}

📝 **Message Sources:**
• Manual: {stats['manual_messages']}
• UC Tests: {stats['uc_test_messages']}
• External API: {stats['external_api_messages']}

✅ **Results:**
• Successful: {stats['successful_pipelines']}
• Failed: {stats['failed_pipelines']}
"""
        await message.answer(stats_text, parse_mode='Markdown')
    
    async def manual_message_handler(self, message: types.Message):
        """Handle manual text messages through unified processor"""
        logger.info(f"📝 Manual message from {message.from_user.id}: '{message.text}'")
        
        request_id = await self.processor.submit_message_request(
            user_id=message.from_user.id,
            message_text=message.text,
            source='manual',
            metadata={'telegram_message_id': message.message_id}
        )
        
        logger.info(f"📋 Manual message queued as {request_id}")
    
    async def start_api_server(self):
        """Start external API server for UC tests"""
        from aiohttp import web
        
        app = web.Application()
        app.router.add_post('/submit_message', self.api_submit_message)
        app.router.add_get('/request_status/{request_id}', self.api_request_status)
        app.router.add_get('/stats', self.api_stats)
        app.router.add_get('/health', self.api_health)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.api_port)
        await site.start()
        
        logger.info(f"🌐 Unified API server started on port {self.api_port}")
        return runner
    
    async def api_submit_message(self, request):
        """API endpoint for external message submission"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            message_text = data.get('message_text')
            source = data.get('source', 'external_api')
            metadata = data.get('metadata', {})
            
            if not user_id or not message_text:
                return web.json_response({'error': 'user_id and message_text required'}, status=400)
            
            request_id = await self.processor.submit_message_request(
                user_id=int(user_id),
                message_text=message_text,
                source=source,
                metadata=metadata
            )
            
            return web.json_response({
                'success': True,
                'request_id': request_id,
                'message': f'Message queued for processing'
            })
            
        except Exception as e:
            logger.error(f"❌ API submit error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def api_request_status(self, request):
        """API endpoint for request status checking"""
        request_id = request.match_info['request_id']
        status = await self.processor.get_request_status(request_id)
        
        if status:
            return web.json_response(status)
        else:
            return web.json_response({'error': 'Request not found'}, status=404)
    
    async def api_stats(self, request):
        """API endpoint for pipeline statistics"""
        stats = self.processor.get_pipeline_stats()
        return web.json_response(stats)
    
    async def api_health(self, request):
        """API health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'queue_size': self.processor.message_queue.qsize()
        })
    
    async def start_unified_bot(self):
        """Start the unified bot with both polling and API server"""
        logger.info("🤖 Starting Unified Message Processor Bot...")
        
        try:
            # Test bot connection
            me = await self.bot.get_me()
            logger.info(f"✅ Bot connected: {me.first_name} (@{me.username})")
            
            # Start processor
            await self.processor.start_processing_worker()
            
            # Start API server
            api_runner = await self.start_api_server()
            
            # Clear webhooks and start polling
            await self.bot.delete_webhook(drop_pending_updates=True)
            logger.info("🧹 Webhooks cleared")
            
            logger.info("🔄 Starting unified polling...")
            await self.dp.start_polling(self.bot, skip_updates=False)
            
        except KeyboardInterrupt:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}", exc_info=True)
        finally:
            await self.processor.stop_processing_worker()
            try:
                if 'api_runner' in locals():
                    await api_runner.cleanup()
            except:
                pass
            await self.bot.session.close()
            logger.info("🔌 Unified bot session closed")

# External API client for UC tests
class UnifiedAPIClient:
    """Client for UC tests to submit messages without polling conflicts"""
    
    def __init__(self, api_url: str = None):
        self.api_url = api_url or f"http://localhost:{os.getenv('UNIFIED_API_PORT', '8765')}"
        self.session = None
    
    @asynccontextmanager
    async def session_context(self):
        """Async context manager for HTTP session"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        try:
            yield self.session
        finally:
            await self.session.close()
    
    async def submit_uc_message(self, user_id: int, message_text: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        """Submit UC test message via API (no polling conflicts)"""
        async with self.session_context() as session:
            try:
                payload = {
                    'user_id': user_id,
                    'message_text': message_text,
                    'source': 'uc_test',
                    'metadata': metadata or {'test_type': 'automated_uc'}
                }
                
                async with session.post(f"{self.api_url}/submit_message", json=payload) as response:
                    result = await response.json()
                    
                    if result.get('success'):
                        logger.info(f"✅ UC message submitted: {result['request_id']}")
                        return result['request_id']
                    else:
                        logger.error(f"❌ UC submission failed: {result.get('error')}")
                        return None
                        
            except Exception as e:
                logger.error(f"❌ UC API error: {e}")
                return None
    
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of submitted request"""
        async with self.session_context() as session:
            try:
                async with session.get(f"{self.api_url}/request_status/{request_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"⚠️ Request {request_id} status: {response.status}")
                        return None
                        
            except Exception as e:
                logger.error(f"❌ Status check error: {e}")
                return None
    
    async def wait_for_completion(self, request_id: str, timeout: int = 120) -> Dict[str, Any]:
        """Wait for request completion with timeout"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            status = await self.get_request_status(request_id)
            
            if status and status.get('status') in ['completed', 'failed']:
                logger.info(f"✅ UC request {request_id} finished: {status['status']}")
                return status
            
            await asyncio.sleep(2)
        
        logger.warning(f"⏰ UC request {request_id} timeout after {timeout}s")
        return {'status': 'timeout', 'error': 'Request timeout'}

async def main():
    """Main execution"""
    bot = UnifiedTelegramBot()
    await bot.start_unified_bot()

if __name__ == '__main__':
    asyncio.run(main())