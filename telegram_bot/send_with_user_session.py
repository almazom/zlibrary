#!/usr/bin/env python3
"""
Send message using USER SESSION to trigger EPUB book search
This creates IDENTICAL pipeline as manual typing
"""

import asyncio
import os
from telethon import TelegramClient
import sys

async def send_with_user_session(book_title="Clean Code Robert Martin"):
    """Send message as USER to bot to trigger book search"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("🤖 SENDING WITH USER SESSION")
    print(f"📚 Book: '{book_title}'")
    print("🎯 Target: @epub_toc_based_sample_bot")
    print("🔧 This will trigger IDENTICAL pipeline as manual typing!")
    print("-" * 60)
    
    try:
        # Use user session to send message
        async with TelegramClient('user_send_session', api_id, api_hash) as client:
            
            # Send message to bot AS USER
            print("📤 Sending message as user to bot...")
            
            message = await client.send_message('@epub_toc_based_sample_bot', book_title)
            
            print(f"✅ USER MESSAGE SENT!")
            print(f"📋 Message ID: {message.id}")
            print(f"📅 Timestamp: {message.date}")
            print("🎯 This should trigger IDENTICAL pipeline!")
            print("-" * 60)
            print("📊 Expected pipeline (from bot logs):")
            print("1. 📝 Text message from user 14835038: 'Clean Code Robert Martin'")
            print("2. 📨 Received message from user 14835038: 'Clean Code Robert Martin'") 
            print("3. 🚀 Processing book request from user 14835038: 'Clean Code Robert Martin'")
            print("4. 🔍 Searching for book: 'Clean Code Robert Martin'")
            print("5. 📚 Sending EPUB file...")
            print("6. ✅ EPUB file sent successfully!")
            print("-" * 60)
            print("📱 Check your Telegram and bot logs for responses!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 This might be first run - authentication needed")
        return False

if __name__ == '__main__':
    book_title = sys.argv[1] if len(sys.argv) > 1 else "Clean Code Robert Martin"
    
    print("🚀 USER SESSION MESSAGE SENDER")
    print("This sends messages AS USER to trigger book search pipeline")
    print("")
    
    success = asyncio.run(send_with_user_session(book_title))
    
    if success:
        print("\n🎉 SUCCESS: User session message sent!")
        print("📊 This should create IDENTICAL pipeline as manual typing")
        print("📱 Check bot logs and your Telegram for the complete flow!")
    else:
        print("\n❌ Need to authenticate user session first")
        print("💡 Run this script and follow authentication prompts")