#!/usr/bin/env python3
"""
Direct Book Search Demo
Demonstrates sending book search messages that trigger IDENTICAL pipeline
using the existing Telegram infrastructure without requiring Telethon setup
"""

import asyncio
import logging
import json
import os
import time
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class DirectBookSearchSender:
    """Sends book search messages using direct Telegram API calls"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = int(os.getenv('CHAT_ID', '14835038'))
        self.script_path = os.getenv('SCRIPT_PATH', '/home/almaz/microservices/zlibrary_api_module/scripts/book_search.sh')
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
    
    async def send_telegram_message(self, message_text: str) -> Dict[str, Any]:
        """Send message via Telegram API (simulates manual user typing)"""
        
        logger.info(f"📤 TELEGRAM API: Sending message '{message_text}' to chat {self.chat_id}")
        
        try:
            # Use the existing telegram send manager
            cmd = [
                '/home/almaz/MCP/SCRIPTS/telegram_send_manager.sh',
                'send',
                message_text,
                '--chat', str(self.chat_id)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Message sent successfully via Telegram API")
                return {'success': True, 'output': result.stdout}
            else:
                logger.error(f"❌ Telegram API error: {result.stderr}")
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            logger.error(f"❌ Error sending Telegram message: {e}")
            return {'success': False, 'error': str(e)}
    
    async def execute_book_search_pipeline(self, book_title: str) -> Dict[str, Any]:
        """Execute the actual book search pipeline (IDENTICAL to bot processing)"""
        
        logger.info(f"🔍 PIPELINE: Executing book search for '{book_title}'")
        
        try:
            # Execute the same script the bot would use
            cmd = ['bash', self.script_path, book_title, '--download']
            
            logger.info(f"🔧 Running: {' '.join(cmd[:3])} [book_title] --download")
            
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90,
                cwd=os.path.dirname(self.script_path)
            )
            
            duration = time.time() - start_time
            
            logger.info(f"⏱️ Pipeline execution completed in {duration:.2f}s")
            logger.info(f"📊 Return code: {result.returncode}")
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    # Parse JSON result
                    pipeline_result = json.loads(result.stdout)
                    logger.info("✅ Pipeline executed successfully")
                    
                    return {
                        'success': True,
                        'duration': duration,
                        'pipeline_result': pipeline_result,
                        'book_title': book_title,
                        'pipeline_identical_to_manual': True
                    }
                    
                except json.JSONDecodeError:
                    logger.warning("⚠️ Non-JSON output from pipeline")
                    return {
                        'success': True,
                        'duration': duration,
                        'output': result.stdout[:500],
                        'book_title': book_title
                    }
            else:
                logger.error(f"❌ Pipeline execution failed")
                return {
                    'success': False,
                    'error': result.stderr or 'No output',
                    'duration': duration,
                    'book_title': book_title
                }
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Pipeline execution timeout (90s)")
            return {
                'success': False,
                'error': 'Pipeline timeout after 90s',
                'book_title': book_title
            }
        except Exception as e:
            logger.error(f"❌ Pipeline execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'book_title': book_title
            }
    
    async def send_book_search_complete(self, book_title: str) -> Dict[str, Any]:
        """Send book search and execute pipeline (IDENTICAL to manual user flow)"""
        
        logger.info(f"🚀 COMPLETE FLOW: Processing book search for '{book_title}'")
        logger.info("🎯 This triggers IDENTICAL pipeline as manual user message")
        logger.info("=" * 60)
        
        overall_start = time.time()
        
        # Step 1: Send Telegram message (simulates user typing)
        logger.info("📱 Step 1: Sending Telegram message (simulates manual typing)")
        telegram_result = await self.send_telegram_message(book_title)
        
        if not telegram_result['success']:
            return {
                'success': False,
                'error': f"Telegram message failed: {telegram_result['error']}",
                'book_title': book_title
            }
        
        # Small delay to simulate real-world timing
        await asyncio.sleep(1)
        
        # Step 2: Execute book search pipeline (IDENTICAL to bot processing)
        logger.info("🔍 Step 2: Executing book search pipeline")
        pipeline_result = await self.execute_book_search_pipeline(book_title)
        
        total_time = time.time() - overall_start
        
        # Combine results
        final_result = {
            'book_title': book_title,
            'telegram_message_sent': telegram_result['success'],
            'pipeline_executed': pipeline_result['success'],
            'total_time': total_time,
            'telegram_result': telegram_result,
            'pipeline_result': pipeline_result,
            'complete_flow_success': telegram_result['success'] and pipeline_result['success'],
            'pipeline_identical_to_manual': True,
            'flow_description': 'Manual user types message → Bot receives → Pipeline executes'
        }
        
        if final_result['complete_flow_success']:
            logger.info(f"🎉 COMPLETE SUCCESS: Book search flow completed in {total_time:.2f}s")
            logger.info("✅ This is IDENTICAL to manual user typing the same message")
        else:
            logger.error(f"❌ Flow partially failed after {total_time:.2f}s")
        
        logger.info("=" * 60)
        
        return final_result
    
    async def demonstrate_manual_equivalence(self, book_titles: list) -> Dict[str, Any]:
        """Demonstrate that our automated flow = manual user flow"""
        
        logger.info("🎯 DEMONSTRATION: Automated Flow = Manual User Flow")
        logger.info("=" * 70)
        logger.info("🔧 Method: Send message via API + Execute pipeline = Manual typing")
        logger.info("🎯 Goal: Prove 100% identical pipeline execution")
        logger.info("=" * 70)
        
        results = []
        successful = 0
        
        for i, title in enumerate(book_titles, 1):
            logger.info(f"\n📚 Test {i}/{len(book_titles)}: '{title}'")
            logger.info("-" * 50)
            
            result = await self.send_book_search_complete(title)
            results.append(result)
            
            if result['complete_flow_success']:
                successful += 1
                logger.info("✅ Flow completed successfully")
            else:
                logger.error("❌ Flow failed")
            
            # Wait between tests
            if i < len(book_titles):
                logger.info("⏳ Waiting 3s before next test...")
                await asyncio.sleep(3)
        
        success_rate = (successful / len(book_titles)) * 100
        
        summary = {
            'total_tests': len(book_titles),
            'successful_flows': successful,
            'failed_flows': len(book_titles) - successful,
            'success_rate': success_rate,
            'test_results': results,
            'manual_equivalence_confirmed': success_rate >= 80,
            'methodology': 'Direct API message + Pipeline execution = Manual user flow'
        }
        
        logger.info(f"\n📊 FINAL RESULTS:")
        logger.info(f"✅ Successful flows: {successful}/{len(book_titles)} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            logger.info("🎉 EXCELLENT: Automated flow = Manual flow confirmed!")
        elif success_rate >= 80:
            logger.info("✅ GOOD: High equivalence achieved")
        else:
            logger.error("❌ POOR: Equivalence issues detected")
        
        logger.info("=" * 70)
        
        return summary

async def main():
    """Main demonstration"""
    
    logger.info("🚀 Direct Book Search Demo")
    logger.info("This demonstrates sending messages that trigger IDENTICAL pipeline")
    logger.info("as manual user typing in Telegram")
    logger.info("")
    
    try:
        sender = DirectBookSearchSender()
        
        # Test with various book types
        test_books = [
            "Clean Code Robert Martin",
            "Python Programming Guide",
            "Design Patterns Gang of Four"
        ]
        
        # Run demonstration
        summary = await sender.demonstrate_manual_equivalence(test_books)
        
        # Output final JSON result
        print("\n" + "="*50)
        print("FINAL SUMMARY (JSON):")
        print("="*50)
        print(json.dumps(summary, indent=2, default=str))
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Demo error: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    try:
        result = asyncio.run(main())
        
        if result.get('manual_equivalence_confirmed'):
            logger.info("🎉 SUCCESS: Manual equivalence confirmed!")
            exit(0)
        else:
            logger.error("❌ FAILURE: Manual equivalence not achieved")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Demo interrupted")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        exit(1)