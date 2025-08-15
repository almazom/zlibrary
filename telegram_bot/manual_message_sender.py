#!/usr/bin/env python3
"""
Manual Message Sender - Simulates manual user input through unified API
This tool allows sending messages that will be processed IDENTICALLY to actual manual Telegram messages
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from unified_message_processor import UnifiedAPIClient
import argparse

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | MANUAL_SENDER | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('manual_sender.log')
    ]
)

logger = logging.getLogger(__name__)

class ManualMessageSender:
    """Sends messages through unified API that are processed identically to manual messages"""
    
    def __init__(self):
        self.user_id = int(os.getenv('CHAT_ID', '14835038'))
        self.api_client = UnifiedAPIClient()
        
    async def send_manual_message(self, message_text: str, wait_for_completion: bool = True) -> Dict[str, Any]:
        """Send a message that will be processed identically to manual Telegram input"""
        
        logger.info(f"📝 Sending manual-style message: '{message_text}'")
        
        try:
            # Submit message with 'manual' source (same as real manual messages)
            request_id = await self.api_client.submit_uc_message(
                user_id=self.user_id,
                message_text=message_text,
                metadata={
                    'simulated_manual': True,
                    'sent_via': 'manual_message_sender',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            if not request_id:
                return {
                    'success': False,
                    'error': 'Failed to submit message to unified API'
                }
            
            logger.info(f"✅ Message submitted - Request ID: {request_id}")
            
            if wait_for_completion:
                logger.info("⏳ Waiting for processing completion...")
                result = await self.api_client.wait_for_completion(request_id, timeout=120)
                
                if result.get('status') == 'completed':
                    logger.info("✅ Message processed successfully!")
                    logger.info(f"📋 Pipeline stages: {result.get('pipeline_log', [])}")
                elif result.get('status') == 'failed':
                    logger.error(f"❌ Message processing failed: {result.get('error')}")
                else:
                    logger.warning(f"⏰ Processing status: {result.get('status')}")
                
                return {
                    'success': result.get('status') == 'completed',
                    'request_id': request_id,
                    'processing_result': result,
                    'pipeline_identical_to_manual': True
                }
            else:
                return {
                    'success': True,
                    'request_id': request_id,
                    'message': 'Message submitted, not waiting for completion'
                }
                
        except Exception as e:
            logger.error(f"❌ Error sending manual message: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def interactive_mode(self):
        """Interactive mode for manual message sending"""
        logger.info("🎯 Manual Message Sender - Interactive Mode")
        logger.info("📝 Type book titles to search (type 'quit' to exit)")
        logger.info("-" * 50)
        
        while True:
            try:
                user_input = input("\n📖 Enter book title: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("👋 Exiting interactive mode")
                    break
                
                if not user_input:
                    continue
                
                logger.info(f"🚀 Processing: '{user_input}'")
                result = await self.send_manual_message(user_input)
                
                if result['success']:
                    logger.info("✅ Message sent and processed successfully!")
                else:
                    logger.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                logger.info("\n👋 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Interactive mode error: {e}")

async def main():
    """Main execution with command line arguments"""
    parser = argparse.ArgumentParser(description='Manual Message Sender - Send messages through unified API')
    parser.add_argument('message', nargs='?', help='Message to send (if not provided, starts interactive mode)')
    parser.add_argument('--no-wait', action='store_true', help='Don\'t wait for processing completion')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')
    
    args = parser.parse_args()
    
    sender = ManualMessageSender()
    
    if args.message:
        # Single message mode
        result = await sender.send_manual_message(args.message, not args.no_wait)
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result['success']:
                print(f"✅ Message '{args.message}' processed successfully!")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        # Interactive mode
        await sender.interactive_mode()

if __name__ == '__main__':
    # Check if unified processor is running
    try:
        import aiohttp
        
        async def check_api_health():
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get('http://localhost:8765/health') as response:
                        return response.status == 200
                except:
                    return False
        
        # Run health check first
        health_check = asyncio.run(check_api_health())
        
        if health_check:
            logger.info("✅ Unified API processor is running")
            asyncio.run(main())
        else:
            logger.error("❌ Unified message processor is not running!")
            logger.error("🔧 Please start it first:")
            logger.error("   python telegram_bot/unified_message_processor.py")
            
    except ImportError:
        logger.error("❌ Missing dependencies. Please install aiohttp")
    except Exception as e:
        logger.error(f"❌ Error: {e}")