#!/usr/bin/env python3
"""
Simple test to see if we can authenticate and send a message as user
"""

import asyncio
from telethon import TelegramClient

API_ID = 29950132
API_HASH = 'e0bf78283481e2341805e3e4e90d289a'
PHONE = '+79163708898'
BOT_USERNAME = '@epub_toc_based_sample_bot'

async def test_user_session():
    """Test user session authentication and message sending"""
    
    print("🧪 Testing User Session Authentication")
    print("="*50)
    
    # Create client
    client = TelegramClient('test_session', API_ID, API_HASH)
    
    try:
        # Start client
        await client.start(phone=PHONE)
        
        # Check if authenticated
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Authenticated as: {me.first_name} ({me.id})")
            
            # Send message to bot
            print(f"📤 Sending message to {BOT_USERNAME}...")
            message = await client.send_message(BOT_USERNAME, 'Effective Python Brett Slatkin')
            
            print(f"✅ Message sent!")
            print(f"📋 Message ID: {message.id}")
            print(f"👤 From user: {me.first_name} (ID: {me.id})")
            print(f"🎯 To: {BOT_USERNAME}")
            print("📱 Check Telegram for bot response and EPUB delivery!")
            
            return True
        else:
            print("❌ Not authenticated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == '__main__':
    result = asyncio.run(test_user_session())
    print(f"\n🎯 Result: {'Success' if result else 'Failed'}")