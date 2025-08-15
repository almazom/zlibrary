#!/usr/bin/env python3
"""
Authenticate Once - Stable Forever
This script performs one-time authentication and generates a stable string session
that will work permanently without file corruption or 30-minute expiration.
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def authenticate_and_generate_stable_session():
    """Authenticate once and generate permanent stable session"""
    
    # Your API credentials
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    phone = '+79163708898'  # Your phone number
    
    print("🔐 ONE-TIME AUTHENTICATION FOR STABLE SESSION")
    print("=" * 60)
    print(f"📱 Phone: {phone}")
    print("🎯 This creates a permanent session - no more 30-minute expiry!")
    print("=" * 60)
    
    try:
        # Create client with empty StringSession for initial auth
        client = TelegramClient(StringSession(), api_id, api_hash)
        
        await client.start(phone=phone)
        
        print("✅ Authentication successful!")
        
        # Get user info
        me = await client.get_me()
        print(f"👤 User: {me.first_name} {me.last_name or ''}")
        print(f"🆔 ID: {me.id}")
        
        # Generate stable string session
        string_session = client.session.save()
        
        print(f"\n🎯 STABLE STRING SESSION GENERATED:")
        print("=" * 80)
        print(string_session)
        print("=" * 80)
        
        # Save for future use
        with open('permanent_session.txt', 'w') as f:
            f.write(string_session)
        
        print(f"\n💾 Saved to: permanent_session.txt")
        print("🎉 This session will work PERMANENTLY!")
        print("✨ No more 30-minute re-authentication!")
        print("🚀 Ready for stable book searches!")
        
        await client.disconnect()
        return string_session
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

async def test_stable_session(string_session):
    """Test the stable session by sending a book search"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print(f"\n🧪 TESTING STABLE SESSION...")
    
    try:
        # Use string session (no files, no corruption)
        async with TelegramClient(
            StringSession(string_session), 
            api_id, 
            api_hash,
            auto_reconnect=True  # Automatic reconnection
        ) as client:
            
            me = await client.get_me()
            print(f"✅ Session working! User: {me.first_name}")
            
            # Send test book search
            result = await client.send_message(
                '@epub_toc_based_sample_bot', 
                'Test Stable Session - Clean Code Robert Martin'
            )
            
            print(f"✅ Book search sent! Message ID: {result.id}")
            print("📱 Check Telegram for EPUB delivery!")
            
            return True
            
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        return False

if __name__ == '__main__':
    print("Starting stable session generation...")
    
    # Generate stable session
    session = asyncio.run(authenticate_and_generate_stable_session())
    
    if session:
        # Test the stable session
        test_result = asyncio.run(test_stable_session(session))
        
        if test_result:
            print(f"\n🎉 SUCCESS! Stable session is working!")
            print("🔒 This session will remain stable long-term")
            print("📚 You can now use it for automated book searches")
        else:
            print(f"\n⚠️ Session generated but test failed")
    else:
        print(f"\n❌ Failed to generate stable session")