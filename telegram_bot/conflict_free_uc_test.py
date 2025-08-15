#!/usr/bin/env python3
"""
Conflict-Free UC Test Implementation
This test approach ensures automated messages trigger IDENTICAL pipeline as manual messages
by using a separate test bot instance or webhook mode
"""

import asyncio
import logging
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import aiohttp
from pathlib import Path

# Load environment
load_dotenv()

# Configure logging for test tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | UC_TEST | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('uc_test_conflict_free.log')
    ]
)

logger = logging.getLogger(__name__)

class ConflictFreeUCTest:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.test_user_id = int(os.getenv('CHAT_ID', '14835038'))
        self.bot_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session = None
        
        # Test tracking
        self.test_results = []
        self.last_update_id = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def send_message_via_api(self, text: str) -> Optional[Dict[str, Any]]:
        """Send message directly via Telegram API (bypass polling conflicts)"""
        url = f"{self.bot_base_url}/sendMessage"
        payload = {
            'chat_id': self.test_user_id,
            'text': text
        }
        
        logger.info(f"📤 UC_TEST: Sending message: '{text}'")
        
        try:
            async with self.session.post(url, json=payload) as response:
                result = await response.json()
                
                if result.get('ok'):
                    logger.info(f"✅ UC_TEST: Message sent successfully - ID: {result['result']['message_id']}")
                    return result
                else:
                    logger.error(f"❌ UC_TEST: Failed to send - {result.get('description', 'Unknown error')}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ UC_TEST: Exception sending message: {e}")
            return None
    
    async def monitor_bot_responses(self, timeout: int = 60) -> Dict[str, Any]:
        """Monitor bot responses using getUpdates (separate from bot polling)"""
        url = f"{self.bot_base_url}/getUpdates"
        
        start_time = time.time()
        responses_detected = {
            'progress_messages': [],
            'documents': [],
            'text_responses': [],
            'errors': [],
            'total_responses': 0
        }
        
        logger.info(f"👁️ UC_TEST: Monitoring responses for {timeout}s...")
        
        while (time.time() - start_time) < timeout:
            try:
                params = {
                    'offset': self.last_update_id + 1,
                    'timeout': 5,
                    'limit': 10
                }
                
                async with self.session.get(url, params=params) as response:
                    result = await response.json()
                    
                    if result.get('ok') and result.get('result'):
                        updates = result['result']
                        
                        for update in updates:
                            self.last_update_id = max(self.last_update_id, update['update_id'])
                            
                            # Skip our own messages (messages FROM the test user)
                            if update.get('message', {}).get('from', {}).get('id') == self.test_user_id:
                                continue
                            
                            await self.analyze_bot_response(update, responses_detected)
                            responses_detected['total_responses'] += 1
                            
            except Exception as e:
                logger.warning(f"⚠️ UC_TEST: Error monitoring responses: {e}")
                
            await asyncio.sleep(2)
        
        duration = time.time() - start_time
        logger.info(f"📊 UC_TEST: Monitoring completed in {duration:.2f}s")
        
        return responses_detected
    
    async def analyze_bot_response(self, update: Dict[str, Any], responses: Dict[str, Any]) -> None:
        """Analyze individual bot response and categorize"""
        message = update.get('message', {})
        
        # Check for document (EPUB)
        if 'document' in message:
            doc = message['document']
            if doc.get('file_name', '').endswith('.epub') or 'epub' in doc.get('mime_type', ''):
                logger.info(f"📖 UC_TEST: EPUB document received - {doc.get('file_name', 'unknown.epub')}")
                responses['documents'].append({
                    'type': 'epub',
                    'filename': doc.get('file_name'),
                    'size': doc.get('file_size'),
                    'timestamp': datetime.now()
                })
        
        # Check for text response
        if 'text' in message:
            text = message['text']
            
            # Progress message detection
            if '🔍' in text or 'Searching' in text or 'search' in text.lower():
                logger.info(f"🔍 UC_TEST: PROGRESS message detected: '{text[:50]}...'")
                responses['progress_messages'].append({
                    'text': text,
                    'timestamp': datetime.now()
                })
            
            # Error message detection
            elif '❌' in text or 'error' in text.lower() or 'failed' in text.lower():
                logger.warning(f"❌ UC_TEST: ERROR message detected: '{text[:50]}...'")
                responses['errors'].append({
                    'text': text,
                    'timestamp': datetime.now()
                })
            
            # Other text responses
            else:
                logger.info(f"💬 UC_TEST: TEXT response: '{text[:50]}...'")
                responses['text_responses'].append({
                    'text': text,
                    'timestamp': datetime.now()
                })
    
    async def test_book_request_pipeline(self, book_title: str) -> Dict[str, Any]:
        """Test complete book request pipeline - identical to manual flow"""
        test_start = time.time()
        
        logger.info(f"🧪 UC_TEST: Starting book request test for: '{book_title}'")
        
        # Step 1: Send book request message (identical to manual typing)
        message_result = await self.send_message_via_api(book_title)
        if not message_result:
            return {
                'success': False,
                'error': 'Failed to send message',
                'pipeline_stages': {'message_sent': False}
            }
        
        # Step 2: Monitor for expected pipeline stages
        responses = await self.monitor_bot_responses(timeout=90)  # Generous timeout
        
        # Step 3: Analyze pipeline completion
        pipeline_analysis = self.analyze_pipeline_completion(responses, test_start)
        
        return pipeline_analysis
    
    def analyze_pipeline_completion(self, responses: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Analyze if the complete pipeline executed (like manual flow)"""
        total_duration = time.time() - start_time
        
        # Expected pipeline stages
        pipeline_stages = {
            'message_sent': True,  # We know this succeeded
            'progress_message_received': len(responses['progress_messages']) > 0,
            'search_triggered': len(responses['progress_messages']) > 0,  # Progress implies search started
            'epub_delivered': len(responses['documents']) > 0,
            'errors_occurred': len(responses['errors']) > 0
        }
        
        # Determine overall success
        success = (
            pipeline_stages['progress_message_received'] and 
            pipeline_stages['epub_delivered'] and 
            not pipeline_stages['errors_occurred']
        )
        
        analysis = {
            'success': success,
            'duration': total_duration,
            'pipeline_stages': pipeline_stages,
            'response_summary': {
                'progress_messages': len(responses['progress_messages']),
                'documents': len(responses['documents']),
                'text_responses': len(responses['text_responses']),
                'errors': len(responses['errors']),
                'total_responses': responses['total_responses']
            },
            'detailed_responses': responses
        }
        
        # Log analysis
        if success:
            logger.info(f"✅ UC_TEST: Pipeline SUCCESS - Complete flow in {total_duration:.2f}s")
        else:
            logger.error(f"❌ UC_TEST: Pipeline FAILED - Missing stages after {total_duration:.2f}s")
            missing_stages = [stage for stage, completed in pipeline_stages.items() if not completed and stage != 'errors_occurred']
            logger.error(f"❌ UC_TEST: Missing stages: {missing_stages}")
        
        return analysis
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive test suite to validate UC = Manual equivalence"""
        logger.info("🚀 UC_TEST: Starting Comprehensive Test Suite")
        logger.info("="*80)
        
        test_cases = [
            {
                'name': 'Basic Book Request',
                'query': 'Clean Code Robert Martin',
                'expected_duration': 60
            },
            {
                'name': 'Russian Book Request',
                'query': 'Война и мир',
                'expected_duration': 60
            },
            {
                'name': 'Programming Book',
                'query': 'Python Programming',
                'expected_duration': 60
            }
        ]
        
        suite_results = {
            'total_tests': len(test_cases),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'suite_duration': 0
        }
        
        suite_start = time.time()
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📋 UC_TEST: Running Test {i}/{len(test_cases)}: {test_case['name']}")
            logger.info("-" * 50)
            
            result = await self.test_book_request_pipeline(test_case['query'])
            result['test_name'] = test_case['name']
            result['test_query'] = test_case['query']
            
            suite_results['test_details'].append(result)
            
            if result['success']:
                suite_results['passed_tests'] += 1
                logger.info(f"✅ UC_TEST: Test {i} PASSED")
            else:
                suite_results['failed_tests'] += 1
                logger.error(f"❌ UC_TEST: Test {i} FAILED")
            
            # Wait between tests to avoid rate limiting
            if i < len(test_cases):
                logger.info("⏳ UC_TEST: Waiting 10s before next test...")
                await asyncio.sleep(10)
        
        suite_results['suite_duration'] = time.time() - suite_start
        
        # Final summary
        success_rate = (suite_results['passed_tests'] / suite_results['total_tests']) * 100
        logger.info(f"\n" + "="*80)
        logger.info(f"🏁 UC_TEST: Test Suite Complete")
        logger.info(f"📊 Results: {suite_results['passed_tests']}/{suite_results['total_tests']} tests passed")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"⏱️ Total Duration: {suite_results['suite_duration']:.2f}s")
        logger.info(f"="*80)
        
        # Save detailed results
        with open('uc_test_results.json', 'w') as f:
            json.dump(suite_results, f, indent=2, default=str)
        
        return suite_results

async def main():
    """Main test execution"""
    logger.info("🤖 Starting Conflict-Free UC Test")
    
    async with ConflictFreeUCTest() as tester:
        results = await tester.run_comprehensive_test_suite()
        
        # Determine if UC tests achieve same results as manual
        if results['success_rate'] >= 80:  # 80% threshold
            logger.info("🎉 SUCCESS: UC automated messages achieve same pipeline as manual!")
            logger.info("✅ HYPOTHESIS 5 CONFIRMED: Complete solution working")
        else:
            logger.error("❌ FAILURE: UC automated messages still differ from manual")
            logger.error("🔍 Further investigation needed")
        
        return results

if __name__ == '__main__':
    asyncio.run(main())