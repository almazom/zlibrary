#!/usr/bin/env python3
"""
CORRECT WAY to test book search pipeline
Sends messages AS USER TO BOT (identical to manual typing)
"""

import asyncio
import os
import time
from telethon import TelegramClient
from telethon.sync import TelegramClient as SyncTelegramClient

async def test_as_user_to_bot():
    """Test the CORRECT way - as user sending TO bot"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    bot_username = '@epub_toc_based_sample_bot'
    
    print("🎯 TESTING THE CORRECT WAY")
    print("=" * 50)
    print("📱 Method: USER SESSION → BOT (identical to manual)")
    print(f"🤖 Target: {bot_username}")
    print("🔧 This creates REAL incoming messages to bot")
    print("=" * 50)
    
    try:
        # Try using sync client to avoid auth issues
        with SyncTelegramClient('test_user_session', api_id, api_hash) as client:
            
            # Check if authenticated
            if not client.is_user_authorized():
                print("📞 Need to authenticate (first time only)")
                phone = input("Enter phone: ")
                client.send_code_request(phone)
                code = input("Enter code: ")
                client.sign_in(phone, code)
            
            print("✅ User session authenticated")
            
            # Get user info
            me = client.get_me()
            print(f"👤 Sending as: {me.first_name} (@{me.username})")
            
            # Send test message to bot
            book_title = "Clean Code Robert Martin"
            
            print(f"📤 Sending: '{book_title}'")
            print(f"📍 To: {bot_username}")
            print("⏱️ Sending now...")
            
            message = client.send_message(bot_username, book_title)
            
            print(f"✅ MESSAGE SENT SUCCESSFULLY!")
            print(f"📋 Message ID: {message.id}")
            print(f"🎯 This is IDENTICAL to manual typing!")
            print("=" * 50)
            print("📊 Expected pipeline:")
            print("1. Bot receives incoming message from YOU")  
            print("2. Bot sends: '🔍 Searching for book...'")
            print("3. Bot executes book_search.sh script")
            print("4. Bot processes results")
            print("5. Bot sends EPUB file")
            print("=" * 50)
            print("📱 Check your Telegram for bot responses!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_without_auth():
    """Alternative test using existing session if available"""
    
    print("🔄 ALTERNATIVE TEST - Using existing session")
    
    try:
        # Try to use existing session without re-auth
        api_id = 29950132
        api_hash = 'e0bf78283481e2341805e3e4e90d289a'
        
        client = TelegramClient('existing_user_session', api_id, api_hash)
        
        # Try sync connection
        client.start()
        
        if client.is_user_authorized():
            print("✅ Found existing authenticated session")
            
            me = client.get_me()
            print(f"👤 User: {me.first_name}")
            
            # Send message
            message = client.send_message('@epub_toc_based_sample_bot', 'Test Book Request')
            print(f"✅ Test message sent! ID: {message.id}")
            
            client.disconnect()
            return True
        else:
            print("❌ No authenticated session found")
            client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 CORRECT TESTING METHOD")
    print("This sends messages AS USER TO BOT (like manual typing)")
    print()
    
    # First try without auth (using existing session)
    if not test_without_auth():
        print("\n📞 Trying with authentication...")
        # If that fails, try with auth
        asyncio.run(test_as_user_to_bot())
    
    print("\n🎯 If successful, check bot logs and your Telegram!")
    print("The bot should respond with progress messages and EPUB delivery.")