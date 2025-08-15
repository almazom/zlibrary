#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def test_simple_book():
    with open('stable_string_session.txt', 'r') as f:
        string_session = f.read().strip()
    
    client = TelegramClient(StringSession(string_session), 29950132, 'e0bf78283481e2341805e3e4e90d289a')
    await client.connect()
    
    print('Testing with a very simple book request...')
    message = await client.send_message('@epub_toc_based_sample_bot', 'Python')
    print(f'Sent simple request: Python (Message ID: {message.id})')
    
    # Wait for response
    await asyncio.sleep(15)
    
    # Check latest messages
    messages = await client.get_messages('@epub_toc_based_sample_bot', limit=5)
    
    print('Latest responses:')
    for i, msg in enumerate(messages[:3]):
        timestamp = msg.date.strftime('%H:%M:%S')
        sender_id = msg.from_id.user_id if msg.from_id else 'Unknown'
        is_bot = sender_id != 5282615364
        sender_type = 'BOT' if is_bot else 'USER'
        text = msg.text or '[Media/File]'
        print(f'  {i+1}. [{timestamp}] {sender_type}: {text}')
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_simple_book())