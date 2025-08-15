#!/usr/bin/env python3
"""
Simple test to verify the complete solution works
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | TEST | %(levelname)s | %(message)s'
)

logger = logging.getLogger(__name__)

async def test_imports():
    """Test that all imports work correctly"""
    logger.info("🧪 Testing imports...")
    
    try:
        # Test aiogram imports
        from aiogram import Bot, Dispatcher, types
        from aiogram.types import FSInputFile
        from aiogram.filters import Command
        logger.info("✅ aiogram imports successful")
        
        # Test aiohttp import
        import aiohttp
        logger.info("✅ aiohttp import successful")
        
        # Test complete solution import
        try:
            from complete_solution import CompleteSolutionBot, MessageQueue, PipelineGuaranteor
            logger.info("✅ complete_solution imports successful")
        except Exception as e:
            logger.error(f"❌ complete_solution import failed: {e}")
            return False
        
        # Test bot initialization
        TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        if not TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment")
            return False
            
        bot = Bot(token=TOKEN)
        logger.info("✅ Bot initialization successful")
        
        # Test connection (optional)
        try:
            me = await bot.get_me()
            logger.info(f"✅ Bot connection test successful: {me.first_name} (@{me.username})")
        except Exception as e:
            logger.warning(f"⚠️ Bot connection test failed (may be due to rate limiting): {e}")
        finally:
            await bot.session.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import test failed: {e}")
        return False

async def test_message_queue():
    """Test message queue functionality"""
    logger.info("🧪 Testing message queue...")
    
    try:
        from complete_solution import MessageQueue, MessageRequest
        from datetime import datetime
        
        queue = MessageQueue()
        
        # Test adding request
        request = MessageRequest(
            request_id="test-123",
            user_id=12345,
            message_text="Test message",
            timestamp=datetime.now(),
            source="test"
        )
        
        request_id = await queue.add_request(request)
        logger.info(f"✅ Message queue add successful: {request_id}")
        
        # Test getting request
        retrieved = await queue.get_next_request()
        if retrieved and retrieved.request_id == request.request_id:
            logger.info("✅ Message queue get successful")
        else:
            logger.error("❌ Message queue get failed")
            return False
        
        # Test marking completed
        await queue.mark_completed(request_id, {"status": "success"})
        logger.info("✅ Message queue completion marking successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Message queue test failed: {e}")
        return False

async def run_tests():
    """Run all tests"""
    logger.info("🚀 Starting Complete Solution Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Message Queue Test", test_message_queue),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 30)
        
        try:
            if await test_func():
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n" + "=" * 50)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - Complete Solution Ready!")
        return True
    else:
        logger.error("❌ Some tests failed - Solution needs fixes")
        return False

if __name__ == '__main__':
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)