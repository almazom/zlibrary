# siuc_02: Happy Path E2E Book Search Test

# --- Architectural Guardian Comments ---
# PURPOSE: This test validates the single most important user journey: a successful book search that results in a delivered EPUB file. It is the "golden path" test for the application's core value proposition.
# RISK: A failure in this test indicates a critical failure in the main user-facing feature. The entire system could be considered "down" if this test fails.
# STRATEGY: A full end-to-end (E2E) test is necessary here because the book search process is asynchronous and involves multiple steps (progress messages, file delivery). A simpler integration test would not be sufficient to validate the complete user experience.

import asyncio
import sys
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# --- Senior Developer Comments ---
# This script tests a complex, asynchronous, multi-step conversation.
# It uses loops with timeouts to wait for specific messages (the progress
# message and the final file delivery), which is a standard pattern for testing
# asynchronous conversational bots.
# Note the use of `message.document` to specifically check for a file attachment.

# --- Configuration ---
API_ID = os.environ.get("TELEGRAM_API_ID", "29950132")
API_HASH = os.environ.get("TELEGRAM_API_HASH", "e0bf78283481e2341805e3e4e90d289a")
STRING_SESSION = os.environ.get("IUC_STRING_SESSION", "1ApWapzMBu4PfiXOaKlWyf87-hEiVPCmh152Zt4x2areHOfSfMNDENrJBepoLDZBGqqwrfPvo4zeDB6M8jZZkgUy8pwU9Ba67fDMlnIkESlhbX_aJFLuzbfbd3IwSYh60pLsa0mk8huWxXwHpVNDBeISwp4uGxqF6R_lxWBv_4l3pU3szXcJPS4kw9cTXZkwazvH28AOteP400dazpNpyEt2MbB56GIl9r5B7vQLcATUSW0rvd5-fWF_u2aw243XIHs7H39e_pJt2u0encXQM2Ca7X992Aad2WuHQDv7rDf1CuOO5s8UDZpvxc7ul4W53-PHyEguqLorV1uURpJH6HDDchK4WiTI=")
BOT_USERNAME = os.environ.get("IUC_TARGET_BOT", "epub_toc_based_sample_bot")
TEST_BOOK_TITLE = "MANIAC Лабатут Б."
PROGRESS_MESSAGE = "🔍 Searching for book..."
TOTAL_STEPS = 4

# --- UI & Logging ---
def log_header():
    print("="*50)
    print("🔬 TEST: siuc_02: Happy Path E2E Book Search")
    print("PURPOSE: To verify the full, live, end-to-end book search flow.")
    print("EXPECTED: The bot sends a progress message, then delivers an EPUB file.")
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

# --- Main Test Logic ---
async def run_test():
    log_header()
    if not STRING_SESSION or "..." in STRING_SESSION:
        log_error("IUC_STRING_SESSION environment variable not set.")
        sys.exit(1)

    pipeline = []
    try:
        async with TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH) as client:
            log_step(1, "🔐 Authenticating Session")
            me = await client.get_me()
            log_success(f"Authenticated as: {me.first_name} (ID: {me.id})")
            pipeline.append("[🔐 Auth OK]")

            log_step(2, "📤 Sending Book Title")
            log_info(f"Sending title: '{TEST_BOOK_TITLE}' to @{BOT_USERNAME}...")
            await client.send_message(BOT_USERNAME, TEST_BOOK_TITLE)
            log_success("Message sent successfully.")
            pipeline.append("[📤 Send OK]")

            log_step(3, "📥 Verifying Progress Message")
            log_info(f"Waiting for progress message: '{PROGRESS_MESSAGE}'...")
            progress_found = False
            for i in range(5):
                await asyncio.sleep(2)
                messages = await client.get_messages(BOT_USERNAME, limit=1)
                if messages and PROGRESS_MESSAGE in messages[0].text:
                    log_success("Progress message found.")
                    progress_found = True
                    break
                log_info(f"Progress message not found yet... (Attempt {i+1} of 5)")
            
            if not progress_found:
                log_error("Did not receive progress message within 10 seconds.")
                log_summary("FAIL", pipeline)
                sys.exit(1)
            pipeline.append("[📥 Progress OK]")

            log_step(4, "📦 Verifying EPUB File Delivery")
            log_info("Waiting for EPUB file delivery...")
            file_found = False
            for i in range(15):
                await asyncio.sleep(2)
                messages = await client.get_messages(BOT_USERNAME, limit=1)
                # Senior Developer Comment: We check `message.document` to see if the message is a file.
                # We then check the mime_type to be sure it's an EPUB file.
                if messages and messages[0].document and messages[0].document.mime_type == 'application/epub+zip':
                    log_success("EPUB file received!")
                    log_info(f"File name: {messages[0].document.attributes[0].file_name}")
                    file_found = True
                    break
                log_info(f"EPUB file not found yet... (Attempt {i+1} of 15)")

            if not file_found:
                log_error("Did not receive EPUB file within 30 seconds.")
                log_summary("FAIL", pipeline)
                sys.exit(1)
            pipeline.append("[📦 EPUB OK]")

    except Exception as e:
        log_error(f"An unexpected error occurred during execution: {e}")
        log_summary("ERROR", pipeline)
        sys.exit(1)

    log_summary("PASS", pipeline)
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(run_test())
