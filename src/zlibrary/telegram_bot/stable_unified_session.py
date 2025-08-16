#!/usr/bin/env python3
"""
Stable Unified aiogram-Telethon Integration
Uses string session for maximum stability and proper event loop management
Based on deep research patterns for production deployment
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Configuration from your authenticated session
API_ID = 29950132
API_HASH = 'e0bf78283481e2341805e3e4e90d289a'
BOT_TOKEN = "7956300223:AAE9AYxSHldGJ6NotUcV2SiCpPNp_tP0TTI"  # Your bot token
TARGET_BOT = "epub_toc_based_sample_bot"

# Your stable string session - corruption-proof and long-term
STRING_SESSION = "1ApWapzMBu4PfiXOaKlWyf87-hEiVPCmh152Zt4x2areHOfSfMNDENrJBepoLDZBGqqwrfPvo4zeDB6M8jZZkgUy8pwU9Ba67fDMlnIkESlhbX_aJFLuzbfbd3IwSYh60pLsa0mk8huWxXwHpVNDENrJBepoLDZBGqqwrfPvo4zeDB6M8jZZkgUy8pwU9Ba67fDMlnIkESlhbX_aJFLuzbfbd3IwSYh60pLsa0mk8huWxXwHpVNDBeISwp4uGxqF6R_lxWBv_4l3pU3szXcJPS4kw9cTXZkwazvH28AOteP400dazpNpyEt2MbB56GIl9r5B7vQLcATUSW0rvd5-fWF_u2aw243XIHs7H39e_pJt2u0encXQM2Ca7X992Aad2WuHQDv7rDf1CuOO5s8UDZpvxc7ul4W53-PHyEguqLorV1uURpJH6HDDchK4WiTI="

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedMessageRouter:
    """
    Production-ready unified message router following deep research patterns
    Eliminates event loop conflicts and provides stable session management
    """
    
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        
        # Critical: Use StringSession for corruption-free persistence
        self.client = TelegramClient(
            StringSession(STRING_SESSION), 
            API_ID, 
            API_HASH,
            connection_retries=5,
            retry_delay=2,
            auto_reconnect=True,
            request_retries=3,
            timeout=30
        )
        
        self.message_queue = asyncio.Queue()
        self.is_running = False
        
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup handlers for both aiogram and Telethon"""
        
        # Aiogram bot handlers
        @self.dp.message(Command("start"))
        async def start_handler(message: types.Message):
            await self.process_message(message, "aiogram_bot")
        
        @self.dp.message()
        async def message_handler(message: types.Message):
            await self.process_message(message, "aiogram_bot")
            
        # Telethon user session handlers
        @self.client.on(events.NewMessage)
        async def telethon_handler(event):
            await self.process_message(event, "telethon_user")
    
    async def process_message(self, message, source: str):
        """Route messages from both sources to unified pipeline"""
        try:
            await self.message_queue.put({
                'message': message,
                'source': source,
                'timestamp': datetime.now().isoformat(),
                'user_id': self._extract_user_id(message, source)
            })
            logger.info(f"📨 Queued message from {source}")
        except Exception as e:
            logger.error(f"❌ Error queuing message: {e}")
    
    def _extract_user_id(self, message, source: str) -> Optional[int]:
        """Extract user ID from different message types"""
        try:
            if source == "aiogram_bot":
                return message.from_user.id if message.from_user else None
            elif source == "telethon_user":
                return getattr(message, 'sender_id', None)
        except:
            return None
    
    async def unified_handler(self):
        """Process messages from both aiogram and Telethon"""
        logger.info("🚀 Starting unified message processor")
        
        while self.is_running:
            try:
                # Wait for messages with timeout to allow graceful shutdown
                item = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                source = item['source']
                message = item['message']
                user_id = item['user_id']
                
                logger.info(f"🔄 Processing message from {source} (user: {user_id})")
                
                if source == "aiogram_bot":
                    await self._handle_bot_message(message)
                elif source == "telethon_user":
                    await self._handle_user_message(message)
                    
            except asyncio.TimeoutError:
                # Normal timeout for graceful shutdown check
                continue
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
    
    async def _handle_bot_message(self, message: types.Message):
        """Handle messages received via bot API"""
        text = message.text or ""
        user_id = message.from_user.id if message.from_user else "unknown"
        
        logger.info(f"🤖 Bot message from {user_id}: {text}")
        
        if text.startswith("/start"):
            await message.reply("✅ Unified bot is running!\nSend any message to test.")
        else:
            await message.reply(f"🔄 Echo from bot: {text}")
    
    async def _handle_user_message(self, event):
        """Handle messages from user session"""
        text = getattr(event, 'text', '') or ""
        user_id = getattr(event, 'sender_id', 'unknown')
        
        logger.info(f"👤 User session message from {user_id}: {text}")
        
        # This is where you can implement your book search logic
        # For now, just acknowledge receipt
        try:
            await event.reply(f"✅ Received via user session: {text}")
        except:
            pass  # May not be able to reply to all message types
    
    async def send_as_user(self, target: str, message: str):
        """
        Send message as authenticated user (100% manual emulation)
        This is your key method for triggering bot pipelines
        """
        try:
            if not self.client.is_connected():
                await self.client.connect()
                
            me = await self.client.get_me()
            sent_message = await self.client.send_message(target, message)
            
            logger.info(f"📤 Message sent as user {me.first_name} (ID: {me.id})")
            logger.info(f"🎯 To: {target}")
            logger.info(f"📋 Message ID: {sent_message.id}")
            logger.info(f"📖 Content: {message}")
            
            return {
                'success': True,
                'message_id': sent_message.id,
                'sender_name': me.first_name,
                'sender_id': me.id,
                'target': target,
                'content': message
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send as user: {e}")
            return {'success': False, 'error': str(e)}
    
    async def start(self):
        """Start the unified system with proper event loop management"""
        logger.info("🚀 Starting Unified aiogram-Telethon System")
        
        self.is_running = True
        
        try:
            # Critical: Use async context manager to avoid event loop conflicts
            async with self.client:
                me = await self.client.get_me()
                logger.info(f"✅ Telethon authenticated: {me.first_name} (ID: {me.id})")
                
                # Start all components in parallel - no event loop conflicts
                await asyncio.gather(
                    self.dp.start_polling(self.bot, skip_updates=True),
                    self.unified_handler(),
                    self.client.run_until_disconnected()
                )
        except KeyboardInterrupt:
            logger.info("👋 Shutting down gracefully...")
        except Exception as e:
            logger.error(f"❌ System error: {e}")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Graceful shutdown"""
        logger.info("🛑 Stopping unified system")
        self.is_running = False
        await self.bot.session.close()

class StableBookSearcher:
    """
    Dedicated class for stable book searches using your authenticated session
    """
    
    def __init__(self, router: UnifiedMessageRouter):
        self.router = router
        
    async def search_book(self, book_title: str, target_bot: str = TARGET_BOT):
        """
        Send book search as real user - 100% identical to manual typing
        This is your main method for EPUB retrieval
        """
        logger.info(f"📚 Initiating book search: '{book_title}'")
        
        result = await self.router.send_as_user(f"@{target_bot}", book_title)
        
        if result['success']:
            logger.info("🎯 Book search sent successfully!")
            logger.info("Expected pipeline:")
            logger.info(f"  📝 Bot logs: 'Text message from user {result['sender_id']}: {book_title}'")
            logger.info("  🔍 Z-Library search initiated")
            logger.info("  📄 EPUB delivery to your Telegram")
            logger.info("  ⏱️  Processing time: 8-12 seconds")
            
            return result
        else:
            logger.error(f"❌ Book search failed: {result.get('error')}")
            return result

# Main execution functions
async def test_book_search():
    """Test function for immediate book search"""
    router = UnifiedMessageRouter()
    searcher = StableBookSearcher(router)
    
    try:
        # Connect client for testing
        await router.client.connect()
        
        # Send your test message
        result = await searcher.search_book("Python Programming Guide Test")
        
        if result['success']:
            print("✅ SUCCESS! Check your Telegram for EPUB download!")
            print(f"📋 Message ID: {result['message_id']}")
            print(f"👤 Sent as: {result['sender_name']} (ID: {result['sender_id']})")
        else:
            print(f"❌ FAILED: {result['error']}")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        await router.client.disconnect()

async def run_full_system():
    """Run the complete unified system"""
    router = UnifiedMessageRouter()
    
    # Start the full system
    await router.start()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Quick test mode
        print("🧪 Running quick book search test...")
        asyncio.run(test_book_search())
    else:
        # Full system mode
        print("🚀 Starting full unified system...")
        asyncio.run(run_full_system())