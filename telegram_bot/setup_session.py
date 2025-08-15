#!/usr/bin/env python3
"""
Simple session setup - run this in your terminal
"""

from telethon.sync import TelegramClient

# Your credentials
api_id = 29950132
api_hash = 'e0bf78283481e2341805e3e4e90d289a'
phone = '+79163708898'

print("🔐 Setting up Telegram user session...")
print("📱 You'll get SMS code, enter it when prompted")
print("-" * 50)

# Authenticate
with TelegramClient('user_session_final', api_id, api_hash) as client:
    me = client.get_me()
    print(f"✅ Authenticated as: {me.first_name}")
    
    # Test message to bot
    message = client.send_message('@epub_toc_based_sample_bot', 'Session Test - Programming Pearls')
    print(f"📤 Test message sent! ID: {message.id}")
    print("🎯 Check your Telegram for bot response!")
    print("📁 Session saved for reuse!")