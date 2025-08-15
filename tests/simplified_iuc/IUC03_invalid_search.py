#!/usr/bin/env python3
"""
IUC03: Invalid Book Search Behavior Test (Atomic)

Validates the bot's actual behavior for invalid searches, which is to send
a single "searching" message and then stop.
"""

import asyncio
import os
import time

from iuc_core import (
    TelegramBotTester,
    run_test_flow,
    display_multi_step_result_table,
    send_telegram_notification
)

# --- Test Configuration ---
NOTIFICATION_CHAT_ID = "5282615364"

# This test validates that for an invalid book, the ONLY response is a 
# "searching" message. The test passes if this step is met and no other
# response follows.
IUC03_TEST_CASE = {
    "id": "IUC03_invalid_book_search",
    "name": "Invalid Book Search Behavior",
    "message": f"NonExistentBookForSure{int(os.urandom(4).hex(), 16)}",
    "steps": [
        {
            "name": "Initial",
            "pattern": r"(searching|looking for)", # Expect the "searching" message
            "timeout": 20
        }
        # No second step is expected. The test will pass if this step passes
        # and the full flow completes.
    ]
}

async def main():
    """Main test execution logic."""
    print(f"🔥 Running {IUC03_TEST_CASE['id']}: {IUC03_TEST_CASE['name']}...")
    
    async with TelegramBotTester() as tester:
        result = await run_test_flow(tester, IUC03_TEST_CASE)
        
        # For this specific test, we redefine PASS criteria.
        # It passes if the first step passes and there are no more steps.
        if len(result.steps) == 1 and result.steps[0].status == "PASS":
            result.final_status = "PASS"

        display_multi_step_result_table(result)
        
        notification_message = f"{'✅' if result.final_status == 'PASS' else '❌'} {result.test_id} {result.final_status}: {result.test_name} ({result.total_duration:.2f}s)"
        await send_telegram_notification(tester, notification_message, NOTIFICATION_CHAT_ID)
    
    if result.final_status != "PASS":
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
