#!/usr/bin/env python3
"""
IUC05: Book Discovery and Variety Test

Accepts a title and author extracted by the agent, then runs the test flow.
"""

import asyncio
import sys
import re
import time

from iuc_core import (
    TelegramBotTester,
    run_test_flow,
    display_multi_step_result_table,
    send_telegram_notification
)

# --- Test Configuration ---
NOTIFICATION_CHAT_ID = "5282615364"

async def main(title: str, author: str):
    """Main test execution logic."""
    test_id = "IUC05_book_discovery_and_variety"
    test_name = f"Discovery Test for '{title[:30]}...'"
    print(f"🔥 Running {test_id}: {test_name}...")

    # Build the test case dynamically from the provided arguments
    search_query = f"{title} {author}"
    title_keywords = " ".join(title.split()[:3])
    expected_pattern = f"(searching|{re.escape(title_keywords)}|file|epub)"

    dynamic_test_case = {
        "id": test_id,
        "name": test_name,
        "message": search_query,
        "steps": [
            {
                "name": "Progress",
                "pattern": r"(searching|looking for)",
                "timeout": 20
            },
            {
                "name": "Final",
                "pattern": expected_pattern,
                "timeout": 40
            }
        ]
    }

    # Run the test
    async with TelegramBotTester() as tester:
        result = await run_test_flow(tester, dynamic_test_case)
        
        display_multi_step_result_table(result)
        
        notification_message = f"{('✅' if result.final_status == 'PASS' else '❌')} {result.test_id} {result.final_status}: {result.test_name} ({result.total_duration:.2f}s)"
        await send_telegram_notification(tester, notification_message, NOTIFICATION_CHAT_ID)
    
    if result.final_status != "PASS":
        exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./IUC05_book_discovery.py \"<book_title>\" \"<book_author>\"")
        exit(1)
    
    book_title_arg = sys.argv[1]
    book_author_arg = sys.argv[2]
    
    asyncio.run(main(book_title_arg, book_author_arg))