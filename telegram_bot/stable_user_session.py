#!/usr/bin/env python3
"""
Stable User Session for Book Search
Maintains persistent authentication and handles session recovery
"""

import asyncio
import os
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

class StableUserSession:
    def __init__(self):
        self.api_id = 29950132
        self.api_hash = 'e0bf78283481e2341805e3e4e90d289a'
        self.phone = '+79163708898'
        self.bot_username = '@epub_toc_based_sample_bot'
        self.session_name = 'persistent_user_session'
        
    async def ensure_authenticated(self):
        """Ensure user session is authenticated and working"""
        
        client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        
        try:
            await client.start()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"✅ Session authenticated: {me.first_name} (ID: {me.id})")
                return client, me
            else:
                print("❌ Session not authenticated - needs re-auth")
                await client.disconnect()
                return None, None
                
        except Exception as e:
            print(f"❌ Session error: {e}")
            await client.disconnect()
            return None, None
    
    async def send_book_search(self, book_query):
        """Send book search message as authenticated user"""
        
        client, me = await self.ensure_authenticated()
        
        if not client or not me:
            print("❌ Cannot send - session not authenticated")
            return False
            
        try:
            print(f"📤 Sending book search: '{book_query}'")
            print(f"👤 From user: {me.first_name} (ID: {me.id})")
            print(f"🎯 To bot: {self.bot_username}")
            print(f"📍 Direction: USER → BOT (triggers pipeline)")
            
            message = await client.send_message(self.bot_username, book_query)
            
            print(f"✅ Message sent successfully!")
            print(f"📋 Message ID: {message.id}")
            print("📱 Check Telegram for EPUB delivery!")
            
            await client.disconnect()
            return True
            
        except Exception as e:
            print(f"❌ Send failed: {e}")
            await client.disconnect()
            return False
    
    def backup_working_session(self):
        """Backup current session if it's working"""
        session_file = f"{self.session_name}.session"
        backup_file = f"{session_file}.backup"
        
        if os.path.exists(session_file):
            os.system(f"cp {session_file} {backup_file}")
            print(f"✅ Session backed up to {backup_file}")
    
    def restore_session_backup(self):
        """Restore session from backup"""
        session_file = f"{self.session_name}.session"
        backup_file = f"{session_file}.backup"
        
        if os.path.exists(backup_file):
            os.system(f"cp {backup_file} {session_file}")
            print(f"🔄 Session restored from {backup_file}")
            return True
        return False

async def main():
    """Main function for testing and using stable session"""
    import sys
    
    session = StableUserSession()
    
    if len(sys.argv) < 2:
        print("📚 STABLE USER SESSION - Book Search")
        print("Usage: python3 stable_user_session.py 'Book Title Author'")
        print("")
        print("Examples:")
        print("  python3 stable_user_session.py 'Clean Code Robert Martin'")
        print("  python3 stable_user_session.py 'The Pragmatic Programmer'")
        return
    
    book_query = " ".join(sys.argv[1:])
    
    print("🔍 STABLE USER SESSION TEST")
    print("="*50)
    
    # Try to send book search
    success = await session.send_book_search(book_query)
    
    if success:
        print("\n🎉 SUCCESS! Book search sent via user session")
        print("📊 This creates IDENTICAL pipeline as manual typing")
        session.backup_working_session()
    else:
        print("\n❌ FAILED! Session needs re-authentication")
        print("💡 Run: python3 authenticate_step_by_step.py")

if __name__ == '__main__':
    asyncio.run(main())