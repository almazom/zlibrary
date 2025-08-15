#!/usr/bin/env python3
"""
Critical test to prove the progress message timing issue
"""

import asyncio
import logging
from datetime import datetime

# Configure logging to match the bot exactly
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

logger = logging.getLogger(__name__)

async def simulate_bot_process_request():
    """Simulate the exact bot sequence to identify where progress message should appear"""
    
    print("=" * 80)
    print("HYPOTHESIS 3 TEST: Simulating bot sequence")
    print("=" * 80)
    
    # Step 1: Message received (this happens)
    timestamp1 = datetime.now()
    logger.info("🚀 Processing book request from user 14835038: 'The Pragmatic Programmer'")
    
    # Step 2: Progress message should be sent HERE (line 100 in bot code)
    # await message.answer("🔍 Searching for book...")
    timestamp2 = datetime.now()
    print(f"🔍 CRITICAL POINT: Progress message should be sent here")
    print(f"⏱️  Time since processing started: {(timestamp2-timestamp1).total_seconds()*1000:.1f}ms")
    
    # Simulate some delay before the search log
    await asyncio.sleep(0.13)  # 130ms gap from real logs
    
    # Step 3: Search begins (this happens and is logged)
    timestamp3 = datetime.now()
    logger.info("🔍 Searching for book: 'The Pragmatic Programmer'")
    print(f"⏱️  Gap between processing and search log: {(timestamp3-timestamp1).total_seconds()*1000:.1f}ms")
    
    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("1. ✅ Bot processes request - LOGGED")
    print("2. ❓ Progress message should be sent - NOT FOUND IN LOGS")
    print("3. ✅ Search begins - LOGGED")
    print("4. 🔍 The 130ms gap is where progress message.answer() should execute")
    print("=" * 80)

async def main():
    await simulate_bot_process_request()

if __name__ == '__main__':
    asyncio.run(main())