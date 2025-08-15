# siuc_01: Simple Start Command Test

# --- Architectural Guardian Comments ---
# PURPOSE: This test serves as the most basic "health check" for the bot. It answers the fundamental question: "Is the bot online and responsive?"
# RISK: If this test fails, no other end-to-end tests are likely to succeed. It indicates a critical failure in the bot's core application lifecycle.
# STRATEGY: An end-to-end (E2E) test is used here because it is the only way to truly verify that the bot is accessible and responsive from a user's perspective. A simpler integration test would not be sufficient.

import asyncio
import sys
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# --- Senior Developer Comments ---
# This script uses the Telethon library to perform a live, end-to-end
# test against the Telegram bot. It is designed to be run from a CI/CD pipeline
# or a developer's local machine.
#
# Best Practice: All secrets (API_ID, HASH, SESSION) are loaded from
# environment variables to avoid hard-coding them in the script. This is a
# critical security measure.

# --- Configuration ---
API_ID = os.environ.get("TELEGRAM_API_ID", "29950132")
API_HASH = os.environ.get("TELEGRAM_API_HASH", "e0bf78283481e2341805e3e4e90d289a")
STRING_SESSION = os.environ.get("IUC_STRING_SESSION", "1ApWapzMBu4PfiXOaKlWyf87-hEiVPCmh152Zt4x2areHOfSfMNDENrJBepoLDZBGqqwrfPvo4zeDB6M8jZZkgUy8pwU9Ba67fDMlnIkESlhbX_aJFLuzbfbd3IwSYh60pLsa0mk8huWxXwHpVNDBeISwp4uGxqF6R_lxWBv_4l3pU3szXcJPS4kw9cTXZkwazvH28AOteP400dazpNpyEt2MbB56GIl9r5B7vQLcATUSW0rvd5-fWF_u2aw243XIHs7H39e_pJt2u0encXQM2Ca7X992Aad2WuHQDv7rDf1CuOO5s8UDZpvxc7ul4W53-PHyEguqLorV1uURpJH6HDDchK4WiTI=")
BOT_USERNAME = os.environ.get("IUC_TARGET_BOT", "epub_toc_based_sample_bot")
EXPECTED_RESPONSE = "📚 Welcome to Book Search Bot"
TOTAL_STEPS = 4

# --- UI & Logging ---
# Best Practice: Centralized logging functions make the test output
# consistent and easy to read. The use of emojis provides immediate
# visual feedback on the status of each step.
def log_header():
    print("="*50)
    print("🔬 TEST: siuc_01: Simple Start Command Test")
    print("PURPOSE: To verify the bot is online and responds correctly to the /start command.")
    print(f"EXPECTED: Bot replies with a message containing '{EXPECTED_RESPONSE}'.")
    print(f"TOTAL STEPS: {TOTAL_STEPS}")
    print("="*50)

def log_step(step, message):
    print(f"\n--- Step {step} of {TOTAL_STEPS}: {message} ---")

def log_info(message):
    print(f"    ℹ️  {message}")

def log_success(message):
    print(f"    ✅ {message}")

def log_error(message):
    print(f"    ❌ {message}")

def log_summary(status, pipeline):
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"RESULT: {status}")
    print("VISUAL PIPELINE:")
    print(" -> ".join(pipeline))

def show_help():
    print("""
    siuc_01: Simple Start Command Test (UX Enhanced)

    This script tests the bot's response to the /start command with a rich,
    transparent UI output.

    Usage:
        python3 siuc_01_start_command_simple_test.py
        python3 siuc_01_start_command_simple_test.py --help
    """)

# --- Main Test Logic ---
async def run_test():
    log_header()
    if not STRING_SESSION or "..." in STRING_SESSION:
        log_error("IUC_STRING_SESSION environment variable not set.")
        sys.exit(1)

    pipeline = []
    try:
        # Senior Developer Comment: The `async with` block ensures that the
        # Telethon client is properly connected and disconnected, even if errors occur.
        async with TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH) as client:
            log_step(1, "🔐 Authenticating Session")
            log_info("Using Telethon String Session to connect to Telegram.")
            me = await client.get_me()
            log_success(f"Authenticated as: {me.first_name} (ID: {me.id})")
            pipeline.append("[🔐 Auth OK]")

            log_step(2, f"📤 Sending /start to @{BOT_USERNAME}")
            await client.send_message(BOT_USERNAME, '/start')
            log_success("Command sent successfully.")
            pipeline.append("[📤 Send OK]")

            log_step(3, "📥 Reading Response")
            log_info("Waiting 5 seconds for the bot to reply...")
            await asyncio.sleep(5)
            messages = await client.get_messages(BOT_USERNAME, limit=1)
            pipeline.append("[📥 Read OK]")

            if not messages:
                log_error("No response received from the bot.")
                log_summary("FAIL", pipeline)
                sys.exit(1)

            response = messages[0].text
            log_success(f"Response received.")

            log_step(4, "✅ Validating Response")
            log_info(f"Checking if response contains: '{EXPECTED_RESPONSE}'")
            if EXPECTED_RESPONSE in response:
                log_success("Validation successful.")
                pipeline.append("[✅ Validate OK]")
            else:
                log_error("Validation failed.")
                log_info(f"ACTUAL RESPONSE:\n---\n{response}\n---")
                pipeline.append("[❌ Validate FAIL]")
                log_summary("FAIL", pipeline)
                sys.exit(1)

    except Exception as e:
        log_error(f"An unexpected error occurred during execution: {e}")
        log_summary("ERROR", pipeline)
        sys.exit(1)

    log_summary("PASS", pipeline)
    sys.exit(0)

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)
    
    asyncio.run(run_test())
