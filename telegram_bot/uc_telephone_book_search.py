#!/usr/bin/env python3
"""
UC Telephone Book Search via User Session
Sends book search using authenticated user session to trigger EPUB pipeline
"""

from telethon.sync import TelegramClient
import asyncio

def uc_telephone_book_search():
    """Send book search via UC telephone user session"""
    
    api_id = 29950132
    api_hash = 'e0bf78283481e2341805e3e4e90d289a'
    
    print("📞 UC TELEPHONE BOOK SEARCH VIA USER SESSION")
    print("=" * 50)
    print("🎯 Target: @epub_toc_based_sample_bot")
    print("🔧 Method: User Session (IDENTICAL to manual typing)")
    print("=" * 50)
    
    try:
        # Use existing session if available, otherwise authenticate
        with TelegramClient('uc_telephone_session', api_id, api_hash) as client:
            
            if client.is_user_authorized():
                me = client.get_me()
                print(f"✅ UC Session authenticated: {me.first_name} (ID: {me.id})")
                
                # Send book search
                book_title = "Design Patterns Elements of Reusable Object-Oriented Software"
                
                print(f"📤 UC Telephone sending: '{book_title}'")
                message = client.send_message('@epub_toc_based_sample_bot', book_title)
                
                print(f"✅ UC TELEPHONE MESSAGE SENT!")
                print(f"📋 Message ID: {message.id}")
                print(f"⏰ Timestamp: {message.date}")
                print("=" * 50)
                print("🎯 Expected bot logs (IDENTICAL to manual):")
                print(f"   📝 Text message from user {me.id}: '{book_title}'")
                print(f"   🚀 Processing book request from user {me.id}: '{book_title}'")
                print("   🔍 Searching for book...")
                print("   📚 Sending EPUB file...")
                print("   ✅ EPUB file sent successfully!")
                print("=" * 50)
                print("📱 CHECK YOUR TELEGRAM FOR EPUB DELIVERY!")
                
                return True
                
            else:
                print("❌ UC Session not authenticated")
                print("💡 Need to run authentication first:")
                print("   python3 authenticate_step_by_step.py")
                return False
                
    except Exception as e:
        print(f"❌ UC Telephone error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 UC TELEPHONE BOOK SEARCH SYSTEM")
    print("This demonstrates UC telephone user session book search")
    print("")
    
    success = uc_telephone_book_search()
    
    if success:
        print("\n🎉 UC TELEPHONE SUCCESS!")
        print("📊 User session message creates IDENTICAL pipeline as manual")
        print("📱 Monitor your Telegram for complete EPUB delivery!")
    else:
        print("\n❌ UC Telephone authentication required")