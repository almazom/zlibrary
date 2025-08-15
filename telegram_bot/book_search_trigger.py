#!/usr/bin/env python3
"""
Easy book search trigger via user session
Usage: python3 book_search_trigger.py "Book Title Author"
"""

from telethon.sync import TelegramClient
import sys

def trigger_book_search(book_query):
    """Trigger book search using authenticated user session"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    try:
        with TelegramClient('user_session_final', api_id, api_hash) as client:
            me = client.get_me()
            message = client.send_message('@epub_toc_based_sample_bot', book_query)
            
            print(f"✅ Book search sent: '{book_query}'")
            print(f"📋 Message ID: {message.id}")
            print(f"👤 From user: {me.first_name} (ID: {me.id})")
            print("📱 Check your Telegram for EPUB delivery!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("📚 BOOK SEARCH TRIGGER")
        print("Usage: python3 book_search_trigger.py 'Book Title Author'")
        print("")
        print("Examples:")
        print("  python3 book_search_trigger.py 'Clean Code Robert Martin'")
        print("  python3 book_search_trigger.py 'Design Patterns Gang of Four'")
        print("  python3 book_search_trigger.py 'Effective Python Brett Slatkin'")
        sys.exit(1)
    
    book_query = " ".join(sys.argv[1:])
    print(f"🚀 Triggering book search: '{book_query}'")
    
    if trigger_book_search(book_query):
        print("🎯 Book search triggered via user session!")
        print("📊 This creates IDENTICAL pipeline as manual typing")
    else:
        print("❌ Book search failed")