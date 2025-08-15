#!/usr/bin/env python3
"""
IUC02: Valid Book Search (Atomic)

Tests a valid book search, checking for the multi-step "searching" -> "file" response.
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

IUC02_TEST_CASE = {
    "id": "IUC02_valid_book_search",
    "name": "Valid Book Search (Atomic)",
    "message": "The Pragmatic Programmer",
    "steps": [
        {
            "name": "Progress",
            "pattern": r"(searching|looking for)",
            "timeout": 15
        },
        {
            "name": "Final",
            "pattern": r"(pragmatic programmer|file|epub)", # Expect file or title confirmation
            "timeout": 40
        }
    ]
}

async def main():
    """Main test execution logic."""
    print(f"🔥 Running {IUC02_TEST_CASE['id']}: {IUC02_TEST_CASE['name']}...")
    
    async with TelegramBotTester() as tester:
        result = await run_test_flow(tester, IUC02_TEST_CASE)
        
        display_multi_step_result_table(result)
        
        notification_message = f"{'✅' if result.final_status == 'PASS' else '❌'} {result.test_id} {result.final_status}: {result.test_name} ({result.total_duration:.2f}s)"
        await send_telegram_notification(tester, notification_message, NOTIFICATION_CHAT_ID)
    
    if result.final_status != "PASS":
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())