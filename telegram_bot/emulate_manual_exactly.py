#!/usr/bin/env python3
"""
Emulate manual message EXACTLY using Telegram user session
Creates identical log pattern: "Text message from user 14835038"
"""

from telethon import TelegramClient
import sys
import asyncio

# Your exact credentials from manual message logs
TARGET_USER_ID = 14835038  # Your user ID from logs
API_ID = 29950132
API_HASH = 'e0bf78283481e2341805e3e4e90d289a'
PHONE = '+79163708898'

async def emulate_manual_message():
    """Send message exactly like manual - creates identical logs"""
    
    book_title = "The Pragmatic Programmer"
    
    print("🎯 EMULATING MANUAL MESSAGE EXACTLY")
    print(f"👤 User ID: {TARGET_USER_ID} (your account)")
    print(f"📚 Message: '{book_title}'")
    print("🔧 Expected logs:")
    print(f"   📝 Text message from user {TARGET_USER_ID}: '{book_title}'")
    print(f"   📨 Received message from user {TARGET_USER_ID}: '{book_title}'")
    print(f"   🚀 Processing book request from user {TARGET_USER_ID}: '{book_title}'")
    print("=" * 60)
    
    try:
        # Create client with your exact credentials
        client = TelegramClient('exact_emulation_session', API_ID, API_HASH)
        
        # Start with your phone
        await client.start(phone=PHONE)
        
        # Verify it's your account
        me = await client.get_me()
        if me.id != TARGET_USER_ID:
            print(f"⚠️ Warning: Expected user {TARGET_USER_ID}, got {me.id}")
        else:
            print(f"✅ Verified: User {me.id} ({me.first_name})")
        
        print(f"📤 Sending as user {me.id} to @epub_toc_based_sample_bot...")
        
        # Send message EXACTLY like manual
        message = await client.send_message('@epub_toc_based_sample_bot', book_title)
        
        print(f"✅ USER MESSAGE SENT!")
        print(f"📋 Message ID: {message.id}")
        print(f"👤 From user: {me.id}")
        print(f"🤖 To bot: @epub_toc_based_sample_bot")
        print("=" * 60)
        print("🎯 This should create IDENTICAL logs as manual:")
        print(f"📝 Text message from user {TARGET_USER_ID}: '{book_title}'")
        print("📱 CHECK BOT LOGS AND YOUR TELEGRAM!")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("🚀 EXACT MANUAL MESSAGE EMULATION")
    print("This creates the SAME log pattern as your manual message")
    print("")
    
    success = await emulate_manual_message()
    
    if success:
        print("\n🎉 SUCCESS: Manual message emulated exactly!")
        print("📊 Check bot logs for identical pattern!")
    else:
        print("\n❌ Emulation failed")

if __name__ == '__main__':
    asyncio.run(main())