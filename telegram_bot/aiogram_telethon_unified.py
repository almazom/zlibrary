#!/usr/bin/env python3
"""
Aiogram-Telethon Unified Message Sender
Based on deep research for conflict-free integration

ARCHITECTURE:
- Single event loop (no RuntimeError conflicts)
- Message queue coordination between aiogram/Telethon
- Unified pipeline ensures manual = automated pipeline 100%
- Proper event loop management (no .start() before asyncio.run())
"""

import asyncio
import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import uuid
from dotenv import load_dotenv

# Import both libraries with proper initialization
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.types import User

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aiogram_telethon_unified.log')
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class UnifiedMessage:
    """Unified message structure for both aiogram and Telethon"""
    message_id: str
    user_id: int
    text: str
    source: str  # 'aiogram_bot', 'telethon_user', 'manual_simulation'
    timestamp: datetime
    chat_id: Optional[int] = None
    metadata: Dict[str, Any] = None

class UnifiedMessageRouter:
    """Routes messages from both aiogram and Telethon to unified pipeline"""
    
    def __init__(self, bot_token: str, api_id: int, api_hash: str, session_name: str = 'unified_session'):
        # Initialize both clients (NO .start() calls here!)
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()
        self.client = TelegramClient(session_name, api_id, api_hash)
        
        # Message queue for unified processing
        self.message_queue = asyncio.Queue()
        self.processed_messages = {}
        self.stats = {
            'aiogram_messages': 0,
            'telethon_messages': 0,
            'manual_simulations': 0,
            'successful_pipelines': 0,
            'failed_pipelines': 0
        }
        
        # Setup handlers
        self._setup_aiogram_handlers()
        self._setup_telethon_handlers()
        
        logger.info("🔧 Unified Message Router initialized")
    
    def _setup_aiogram_handlers(self):
        """Setup aiogram bot handlers"""
        
        @self.dp.message(Command(commands=['start']))
        async def start_handler(message: types.Message):
            logger.info(f"🤖 AIOGRAM: /start from user {message.from_user.id}")
            await message.answer(
                "📚 Unified Book Search Bot\n\n"
                "✨ This bot uses aiogram-Telethon unified architecture\n"
                "🔧 Send book titles to trigger identical pipeline processing\n\n"
                "Example: 'Clean Code Robert Martin'"
            )
        
        @self.dp.message()
        async def message_handler(message: types.Message):
            """Handle all text messages through unified pipeline"""
            logger.info(f"📝 AIOGRAM: Message from user {message.from_user.id}: '{message.text}'")
            
            unified_msg = UnifiedMessage(
                message_id=str(uuid.uuid4()),
                user_id=message.from_user.id,
                text=message.text,
                source='aiogram_bot',
                timestamp=datetime.now(),
                chat_id=message.chat.id,
                metadata={'telegram_message_id': message.message_id}
            )
            
            await self.route_to_unified_pipeline(unified_msg)
    
    def _setup_telethon_handlers(self):
        """Setup Telethon user session handlers"""
        
        @self.client.on(events.NewMessage)
        async def telethon_handler(event):
            """Handle messages from user session"""
            # Skip messages from bots to avoid loops
            if hasattr(event.sender, 'bot') and event.sender.bot:
                return
                
            logger.info(f"👤 TELETHON: Message from user {event.sender_id}: '{event.text}'")
            
            unified_msg = UnifiedMessage(
                message_id=str(uuid.uuid4()),
                user_id=event.sender_id,
                text=event.text,
                source='telethon_user',
                timestamp=datetime.now(),
                chat_id=event.chat_id,
                metadata={'telethon_event_id': event.id}
            )
            
            await self.route_to_unified_pipeline(unified_msg)
    
    async def route_to_unified_pipeline(self, message: UnifiedMessage):
        """Route message to unified processing pipeline"""
        await self.message_queue.put(message)
        self.stats[f'{message.source.split("_")[0]}_messages'] += 1
        logger.info(f"📥 ROUTER: Queued {message.source} message {message.message_id}")
    
    async def unified_pipeline_processor(self):
        """Process messages from unified queue (IDENTICAL pipeline for all sources)"""
        logger.info("👷 PIPELINE: Unified processor started")
        
        while True:
            try:
                message = await self.message_queue.get()
                await self._process_unified_message(message)
            except asyncio.CancelledError:
                logger.info("👷 PIPELINE: Processor cancelled")
                break
            except Exception as e:
                logger.error(f"❌ PIPELINE: Processor error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _process_unified_message(self, message: UnifiedMessage):
        """Process single message with IDENTICAL pipeline regardless of source"""
        logger.info(f"🚀 PIPELINE: Processing {message.source} message - ID: {message.message_id}")
        logger.info(f"📖 Query: '{message.text}' from user {message.user_id}")
        
        start_time = time.time()
        pipeline_stages = []
        
        try:
            # Stage 1: Send progress message (IDENTICAL for all sources)
            progress_sent = await self._send_progress_message(message)
            pipeline_stages.append(f"Progress: {'✅' if progress_sent else '❌'}")
            
            if not progress_sent:
                raise Exception("Progress message failed")
            
            # Stage 2: Execute book search (IDENTICAL logic)
            search_result = await self._execute_book_search_pipeline(message.text)
            pipeline_stages.append(f"Search: {'✅' if search_result.get('success') else '❌'}")
            
            # Stage 3: Handle results (IDENTICAL response logic)
            if not search_result.get('success'):
                await self._send_error_response(message, search_result.get('error', 'Search failed'))
                pipeline_stages.append("Error sent: ✅")
            else:
                # Success - send book result
                book_info = search_result.get('book_info', {})
                if book_info.get('found'):
                    await self._send_book_result(message, book_info)
                    pipeline_stages.append("Book result sent: ✅")
                else:
                    await self._send_not_found(message)
                    pipeline_stages.append("Not found sent: ✅")
            
            duration = time.time() - start_time
            self.stats['successful_pipelines'] += 1
            
            # Store processing result
            self.processed_messages[message.message_id] = {
                'message': message,
                'success': True,
                'duration': duration,
                'pipeline_stages': pipeline_stages,
                'processed_at': datetime.now()
            }
            
            logger.info(f"✅ PIPELINE: Message {message.message_id} processed in {duration:.2f}s")
            logger.info(f"📋 Stages: {' | '.join(pipeline_stages)}")
            
        except Exception as e:
            duration = time.time() - start_time
            self.stats['failed_pipelines'] += 1
            
            self.processed_messages[message.message_id] = {
                'message': message,
                'success': False,
                'error': str(e),
                'duration': duration,
                'processed_at': datetime.now()
            }
            
            logger.error(f"❌ PIPELINE: Message {message.message_id} failed after {duration:.2f}s - {e}")
    
    async def _send_progress_message(self, message: UnifiedMessage) -> bool:
        """Send progress message via appropriate channel"""
        try:
            progress_text = f"🔍 Searching for book... (via {message.source})"
            
            if message.source == 'aiogram_bot':
                # Send via bot
                await self.bot.send_message(chat_id=message.user_id, text=progress_text)
            else:
                # Send via user session (if we have chat_id)
                if message.chat_id:
                    await self.client.send_message(message.chat_id, progress_text)
            
            logger.info(f"✅ PIPELINE: Progress sent to {message.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ PIPELINE: Progress message failed: {e}")
            return False
    
    async def _execute_book_search_pipeline(self, query: str) -> Dict[str, Any]:
        """Execute book search - IDENTICAL logic for all message sources"""
        logger.info(f"🔍 PIPELINE: Executing search for: '{query}'")
        
        # Simulate book search logic (replace with actual implementation)
        await asyncio.sleep(0.3)  # Simulate search time
        
        # Simple simulation based on query content
        if any(keyword in query.lower() for keyword in ['clean code', 'python', 'programming']):
            return {
                'success': True,
                'book_info': {
                    'found': True,
                    'title': query,
                    'author': 'Various',
                    'format': 'EPUB',
                    'download_ready': True
                }
            }
        elif 'nonexistent' in query.lower():
            return {
                'success': True,
                'book_info': {'found': False}
            }
        else:
            return {
                'success': False,
                'error': 'Search service temporarily unavailable'
            }
    
    async def _send_book_result(self, message: UnifiedMessage, book_info: Dict[str, Any]):
        """Send book result via appropriate channel"""
        try:
            result_text = f"📖 Found: {book_info['title']}\n✅ Ready for download!"
            
            if message.source == 'aiogram_bot':
                await self.bot.send_message(chat_id=message.user_id, text=result_text)
            else:
                if message.chat_id:
                    await self.client.send_message(message.chat_id, result_text)
            
            logger.info(f"✅ PIPELINE: Book result sent to {message.user_id}")
            
        except Exception as e:
            logger.error(f"❌ PIPELINE: Failed to send book result: {e}")
    
    async def _send_error_response(self, message: UnifiedMessage, error_msg: str):
        """Send error response via appropriate channel"""
        try:
            error_text = f"❌ Search failed: {error_msg}"
            
            if message.source == 'aiogram_bot':
                await self.bot.send_message(chat_id=message.user_id, text=error_text)
            else:
                if message.chat_id:
                    await self.client.send_message(message.chat_id, error_text)
            
        except Exception as e:
            logger.error(f"❌ PIPELINE: Failed to send error: {e}")
    
    async def _send_not_found(self, message: UnifiedMessage):
        """Send not found message via appropriate channel"""
        try:
            not_found_text = f"❌ Book not found: '{message.text}'"
            
            if message.source == 'aiogram_bot':
                await self.bot.send_message(chat_id=message.user_id, text=not_found_text)
            else:
                if message.chat_id:
                    await self.client.send_message(message.chat_id, not_found_text)
            
        except Exception as e:
            logger.error(f"❌ PIPELINE: Failed to send not found: {e}")
    
    async def send_manual_simulation(self, user_id: int, message_text: str) -> str:
        """Send message that simulates manual user input (IDENTICAL pipeline)"""
        logger.info(f"🎯 MANUAL SIMULATION: Sending '{message_text}' as if user {user_id} typed it")
        
        unified_msg = UnifiedMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            text=message_text,
            source='manual_simulation',
            timestamp=datetime.now(),
            metadata={'simulated_manual': True}
        )
        
        await self.route_to_unified_pipeline(unified_msg)
        self.stats['manual_simulations'] += 1
        
        logger.info(f"📋 MANUAL SIMULATION: Queued as {unified_msg.message_id}")
        return unified_msg.message_id
    
    async def start_unified_system(self):
        """Start the unified system with proper event loop management"""
        logger.info("🚀 Starting Aiogram-Telethon Unified System...")
        
        try:
            # Test bot connection
            me = await self.bot.get_me()
            logger.info(f"✅ Aiogram bot connected: {me.first_name} (@{me.username})")
            
            # Start Telethon with proper async context (NO .start() call!)
            async with self.client:
                logger.info("✅ Telethon client connected")
                
                # Start unified pipeline processor
                processor_task = asyncio.create_task(self.unified_pipeline_processor())
                
                # Clear webhooks and start aiogram polling
                await self.bot.delete_webhook(drop_pending_updates=True)
                logger.info("🧹 Webhooks cleared, starting polling")
                
                # Run both systems in parallel (shared event loop!)
                await asyncio.gather(
                    self.dp.start_polling(self.bot, skip_updates=False),
                    self.client.run_until_disconnected(),
                    processor_task
                )
                
        except KeyboardInterrupt:
            logger.info("👋 System stopped by user")
        except Exception as e:
            logger.error(f"❌ System error: {e}", exc_info=True)
        finally:
            await self.bot.session.close()
            logger.info("🔌 System shutdown complete")

