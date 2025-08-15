#!/usr/bin/env python3
"""
Test stable MCP session for sending messages as user
"""

import asyncio
from telethon import TelegramClient

API_ID = 29950132
API_HASH = 'e0bf78283481e2341805e3e4e90d289a'
BOT_USERNAME = '@epub_toc_based_sample_bot'

async def test_stable_session():
    """Test stable MCP session"""
    
    print("🔍 Testing Stable MCP Session")
    print("="*40)
    
    client = TelegramClient('stable_session', API_ID, API_HASH)
    
    try:
        await client.start()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Authenticated as: {me.first_name} (ID: {me.id})")
            
            # Send message to bot AS USER
            print(f"📤 Sending message to {BOT_USERNAME} AS USER...")
            message = await client.send_message(BOT_USERNAME, 'The Pragmatic Programmer David Thomas')
            
            print(f"✅ Message sent successfully!")
            print(f"📋 Message ID: {message.id}")
            print(f"👤 From user: {me.first_name} (ID: {me.id})")
            print(f"🎯 Direction: USER → BOT (INCOMING to bot)")
            print("📱 This should trigger bot pipeline and deliver EPUB!")
            print("\n🔍 Expected bot logs:")
            print(f"   📝 Text message from user {me.id}: 'The Pragmatic Programmer David Thomas'")
            print(f"   🚀 Processing book request from user {me.id}")
            print("   ✅ EPUB file sent successfully")
            
            return True
        else:
            print("❌ Session not authenticated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == '__main__':
    result = asyncio.run(test_stable_session())
    print(f"\n🎯 Final Result: {'SUCCESS - User session working!' if result else 'FAILED - Need re-auth'}")