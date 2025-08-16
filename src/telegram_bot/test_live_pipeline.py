#!/usr/bin/env python3
"""
Live Pipeline Test - Demonstrate complete book search to EPUB pipeline
This tests the actual functions without Telegram polling issues
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment
load_dotenv()

from simple_bot import search_book, send_epub_file, process_book_request
from unittest.mock import AsyncMock

async def test_complete_pipeline():
    """Test the complete pipeline manually"""
    
    print("🚀 Testing Complete Book Search Pipeline")
    print("=" * 50)
    
    # Test 1: Book Search Function
    print("\n📚 STEP 1: Testing book search with 'Clean Code Robert Martin'")
    try:
        result = await search_book("Clean Code Robert Martin")
        print(f"✅ Search completed!")
        print(f"Status: {result.get('status')}")
        
        if result.get("status") == "success":
            book_result = result.get("result", {})
            print(f"Found: {book_result.get('found')}")
            
            if book_result.get('found'):
                print(f"Title: {book_result.get('book_info', {}).get('title', 'Unknown')}")
                print(f"EPUB Path: {book_result.get('epub_download_url')}")
                
                epub_path = book_result.get('epub_download_url')
                if epub_path and Path(epub_path).exists():
                    print(f"✅ EPUB file exists: {Path(epub_path).stat().st_size} bytes")
                    
                    # Test 2: EPUB Sending Function
                    print(f"\n📤 STEP 2: Testing EPUB file sending")
                    mock_message = AsyncMock()
                    mock_message.answer_document = AsyncMock()
                    
                    title = book_result.get('book_info', {}).get('title', 'Clean Code')
                    await send_epub_file(mock_message, epub_path, title)
                    
                    if mock_message.answer_document.called:
                        print(f"✅ EPUB file would be sent successfully!")
                        print(f"Document call args: {mock_message.answer_document.call_args}")
                    else:
                        print(f"❌ EPUB sending function was not called")
                        
                else:
                    print(f"❌ EPUB file not found at: {epub_path}")
            else:
                print(f"❌ Book not found in search results")
        else:
            print(f"❌ Search failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Complete Pipeline Function
    print(f"\n🔄 STEP 3: Testing complete pipeline function")
    try:
        mock_message = AsyncMock()
        mock_message.text = "Clean Code Robert Martin"
        mock_message.from_user.id = 12345
        mock_message.answer = AsyncMock()
        mock_message.answer_document = AsyncMock()
        
        await process_book_request(mock_message)
        
        print(f"✅ Pipeline completed!")
        print(f"Progress message calls: {mock_message.answer.call_count}")
        print(f"Document send calls: {mock_message.answer_document.call_count}")
        
        if mock_message.answer.called:
            print(f"Progress message: {mock_message.answer.call_args}")
            
        if mock_message.answer_document.called:
            print(f"✅ Complete pipeline SUCCESS! EPUB would be sent to user.")
        else:
            print(f"❌ Pipeline did not complete - no EPUB sent")
            
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 50)
    print(f"🏁 Pipeline test completed!")

if __name__ == "__main__":
    asyncio.run(test_complete_pipeline())