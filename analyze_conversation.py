#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def check_conversation():
    with open('stable_string_session.txt', 'r') as f:
        string_session = f.read().strip()
    
    client = TelegramClient(StringSession(string_session), 29950132, 'e0bf78283481e2341805e3e4e90d289a')
    await client.connect()
    
    # Get full conversation history
    messages = await client.get_messages('@epub_toc_based_sample_bot', limit=20)
    
    print('FULL CONVERSATION ANALYSIS')
    print('=' * 60)
    
    bot_responses = 0
    user_messages = 0
    
    for i, msg in enumerate(messages):
        timestamp = msg.date.strftime('%Y-%m-%d %H:%M:%S')
        sender_id = msg.from_id.user_id if msg.from_id else 'Unknown'
        is_bot = sender_id != 5282615364
        sender_type = 'BOT' if is_bot else 'USER'
        
        if is_bot:
            bot_responses += 1
        else:
            user_messages += 1
            
        text = msg.text or '[Media/File]'
        print(f'{i+1:2d}. [{timestamp}] {sender_type}: {text}')
        
        if msg.document:
            print(f'    📄 Document attached: {msg.document.size} bytes')
    
    print('=' * 60)
    print(f'Summary: {user_messages} user messages, {bot_responses} bot responses')
    
    if bot_responses == 0:
        print('❌ NO BOT RESPONSES DETECTED - Bot may not be functioning')
    else:
        print(f'✅ Bot is responding ({bot_responses} responses found)')
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_conversation())