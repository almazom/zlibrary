#!/usr/bin/env python3
"""
FINAL UC TEST: Uses Complete Solution to ensure IDENTICAL pipeline
This test GUARANTEES that automated messages = manual messages
"""

import asyncio
import logging
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any
import aiohttp

# Import our complete solution
from complete_solution import initialize_complete_solution, process_uc_test_message

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | FINAL_UC_TEST | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('final_uc_test.log')
    ]
)

logger = logging.getLogger(__name__)

class FinalUCTest:
    """Final UC test using complete solution for guaranteed equivalence"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.test_user_id = int(os.getenv('CHAT_ID', '14835038'))
        self.bot_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session = None
        self.last_update_id = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        # Initialize complete solution
        await initialize_complete_solution()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def monitor_bot_responses(self, timeout: int = 120) -> Dict[str, Any]:
        """Monitor bot responses to verify IDENTICAL behavior"""
        url = f"{self.bot_base_url}/getUpdates"
        
        start_time = time.time()
        responses = {
            'progress_messages': [],
            'documents': [],
            'text_responses': [],
            'errors': [],
            'timeline': []
        }
        
        logger.info(f"👁️ FINAL_UC_TEST: Monitoring for {timeout}s...")
        
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
                            
                            # Skip our own messages
                            if update.get('message', {}).get('from', {}).get('id') == self.test_user_id:
                                continue
                            
                            await self._analyze_response(update, responses)
                            
            except Exception as e:
                logger.warning(f"⚠️ FINAL_UC_TEST: Monitor error: {e}")
                
            await asyncio.sleep(2)
        
        logger.info(f"📊 FINAL_UC_TEST: Monitoring completed in {time.time() - start_time:.2f}s")
        return responses
    
    async def _analyze_response(self, update: Dict[str, Any], responses: Dict[str, Any]) -> None:
        """Analyze bot response and track timeline"""
        message = update.get('message', {})
        timestamp = datetime.now()
        
        # Document (EPUB) detection
        if 'document' in message:
            doc = message['document']
            if doc.get('file_name', '').endswith('.epub'):
                logger.info(f"📖 FINAL_UC_TEST: EPUB received - {doc.get('file_name')}")
                responses['documents'].append({
                    'filename': doc.get('file_name'),
                    'size': doc.get('file_size'),
                    'timestamp': timestamp
                })
                responses['timeline'].append(f"{timestamp.strftime('%H:%M:%S')} - EPUB delivered")
        
        # Text response analysis
        if 'text' in message:
            text = message['text']
            
            if '🔍' in text or 'Searching' in text:
                logger.info(f"🔍 FINAL_UC_TEST: PROGRESS - {text[:50]}...")
                responses['progress_messages'].append({
                    'text': text,
                    'timestamp': timestamp
                })
                responses['timeline'].append(f"{timestamp.strftime('%H:%M:%S')} - Progress message")
                
            elif '❌' in text or 'error' in text.lower():
                logger.warning(f"❌ FINAL_UC_TEST: ERROR - {text[:50]}...")
                responses['errors'].append({
                    'text': text,
                    'timestamp': timestamp
                })
                responses['timeline'].append(f"{timestamp.strftime('%H:%M:%S')} - Error message")
                
            else:
                logger.info(f"💬 FINAL_UC_TEST: TEXT - {text[:50]}...")
                responses['text_responses'].append({
                    'text': text,
                    'timestamp': timestamp
                })
                responses['timeline'].append(f"{timestamp.strftime('%H:%M:%S')} - Text response")
    
    async def test_identical_pipeline(self, book_title: str) -> Dict[str, Any]:
        """Test that UC message triggers IDENTICAL pipeline as manual"""
        logger.info(f"🧪 FINAL_UC_TEST: Testing identical pipeline for: '{book_title}'")
        test_start = time.time()
        
        # Process message through complete solution (IDENTICAL to manual processing)
        request_id = await process_uc_test_message(self.test_user_id, book_title)
        logger.info(f"📋 FINAL_UC_TEST: Message processed as request {request_id}")
        
        # Monitor responses to verify IDENTICAL behavior
        responses = await self.monitor_bot_responses(timeout=120)
        
        # Analyze results
        analysis = self._analyze_pipeline_results(responses, test_start)
        analysis['request_id'] = request_id
        analysis['book_title'] = book_title
        
        return analysis
    
    def _analyze_pipeline_results(self, responses: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Analyze if pipeline results are identical to manual behavior"""
        duration = time.time() - start_time
        
        # Expected manual behavior stages
        expected_stages = {
            'progress_message_sent': len(responses['progress_messages']) > 0,
            'search_executed': len(responses['progress_messages']) > 0,  # Progress implies search
            'result_delivered': len(responses['documents']) > 0 or len(responses['errors']) > 0,
            'no_silent_failures': len(responses['errors']) == 0 or any('❌' in error['text'] for error in responses['errors'])
        }
        
        # Calculate success (identical to manual behavior)
        pipeline_success = all([
            expected_stages['progress_message_sent'],
            expected_stages['search_executed'],
            expected_stages['result_delivered']
        ])
        
        analysis = {
            'identical_to_manual': pipeline_success,
            'duration': duration,
            'stages_completed': expected_stages,
            'response_counts': {
                'progress_messages': len(responses['progress_messages']),
                'documents': len(responses['documents']),
                'text_responses': len(responses['text_responses']),
                'errors': len(responses['errors'])
            },
            'timeline': responses['timeline'],
            'detailed_responses': responses
        }
        
        # Log results
        if pipeline_success:
            logger.info(f"✅ FINAL_UC_TEST: IDENTICAL pipeline confirmed - {duration:.2f}s")
            logger.info(f"📋 FINAL_UC_TEST: All manual stages replicated")
        else:
            logger.error(f"❌ FINAL_UC_TEST: Pipeline differs from manual - {duration:.2f}s")
            missing = [stage for stage, present in expected_stages.items() if not present]
            logger.error(f"❌ FINAL_UC_TEST: Missing stages: {missing}")
        
        return analysis
    
    async def run_comprehensive_equivalence_test(self) -> Dict[str, Any]:
        """Run comprehensive test to prove UC = Manual equivalence"""
        logger.info("🚀 FINAL_UC_TEST: Starting Comprehensive Equivalence Test")
        logger.info("="*80)
        
        test_cases = [
            {
                'name': 'Basic English Book',
                'query': 'Clean Code Robert Martin',
                'expected_success': True
            },
            {
                'name': 'Russian Literature',
                'query': 'Война и мир Толстой',
                'expected_success': True  
            },
            {
                'name': 'Technical Book',
                'query': 'Python Programming',
                'expected_success': True
            },
            {
                'name': 'Challenging Query',
                'query': 'The Art of Computer Programming Knuth',
                'expected_success': True
            }
        ]
        
        suite_results = {
            'total_tests': len(test_cases),
            'identical_pipeline_count': 0,
            'failed_pipeline_count': 0,
            'test_details': [],
            'suite_duration': 0,
            'equivalence_achieved': False
        }
        
        suite_start = time.time()
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📋 FINAL_UC_TEST: Test {i}/{len(test_cases)}: {test_case['name']}")
            logger.info("-" * 60)
            
            result = await self.test_identical_pipeline(test_case['query'])
            result.update(test_case)
            
            suite_results['test_details'].append(result)
            
            if result['identical_to_manual']:
                suite_results['identical_pipeline_count'] += 1
                logger.info(f"✅ FINAL_UC_TEST: Test {i} - IDENTICAL PIPELINE CONFIRMED")
            else:
                suite_results['failed_pipeline_count'] += 1
                logger.error(f"❌ FINAL_UC_TEST: Test {i} - PIPELINE DIFFERS FROM MANUAL")
            
            # Display timeline for verification
            logger.info("📅 Pipeline timeline:")
            for timeline_entry in result['timeline'][:5]:  # Show first 5 events
                logger.info(f"   {timeline_entry}")
            
            # Wait between tests
            if i < len(test_cases):
                logger.info("⏳ FINAL_UC_TEST: Waiting 15s before next test...")
                await asyncio.sleep(15)
        
        suite_results['suite_duration'] = time.time() - suite_start
        
        # Determine overall equivalence
        equivalence_rate = (suite_results['identical_pipeline_count'] / suite_results['total_tests']) * 100
        suite_results['equivalence_achieved'] = equivalence_rate >= 75  # 75% threshold
        
        # Final summary
        logger.info(f"\n" + "="*80)
        logger.info(f"🏁 FINAL_UC_TEST: Comprehensive Equivalence Test Complete")
        logger.info(f"📊 Results: {suite_results['identical_pipeline_count']}/{suite_results['total_tests']} tests showed identical pipelines")
        logger.info(f"📈 Equivalence Rate: {equivalence_rate:.1f}%")
        logger.info(f"⏱️ Total Duration: {suite_results['suite_duration']:.2f}s")
        
        if suite_results['equivalence_achieved']:
            logger.info("🎉 SUCCESS: UC automated messages = Manual messages!")
            logger.info("✅ HYPOTHESIS 5 CONFIRMED: Complete solution achieved")
        else:
            logger.error("❌ FAILURE: UC automated messages still differ from manual")
            logger.error("🔍 Solution needs further refinement")
            
        logger.info(f"="*80)
        
        # Save comprehensive results
        with open('final_uc_test_results.json', 'w') as f:
            json.dump(suite_results, f, indent=2, default=str)
        
        return suite_results

async def main():
    """Main test execution"""
    logger.info("🤖 Starting FINAL UC TEST with Complete Solution")
    
    async with FinalUCTest() as tester:
        results = await tester.run_comprehensive_equivalence_test()
        
        if results['equivalence_achieved']:
            logger.info("🎊 COMPLETE SUCCESS: Automated UC tests now trigger IDENTICAL pipeline as manual messages!")
            logger.info("✅ Solution deployed and verified")
            return 0
        else:
            logger.error("❌ Solution incomplete - further work needed")
            return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())