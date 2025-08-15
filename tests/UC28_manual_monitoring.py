#!/usr/bin/env python3
"""
UC28: Popular Fiction Real-time Test with Manual Monitoring
Tests popular fiction books with direct Python monitoring instead of MCP
"""

import asyncio
import time
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# Configuration
BOT_USERNAME = "epub_toc_based_sample_bot"
API_ID = 29950132
API_HASH = "e0bf78283481e2341805e3e4e90d289a"

# Popular fiction books
FICTION_BOOKS = [
    "Harry Potter Sorcerer Stone Rowling",
    "The Great Gatsby Fitzgerald", 
    "To Kill a Mockingbird Harper Lee",
    "1984 George Orwell",
    "Pride and Prejudice Jane Austen"
]

# Colors for output
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'

def log_info(msg): print(f"{Colors.BLUE}[UC28]{Colors.NC} {msg}")
def log_success(msg): print(f"{Colors.GREEN}[UC28]{Colors.NC} {msg}")
def log_error(msg): print(f"{Colors.RED}[UC28]{Colors.NC} {msg}")
def log_warn(msg): print(f"{Colors.YELLOW}[UC28]{Colors.NC} {msg}")
def log_fiction(msg): print(f"{Colors.MAGENTA}[UC28]{Colors.NC} {msg}")

