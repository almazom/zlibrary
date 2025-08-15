#!/usr/bin/env python3
"""
Send REAL user message to bot using user session
This creates messages that appear FROM user TO bot (not FROM bot)
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

async def send_real_user_message():
    """Send message as actual user to trigger bot response"""
    
    # User credentials (not bot credentials)
    api_id = int(os.getenv('TELEGRAM_API_ID', '29950132'))
    api_hash = os.getenv('TELEGRAM_API_HASH', 'e0bf78283481e2341805e3e4e90d289a')
    
    print("🔐 Creating user session to send REAL user message...")
    print("📱 This will appear as: USER → @epub_toc_based_sample_bot")
    print("🎯 This should trigger the ACTUAL book search pipeline!")
    print("-" * 60)
    
    session_file = 'user_to_bot_session'
    
    async with TelegramClient(session_file, api_id, api_hash) as client:
        # Check if we need to authenticate
        if not await client.is_user_authorized():
            print("📞 Authentication required. Enter your phone number:")
            phone = input("Phone: ")
            await client.send_code_request(phone)
            
            print("🔢 Enter the code you received:")
            code = input("Code: ")
            await client.sign_in(phone, code)
            
            # Check if password is needed
            try:
                await client.sign_in(password=input("Password (if 2FA enabled): "))
            except SessionPasswordNeededError:
                pass
        
        print("✅ User session authenticated!")
        
        # Send message to the bot
        bot_username = '@epub_toc_based_sample_bot'
        message_text = 'Clean Code Robert Martin'
        
        print(f"📤 Sending message TO {bot_username}")
        print(f"📚 Message: '{message_text}'")
        
        try:
            # This sends FROM user TO bot (real user message)
            result = await client.send_message(bot_username, message_text)
            
            print(f"✅ REAL USER MESSAGE SENT!")
            print(f"📋 Message ID: {result.id}")
            print(f"🎯 This should trigger IDENTICAL pipeline as manual typing!")
            print(f"📖 Expected: Progress message + EPUB file delivery")
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending user message: {e}")
            return False

if __name__ == '__main__':
    try:
        success = asyncio.run(send_real_user_message())
        if success:
            print("\n🎉 Real user message sent successfully!")
            print("📱 Check bot logs and your Telegram for responses")
        else:
            print("\n❌ Failed to send real user message")
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")