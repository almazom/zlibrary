#!/usr/bin/env python3
"""
Test to reproduce the missing progress message issue
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.exceptions import TelegramConflictError, TelegramNetworkError

load_dotenv()

# Configure comprehensive logging to see ALL aiogram activity
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

# Enable ALL aiogram internal logging
for logger_name in ['aiogram', 'aiohttp', 'aiogram.dispatcher', 'aiogram.event', 'aiogram.client', 'aiogram.methods']:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def test_progress_message_behavior():
    """Test if progress messages are sent but lost during conflicts"""
    bot = Bot(token=TOKEN)
    user_id = 14835038  # Test user from logs
    
    print("🧪 Testing progress message behavior during simulated conflicts...")
    
    try:
        # Test 1: Send a progress message
        print("📤 Test 1: Sending progress message...")
        result1 = await bot.send_message(
            chat_id=user_id,
            text="🔍 Searching for book... (TEST 1)"
        )
        print(f"✅ Progress message sent: {result1.message_id}")
        
        # Simulate processing delay (like the book search)
        await asyncio.sleep(2)
        
        # Test 2: Send final result
        print("📤 Test 2: Sending final result...")
        result2 = await bot.send_message(
            chat_id=user_id,
            text="✅ Book found! (TEST 2)"
        )
        print(f"✅ Final message sent: {result2.message_id}")
        
        # Test 3: Multiple rapid messages to simulate conflicts
        print("📤 Test 3: Sending multiple rapid messages...")
        for i in range(3):
            try:
                result = await bot.send_message(
                    chat_id=user_id,
                    text=f"🔍 Rapid message {i+1}/3"
                )
                print(f"✅ Rapid message {i+1} sent: {result.message_id}")
            except (TelegramConflictError, TelegramNetworkError) as e:
                print(f"❌ Rapid message {i+1} failed: {e}")
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(test_progress_message_behavior())