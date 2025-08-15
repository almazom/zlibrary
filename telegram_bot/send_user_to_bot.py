#!/usr/bin/env python3
"""
Send message as USER to bot using existing session
This triggers the ACTUAL book search pipeline
"""

import asyncio
import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

async def send_user_to_bot(message_text: str = "Clean Code Robert Martin"):
    """Send message as user to bot to trigger pipeline"""
    
    api_id = int(os.getenv('TELEGRAM_API_ID', '29950132'))
    api_hash = os.getenv('TELEGRAM_API_HASH', 'e0bf78283481e2341805e3e4e90d289a')
    
    print("🤖 SENDING AS USER TO BOT")
    print(f"📚 Message: '{message_text}'")
    print(f"🎯 Target: @epub_toc_based_sample_bot")
    print("🔧 Using existing user session")
    print("-" * 60)
    
    try:
        # Use existing session
        client = TelegramClient('user_session', api_id, api_hash)
        await client.start()
        
        if await client.is_user_authorized():
            print("✅ User session authenticated")
            
            # Send message to bot
            result = await client.send_message('@epub_toc_based_sample_bot', message_text)
            
            print(f"✅ USER MESSAGE SENT!")
            print(f"📋 Message ID: {result.id}")
            print(f"🎯 This triggers IDENTICAL pipeline as manual typing!")
            
            await client.disconnect()
            return True
            
        else:
            print("❌ User session not authorized")
            await client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = asyncio.run(send_user_to_bot())
    if success:
        print("\n🎉 SUCCESS: User message sent to bot!")
        print("📱 Check bot logs for pipeline activation")
    else:
        print("\n❌ FAILED to send user message")