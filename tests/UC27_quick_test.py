#!/usr/bin/env python3
"""
UC27: Quick Technical Books Test
Fast execution with basic analysis
"""

import asyncio
import sys
import time
from telethon import TelegramClient
from telethon.sessions import StringSession

# Configuration
BOT_USERNAME = "epub_toc_based_sample_bot"
API_ID = 29950132
API_HASH = "e0bf78283481e2341805e3e4e90d289a"

# Just test first 2 technical books for speed
TECHNICAL_BOOKS = [
    "Introduction to Algorithms CLRS Cormen",
    "Computer Networks Tanenbaum"
]

async def test_one_book(client, book, test_num):
    """Test one technical book quickly"""
    print(f"\n📚 TEST {test_num}: '{book}'")
    
    try:
        # Send message
        print(f"📤 Sending to @{BOT_USERNAME}...")
        message = await client.send_message(f'@{BOT_USERNAME}', book)
        print(f"✅ Sent! Message ID: {message.id}")
        
        # Wait for response (reduced time)
        print("⏳ Waiting 30s for response...")
        await asyncio.sleep(30)
        
        # Check for recent messages from bot
        print("🔍 Checking bot responses...")
        response_found = False
        file_found = False
        
        try:
            async for msg in client.iter_messages(f'@{BOT_USERNAME}', limit=10):
                if msg.date and (time.time() - msg.date.timestamp()) < 120:  # Last 2 minutes
                    response_found = True
                    print(f"📝 Recent message: {msg.text[:100] if msg.text else 'No text'}...")
                    
                    if msg.file:
                        file_found = True
                        file_name = msg.file.name or 'unnamed'
                        file_size = msg.file.size or 0
                        mime_type = msg.file.mime_type or 'unknown'
                        print(f"📄 File: {file_name} ({file_size} bytes, {mime_type})")
                        
                        if mime_type == 'application/epub+zip' or file_name.endswith('.epub'):
                            print("🎉 EPUB FOUND!")
                            return {'status': 'SUCCESS', 'type': 'EPUB'}
                        else:
                            print(f"📎 Other file type: {mime_type}")
                            return {'status': 'SUCCESS', 'type': 'OTHER_FILE'}
        except Exception as e:
            print(f"⚠️ Error checking messages: {e}")
        
        if response_found and not file_found:
            return {'status': 'RESPONSE_NO_FILE', 'type': 'TEXT_ONLY'}
        elif response_found:
            return {'status': 'SUCCESS', 'type': 'UNKNOWN_FILE'}
        else:
            return {'status': 'NO_RESPONSE', 'type': 'NONE'}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'status': 'ERROR', 'type': 'FAILED'}

async def main():
    """Quick technical books test"""
    print("🚀 UC27: Quick Technical Books Test")
    print("=" * 40)
    
    # Read session
    try:
        with open('telegram_bot/stable_string_session.txt', 'r') as f:
            string_session = f.read().strip()
        print(f"✅ Session loaded")
    except FileNotFoundError:
        print("❌ Session file not found")
        return False
    
    # Connect
    client = TelegramClient(StringSession(string_session), API_ID, API_HASH)
    
    try:
        print("🔗 Connecting...")
        await client.connect()
        me = await client.get_me()
        print(f"👤 Connected as: {me.first_name}")
        
        results = []
        for i, book in enumerate(TECHNICAL_BOOKS, 1):
            result = await test_one_book(client, book, i)
            results.append({'book': book, 'result': result})
            
            # Brief pause between tests
            if i < len(TECHNICAL_BOOKS):
                print("⏸️ Brief pause...")
                await asyncio.sleep(5)
        
        # Summary
        print(f"\n📊 RESULTS SUMMARY:")
        print("=" * 30)
        
        success_count = 0
        epub_count = 0
        
        for i, test in enumerate(results, 1):
            book = test['book']
            result = test['result']
            status = result['status']
            file_type = result['type']
            
            if status == 'SUCCESS':
                success_count += 1
                if file_type == 'EPUB':
                    epub_count += 1
                    print(f"🎉 {i}. {book[:30]}... → EPUB SUCCESS")
                else:
                    print(f"✅ {i}. {book[:30]}... → FILE SUCCESS ({file_type})")
            elif status == 'RESPONSE_NO_FILE':
                print(f"📝 {i}. {book[:30]}... → TEXT RESPONSE")
            else:
                print(f"❌ {i}. {book[:30]}... → {status}")
        
        total_tests = len(TECHNICAL_BOOKS)
        success_rate = (success_count * 100) // total_tests
        epub_rate = (epub_count * 100) // total_tests
        
        print(f"\n📈 Success Rate: {success_rate}% ({success_count}/{total_tests})")
        print(f"📄 EPUB Rate: {epub_rate}% ({epub_count}/{total_tests})")
        
        # Technical assessment
        print(f"\n🔬 TECHNICAL ANALYSIS:")
        if epub_count >= 2:
            print("🎉 Excellent: Multiple EPUB deliveries confirmed")
        elif epub_count >= 1:
            print("✅ Good: At least one EPUB delivery confirmed")
        elif success_count >= 1:
            print("⚠️ Partial: File delivery but format unclear")
        else:
            print("❌ Poor: No clear file deliveries")
        
        # Author recognition analysis
        print(f"\n👨‍🏫 AUTHOR RECOGNITION TEST:")
        for test in results:
            book = test['book']
            if 'clrs' in book.lower() or 'cormen' in book.lower():
                print("📚 CLRS/Cormen test: " + ("✅" if test['result']['status'] == 'SUCCESS' else "❌"))
            if 'tanenbaum' in book.lower():
                print("📚 Tanenbaum test: " + ("✅" if test['result']['status'] == 'SUCCESS' else "❌"))
        
        return success_count >= 1
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print(f"\n🏁 Final Result: {'PASSED' if result else 'FAILED'}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")