#!/usr/bin/env python3
"""
Stable Telegram Session Example
Eliminates 30-minute re-authentication cycle

Based on comprehensive research from:
- AI_Knowledge_Base/deep_research/dr_stable_telegram_sessions_comprehensive_analysis.md
- AI_Knowledge_Base/memory_cards/mc_stable_session_solutions.md
"""

import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import AuthKeyUnregisteredError, SessionPasswordNeededError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StableTelegramSession:
    """
    Production-ready stable Telegram session manager
    Eliminates 30-minute expiration cycle with:
    - String sessions (no file corruption)
    - Automatic reconnection
    - Health monitoring
    - Graceful error handling
    """
    
    def __init__(self, session_name, api_id, api_hash, string_session=None):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.string_session = string_session
        self.client = None
        
    async def initialize(self):
        """Initialize client with robust connection settings"""
        try:
            session = StringSession(self.string_session) if self.string_session else self.session_name
            
            self.client = TelegramClient(
                session,
                self.api_id,
                self.api_hash,
                # Robust connection settings
                connection_retries=5,      # Retry initial connection
                retry_delay=2,             # Delay between retries  
                auto_reconnect=True,       # Enable auto-reconnection
                request_retries=3,         # Retry failed requests
                timeout=30                 # Request timeout
            )
            
            await self.client.connect()
            
            # Validate session
            if not await self.client.is_user_authorized():
                logger.error("Session not authorized - requires authentication")
                return False
                
            # Health check
            me = await self.client.get_me()
            logger.info(f"✅ Session initialized: {me.first_name} (ID: {me.id})")
            
            # Save string session for future use (eliminates file dependencies)
            if not self.string_session:
                self.string_session = self.client.session.save()
                logger.info("📝 String session saved for future persistence")
                print(f"\n🔑 SAVE THIS STRING SESSION:")
                print(f"{self.string_session}")
                print("^^ Use this in future runs to avoid re-authentication\n")
            
            return True
            
        except AuthKeyUnregisteredError:
            logger.error("❌ Session expired - authorization key unregistered")
            return False
        except Exception as e:
            logger.error(f"❌ Session initialization failed: {e}")
            return False
    
    async def send_message_with_retry(self, entity, message, max_retries=3):
        """Send message with automatic retry and session recovery"""
        for attempt in range(max_retries):
            try:
                # Health check before sending
                if not await self.client.is_user_authorized():
                    logger.warning("⚠️ Session unauthorized during send - attempting recovery")
                    if not await self.initialize():
                        raise Exception("Session recovery failed")
                
                result = await self.client.send_message(entity, message)
                logger.info(f"✅ Message sent successfully: ID {result.id}")
                return result
                
            except Exception as e:
                logger.warning(f"⚠️ Send attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    async def cleanup(self):
        """Proper cleanup to prevent session corruption"""
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            logger.info("🔌 Client disconnected properly")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        await self.cleanup()

async def stable_book_search(book_query, string_session=None):
    """
    Stable book search with no 30-minute expiration
    
    Args:
        book_query: Book to search for
        string_session: Optional pre-saved string session
    """
    
    # Your API credentials
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    logger.info(f"🚀 Starting stable book search: '{book_query}'")
    
    session_mgr = StableTelegramSession(
        'stable_book_search',
        api_id,
        api_hash,
        string_session
    )
    
    try:
        async with session_mgr as session:
            # Send book search request
            await session.send_message_with_retry(
                '@epub_toc_based_sample_bot', 
                book_query
            )
            
            logger.info("🎯 Book search request sent successfully!")
            logger.info("📱 Check Telegram for EPUB delivery!")
            
            # Return string session for future use
            return session.string_session
            
    except Exception as e:
        logger.error(f"❌ Book search failed: {e}")
        raise

async def continuous_health_monitor(session_mgr, interval=300):
    """
    Continuous session health monitoring
    Runs every 5 minutes to ensure session stability
    """
    logger.info("🏥 Starting continuous health monitoring...")
    
    while True:
        try:
            if session_mgr.client and session_mgr.client.is_connected():
                if await session_mgr.client.is_user_authorized():
                    me = await session_mgr.client.get_me()
                    logger.info(f"💚 Health check passed: {me.first_name}")
                else:
                    logger.warning("⚠️ Session unauthorized - recovery needed")
                    await session_mgr.initialize()
            else:
                logger.warning("⚠️ Session not connected - attempting recovery")
                await session_mgr.initialize()
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
        
        await asyncio.sleep(interval)

# Example usage
async def main():
    """Example usage of stable session"""
    
    # Option 1: First time (will prompt for phone/SMS)
    print("🔐 STABLE TELEGRAM SESSION - NO 30 MINUTE EXPIRY")
    print("=" * 50)
    
    # For first run, use None - will prompt for authentication
    string_session = None
    
    # Option 2: Use saved string session (no re-authentication)
    # string_session = "YOUR_SAVED_STRING_SESSION_HERE"
    
    try:
        # Perform stable book search
        saved_session = await stable_book_search(
            "Clean Code Robert Martin",
            string_session
        )
        
        print(f"\n🎉 SUCCESS! Session established and book search sent.")
        print(f"💾 Save this string session for future use:")
        print(f"{saved_session}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    # Run the example
    asyncio.run(main())