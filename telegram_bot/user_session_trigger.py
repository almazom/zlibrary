#!/usr/bin/env python3
"""
Send message via USER SESSION to trigger EPUB book search pipeline
This creates IDENTICAL pipeline as manual typing!
"""

import asyncio
from telethon import TelegramClient

async def trigger_via_user_session():
    """Send message AS USER to bot - triggers identical pipeline"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("🤖 TRIGGERING EPUB BOOK SEARCH VIA USER SESSION")
    print("🎯 Target: @epub_toc_based_sample_bot")
    print("📚 This creates IDENTICAL pipeline as manual typing!")
    print("=" * 60)
    
    try:
        # Use async client with your credentials
        client = TelegramClient('pipeline_trigger_session', api_id, api_hash)
        
        # Start client (will use existing session or prompt for auth)
        await client.start()
        
        print("✅ User session connected")
        
        # Get your user info
        me = await client.get_me()
        print(f"👤 Sending as USER: {me.first_name} (ID: {me.id})")
        
        # Send book search message to bot AS USER
        book_title = "The Pragmatic Programmer"
        
        print(f"📤 Sending: '{book_title}'")
        print("🔧 This appears as: USER → BOT (INCOMING message)")
        
        message = await client.send_message('@epub_toc_based_sample_bot', book_title)
        
        print(f"✅ USER MESSAGE SENT TO BOT!")
        print(f"📋 Message ID: {message.id}")
        print(f"⏰ Timestamp: {message.date}")
        print("=" * 60)
        print("🎯 EXPECTED PIPELINE (identical to manual):")
        print("1. 📝 Text message from user 14835038: 'The Pragmatic Programmer'")
        print("2. 📨 Received message from user 14835038: 'The Pragmatic Programmer'")
        print("3. 🚀 Processing book request from user 14835038: 'The Pragmatic Programmer'")
        print("4. 🔍 Searching for book: 'The Pragmatic Programmer'")
        print("5. 📚 Sending EPUB file...")
        print("6. ✅ EPUB file sent successfully!")
        print("=" * 60)
        print("📱 CHECK YOUR TELEGRAM FOR BOT RESPONSES!")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 USER SESSION EPUB BOOK SEARCH TRIGGER")
    print("This sends messages AS USER to trigger 100% identical pipeline")
    print("")
    
    success = asyncio.run(trigger_via_user_session())
    
    if success:
        print("\n🎉 SUCCESS: USER SESSION MESSAGE SENT!")
        print("📊 This should create IDENTICAL pipeline as manual typing")
        print("📱 Check bot logs and your Telegram for complete EPUB delivery!")
    else:
        print("\n❌ Failed to send via user session")