class UnifiedBookSearchDemo:
    """Demonstrates unified book search with aiogram-Telethon integration"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '')
        self.test_user_id = int(os.getenv('CHAT_ID', '14835038'))
        
        if not all([self.bot_token, self.api_id, self.api_hash]):
            raise ValueError("Missing required environment variables")
        
        self.router = UnifiedMessageRouter(
            bot_token=self.bot_token,
            api_id=self.api_id,
            api_hash=self.api_hash
        )
    
    async def demonstrate_unified_pipeline(self):
        """Demonstrate that manual simulation triggers identical pipeline"""
        logger.info("🎯 DEMONSTRATION: Unified Pipeline with Aiogram-Telethon")
        logger.info("=" * 70)
        
        # Test book titles
        test_books = [
            "Clean Code Robert Martin",
            "Python Programming Guide",
            "Design Patterns Gang of Four"
        ]
        
        for i, book in enumerate(test_books, 1):
            logger.info(f"\n📚 Test {i}: '{book}'")
            logger.info("-" * 50)
            
            # Send manual simulation (triggers IDENTICAL pipeline as real manual message)
            message_id = await self.router.send_manual_simulation(self.test_user_id, book)
            
            # Wait for processing
            await asyncio.sleep(3)
            
            # Check result
            if message_id in self.router.processed_messages:
                result = self.router.processed_messages[message_id]
                if result['success']:
                    logger.info(f"✅ Pipeline executed successfully in {result['duration']:.2f}s")
                    logger.info(f"📋 Stages: {result['pipeline_stages']}")
                else:
                    logger.error(f"❌ Pipeline failed: {result.get('error')}")
            else:
                logger.warning("⏳ Message still processing...")
        
        # Show statistics
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"Stats: {self.router.stats}")
        logger.info("=" * 70)

async def main():
    """Main execution with proper event loop management"""
    demo = UnifiedBookSearchDemo()
    
    # Start demonstration
    demo_task = asyncio.create_task(demo.demonstrate_unified_pipeline())
    
    # Start unified system (this will run indefinitely)
    system_task = asyncio.create_task(demo.router.start_unified_system())
    
    try:
        # Wait for demonstration to complete, then optionally continue system
        await demo_task
        logger.info("🎉 Demonstration complete! System will continue running...")
        logger.info("Send messages to the bot to see unified pipeline in action")
        logger.info("Press Ctrl+C to stop")
        
        # Keep system running
        await system_task
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
        demo_task.cancel()
        system_task.cancel()

if __name__ == '__main__':
    # Critical: Single asyncio.run() call for proper event loop management
    asyncio.run(main())