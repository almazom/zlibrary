#!/usr/bin/env python3
"""
Test script to understand aiogram's message sending logging behavior
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

# Enable aiogram internal logging
aiogram_logger = logging.getLogger('aiogram')
aiogram_logger.setLevel(logging.DEBUG)

# Enable aiohttp logging (used by aiogram for HTTP requests)
aiohttp_logger = logging.getLogger('aiohttp')
aiohttp_logger.setLevel(logging.DEBUG)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def test_message_logging():
    """Test what gets logged during message sending"""
    bot = Bot(token=TOKEN)
    
    print("🧪 Testing aiogram message logging...")
    
    # Test user ID from logs
    user_id = 14835038
    
    try:
        # Attempt to send a test message
        print(f"📤 Attempting to send test message to user {user_id}")
        result = await bot.send_message(
            chat_id=user_id,
            text="🧪 TEST: This is a test message to check logging behavior"
        )
        print(f"✅ Message sent successfully: {result}")
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(test_message_logging())