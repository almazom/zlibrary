#!/usr/bin/env python3
"""
Send message as USER to @epub_toc_based_sample_bot
This triggers the ACTUAL book search pipeline (bots can't message bots)
"""

import asyncio
import logging
import os
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

async def send_user_message_to_bot(message_text: str):
    """Send message as USER to the book search bot"""
    
    # Get user API credentials
    api_id = int(os.getenv('TELEGRAM_API_ID', '29950132'))
    api_hash = os.getenv('TELEGRAM_API_HASH', 'e0bf78283481e2341805e3e4e90d289a')
    bot_username = '@epub_toc_based_sample_bot'
    
    logger.info(f"👤 SENDING AS USER TO BOT: {bot_username}")
    logger.info(f"📚 Message: '{message_text}'")
    logger.info("🎯 This will trigger ACTUAL book search pipeline!")
    logger.info("-" * 60)
    
    try:
        # Create user client session
        async with TelegramClient('user_session', api_id, api_hash) as client:
            logger.info("🔐 User session connected")
            
            # Send message to the bot
            logger.info(f"📤 Sending message to {bot_username}...")
            
            result = await client.send_message(bot_username, message_text)
            
            logger.info(f"✅ Message sent successfully!")
            logger.info(f"📋 Message ID: {result.id}")
            logger.info("🔍 Book search pipeline should now be triggered...")
            logger.info("📖 Expected response: Progress message + EPUB file")
            
            return {
                'success': True,
                'message_id': result.id,
                'target_bot': bot_username,
                'message_text': message_text,
                'sent_as': 'user',
                'pipeline_triggered': True
            }
            
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return {
            'success': False,
            'error': str(e),
            'target_bot': bot_username,
            'message_text': message_text
        }

async def main():
    """Send test book search to the bot"""
    
    book_title = "Clean Code Robert Martin"
    
    logger.info("🚀 User-to-Bot Message Sender")
    logger.info("This sends REAL USER messages to trigger ACTUAL book search")
    logger.info("")
    
    result = await send_user_message_to_bot(book_title)
    
    if result['success']:
        logger.info("🎉 SUCCESS: Message sent as user to bot!")
        logger.info("🔍 Book search pipeline should now be running")
        logger.info("📱 Check your Telegram for bot responses")
    else:
        logger.error(f"❌ FAILED: {result['error']}")
    
    return result

if __name__ == '__main__':
    try:
        result = asyncio.run(main())
        if result['success']:
            print("\n✅ User message sent to book search bot successfully!")
            exit(0)
        else:
            print(f"\n❌ Failed to send user message: {result['error']}")
            exit(1)
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)