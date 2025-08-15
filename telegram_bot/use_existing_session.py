#!/usr/bin/env python3
"""
Use existing authenticated session to trigger book search
"""

from telethon.sync import TelegramClient
import sys

def send_book_search():
    """Use existing session to send book search"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    book_title = "Design Patterns Gang of Four"
    
    print(f"🤖 USING EXISTING SESSION TO TRIGGER BOOK SEARCH")
    print(f"📚 Book: '{book_title}'")
    print("=" * 50)
    
    try:
        # Try existing session without authentication
        client = TelegramClient('user_session', api_id, api_hash)
        client.connect()
        
        if client.is_user_authorized():
            print("✅ Found authenticated session!")
            
            # Get user info
            me = client.get_me()
            print(f"👤 Sending as: {me.first_name}")
            
            # Send message to bot
            message = client.send_message('@epub_toc_based_sample_bot', book_title)
            
            print(f"✅ BOOK SEARCH MESSAGE SENT!")
            print(f"📋 Message ID: {message.id}")
            print(f"🎯 This creates INCOMING message to bot!")
            print("📱 Bot should now process this and send EPUB!")
            
            client.disconnect()
            return True
            
        else:
            print("❌ Session not authenticated")
            client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = send_book_search()
    
    if success:
        print("\n🎉 SUCCESS! Book search triggered via user session!")
        print("📊 Check bot logs for pipeline execution!")
    else:
        print("\n❌ Could not use existing session")