#!/usr/bin/env python3
"""
Manual Book Search Sender
Uses aiogram-Telethon unified architecture to send book search messages
that trigger IDENTICAL pipeline as manual user typing

FEATURES:
- Single event loop management (no conflicts)
- Message queue coordination
- Identical pipeline for all message sources
- Proper error handling with exponential backoff
"""

import asyncio
import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import argparse
from dotenv import load_dotenv

# Import the unified system
from aiogram_telethon_unified import UnifiedMessageRouter

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class ManualBookSearchSender:
    """Sends book search messages that trigger IDENTICAL pipeline as manual messages"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_id = int(os.getenv('TELEGRAM_API_ID', '0'))
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '')
        self.test_user_id = int(os.getenv('CHAT_ID', '14835038'))
        
        if not all([self.bot_token, self.api_id, self.api_hash]):
            raise ValueError("Missing required environment variables")
        
        self.router = None
    
    async def initialize_router(self):
        """Initialize the unified router with proper event loop management"""
        logger.info("🔧 Initializing aiogram-Telethon unified router...")
        
        self.router = UnifiedMessageRouter(
            bot_token=self.bot_token,
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_name='manual_sender_session'
        )
        
        # Start the pipeline processor
        self.processor_task = asyncio.create_task(self.router.unified_pipeline_processor())
        
        logger.info("✅ Router initialized and processor started")
    
    async def send_book_search_message(self, book_title: str, wait_for_result: bool = True) -> Dict[str, Any]:
        """Send book search message that triggers IDENTICAL pipeline as manual typing"""
        
        if not self.router:
            await self.initialize_router()
        
        logger.info(f"📚 MANUAL SEARCH: Sending book search for '{book_title}'")
        logger.info(f"🎯 This will trigger IDENTICAL pipeline as if user manually typed the message")
        
        start_time = time.time()
        
        try:
            # Send manual simulation (IDENTICAL to user typing)
            message_id = await self.router.send_manual_simulation(
                user_id=self.test_user_id,
                message_text=book_title
            )
            
            logger.info(f"📤 Message sent - ID: {message_id}")
            
            if wait_for_result:
                # Wait for processing with timeout
                timeout = 30
                wait_start = time.time()
                
                logger.info(f"⏳ Waiting for pipeline execution (timeout: {timeout}s)...")
                
                while (time.time() - wait_start) < timeout:
                    if message_id in self.router.processed_messages:
                        result = self.router.processed_messages[message_id]
                        total_time = time.time() - start_time
                        
                        logger.info(f"✅ Pipeline completed in {total_time:.2f}s")
                        
                        return {
                            'success': True,
                            'message_id': message_id,
                            'book_title': book_title,
                            'pipeline_result': result,
                            'total_time': total_time,
                            'pipeline_identical_to_manual': True
                        }
                    
                    await asyncio.sleep(0.5)
                
                # Timeout
                logger.warning(f"⏰ Pipeline execution timeout after {timeout}s")
                return {
                    'success': False,
                    'error': 'Pipeline execution timeout',
                    'message_id': message_id,
                    'book_title': book_title
                }
            else:
                return {
                    'success': True,
                    'message_id': message_id,
                    'book_title': book_title,
                    'message': 'Sent without waiting for result'
                }
                
        except Exception as e:
            logger.error(f"❌ Error sending book search: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'book_title': book_title
            }
    
    async def batch_book_search(self, book_titles: list, delay_between: float = 2.0) -> Dict[str, Any]:
        """Send multiple book searches with delays"""
        
        logger.info(f"📚 BATCH SEARCH: Processing {len(book_titles)} books")
        logger.info("=" * 60)
        
        results = []
        successful = 0
        
        for i, title in enumerate(book_titles, 1):
            logger.info(f"\n🔍 Book {i}/{len(book_titles)}: '{title}'")
            logger.info("-" * 40)
            
            result = await self.send_book_search_message(title)
            results.append(result)
            
            if result['success']:
                successful += 1
                if 'pipeline_result' in result:
                    pipeline_info = result['pipeline_result']
                    logger.info(f"📋 Pipeline stages: {pipeline_info.get('pipeline_stages', [])}")
                    logger.info(f"⏱️ Processing time: {pipeline_info.get('duration', 0):.2f}s")
            
            # Wait before next book (except for last one)
            if i < len(book_titles):
                logger.info(f"⏳ Waiting {delay_between}s before next book...")
                await asyncio.sleep(delay_between)
        
        success_rate = (successful / len(book_titles)) * 100
        
        summary = {
            'total_books': len(book_titles),
            'successful': successful,
            'failed': len(book_titles) - successful,
            'success_rate': success_rate,
            'results': results,
            'pipeline_identical_guarantee': True
        }
        
        logger.info(f"\n📊 BATCH SUMMARY:")
        logger.info(f"✅ Successful: {successful}/{len(book_titles)} ({success_rate:.1f}%)")
        logger.info("=" * 60)
        
        return summary
    
    async def interactive_mode(self):
        """Interactive mode for manual book search sending"""
        
        logger.info("🎯 Interactive Book Search Sender")
        logger.info("📚 Type book titles to send search requests")
        logger.info("🔧 Each message triggers IDENTICAL pipeline as manual user typing")
        logger.info("💡 Type 'quit' to exit, 'stats' for statistics")
        logger.info("-" * 60)
        
        if not self.router:
            await self.initialize_router()
        
        while True:
            try:
                user_input = input("\n📖 Enter book title: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("👋 Exiting interactive mode")
                    break
                
                if user_input.lower() == 'stats':
                    logger.info(f"📊 Statistics: {self.router.stats}")
                    continue
                
                if not user_input:
                    continue
                
                result = await self.send_book_search_message(user_input)
                
                if result['success']:
                    logger.info("🎉 Book search completed successfully!")
                else:
                    logger.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                logger.info("\n👋 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Interactive mode error: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.router and hasattr(self, 'processor_task'):
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass

async def main():
    """Main execution with command line arguments"""
    
    parser = argparse.ArgumentParser(
        description='Manual Book Search Sender - Aiogram-Telethon Unified Architecture'
    )
    parser.add_argument('book_title', nargs='?', help='Book title to search for')
    parser.add_argument('--batch', nargs='+', help='Send multiple book searches')
    parser.add_argument('--no-wait', action='store_true', help='Don\'t wait for pipeline result')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between batch requests (default: 2.0s)')
    
    args = parser.parse_args()
    
    sender = ManualBookSearchSender()
    
    try:
        if args.batch:
            # Batch mode
            logger.info(f"🔄 Batch mode: {len(args.batch)} books")
            result = await sender.batch_book_search(args.batch, args.delay)
            
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                logger.info(f"📊 Batch completed: {result['success_rate']:.1f}% success rate")
        
        elif args.book_title:
            # Single book mode
            result = await sender.send_book_search_message(args.book_title, not args.no_wait)
            
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                if result['success']:
                    logger.info(f"✅ Book search for '{args.book_title}' completed successfully!")
                else:
                    logger.error(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        else:
            # Interactive mode
            await sender.interactive_mode()
    
    finally:
        await sender.cleanup()

if __name__ == '__main__':
    try:
        # Critical: Single asyncio.run() call for proper event loop management
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Program interrupted")
    except Exception as e:
        logger.error(f"❌ Program error: {e}", exc_info=True)