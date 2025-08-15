#!/usr/bin/env python3
"""
Authenticate user session once and send book search
"""

from telethon.sync import TelegramClient

def authenticate_and_send():
    """Authenticate once and send book search message"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("🔐 Authenticating user session...")
    print("📱 Enter your phone number and verification code when prompted")
    print("=" * 50)
    
    try:
        with TelegramClient('authenticated_session', api_id, api_hash) as client:
            
            # This will prompt for phone and code if not authenticated
            me = client.get_me()
            
            print(f"✅ Authenticated as: {me.first_name}")
            print(f"👤 Username: @{me.username if me.username else 'no_username'}")
            
            # Send book search message
            book_title = "The Pragmatic Programmer"
            
            print(f"📤 Sending book search: '{book_title}'")
            message = client.send_message('@epub_toc_based_sample_bot', book_title)
            
            print(f"✅ BOOK SEARCH MESSAGE SENT!")
            print(f"📋 Message ID: {message.id}")
            print("🎯 This should trigger IDENTICAL pipeline as manual typing!")
            print("📱 Check your Telegram for bot responses!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 USER SESSION AUTHENTICATION & BOOK SEARCH")
    print("This will authenticate your user session and send a book search")
    print("")
    
    success = authenticate_and_send()
    
    if success:
        print("\n🎉 SUCCESS! Book search triggered via authenticated user session!")
    else:
        print("\n❌ Authentication or sending failed")