#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from datetime import datetime, timedelta

async def check_responses():
    try:
        with open('stable_string_session.txt', 'r') as f:
            string_session = f.read().strip()
        
        client = TelegramClient(StringSession(string_session), 29950132, 'e0bf78283481e2341805e3e4e90d289a')
        
        await client.connect()
        
        # Get messages from the bot conversation
        messages = await client.get_messages('@epub_toc_based_sample_bot', limit=10)
        
        print(f'Found {len(messages)} recent messages:')
        print('=' * 60)
        
        for i, msg in enumerate(messages):
            timestamp = msg.date.strftime('%Y-%m-%d %H:%M:%S')
            sender = 'Bot' if msg.from_id and msg.from_id.user_id != 5282615364 else 'User'
            text = msg.text or msg.message or '[Media/File]'
            
            print(f'{i+1}. [{timestamp}] {sender}:')
            print(f'   Message: {text}')
            
            # Check for file/document
            if msg.document:
                attrs = msg.document.attributes
                filename = 'Unknown'
                for attr in attrs:
                    if hasattr(attr, 'file_name') and attr.file_name:
                        filename = attr.file_name
                        break
                print(f'   📄 Document: {filename} ({msg.document.size} bytes)')
                
            # Check for EPUB indicators
            if text and any(keyword in text.lower() for keyword in ['epub', '.epub', 'book sent', 'file sent']):
                print(f'   ✅ EPUB indicator detected!')
            print()
            
        await client.disconnect()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_responses())