class RealTimeMonitor:
    def __init__(self):
        self.client = None
        
    async def init_client(self):
        """Initialize Telegram client"""
        try:
            with open('telegram_bot/stable_string_session.txt', 'r') as f:
                string_session = f.read().strip()
            
            self.client = TelegramClient(StringSession(string_session), API_ID, API_HASH)
            await self.client.connect()
            
            me = await self.client.get_me()
            log_info(f"📱 Connected as: {me.first_name} (ID: {me.id})")
            return True
            
        except Exception as e:
            log_error(f"❌ Failed to initialize client: {e}")
            return False
    
    async def send_book_request(self, book_title, test_num):
        """Send book request to bot"""
        try:
            log_fiction(f"📚 FICTION TEST {test_num}: '{book_title}'")
            message = await self.client.send_message(f'@{BOT_USERNAME}', book_title)
            log_success(f"✅ Book request sent! Message ID: {message.id}")
            return message.id
        except Exception as e:
            log_error(f"❌ Failed to send book request: {e}")
            return None
    
    async def monitor_response(self, book_title, message_id, test_num):
        """Monitor for bot response in real-time"""
        log_fiction(f"🎬 REAL-TIME MONITORING for '{book_title}'")
        
        monitoring_duration = 45  # seconds
        check_interval = 5       # seconds  
        checks_total = monitoring_duration // check_interval
        
        log_info(f"⏱️ Monitoring for {monitoring_duration}s ({checks_total} checks every {check_interval}s)")
        
        # Initialize tracking
        progress_detected = 0
        epub_detected = 0
        error_detected = 0
        final_result = []
        
        start_time = time.time()
        
        # Real-time monitoring loop
        for i in range(1, checks_total + 1):
            elapsed = int(time.time() - start_time)
            log_info(f"📡 Check {i}/{checks_total} ({elapsed}s elapsed)")
            
            try:
                # Get recent messages from bot
                messages = await self.client.get_messages(f'@{BOT_USERNAME}', limit=8)
                
                recent_msgs = []
                for msg in messages:
                    if msg.date.timestamp() > start_time - 60:  # Messages from last minute
                        content = msg.message if msg.message else "[Media/File]"
                        recent_msgs.append({
                            'content': content,
                            'has_file': bool(msg.file),
                            'timestamp': msg.date.strftime('%H:%M:%S')
                        })
                        
                        # Check for file delivery
                        if msg.file and msg.file.name and '.epub' in msg.file.name.lower():
                            if epub_detected == 0:
                                epub_detected = i
                                log_success(f"📄 EPUB DELIVERY detected at check {i}!")
                                log_success(f"📎 File: {msg.file.name} ({msg.file.size} bytes)")
                                final_result = recent_msgs.copy()
                                break
                
                # Analyze text messages
                recent_text = ' '.join([m['content'] for m in recent_msgs])
                
                # Check for progress indicators  
                if progress_detected == 0:
                    if any(word in recent_text.lower() for word in ['searching', 'looking', 'processing', 'найдено', 'found']):
                        progress_detected = i
                        log_fiction(f"🔍 PROGRESS detected at check {i}!")
                
                # Check for errors
                if any(word in recent_text.lower() for word in ['error', 'failed', 'not found', 'unavailable']):
                    if error_detected == 0:
                        error_detected = i
                        log_warn(f"❌ Error detected at check {i}")
                
                # Save current state
                if not final_result and (progress_detected or error_detected):
                    final_result = recent_msgs.copy()
                    
            except Exception as e:
                log_warn(f"📭 Error reading messages at check {i}: {e}")
            
            # Wait between checks (except last)
            if i < checks_total and epub_detected == 0:
                await asyncio.sleep(check_interval)
        
        # Analyze results
        total_time = int(time.time() - start_time)
        log_fiction("📊 REAL-TIME ANALYSIS:")
        log_fiction(f"   🔍 Progress: Check {progress_detected}/{checks_total}")
        log_fiction(f"   📄 EPUB: Check {epub_detected}/{checks_total}")  
        log_fiction(f"   ❌ Errors: Check {error_detected}/{checks_total}")
        log_fiction(f"   ⏱️ Total time: {total_time}s")
        
        # Save results
        safe_title = book_title.replace(' ', '_').replace('/', '_')
        result_file = f"test_results/UC28_{test_num}_{safe_title}_monitoring.txt"
        
        try:
            with open(result_file, 'w') as f:
                f.write("=== UC28 REAL-TIME MONITORING RESULTS ===\n")
                f.write(f"Book: {book_title}\n")
                f.write(f"Message ID: {message_id}\n")
                f.write(f"Total Time: {total_time}s\n")
                f.write(f"Progress Detected: Check {progress_detected}\n")
                f.write(f"EPUB Detected: Check {epub_detected}\n")
                f.write(f"Error Detected: Check {error_detected}\n")
                f.write("\n=== FINAL MESSAGES ===\n")
                for msg in final_result[:5]:
                    f.write(f"[{msg['timestamp']}] {msg['content'][:100]}\n")
                    if msg['has_file']:
                        f.write("    📎 [File attachment detected]\n")
        except Exception as e:
            log_warn(f"Failed to save results: {e}")
        
        # Return result code
        if epub_detected > 0:
            response_time = epub_detected * check_interval
            log_success(f"🎉 EPUB delivered in ~{response_time}s!")
            return 0  # Clear success
        elif progress_detected > 0:
            log_warn("⚠️ Progress detected but no clear EPUB delivery")
            return 1  # Partial success
        else:
            log_error("❌ No significant activity detected")
            return 2  # No activity

    async def test_fiction_book(self, book, test_num, total):
        """Test a single fiction book"""
        log_info(f"🔥 REAL-TIME FICTION TEST {test_num}/{total}")
        log_fiction(f"📖 Book: '{book}'")
        log_fiction(f"🎭 Genre: Popular Fiction")
        log_fiction(f"⏱️ Mode: Real-time monitoring")
        print("=" * 80)
        
        message_id = await self.send_book_request(book, test_num)
        if not message_id:
            log_error(f"❌ TEST {test_num} SEND FAILED")
            return 3
        
        result_code = await self.monitor_response(book, message_id, test_num)
        
        if result_code == 0:
            log_success(f"🎉 TEST {test_num} SUCCESS: EPUB delivered with timing!")
        elif result_code == 1:
            log_warn(f"⚠️ TEST {test_num} PARTIAL: Activity detected, unclear delivery")
        else:
            log_error(f"❌ TEST {test_num} NO ACTIVITY: No significant response")
        
        return result_code

    async def run_all_tests(self):
        """Run all fiction book tests"""
        log_info("🚀 UC28: Popular Fiction Real-time Test")
        log_info("========================================")
        log_fiction(f"📚 Fiction books: {len(FICTION_BOOKS)}")
        log_fiction("🎭 Genre: Popular/Classic Fiction")
        log_fiction("⏱️ Method: Real-time monitoring")
        log_info(f"🎯 Target: @{BOT_USERNAME}")
        log_fiction("📡 Monitor: Direct Python/Telethon")
        log_info("========================================")
        
        # Initialize client
        if not await self.init_client():
            log_error("❌ Failed to initialize Telegram client")
            return False
        
        # Create results directory
        import os
        os.makedirs("test_results", exist_ok=True)
        
        # Test counters
        total_tests = len(FICTION_BOOKS)
        delivered = 0
        partial = 0
        no_activity = 0
        send_failed = 0
        
        # Test each fiction book
        for i, book in enumerate(FICTION_BOOKS):
            test_num = i + 1
            
            print()
            result_code = await self.test_fiction_book(book, test_num, total_tests)
            
            if result_code == 0:
                delivered += 1
            elif result_code == 1:
                partial += 1
            elif result_code == 2:
                no_activity += 1
            else:
                send_failed += 1
            
            # Wait between tests
            if test_num < total_tests:
                log_info("⏸️ Cooling down 12s before next fiction test...")
                await asyncio.sleep(12)
        
        # Final analysis
        await self.print_final_results(total_tests, delivered, partial, no_activity, send_failed)
        
        # Cleanup
        if self.client:
            await self.client.disconnect()
        
        return delivered >= 3  # Success if at least 3 books delivered

    async def print_final_results(self, total_tests, delivered, partial, no_activity, send_failed):
        """Print comprehensive test results"""
        print()
        log_info("🎯 UC28 REAL-TIME FICTION RESULTS")
        log_info("==================================")
        log_fiction(f"Total Fiction Tests: {total_tests}")
        log_success(f"🎉 EPUB Delivered: {delivered}")
        log_warn(f"⚠️ Partial Response: {partial}")
        log_error(f"📭 No Activity: {no_activity}")
        log_error(f"❌ Send Failed: {send_failed}")
        
        total_responsive = delivered + partial
        delivery_rate = (delivered * 100) // total_tests if total_tests > 0 else 0
        response_rate = (total_responsive * 100) // total_tests if total_tests > 0 else 0
        
        log_fiction(f"📊 EPUB Delivery Rate: {delivery_rate}%")
        log_fiction(f"📡 Response Rate: {response_rate}%")
        log_info("📁 Real-time logs: test_results/UC28_*_monitoring.txt")
        log_info("==================================")
        
        # Performance insights
        print()
        log_fiction("⏱️ PERFORMANCE INSIGHTS:")
        
        if delivered >= 4:
            log_success("🚀 Excellent fiction book delivery performance")
            log_fiction("📚 Popular books: READILY AVAILABLE")
            log_fiction("⚡ Response times: FAST")
        elif delivered >= 3:
            log_success("✅ Good fiction book availability")
            log_fiction("📖 Classic literature: WORKING")
        elif total_responsive >= 3:
            log_warn("🔍 Fiction search active but delivery inconsistent")
            log_fiction("⏱️ May need longer processing times")
        else:
            log_error("🔧 Fiction book system may need investigation")
        
        # Overall assessment
        if delivered >= 4:
            log_success("🎉 UC28 EXCELLENT: Real-time fiction delivery working!")
        elif delivered >= 3:
            log_success("✅ UC28 GOOD: Fiction books mostly delivered")
        elif total_responsive >= 3:
            log_warn("⚠️ UC28 PARTIAL: Some fiction response detected")
        else:
            log_error("❌ UC28 FAILED: Fiction delivery not working")

async def main():
    """Main execution function"""
    monitor = RealTimeMonitor()
    success = await monitor.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)