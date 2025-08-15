#!/usr/bin/env python3
"""
Use USER SESSION to trigger book search - identical to manual typing
"""

import asyncio
from telethon import TelegramClient
import sys

async def trigger_book_search_via_user():
    """Send message as USER to trigger book search"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    phone = '+79163708898'  # Your phone number
    
    book_title = "Python Programming Guide"
    bot_username = '@epub_toc_based_sample_bot'
    
    print(f"🤖 TRIGGERING BOOK SEARCH VIA USER SESSION")
    print(f"📚 Book: '{book_title}'")
    print(f"🎯 Target: {bot_username}")
    print("=" * 50)
    
    client = TelegramClient('book_search_session', api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        
        print("✅ User session connected")
        
        # Get user info
        me = await client.get_me()
        print(f"👤 Sending as: {me.first_name} (@{me.username if me.username else 'no_username'})")
        
        # Send message to bot AS USER
        print(f"📤 Sending message to {bot_username}...")
        
        message = await client.send_message(bot_username, book_title)
        
        print(f"✅ MESSAGE SENT AS USER!")
        print(f"📋 Message ID: {message.id}")
        print(f"🎯 This creates INCOMING message to bot!")
        print("=" * 50)
        print("🔍 Expected bot response:")
        print("1. Bot receives: 'Python Programming Guide' from USER")
        print("2. Bot sends: '🔍 Searching for book...'")
        print("3. Bot executes: book_search.sh --download")
        print("4. Bot processes results and sends EPUB")
        print("=" * 50)
        print("📱 Check your Telegram for bot responses!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == '__main__':
    success = asyncio.run(trigger_book_search_via_user())
    
    if success:
        print("\n🎉 USER SESSION BOOK SEARCH TRIGGERED!")
    else:
        print("\n❌ Failed to trigger via user session")