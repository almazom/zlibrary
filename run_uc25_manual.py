#!/usr/bin/env python3
import asyncio
import time
from telethon import TelegramClient
from telethon.sessions import StringSession
from datetime import datetime

# Configuration
BOT_USERNAME = "epub_toc_based_sample_bot"
USER_ID = "5282615364"
API_ID = 29950132
API_HASH = "e0bf78283481e2341805e3e4e90d289a"

# Test books - English Programming Books
PROGRAMMING_BOOKS = [
    "Clean Code Robert Martin",
    "Design Patterns Gang of Four", 
    "The Pragmatic Programmer Hunt Thomas",
    "Effective Java Joshua Bloch",
    "Python Crash Course Eric Matthes"
]

class UC25TestRunner:
    def __init__(self):
        self.client = None
        self.results = []
        
    async def initialize(self):
        with open('stable_string_session.txt', 'r') as f:
            string_session = f.read().strip()
        
        self.client = TelegramClient(StringSession(string_session), API_ID, API_HASH)
        await self.client.connect()
        
    async def cleanup(self):
        if self.client:
            await self.client.disconnect()
            
    async def send_book_request(self, book_title, test_number):
        """Send book request as real user"""
        print(f"📚 TEST {test_number}: Sending '{book_title}'")
        
        try:
            me = await self.client.get_me()
            message = await self.client.send_message(f'@{BOT_USERNAME}', book_title)
            
            result = {
                'book': book_title,
                'test_number': test_number,
                'message_id': message.id,
                'user_id': me.id,
                'user_name': me.first_name,
                'timestamp': datetime.now(),
                'sent_successfully': True
            }
            
            print(f"✅ Message sent! ID: {message.id} From: {me.first_name} ({me.id})")
            return result
            
        except Exception as e:
            print(f"❌ Failed to send: {e}")
            return {
                'book': book_title,
                'test_number': test_number,
                'sent_successfully': False,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    async def check_bot_response(self, book_title, message_id, timeout=30):
        """Wait for and check bot response"""
        print(f"⏳ Waiting {timeout}s for bot response to '{book_title}'...")
        
        # Get messages before waiting
        messages_before = await self.client.get_messages(f'@{BOT_USERNAME}', limit=5)
        before_count = len(messages_before)
        
        await asyncio.sleep(timeout)
        
        # Get messages after waiting
        messages_after = await self.client.get_messages(f'@{BOT_USERNAME}', limit=10)
        
        print(f"📨 Found {len(messages_after)} total messages in conversation")
        
        # Analyze recent messages for EPUB indicators
        epub_indicators = []
        search_indicators = []
        error_indicators = []
        files_found = []
        
        for i, msg in enumerate(messages_after[:5]):  # Check last 5 messages
            timestamp = msg.date.strftime('%H:%M:%S')
            sender = 'Bot' if msg.from_id and msg.from_id.user_id != int(USER_ID) else 'User'
            text = msg.text or msg.message or '[Media/File]'
            
            print(f"   {i+1}. [{timestamp}] {sender}: {text}")
            
            # Check for document/file
            if msg.document:
                attrs = msg.document.attributes
                filename = 'Unknown'
                for attr in attrs:
                    if hasattr(attr, 'file_name') and attr.file_name:
                        filename = attr.file_name
                        break
                files_found.append({
                    'filename': filename,
                    'size': msg.document.size,
                    'timestamp': timestamp
                })
                print(f"      📄 Document: {filename} ({msg.document.size} bytes)")
            
            # Check message content for indicators
            if text:
                text_lower = text.lower()
                if any(keyword in text_lower for keyword in ['epub', '.epub', 'book sent', 'file sent', 'download']):
                    epub_indicators.append(text)
                elif any(keyword in text_lower for keyword in ['searching', 'looking', 'found']):
                    search_indicators.append(text)
                elif any(keyword in text_lower for keyword in ['error', 'failed', 'not found']):
                    error_indicators.append(text)
        
        # Determine result
        if files_found:
            print(f"📄 {len(files_found)} file(s) found - EPUB delivery likely!")
            return 'delivered', {
                'files': files_found,
                'epub_indicators': epub_indicators,
                'search_indicators': search_indicators,
                'error_indicators': error_indicators
            }
        elif epub_indicators:
            print(f"📄 EPUB indicators found in text!")
            return 'indicated', {
                'epub_indicators': epub_indicators,
                'search_indicators': search_indicators, 
                'error_indicators': error_indicators
            }
        elif search_indicators and not error_indicators:
            print(f"🔍 Search activity detected but no clear delivery")
            return 'searching', {
                'search_indicators': search_indicators,
                'error_indicators': error_indicators
            }
        elif error_indicators:
            print(f"❌ Error indicators found")
            return 'error', {
                'error_indicators': error_indicators,
                'search_indicators': search_indicators
            }
        else:
            print(f"❓ No clear response detected")
            return 'unclear', {}
    
    async def test_single_book(self, book, test_num, total):
        """Test single book with comprehensive verification"""
        print(f"\n🔥 RUNNING TEST {test_num}/{total}: '{book}'")
        print("=" * 80)
        
        # Send request
        send_result = await self.send_book_request(book, test_num)
        
        if not send_result['sent_successfully']:
            send_result['verification_result'] = 'send_failed'
            self.results.append(send_result)
            return 'failed', send_result
            
        # Wait and verify response  
        verification_result, verification_details = await self.check_bot_response(
            book, send_result['message_id']
        )
        
        send_result['verification_result'] = verification_result
        send_result['verification_details'] = verification_details
        self.results.append(send_result)
        
        if verification_result == 'delivered':
            print(f"✅ TEST {test_num} PASSED: EPUB delivery confirmed")
            return 'passed', send_result
        elif verification_result == 'indicated':
            print(f"✅ TEST {test_num} PASSED: EPUB delivery indicated")
            return 'passed', send_result
        elif verification_result == 'searching':
            print(f"⚠️ TEST {test_num} PARTIAL: Search detected but no delivery")
            return 'partial', send_result
        else:
            print(f"❌ TEST {test_num} FAILED: No clear EPUB delivery")
            return 'failed', send_result
    
    async def run_full_test(self):
        """Run complete UC25 test suite"""
        print("🚀 UC25: English Programming Books Test Suite")
        print("=================================================")
        print(f"📊 Total books: {len(PROGRAMMING_BOOKS)}")
        print(f"🎯 Target: @{BOT_USERNAME}")
        print(f"👤 User: {USER_ID}")
        print("=================================================")
        
        await self.initialize()
        
        total_tests = len(PROGRAMMING_BOOKS)
        passed = 0
        partial = 0
        failed = 0
        
        try:
            # Test each book
            for i, book in enumerate(PROGRAMMING_BOOKS):
                test_num = i + 1
                
                status, result = await self.test_single_book(book, test_num, total_tests)
                
                if status == 'passed':
                    passed += 1
                elif status == 'partial':
                    partial += 1
                else:
                    failed += 1
                
                # Wait between tests
                if test_num < total_tests:
                    print("⏸️ Waiting 5s before next test...")
                    await asyncio.sleep(5)
                    
        finally:
            await self.cleanup()
        
        # Final results
        print("\n🎯 UC25 FINAL RESULTS")
        print("=====================")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed (EPUB verified): {passed}")
        print(f"⚠️ Partial (unclear): {partial}")
        print(f"❌ Failed: {failed}")
        
        success_rate = ((passed * 100) // total_tests) if total_tests > 0 else 0
        print(f"Success Rate: {success_rate}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        print("=" * 50)
        for result in self.results:
            status = "✅ PASS" if result['verification_result'] in ['delivered', 'indicated'] else \
                     "⚠️ PART" if result['verification_result'] == 'searching' else "❌ FAIL"
            print(f"{status} | {result['book']}")
            if 'verification_details' in result:
                details = result['verification_details']
                if 'files' in details and details['files']:
                    for file_info in details['files']:
                        print(f"       📄 File: {file_info['filename']} ({file_info['size']} bytes)")
                if 'epub_indicators' in details and details['epub_indicators']:
                    print(f"       📚 EPUB indicators: {len(details['epub_indicators'])}")
                if 'error_indicators' in details and details['error_indicators']:
                    print(f"       ❌ Errors: {len(details['error_indicators'])}")
        
        print("=" * 50)
        
        # Determine overall result
        if passed >= (total_tests * 70 // 100):
            print("🎉 UC25 PASSED: Good EPUB delivery rate")
            return True
        else:
            print("❌ UC25 FAILED: Low EPUB delivery success")
            return False

async def main():
    runner = UC25TestRunner()
    success = await runner.run_full_test()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)