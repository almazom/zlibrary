#!/usr/bin/env python3
"""
Live Feedback Test - Send message to bot and monitor response
Following UC3 pattern but in Python for real-time monitoring
"""
import asyncio
import json
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID', '14835038')  # From UC3 pattern

class TelegramBotTester:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_update_id = 0
        
    def send_message(self, text):
        """Send message to bot"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text
        }
        
        print(f"📤 SENDING MESSAGE: '{text}'")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ MESSAGE SENT SUCCESSFULLY")
                return True
            else:
                print(f"❌ SEND FAILED: {result.get('description')}")
                return False
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            return False
    
    def get_updates(self, timeout=10):
        """Get bot updates (responses)"""
        url = f"{self.base_url}/getUpdates"
        params = {
            "offset": self.last_update_id + 1,
            "timeout": timeout
        }
        
        try:
            response = requests.get(url, params=params, timeout=timeout+5)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok') and result.get('result'):
                    updates = result['result']
                    if updates:
                        # Update last_update_id
                        self.last_update_id = updates[-1]['update_id']
                    return updates
                return []
            else:
                print(f"❌ UPDATE ERROR: {response.status_code}")
                return []
        except requests.exceptions.Timeout:
            return []
        except Exception as e:
            print(f"❌ UPDATE EXCEPTION: {e}")
            return []
    
    def monitor_responses(self, timeout_seconds=60):
        """Monitor bot responses after sending message"""
        print(f"👁️ MONITORING RESPONSES (timeout: {timeout_seconds}s)...")
        
        start_time = time.time()
        found_responses = []
        
        while time.time() - start_time < timeout_seconds:
            updates = self.get_updates(timeout=5)
            
            for update in updates:
                message = update.get('message', {})
                if not message:
                    continue
                    
                # Skip our own messages
                if message.get('from', {}).get('id') == int(self.chat_id):
                    continue
                
                # This is a bot response
                response_text = message.get('text', '')
                document = message.get('document')
                
                if document:
                    file_name = document.get('file_name', '')
                    file_size = document.get('file_size', 0)
                    mime_type = document.get('mime_type', '')
                    
                    print(f"📎 DOCUMENT RECEIVED:")
                    print(f"   📄 File: {file_name}")
                    print(f"   📊 Size: {file_size} bytes")
                    print(f"   🔧 Type: {mime_type}")
                    
                    if file_name.endswith('.epub') or 'epub' in mime_type.lower():
                        print(f"✅ EPUB FILE DETECTED! SUCCESS!")
                        found_responses.append({
                            'type': 'epub_document',
                            'file_name': file_name,
                            'file_size': file_size,
                            'mime_type': mime_type,
                            'timestamp': time.time()
                        })
                    else:
                        print(f"📄 Document received (not EPUB)")
                        found_responses.append({
                            'type': 'other_document',
                            'file_name': file_name,
                            'timestamp': time.time()
                        })
                
                elif response_text:
                    print(f"💬 TEXT RESPONSE: {response_text[:100]}...")
                    
                    # Check for progress messages
                    if "🔍" in response_text or "Searching" in response_text:
                        print(f"🔍 PROGRESS MESSAGE DETECTED")
                        found_responses.append({
                            'type': 'progress_message',
                            'text': response_text,
                            'timestamp': time.time()
                        })
                    elif "❌" in response_text or "не найдено" in response_text or "not found" in response_text:
                        print(f"❌ ERROR MESSAGE DETECTED")
                        found_responses.append({
                            'type': 'error_message',
                            'text': response_text,
                            'timestamp': time.time()
                        })
                    elif "✅" in response_text or "найдено" in response_text or "found" in response_text:
                        print(f"✅ SUCCESS MESSAGE DETECTED")
                        found_responses.append({
                            'type': 'success_message',
                            'text': response_text,
                            'timestamp': time.time()
                        })
                    else:
                        print(f"📝 GENERAL RESPONSE")
                        found_responses.append({
                            'type': 'text_response',
                            'text': response_text,
                            'timestamp': time.time()
                        })
            
            if not updates:
                print("⏳ Waiting for responses...")
            
            time.sleep(2)
        
        print(f"⏰ MONITORING FINISHED ({timeout_seconds}s)")
        return found_responses
    
    def test_book_search(self, book_query, timeout=120):
        """Complete test: send book query and monitor responses"""
        print(f"🚀 STARTING BOOK SEARCH TEST")
        print(f"📚 Query: '{book_query}'")
        print(f"🤖 Bot: @epub_toc_based_sample_bot")
        print(f"💬 Chat ID: {self.chat_id}")
        print("=" * 60)
        
        # Send the message
        if not self.send_message(book_query):
            print("❌ FAILED TO SEND MESSAGE")
            return False
        
        # Monitor responses
        responses = self.monitor_responses(timeout)
        
        print("=" * 60)
        print(f"📊 RESULTS SUMMARY:")
        print(f"📈 Total Responses: {len(responses)}")
        
        response_types = {}
        for response in responses:
            response_type = response['type']
            response_types[response_type] = response_types.get(response_type, 0) + 1
        
        for response_type, count in response_types.items():
            print(f"   {response_type}: {count}")
        
        # Check for success criteria
        has_epub = any(r['type'] == 'epub_document' for r in responses)
        has_progress = any(r['type'] == 'progress_message' for r in responses)
        has_responses = len(responses) > 0
        
        print(f"✅ Has Progress Messages: {has_progress}")
        print(f"✅ Has EPUB Download: {has_epub}")
        print(f"✅ Has Any Response: {has_responses}")
        
        if has_epub and has_progress:
            print(f"🎉 COMPLETE SUCCESS - Progress messages + EPUB file!")
            return True
        elif has_responses:
            print(f"⚠️ PARTIAL SUCCESS - Bot responded but no EPUB")
            return True
        else:
            print(f"❌ FAILURE - No response from bot")
            return False

async def main():
    """Run the live feedback test"""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return
    
    tester = TelegramBotTester(BOT_TOKEN, CHAT_ID)
    
    # Test book queries
    book_queries = [
        "Clean Code Robert Martin",
        "Python Programming", 
        "1984 George Orwell"
    ]
    
    for i, query in enumerate(book_queries, 1):
        print(f"\n🔥 TEST {i}/{len(book_queries)}")
        success = tester.test_book_search(query, timeout=120)
        
        if success:
            print(f"✅ TEST {i} PASSED")
        else:
            print(f"❌ TEST {i} FAILED")
        
        if i < len(book_queries):
            print(f"⏳ Waiting 15 seconds before next test...")
            time.sleep(15)
    
    print(f"\n🏁 ALL TESTS COMPLETED!")

if __name__ == "__main__":
    asyncio.run(main())