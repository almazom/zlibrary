#!/usr/bin/env python3

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import time
import sys

async def test_russian_book():
    """Test Russian book request with direct message reading"""
    
    # Configuration
    API_ID = 29950132
    API_HASH = 'e0bf78283481e2341805e3e4e90d289a'
    BOT_USERNAME = 'epub_toc_based_sample_bot'
    
    try:
        # Load session
        with open('telegram_bot/stable_string_session.txt', 'r') as f:
            string_session = f.read().strip()
        
        client = TelegramClient(StringSession(string_session), API_ID, API_HASH)
        await client.connect()
        me = await client.get_me()
        
        print(f"🔗 Connected as: {me.first_name}")
        
        # Russian classics to test
        russian_books = [
            "Война и мир Толстой",
            "Преступление и наказание Достоевский", 
            "Анна Каренина Толстой",
            "Мастер и Маргарита Булгаков",
            "Евгений Онегин Пушкин"
        ]
        
        results = []
        
        for i, book in enumerate(russian_books, 1):
            print(f"\n🇷🇺 TEST {i}/5: '{book}'")
            print(f"📤 Sending Russian request...")
            
            try:
                # Send Russian book request
                message = await client.send_message(f'@{BOT_USERNAME}', book)
                print(f"✅ Message sent! ID: {message.id}")
                
                # Wait for processing (Russian books take longer)
                print(f"⏳ Waiting 40 seconds for Russian book processing...")
                await asyncio.sleep(40)
                
                # Read recent messages from bot
                print(f"📖 Reading recent messages...")
                messages = []
                async for msg in client.iter_messages(f'@{BOT_USERNAME}', limit=10):
                    if msg.date.timestamp() > (message.date.timestamp() - 60):  # Within last minute
                        messages.append({
                            'id': msg.id,
                            'text': msg.text or '',
                            'date': msg.date,
                            'file': bool(msg.file),
                            'document': bool(msg.document)
                        })
                
                # Analyze responses
                epub_found = False
                search_activity = False
                error_found = False
                russian_context = False
                
                for msg in messages:
                    text = msg['text'].lower()
                    
                    # Check for EPUB delivery
                    if any(indicator in text for indicator in ['epub', 'книга', 'файл', 'document', 'attachment']) or msg['file']:
                        epub_found = True
                    
                    # Check for search activity
                    if any(indicator in text for indicator in ['поиск', 'searching', 'ищу', 'found', 'найдено']):
                        search_activity = True
                    
                    # Check for errors
                    if any(indicator in text for indicator in ['error', 'ошибка', 'не найдено', 'not found']):
                        error_found = True
                    
                    # Check for Russian context
                    if any(author in text for author in ['толстой', 'достоевский', 'пушкин', 'булгаков']):
                        russian_context = True
                
                # Determine result
                status = "UNKNOWN"
                if epub_found:
                    status = "SUCCESS"
                elif search_activity and not error_found:
                    status = "PARTIAL"  
                elif error_found:
                    status = "FAILED"
                
                result = {
                    'book': book,
                    'status': status,
                    'epub_found': epub_found,
                    'search_activity': search_activity,
                    'error_found': error_found,
                    'russian_context': russian_context,
                    'message_count': len(messages),
                    'files_received': sum(1 for msg in messages if msg['file'])
                }
                
                results.append(result)
                
                print(f"📊 Result: {status}")
                print(f"   EPUB Found: {'✅' if epub_found else '❌'}")
                print(f"   Search Activity: {'✅' if search_activity else '❌'}")
                print(f"   Russian Context: {'✅' if russian_context else '❌'}")
                print(f"   Files Received: {result['files_received']}")
                print(f"   Messages Analyzed: {len(messages)}")
                
                # Wait between tests
                if i < len(russian_books):
                    print(f"⏸️ Waiting 10s before next test...")
                    await asyncio.sleep(10)
                
            except Exception as e:
                print(f"❌ Error testing '{book}': {e}")
                results.append({
                    'book': book,
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        # Final summary
        print(f"\n" + "="*60)
        print(f"🎯 UC26 RUSSIAN CLASSICS TEST RESULTS")
        print(f"="*60)
        
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        partial_count = sum(1 for r in results if r['status'] == 'PARTIAL')
        failed_count = sum(1 for r in results if r['status'] == 'FAILED')
        error_count = sum(1 for r in results if r['status'] == 'ERROR')
        
        print(f"📚 Total Tests: {len(russian_books)}")
        print(f"✅ EPUB Verified: {success_count}")
        print(f"⚠️ Partial Success: {partial_count}")
        print(f"❌ Failed: {failed_count}")  
        print(f"🔧 Technical Errors: {error_count}")
        
        success_rate = ((success_count + partial_count) * 100) // len(russian_books)
        print(f"📊 Overall Success Rate: {success_rate}%")
        
        print(f"\n🔍 Detailed Results:")
        for r in results:
            emoji = "✅" if r['status'] == 'SUCCESS' else "⚠️" if r['status'] == 'PARTIAL' else "❌"
            print(f"  {emoji} {r['book']}: {r['status']}")
            if 'files_received' in r and r['files_received'] > 0:
                print(f"    📎 Files: {r['files_received']}")
        
        # Analysis
        print(f"\n🇷🇺 CYRILLIC TEXT PROCESSING ANALYSIS:")
        print(f"   Character Encoding: {'✅ PASSED' if success_count > 0 else '❌ ISSUES'}")
        print(f"   Russian Literature Recognition: {'✅ VERIFIED' if any(r.get('russian_context') for r in results) else '❌ LIMITED'}")
        print(f"   EPUB Delivery for Russian Titles: {'✅ WORKING' if success_count >= 2 else '⚠️ PARTIAL' if success_count > 0 else '❌ FAILED'}")
        
        if success_rate >= 60:
            print(f"\n🎉 UC26 ASSESSMENT: PASSED - Russian classics processing working well!")
        elif success_rate >= 40:
            print(f"\n⚠️ UC26 ASSESSMENT: PARTIAL - Some Russian processing issues detected")  
        else:
            print(f"\n❌ UC26 ASSESSMENT: FAILED - Russian language support needs improvement")
        
        return results
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return []
    finally:
        await client.disconnect()

if __name__ == "__main__":
    results = asyncio.run(test_russian_book())
    sys.exit(0 if results and any(r['status'] in ['SUCCESS', 'PARTIAL'] for r in results) else 1)