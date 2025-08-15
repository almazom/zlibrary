#!/usr/bin/env python3
"""
Send book search with title and authors using authenticated user session
This triggers IDENTICAL pipeline as manual typing
"""

from telethon.sync import TelegramClient
import sys

def send_book_search(book_query):
    """Send book search using authenticated user session"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("🚀 SENDING BOOK SEARCH VIA USER SESSION")
    print(f"📚 Book Query: '{book_query}'")
    print("🎯 Target: @epub_toc_based_sample_bot")
    print("🔧 This triggers IDENTICAL pipeline as manual typing!")
    print("=" * 60)
    
    try:
        # Use authenticated session
        with TelegramClient('user_session_final', api_id, api_hash) as client:
            
            # Verify authentication
            me = client.get_me()
            print(f"✅ Authenticated as: {me.first_name} (ID: {me.id})")
            
            # Send book search message AS USER
            print(f"📤 Sending book search to bot...")
            message = client.send_message('@epub_toc_based_sample_bot', book_query)
            
            print(f"✅ BOOK SEARCH MESSAGE SENT!")
            print(f"📋 Message ID: {message.id}")
            print(f"⏰ Timestamp: {message.date}")
            print("=" * 60)
            print("🎯 Expected bot logs (identical to manual):")
            print(f"   📝 Text message from user {me.id}: '{book_query}'")
            print(f"   📨 Received message from user {me.id}: '{book_query}'")
            print(f"   🚀 Processing book request from user {me.id}: '{book_query}'")
            print(f"   🔍 Searching for book: '{book_query}'")
            print("   📚 Sending EPUB file...")
            print("   ✅ EPUB file sent successfully!")
            print("=" * 60)
            print("📱 CHECK YOUR TELEGRAM FOR:")
            print("   1. Progress message: '🔍 Searching for book...'")
            print("   2. EPUB file download")
            print("   3. Success confirmation")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function with book search options"""
    
    print("📚 USER SESSION BOOK SEARCH SENDER")
    print("=" * 50)
    
    # Book search options
    book_options = [
        "Clean Code Robert Martin",
        "Design Patterns Gang of Four",
        "The Pragmatic Programmer David Thomas",
        "Effective Python Brett Slatkin",
        "Python Tricks Dan Bader"
    ]
    
    # Use command line argument or default
    if len(sys.argv) > 1:
        book_query = " ".join(sys.argv[1:])
    else:
        print("📖 Available book searches:")
        for i, book in enumerate(book_options, 1):
            print(f"   {i}. {book}")
        print()
        book_query = book_options[0]  # Default to Clean Code
        print(f"🎯 Using default: '{book_query}'")
        print()
    
    # Send the book search
    success = send_book_search(book_query)
    
    if success:
        print("\n🎉 SUCCESS: Book search sent via user session!")
        print("📊 This creates IDENTICAL pipeline as manual typing")
        print("📱 Monitor your Telegram for complete EPUB delivery!")
    else:
        print("\n❌ Book search failed")

if __name__ == '__main__':
    main()