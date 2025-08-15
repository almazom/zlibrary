#!/usr/bin/env python3
"""
IUC01: Start Command Feedback Loop

Validates that the bot responds to the /start command.
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

# This test has only one step.
IUC01_TEST_CASE = {
    "id": "IUC01_start_command_feedback",
    "name": "Start Command Feedback Loop",
    "message": "/start",
    "steps": [
        {
            "name": "Welcome",
            "pattern": r"(welcome|book search|📚)",
            "timeout": 20
        }
    ]
}

async def main():
    """Main test execution logic."""
    print(f"🔥 Running {IUC01_TEST_CASE['id']}: {IUC01_TEST_CASE['name']}...")
    
    async with TelegramBotTester() as tester:
        result = await run_test_flow(tester, IUC01_TEST_CASE)
        
        display_multi_step_result_table(result)
        
        notification_message = f"{'✅' if result.final_status == 'PASS' else '❌'} {result.test_id} {result.final_status}: {result.test_name} ({result.total_duration:.2f}s)"
        await send_telegram_notification(tester, notification_message, NOTIFICATION_CHAT_ID)
    
    if result.final_status != "PASS":
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())