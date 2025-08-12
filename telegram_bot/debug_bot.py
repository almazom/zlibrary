#!/usr/bin/env python3
"""
Ultra-debug bot to find the polling issue
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Load environment
load_dotenv()

# Ultra verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug_bot.log')
    ]
)

# Enable all aiogram logging
logging.getLogger("aiogram").setLevel(logging.DEBUG)
logging.getLogger("aiogram.dispatcher").setLevel(logging.DEBUG)
logging.getLogger("aiogram.event").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
logger.info(f"🔧 DEBUG BOT - Token: {TOKEN[:20]}...")

async def debug_message_handler(message: types.Message):
    """Log EVERY message received"""
    logger.critical(f"🚨🚨🚨 MESSAGE RECEIVED! User {message.from_user.id}: '{message.text}' 🚨🚨🚨")
    await message.answer(f"✅ BOT ALIVE! Received: '{message.text}'")
    logger.critical(f"🚨🚨🚨 RESPONSE SENT! 🚨🚨🚨")

async def debug_start_handler(message: types.Message):
    """Handle /start"""
    logger.critical(f"🚨🚨🚨 START COMMAND! User {message.from_user.id} 🚨🚨🚨")
    await message.answer("🤖 DEBUG BOT ACTIVE - Send any message!")
    logger.critical(f"🚨🚨🚨 START RESPONSE SENT! 🚨🚨🚨")

async def main():
    logger.critical("🚨🚨🚨 STARTING DEBUG BOT 🚨🚨🚨")
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Test connection
    try:
        me = await bot.get_me()
        logger.critical(f"🚨🚨🚨 BOT CONNECTED: {me.first_name} (@{me.username}) 🚨🚨🚨")
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return
    
    # Register handlers with maximum verbosity
    logger.critical("🚨🚨🚨 REGISTERING HANDLERS 🚨🚨🚨")
    dp.message.register(debug_start_handler, Command(commands=['start']))
    dp.message.register(debug_message_handler)  # Catch ALL messages
    
    # Clear webhooks aggressively  
    await bot.delete_webhook(drop_pending_updates=True)
    logger.critical("🚨🚨🚨 WEBHOOKS CLEARED 🚨🚨🚨")
    
    # Start polling with skip_updates=False to get all messages
    logger.critical("🚨🚨🚨 STARTING POLLING - SEND MESSAGES NOW! 🚨🚨🚨")
    
    try:
        await dp.start_polling(bot, skip_updates=False)
    except KeyboardInterrupt:
        logger.critical("🚨 STOPPED BY USER")
    except Exception as e:
        logger.error(f"❌ Polling error: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.critical("🚨🚨🚨 BOT SESSION CLOSED 🚨🚨🚨")

if __name__ == '__main__':
    asyncio.run(main())