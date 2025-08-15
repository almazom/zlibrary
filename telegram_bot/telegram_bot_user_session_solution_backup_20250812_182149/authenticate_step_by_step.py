#!/usr/bin/env python3
"""
Step-by-step user session authentication
Run this interactively to authenticate once, then reuse forever
"""

from telethon.sync import TelegramClient

def authenticate_user_session():
    """Interactive authentication - do this ONCE"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    phone = '+79163708898'  # Your phone number
    
    print("🔐 TELEGRAM USER SESSION AUTHENTICATION")
    print("=" * 60)
    print("📱 This authenticates your user account to send messages AS YOU")
    print("🎯 Once done, we can trigger IDENTICAL pipeline as manual typing")
    print("=" * 60)
    print(f"📞 Phone: {phone}")
    print("🔢 You'll receive SMS verification code")
    print("=" * 60)
    
    try:
        # Create client with your credentials
        client = TelegramClient('final_authenticated_session', api_id, api_hash)
        
        print("📱 Connecting to Telegram...")
        client.start(phone=phone)
        
        print("✅ AUTHENTICATION SUCCESSFUL!")
        
        # Get your user info
        me = client.get_me()
        print(f"👤 Authenticated as: {me.first_name} {me.last_name}")
        print(f"🆔 User ID: {me.id}")
        print(f"📱 Username: @{me.username if me.username else 'no_username'}")
        
        print("=" * 60)
        print("🎯 TESTING: Sending test message to bot...")
        
        # Test message to bot
        test_message = "Authentication Test - Clean Code"
        message = client.send_message('@epub_toc_based_sample_bot', test_message)
        
        print(f"✅ TEST MESSAGE SENT!")
        print(f"📋 Message ID: {message.id}")
        print(f"📚 Content: '{test_message}'")
        print("=" * 60)
        print("🎉 AUTHENTICATION COMPLETE!")
        print("📁 Session saved as 'final_authenticated_session.session'")
        print("🔄 You can now reuse this session without re-authentication")
        print("=" * 60)
        print("📱 CHECK YOUR TELEGRAM FOR BOT RESPONSE!")
        
        client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_authenticated_session():
    """Test the authenticated session"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("🧪 TESTING AUTHENTICATED SESSION")
    print("=" * 50)
    
    try:
        client = TelegramClient('final_authenticated_session', api_id, api_hash)
        client.connect()
        
        if client.is_user_authorized():
            print("✅ Session is authenticated!")
            
            me = client.get_me()
            print(f"👤 User: {me.first_name} (ID: {me.id})")
            
            # Send book search message
            book_title = "The Pragmatic Programmer David Thomas"
            message = client.send_message('@epub_toc_based_sample_bot', book_title)
            
            print(f"📤 Book search sent: '{book_title}'")
            print(f"📋 Message ID: {message.id}")
            print("🎯 This should trigger IDENTICAL pipeline as manual!")
            print("📱 Check your Telegram for EPUB delivery!")
            
            client.disconnect()
            return True
        else:
            print("❌ Session not authenticated")
            client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 USER SESSION AUTHENTICATION & TEST")
    print("")
    
    # First authenticate
    print("STEP 1: Authentication")
    if authenticate_user_session():
        print("\nSTEP 2: Testing authenticated session")
        test_authenticated_session()
    else:
        print("\n❌ Authentication failed - try running again")
    
    print("\n🎉 Once authenticated, the session can be reused for automated testing!")