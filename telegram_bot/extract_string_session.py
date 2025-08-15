#!/usr/bin/env python3
"""
Extract string session from existing session file
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def extract_string_session():
    """Extract string session from existing file session"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    # Try different session files in order of recency
    session_files = [
        'user_session_final',
        'stable_session',
        'final_authenticated_session',
        'ready_user_session',
        'stable_book_search',
        'persistent_user_session'
    ]
    
    for session_file in session_files:
        try:
            print(f"🔍 Trying session file: {session_file}")
            
            # Load existing session
            client = TelegramClient(session_file, api_id, api_hash)
            await client.connect()
            
            # Check if authenticated
            if await client.is_user_authorized():
                print(f"✅ Found valid session: {session_file}")
                
                # Get user info
                me = await client.get_me()
                print(f"👤 User: {me.first_name} {me.last_name or ''}")
                print(f"🆔 ID: {me.id}")
                
                # Extract string session
                string_session = client.session.save()
                
                print(f"\n🎯 STRING SESSION EXTRACTED:")
                print("=" * 80)
                print(string_session)
                print("=" * 80)
                
                # Save to file
                with open('extracted_string_session.txt', 'w') as f:
                    f.write(string_session)
                
                print(f"\n💾 Saved to: extracted_string_session.txt")
                
                # Test the string session
                print(f"\n🧪 Testing extracted string session...")
                await client.disconnect()
                
                # Create new client with string session
                test_client = TelegramClient(
                    StringSession(string_session), 
                    api_id, 
                    api_hash,
                    auto_reconnect=True
                )
                
                await test_client.connect()
                if await test_client.is_user_authorized():
                    print("✅ String session works!")
                    
                    # Send test message
                    result = await test_client.send_message(
                        '@epub_toc_based_sample_bot',
                        'String Session Test - Clean Code Robert Martin'
                    )
                    print(f"📤 Test message sent! ID: {result.id}")
                    print("🎯 Check Telegram for EPUB delivery!")
                    
                await test_client.disconnect()
                return string_session
                
            else:
                print(f"❌ Session {session_file} not authorized")
                await client.disconnect()
                
        except Exception as e:
            print(f"❌ Error with {session_file}: {e}")
            try:
                await client.disconnect()
            except:
                pass
    
    print("❌ No valid session found")
    return None

if __name__ == '__main__':
    asyncio.run(extract_string_session())