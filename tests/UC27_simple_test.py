#!/usr/bin/env python3
"""
UC27: Simple Technical Books Test
Direct approach without MCP reader dependency
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

# Advanced technical books
TECHNICAL_BOOKS = [
    "Introduction to Algorithms CLRS Cormen",
    "Computer Networks Tanenbaum",
    "Operating System Concepts Silberschatz", 
    "Database System Concepts Silberschatz",
    "Artificial Intelligence Russell Norvig"
]

async def send_technical_book(client, book_title, test_number):
    """Send technical book request to bot"""
    print(f"📚 TECHNICAL TEST {test_number}: '{book_title}'")
    
    try:
        me = await client.get_me()
        message = await client.send_message(f'@{BOT_USERNAME}', book_title)
        print(f"✅ Technical book sent! ID: {message.id} From: {me.first_name} ({me.id})")
        return message.id
    except Exception as e:
        print(f"❌ Failed to send technical book: {e}")
        return None

async def monitor_bot_response(client, wait_time=45):
    """Monitor bot responses for a specific time period"""
    print(f"🔍 Monitoring bot responses for {wait_time}s...")
    
    start_time = time.time()
    messages_found = []
    
    try:
        # Get recent messages from the bot
        async for message in client.iter_messages(f'@{BOT_USERNAME}', limit=20):
            # Check if message is recent (within last 2 minutes)
            if message.date and (time.time() - message.date.timestamp()) < 120:
                messages_found.append({
                    'id': message.id,
                    'text': message.text or '',
                    'has_file': bool(message.file),
                    'file_name': message.file.name if message.file else None,
                    'file_size': message.file.size if message.file else None,
                    'mime_type': message.file.mime_type if message.file else None,
                    'date': message.date
                })
    except Exception as e:
        print(f"⚠️ Error monitoring messages: {e}")
    
    return messages_found

async def analyze_technical_response(messages, book_title):
    """Analyze technical book response with enhanced scoring"""
    print(f"🔬 TECHNICAL ANALYSIS for '{book_title}'")
    
    if not messages:
        print("❌ No recent messages found from bot")
        return {'score': 0, 'status': 'NO_RESPONSE'}
    
    # Analysis scores
    epub_score = 0
    quality_score = 0
    error_score = 0
    
    all_text = ' '.join([msg.get('text', '') for msg in messages])
    
    print(f"📝 Analyzing {len(messages)} recent messages...")
    
    # EPUB delivery indicators
    for msg in messages:
        if msg.get('has_file'):
            print(f"📄 File found: {msg.get('file_name', 'unnamed')} ({msg.get('file_size', 0)} bytes)")
            if msg.get('mime_type') == 'application/epub+zip' or (msg.get('file_name', '').endswith('.epub')):
                epub_score += 3
                print("✅ EPUB file confirmed!")
            else:
                epub_score += 1
                print(f"📎 Other file type: {msg.get('mime_type', 'unknown')}")
    
    # Text content analysis
    if 'epub' in all_text.lower():
        epub_score += 2
        print("📄 EPUB mentioned in text")
    
    if any(word in all_text.lower() for word in ['sent', 'download', 'file', 'book']):
        epub_score += 1
        print("📤 Delivery indicators found")
    
    # Technical content matching
    technical_terms = ['algorithm', 'network', 'database', 'operating system', 'artificial intelligence']
    if any(term in all_text.lower() for term in technical_terms):
        quality_score += 1
        print("🎯 Technical content match detected")
    
    # Author matching
    authors = ['clrs', 'cormen', 'tanenbaum', 'silberschatz', 'russell', 'norvig']
    if any(author in all_text.lower() for author in authors):
        quality_score += 2
        print("👨‍🏫 Author match confirmed")
    
    # Error detection
    error_terms = ['error', 'failed', 'not found', 'unavailable', 'timeout']
    if any(term in all_text.lower() for term in error_terms):
        error_score += 2
        print("❌ Error indicators detected")
    
    total_score = epub_score + quality_score - error_score
    
    print(f"📊 ANALYSIS SCORES:")
    print(f"   📄 EPUB Score: {epub_score}/7")
    print(f"   🎯 Quality Score: {quality_score}/3")
    print(f"   ❌ Error Penalty: -{error_score}")
    print(f"   📈 Total Score: {total_score}")
    
    # Determine status
    if epub_score >= 4 and error_score == 0:
        status = 'HIGH_SUCCESS'
        print("🎉 HIGH CONFIDENCE: EPUB delivered successfully")
    elif epub_score >= 2 and error_score == 0:
        status = 'GOOD_SUCCESS'
        print("✅ GOOD CONFIDENCE: Likely EPUB delivery")
    elif epub_score >= 1 and error_score <= 1:
        status = 'PARTIAL'
        print("⚠️ MODERATE: Delivery unclear")
    elif error_score >= 2:
        status = 'FAILED'
        print("❌ HIGH ERROR: Delivery likely failed")
    else:
        status = 'UNCLEAR'
        print("❓ UNCLEAR: Mixed or weak signals")
    
    return {
        'score': total_score,
        'status': status,
        'epub_score': epub_score,
        'quality_score': quality_score,
        'error_score': error_score,
        'messages_count': len(messages)
    }

async def test_technical_book(client, book, test_num, total):
    """Test single technical book with comprehensive analysis"""
    print(f"\n{'='*80}")
    print(f"🔥 ADVANCED TECHNICAL TEST {test_num}/{total}")
    print(f"📖 Book: '{book}'")
    print(f"🎓 Category: Computer Science/Engineering")
    print("="*80)
    
    # Send book request
    message_id = await send_technical_book(client, book, test_num)
    if not message_id:
        return {'status': 'SEND_FAILED', 'score': 0}
    
    # Wait for processing (technical books need more time)
    print("⏳ Waiting 45s for technical book processing...")
    await asyncio.sleep(45)
    
    # Monitor and analyze response
    messages = await monitor_bot_response(client, wait_time=5)
    result = await analyze_technical_response(messages, book)
    
    # Log result
    status_emoji = {
        'HIGH_SUCCESS': '🎉',
        'GOOD_SUCCESS': '✅',
        'PARTIAL': '⚠️',
        'FAILED': '❌',
        'UNCLEAR': '❓',
        'NO_RESPONSE': '🔧',
        'SEND_FAILED': '❌'
    }
    
    emoji = status_emoji.get(result['status'], '❓')
    print(f"{emoji} TEST {test_num}: {result['status']} - Score: {result['score']}")
    
    return result

async def main():
    """Main technical books test"""
    print("🚀 UC27: Advanced Technical Books Test (Direct)")
    print("=" * 50)
    print(f"📚 Technical books: {len(TECHNICAL_BOOKS)}")
    print(f"🎓 Domain: Computer Science & Engineering") 
    print(f"🎯 Target: @{BOT_USERNAME}")
    print("=" * 50)
    
    # Read session
    try:
        with open('telegram_bot/stable_string_session.txt', 'r') as f:
            string_session = f.read().strip()
    except FileNotFoundError:
        print("❌ Session file not found: telegram_bot/stable_string_session.txt")
        return False
    
    # Initialize client
    client = TelegramClient(StringSession(string_session), API_ID, API_HASH)
    
    try:
        await client.connect()
        me = await client.get_me()
        print(f"👤 Connected as: {me.first_name} ({me.id})")
        
        # Test results tracking
        results = []
        status_counts = {
            'HIGH_SUCCESS': 0,
            'GOOD_SUCCESS': 0,
            'PARTIAL': 0,
            'FAILED': 0,
            'UNCLEAR': 0,
            'NO_RESPONSE': 0,
            'SEND_FAILED': 0
        }
        
        # Test each technical book
        for i, book in enumerate(TECHNICAL_BOOKS, 1):
            result = await test_technical_book(client, book, i, len(TECHNICAL_BOOKS))
            results.append({
                'book': book,
                'test_num': i,
                'result': result
            })
            status_counts[result['status']] += 1
            
            # Wait between tests
            if i < len(TECHNICAL_BOOKS):
                print("⏸️ Waiting 10s before next test...")
                await asyncio.sleep(10)
        
        # Final analysis
        print(f"\n🎯 UC27 ADVANCED TECHNICAL RESULTS")
        print("=" * 40)
        print(f"Total Technical Tests: {len(TECHNICAL_BOOKS)}")
        for status, count in status_counts.items():
            if count > 0:
                emoji = {
                    'HIGH_SUCCESS': '🎉',
                    'GOOD_SUCCESS': '✅', 
                    'PARTIAL': '⚠️',
                    'FAILED': '❌',
                    'UNCLEAR': '❓',
                    'NO_RESPONSE': '🔧',
                    'SEND_FAILED': '❌'
                }[status]
                print(f"{emoji} {status.replace('_', ' ').title()}: {count}")
        
        total_success = status_counts['HIGH_SUCCESS'] + status_counts['GOOD_SUCCESS']
        success_rate = (total_success * 100) // len(TECHNICAL_BOOKS)
        high_confidence_rate = (status_counts['HIGH_SUCCESS'] * 100) // len(TECHNICAL_BOOKS)
        
        print(f"📊 Success Rate: {success_rate}%")
        print(f"🎯 High Confidence Rate: {high_confidence_rate}%")
        
        # Technical recommendations
        print(f"\n🔬 TECHNICAL ANALYSIS:")
        if status_counts['HIGH_SUCCESS'] >= 3:
            print("📈 Excellent technical book support")
            print("🎓 Computer science books: WORKING")
            print("📄 EPUB delivery: RELIABLE")
        elif status_counts['GOOD_SUCCESS'] >= 2:
            print("📊 Good technical content processing") 
            print("🔍 Search algorithms: EFFECTIVE")
        elif status_counts['PARTIAL'] >= 2:
            print("⚙️ Some technical books need longer processing")
            print("📚 Large technical files may require more time")
        
        # Overall assessment
        if total_success >= 4:
            print("🎉 UC27 PASSED: Technical books working excellently!")
            return True
        elif total_success >= 3:
            print("✅ UC27 GOOD: Technical books mostly working")
            return True
        elif total_success >= 2:
            print("⚠️ UC27 PARTIAL: Some technical book success")
            return False
        else:
            print("❌ UC27 FAILED: Technical books not working reliably")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(3)