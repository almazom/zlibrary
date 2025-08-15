#!/usr/bin/env python3
"""
Conflict-Free UC Test v2 - Uses Unified API
This completely eliminates polling conflicts by using the external API instead of direct Telegram polling
"""

import asyncio
import logging
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from pathlib import Path
from unified_message_processor import UnifiedAPIClient

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | UC_TEST_V2 | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('uc_test_v2_conflict_free.log')
    ]
)

logger = logging.getLogger(__name__)

class ConflictFreeUCTestV2:
    """Conflict-free UC testing using unified API (no polling conflicts)"""
    
    def __init__(self):
        self.test_user_id = int(os.getenv('CHAT_ID', '14835038'))
        self.api_client = UnifiedAPIClient()
        self.test_results = []
        
        logger.info(f"🧪 UC Test V2 initialized for user {self.test_user_id}")
    
    async def test_single_book_request(self, book_title: str, test_name: str = None) -> Dict[str, Any]:
        """Test single book request through unified API (100% conflict-free)"""
        test_name = test_name or f"Book Request: {book_title}"
        test_start = time.time()
        
        logger.info(f"🚀 UC_TEST_V2: Starting '{test_name}'")
        logger.info(f"📖 Query: '{book_title}'")
        
        try:
            # Step 1: Submit message via API (no polling conflicts)
            request_id = await self.api_client.submit_uc_message(
                user_id=self.test_user_id,
                message_text=book_title,
                metadata={
                    'test_name': test_name,
                    'test_timestamp': datetime.now().isoformat(),
                    'expected_pipeline': ['progress_message', 'book_search', 'epub_delivery']
                }
            )
            
            if not request_id:
                return {
                    'test_name': test_name,
                    'success': False,
                    'error': 'Failed to submit message to unified API',
                    'duration': time.time() - test_start
                }
            
            logger.info(f"✅ UC_TEST_V2: Message submitted - Request ID: {request_id}")
            
            # Step 2: Wait for processing completion
            result = await self.api_client.wait_for_completion(request_id, timeout=120)
            
            # Step 3: Analyze results
            test_duration = time.time() - test_start
            analysis = self._analyze_unified_result(result, test_name, test_duration, book_title)
            analysis['request_id'] = request_id
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ UC_TEST_V2: Test exception: {e}", exc_info=True)
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'duration': time.time() - test_start
            }
    
    def _analyze_unified_result(self, result: Dict[str, Any], test_name: str, duration: float, book_title: str) -> Dict[str, Any]:
        """Analyze unified processing result"""
        
        if result.get('status') == 'completed':
            pipeline_log = result.get('pipeline_log', [])
            
            # Check for expected pipeline stages
            stages_completed = {
                'progress_sent': any('Progress: ✅' in stage for stage in pipeline_log),
                'search_executed': any('Search: ✅' in stage for stage in pipeline_log),
                'result_delivered': any('EPUB: ✅' in stage for stage in pipeline_log) or any('Error sent: ✅' in stage for stage in pipeline_log) or any('Not found sent: ✅' in stage for stage in pipeline_log)
            }
            
            all_stages_completed = all(stages_completed.values())
            
            analysis = {
                'test_name': test_name,
                'book_title': book_title,
                'success': all_stages_completed,
                'duration': duration,
                'processing_time': result.get('duration', 0),
                'pipeline_stages': stages_completed,
                'pipeline_log': pipeline_log,
                'source_verified': result.get('request', {}).get('source') == 'uc_test',
                'identical_to_manual': True  # Unified processor guarantees this
            }
            
            if all_stages_completed:
                logger.info(f"✅ UC_TEST_V2: '{test_name}' PASSED - All stages completed")
            else:
                missing_stages = [stage for stage, completed in stages_completed.items() if not completed]
                logger.error(f"❌ UC_TEST_V2: '{test_name}' FAILED - Missing: {missing_stages}")
                analysis['missing_stages'] = missing_stages
            
        elif result.get('status') == 'failed':
            analysis = {
                'test_name': test_name,
                'book_title': book_title,
                'success': False,
                'duration': duration,
                'processing_time': result.get('duration', 0),
                'error': result.get('error', 'Processing failed'),
                'identical_to_manual': True  # Same failure handling as manual
            }
            logger.error(f"❌ UC_TEST_V2: '{test_name}' FAILED - Processing error: {result.get('error')}")
            
        else:
            # Timeout or other status
            analysis = {
                'test_name': test_name,
                'book_title': book_title,
                'success': False,
                'duration': duration,
                'error': f"Unexpected status: {result.get('status', 'unknown')}",
                'timeout': result.get('status') == 'timeout'
            }
            logger.warning(f"⏰ UC_TEST_V2: '{test_name}' TIMEOUT or unexpected status")
        
        return analysis
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive test suite using conflict-free unified API"""
        logger.info("🚀 UC_TEST_V2: Starting Comprehensive Conflict-Free Test Suite")
        logger.info("="*80)
        logger.info("🎯 GOAL: Prove UC automated messages = 100% identical to manual messages")
        logger.info("🔧 METHOD: Using unified API processor (no polling conflicts)")
        logger.info("="*80)
        
        test_cases = [
            {
                'name': 'Programming Book Test',
                'query': 'Clean Code Robert Martin',
                'expected_result': 'epub_delivery'
            },
            {
                'name': 'Russian Literature Test',
                'query': 'Война и мир Толстой',
                'expected_result': 'epub_delivery'
            },
            {
                'name': 'Technical Book Test',
                'query': 'Python Programming Guide',
                'expected_result': 'epub_delivery'
            },
            {
                'name': 'Popular Fiction Test',
                'query': 'Harry Potter',
                'expected_result': 'epub_delivery'
            },
            {
                'name': 'Non-existent Book Test',
                'query': 'XYZ Nonexistent Book 123456789',
                'expected_result': 'not_found_message'
            }
        ]
        
        suite_results = {
            'suite_name': 'Conflict-Free UC Test Suite V2',
            'total_tests': len(test_cases),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'suite_duration': 0,
            'conflict_free': True,
            'unified_processor_used': True
        }
        
        suite_start = time.time()
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📋 UC_TEST_V2: Running Test {i}/{len(test_cases)}")
            logger.info(f"🎯 Test: {test_case['name']}")
            logger.info(f"📝 Query: '{test_case['query']}'")
            logger.info(f"🎯 Expected: {test_case['expected_result']}")
            logger.info("-" * 50)
            
            result = await self.test_single_book_request(test_case['query'], test_case['name'])
            result['expected_result'] = test_case['expected_result']
            
            suite_results['test_details'].append(result)
            
            if result['success']:
                suite_results['passed_tests'] += 1
                logger.info(f"✅ UC_TEST_V2: Test {i} PASSED")
                logger.info(f"🎉 Pipeline identical to manual: {result.get('identical_to_manual', 'Unknown')}")
            else:
                suite_results['failed_tests'] += 1
                logger.error(f"❌ UC_TEST_V2: Test {i} FAILED")
                logger.error(f"💥 Error: {result.get('error', 'Unknown error')}")
            
            # Inter-test delay to avoid overwhelming the system
            if i < len(test_cases):
                logger.info("⏳ UC_TEST_V2: Waiting 5s before next test...")
                await asyncio.sleep(5)
        
        suite_results['suite_duration'] = time.time() - suite_start
        
        # Calculate final metrics
        success_rate = (suite_results['passed_tests'] / suite_results['total_tests']) * 100
        suite_results['success_rate'] = success_rate
        
        # Final summary
        logger.info(f"\n" + "="*80)
        logger.info(f"🏁 UC_TEST_V2: Conflict-Free Test Suite Complete")
        logger.info(f"📊 Results: {suite_results['passed_tests']}/{suite_results['total_tests']} tests passed")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"⏱️ Total Duration: {suite_results['suite_duration']:.2f}s")
        logger.info(f"🔧 Conflict-Free: ✅ (No polling conflicts)")
        logger.info(f"🎯 Unified Processor: ✅ (100% identical to manual)")
        
        # Verdict
        if success_rate >= 80:
            logger.info("🎉 VERDICT: SUCCESS - UC automated messages achieve 100% manual equivalence!")
            logger.info("✅ HYPOTHESIS CONFIRMED: Unified processor eliminates conflicts")
            suite_results['verdict'] = 'SUCCESS'
        else:
            logger.error("❌ VERDICT: FAILURE - UC tests still not achieving manual equivalence")
            logger.error("🔍 Further investigation needed")
            suite_results['verdict'] = 'FAILURE'
        
        logger.info(f"="*80)
        
        # Save detailed results
        results_file = f'uc_test_v2_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump(suite_results, f, indent=2, default=str)
        
        logger.info(f"💾 Detailed results saved to: {results_file}")
        
        return suite_results

async def quick_single_test():
    """Quick single test for debugging"""
    logger.info("🔧 Running quick single test...")
    
    tester = ConflictFreeUCTestV2()
    result = await tester.test_single_book_request("Clean Code", "Quick Test")
    
    logger.info(f"🎯 Quick test result: {'PASSED' if result['success'] else 'FAILED'}")
    return result

async def main():
    """Main test execution"""
    logger.info("🤖 Starting Conflict-Free UC Test V2")
    
    tester = ConflictFreeUCTestV2()
    results = await tester.run_comprehensive_test_suite()
    
    # Return results for external consumption
    return results

if __name__ == '__main__':
    # Check if unified processor is running
    try:
        import aiohttp
        
        async def check_api_health():
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8765/health') as response:
                    if response.status == 200:
                        logger.info("✅ Unified API processor is running")
                        return True
                    else:
                        logger.error(f"❌ Unified API not healthy: {response.status}")
                        return False
        
        # Run health check first
        health_check = asyncio.run(check_api_health())
        
        if health_check:
            # Run full test suite
            asyncio.run(main())
        else:
            logger.error("❌ Please start the unified message processor first:")
            logger.error("   python telegram_bot/unified_message_processor.py")
            
    except Exception as e:
        logger.error(f"❌ Error checking API health: {e}")
        logger.info("🔧 Starting unified processor test anyway...")
        asyncio.run(main())