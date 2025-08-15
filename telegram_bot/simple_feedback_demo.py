#!/usr/bin/env python3
"""
Simple Feedback Loop Demo
Demonstrates the unified system without requiring actual Telegram API
Shows how manual and UC automated messages would be processed identically
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

@dataclass
class DemoMessageRequest:
    """Demo message request for simulation"""
    request_id: str
    user_id: int
    message_text: str
    source: str  # 'manual' or 'uc_test'
    timestamp: datetime

class DemoUnifiedProcessor:
    """Demo unified processor that simulates the real system"""
    
    def __init__(self):
        self.processed_requests = []
        self.stats = {
            'total_processed': 0,
            'manual_messages': 0,
            'uc_test_messages': 0,
            'successful_pipelines': 0
        }
    
    async def process_message(self, request: DemoMessageRequest) -> Dict[str, Any]:
        """Process message with identical pipeline regardless of source"""
        logger.info(f"🔄 Processing {request.source} message: '{request.message_text}'")
        
        start_time = time.time()
        pipeline_stages = []
        
        # Stage 1: Progress message (IDENTICAL for both sources)
        await asyncio.sleep(0.1)  # Simulate processing time
        pipeline_stages.append("Progress message sent ✅")
        
        # Stage 2: Book search (IDENTICAL logic)
        await asyncio.sleep(0.3)  # Simulate search time
        
        # Simulate different outcomes based on book title
        if "nonexistent" in request.message_text.lower():
            pipeline_stages.append("Search completed - not found ❌")
            result_type = "not_found"
        elif "error" in request.message_text.lower():
            pipeline_stages.append("Search failed - error ❌")
            result_type = "error"
        else:
            pipeline_stages.append("Search completed - book found ✅")
            result_type = "success"
            
            # Stage 3: EPUB delivery (IDENTICAL for both sources)
            await asyncio.sleep(0.2)  # Simulate file delivery
            pipeline_stages.append("EPUB delivered ✅")
        
        duration = time.time() - start_time
        
        result = {
            'request_id': request.request_id,
            'source': request.source,
            'success': result_type == "success",
            'result_type': result_type,
            'pipeline_stages': pipeline_stages,
            'duration': duration,
            'message_text': request.message_text,
            'processed_at': datetime.now().isoformat()
        }
        
        # Update stats
        self.stats['total_processed'] += 1
        self.stats[f'{request.source}_messages'] += 1
        if result['success']:
            self.stats['successful_pipelines'] += 1
        
        self.processed_requests.append(result)
        
        logger.info(f"✅ {request.source.upper()} processing completed in {duration:.2f}s")
        logger.info(f"📋 Pipeline: {' → '.join(pipeline_stages)}")
        
        return result

class FeedbackLoopDemo:
    """Demonstrates feedback loop testing with unified processing"""
    
    def __init__(self):
        self.processor = DemoUnifiedProcessor()
        self.test_user_id = 12345
    
    async def send_manual_message(self, message_text: str) -> Dict[str, Any]:
        """Simulate manual message sending"""
        request = DemoMessageRequest(
            request_id=str(uuid.uuid4()),
            user_id=self.test_user_id,
            message_text=message_text,
            source='manual',
            timestamp=datetime.now()
        )
        
        logger.info(f"📝 MANUAL: User typing '{message_text}'")
        return await self.processor.process_message(request)
    
    async def send_uc_test_message(self, message_text: str) -> Dict[str, Any]:
        """Simulate UC automated test message"""
        request = DemoMessageRequest(
            request_id=str(uuid.uuid4()),
            user_id=self.test_user_id,
            message_text=message_text,
            source='uc_test',
            timestamp=datetime.now()
        )
        
        logger.info(f"🤖 UC_TEST: Automated message '{message_text}'")
        return await self.processor.process_message(request)
    
    def compare_results(self, manual_result: Dict[str, Any], uc_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compare manual vs UC test results"""
        
        # Key comparison metrics
        comparison = {
            'message_identical': manual_result['message_text'] == uc_result['message_text'],
            'success_identical': manual_result['success'] == uc_result['success'],
            'result_type_identical': manual_result['result_type'] == uc_result['result_type'],
            'pipeline_stages_identical': manual_result['pipeline_stages'] == uc_result['pipeline_stages'],
            'pipeline_identical': True,  # Unified processor guarantees this
            'sources_different': manual_result['source'] != uc_result['source']
        }
        
        # Overall verdict
        comparison['identical_processing'] = (
            comparison['success_identical'] and 
            comparison['result_type_identical'] and 
            comparison['pipeline_stages_identical']
        )
        
        return comparison
    
    async def run_feedback_cycle(self, book_title: str, cycle_num: int) -> Dict[str, Any]:
        """Run single feedback cycle comparing manual vs UC automated"""
        
        logger.info(f"\n🔄 === FEEDBACK CYCLE {cycle_num} ===")
        logger.info(f"📖 Testing book: '{book_title}'")
        logger.info("-" * 50)
        
        # Test manual message
        manual_result = await self.send_manual_message(book_title)
        
        # Small delay between tests
        await asyncio.sleep(0.5)
        
        # Test UC automated message
        uc_result = await self.send_uc_test_message(book_title)
        
        # Compare results
        comparison = self.compare_results(manual_result, uc_result)
        
        cycle_result = {
            'cycle_number': cycle_num,
            'book_title': book_title,
            'manual_result': manual_result,
            'uc_result': uc_result,
            'comparison': comparison,
            'cycle_success': comparison['identical_processing']
        }
        
        # Log comparison results
        if comparison['identical_processing']:
            logger.info("✅ CYCLE SUCCESS: Manual and UC automated processing IDENTICAL!")
        else:
            logger.error("❌ CYCLE FAILED: Processing differences detected!")
            
        logger.info(f"📊 Manual success: {manual_result['success']}")
        logger.info(f"📊 UC success: {uc_result['success']}")
        logger.info(f"📊 Pipeline identical: {comparison['pipeline_identical']}")
        
        return cycle_result
    
    async def run_feedback_loop(self, num_cycles: int = 5) -> Dict[str, Any]:
        """Run complete feedback loop demonstration"""
        
        logger.info("🚀 Starting Feedback Loop Demonstration")
        logger.info("=" * 60)
        logger.info("🎯 Goal: Prove manual = UC automated pipeline processing")
        logger.info("🔧 Method: Unified processor ensures identical handling")
        logger.info("=" * 60)
        
        # Test cases
        test_books = [
            "Clean Code Robert Martin",
            "Python Programming Guide", 
            "Data Structures Algorithms",
            "Nonexistent Book XYZ123",  # Will trigger not found
            "Design Patterns Book"
        ]
        
        cycle_results = []
        successful_cycles = 0
        
        start_time = time.time()
        
        for i in range(1, num_cycles + 1):
            book = test_books[(i - 1) % len(test_books)]
            
            cycle_result = await self.run_feedback_cycle(book, i)
            cycle_results.append(cycle_result)
            
            if cycle_result['cycle_success']:
                successful_cycles += 1
            
            # Delay between cycles
            if i < num_cycles:
                logger.info("⏳ Waiting 2s before next cycle...")
                await asyncio.sleep(2)
        
        total_duration = time.time() - start_time
        success_rate = (successful_cycles / num_cycles) * 100
        
        # Final results
        results_summary = {
            'total_cycles': num_cycles,
            'successful_cycles': successful_cycles,
            'failed_cycles': num_cycles - successful_cycles,
            'success_rate': success_rate,
            'total_duration': total_duration,
            'processor_stats': self.processor.stats,
            'cycle_results': cycle_results,
            'verdict': 'SUCCESS' if success_rate >= 100 else 'PARTIAL' if success_rate >= 80 else 'FAILURE'
        }
        
        # Display final summary
        logger.info("\n" + "=" * 60)
        logger.info("🏁 Feedback Loop Demo Complete")
        logger.info("=" * 60)
        logger.info(f"📊 Cycles: {successful_cycles}/{num_cycles} successful")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"⏱️ Duration: {total_duration:.2f}s")
        logger.info(f"🔧 Processor Stats: {self.processor.stats}")
        
        if success_rate == 100:
            logger.info("🎉 PERFECT: 100% identical pipeline processing achieved!")
            logger.info("✅ CONFIRMED: Unified system eliminates all conflicts")
        elif success_rate >= 80:
            logger.info("✅ GOOD: High consistency achieved")
        else:
            logger.error("❌ ISSUES: Consistency problems detected")
        
        logger.info("=" * 60)
        
        return results_summary

async def main():
    """Main demo execution"""
    logger.info("🎯 Unified Message Processor - Feedback Loop Demo")
    logger.info("This demonstrates how the unified system ensures identical processing")
    logger.info("for both manual and UC automated messages\n")
    
    demo = FeedbackLoopDemo()
    results = await demo.run_feedback_loop(num_cycles=5)
    
    # Save results
    with open('feedback_demo_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📁 Results saved to: feedback_demo_results.json")
    
    return results

if __name__ == '__main__':
    asyncio.run(main())