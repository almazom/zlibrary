#!/usr/bin/env python3
"""
Ready-to-use user session trigger
Pre-authenticate this once, then use for testing
"""

from telethon.sync import TelegramClient

def setup_authenticated_session():
    """Set up authenticated session (run once)"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("🔐 SETTING UP AUTHENTICATED USER SESSION")
    print("📱 This needs to be done ONCE, then reused")
    print("=" * 50)
    
    try:
        with TelegramClient('ready_user_session', api_id, api_hash) as client:
            
            me = client.get_me()
            print(f"✅ Authenticated as: {me.first_name} (ID: {me.id})")
            
            # Test send to bot
            book_title = "Test Message - Design Patterns"
            message = client.send_message('@epub_toc_based_sample_bot', book_title)
            
            print(f"📤 Test message sent: '{book_title}'")
            print(f"📋 Message ID: {message.id}")
            print("🎯 This should appear in bot logs as:")
            print(f"   📝 Text message from user {me.id}: '{book_title}'")
            print("=" * 50)
            print("🎉 SESSION READY FOR REUSE!")
            
            return True
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def use_existing_session(book_title="Python Guide"):
    """Use pre-authenticated session"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print(f"🤖 USING AUTHENTICATED SESSION")
    print(f"📚 Book: '{book_title}'")
    
    try:
        with TelegramClient('ready_user_session', api_id, api_hash) as client:
            
            if not client.is_user_authorized():
                print("❌ Session not authenticated - run setup first")
                return False
            
            me = client.get_me()
            print(f"👤 Sending as: {me.first_name} (ID: {me.id})")
            
            message = client.send_message('@epub_toc_based_sample_bot', book_title)
            
            print(f"✅ MESSAGE SENT AS USER!")
            print(f"📋 Message ID: {message.id}")
            print("🎯 Expected bot logs:")
            print(f"   📝 Text message from user {me.id}: '{book_title}'")
            print("📱 Check Telegram for EPUB delivery!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 USER SESSION AUTHENTICATION SYSTEM")
    print("Choose: 1=Setup authentication, 2=Use existing session")
    print("")
    
    # Try to use existing session first
    print("Attempting to use existing session...")
    if not use_existing_session("Programming Pearls"):
        print("\nNo authenticated session found. Need to set up authentication.")
        print("Run this script interactively to authenticate once.")
        setup_authenticated_session()