#!/usr/bin/env python3
"""
IUC Core Library - Guardian-Approved Shared Components

Contains the core, reusable components for the simplified IUC test suite.
This module is the stable 'Branch' that all atomic 'Leaf' tests will depend on.
"""

import asyncio
import time
import os
import re
import subprocess
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import logging

# --- Core Components ---

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BotResponse:
    """Simple response container for a single step."""
    text: str
    has_file: bool = False
    found: bool = False
    message_id: Optional[int] = None

@dataclass
class TestStepResult:
    """Result of a single step in a multi-step test."""
    name: str
    expected_pattern: str
    actual_response: str
    status: str
    duration: float

@dataclass
class IUCTestResult:
    """Overall result of a full IUC test case."""
    test_id: str
    test_name: str
    final_status: str
    total_duration: float
    steps: List[TestStepResult] = field(default_factory=list)

class TelegramBotTester:
    """Handles the connection and basic communication with the Telegram bot."""
    
    def __init__(self, 
                 api_id: str = None,
                 api_hash: str = None, 
                 session_string: str = None,
                 bot_username: str = "@epub_toc_based_sample_bot"):
        
        self.api_id = api_id or os.getenv('TELEGRAM_API_ID', '29950132')
        self.api_hash = api_hash or os.getenv('TELEGRAM_API_HASH', 'e0bf78283481e2341805e3e4e90d289a')
        self.session_string = session_string or self._load_session_string()
        self.bot_username = bot_username
        self.client = None
        
    def _load_session_string(self) -> str:
        session_file = "/home/almaz/microservices/zlibrary_api_module/tests/IUC/sessions/klava_teh_podderzhka.txt"
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    content = f.read().strip()
                    for line in content.split('\n'):
                        if 'STRING_SESSION=' in line:
                            return line.split('STRING_SESSION=')[1].strip().strip('"')
                    return content
        except Exception as e:
            logger.warning(f"Could not load session file: {e}")
        return "1ApWapzMBu4PfiXOaOvO2f4-W5v-k3iGUEjLPRKnJZaIxPKL6_PEpn7ZPZ..."
    
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        self.client = TelegramClient(
            StringSession(self.session_string),
            int(self.api_id),
            self.api_hash
        )
        await self.client.connect()
        me = await self.client.get_me()
        logger.info(f"Connected as: {me.first_name} {me.last_name or ''} (ID: {me.id})")
        
    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

# --- Test Execution Logic ---

async def _wait_for_response(tester: TelegramBotTester, since_message_id: int, timeout: int) -> BotResponse:
    """Polls for a new message from the bot after a given message ID."""
    for _ in range(timeout):
        await asyncio.sleep(1)
        async for msg in tester.client.iter_messages(tester.bot_username, limit=10):
            if msg.id > since_message_id and not msg.out:
                text = msg.message or ""
                has_file = bool(msg.media)
                logger.info(f"Bot responded with new message ID {msg.id}: '{text[:100]}...' (has_file: {has_file})")
                return BotResponse(text=text, has_file=has_file, found=True, message_id=msg.id)
    
    logger.warning(f"No new bot response after {timeout}s")
    return BotResponse(text="", has_file=False, found=False, message_id=since_message_id)

async def run_test_flow(tester: TelegramBotTester, test_case: Dict[str, Any]) -> IUCTestResult:
    """Runs a multi-step test case, validating each step."""
    overall_start_time = time.time()
    test_result = IUCTestResult(
        test_id=test_case['id'],
        test_name=test_case['name'],
        final_status="FAIL",
        total_duration=0
    )

    try:
        logger.info(f"Sending initial message: '{test_case['message']}'...")
        last_message_id = 0
        async for msg in tester.client.iter_messages(tester.bot_username, limit=1):
            last_message_id = msg.id

        await tester.client.send_message(tester.bot_username, test_case['message'])

        for i, step in enumerate(test_case['steps']):
            step_name = step['name']
            expected_pattern = step['pattern']
            timeout = step['timeout']
            
            logger.info(f"Executing Step {i+1}: {step_name} (waiting for message after ID {last_message_id})..." )
            step_start_time = time.time()
            
            response = await _wait_for_response(tester, last_message_id, timeout)
            step_duration = time.time() - step_start_time

            if not response.found:
                step_status = "FAIL (No Response)"
                test_result.steps.append(TestStepResult(step_name, expected_pattern, "NO RESPONSE", step_status, step_duration))
                test_result.total_duration = time.time() - overall_start_time
                return test_result

            last_message_id = response.message_id

            if re.search(expected_pattern, response.text, re.IGNORECASE) or (response.has_file and "file" in expected_pattern):
                step_status = "PASS"
            else:
                step_status = "FAIL"

            test_result.steps.append(TestStepResult(step_name, expected_pattern, response.text, step_status, step_duration))

            if step_status == "FAIL":
                test_result.total_duration = time.time() - overall_start_time
                return test_result

        test_result.final_status = "PASS"

    except Exception as e:
        logger.error(f"An exception occurred during test flow for {test_case['id']}: {e}")
        test_result.final_status = "ERROR"

    test_result.total_duration = time.time() - overall_start_time
    return test_result

# --- UI and Notification Functions ---

def display_multi_step_result_table(result: IUCTestResult):
    """Displays a rich table for a multi-step test result."""
    status_emoji = "✅" if result.final_status == "PASS" else "❌"
    
    print(f"\n┌──────────────────────────────────────────────────────────────────────────┐")
    print(f"│ {status_emoji} {result.test_id}: {result.test_name} ({result.total_duration:.2f}s) │")
    print(f"├──────────┬─────────────┬──────────────────────────┬──────────────────────┤")
    print(f"│ Step     │ Status      │ Expected (Pattern)       │ Actual (Response)    │")
    print(f"├──────────┼─────────────┼──────────────────────────┼──────────────────────┤")

    for step in result.steps:
        step_status_emoji = "✅" if "PASS" in step.status else "❌"
        expected_clipped = (step.expected_pattern[:22] + '..') if len(step.expected_pattern) > 24 else step.expected_pattern
        actual_clipped = (step.actual_response.replace("\n", " ").strip()[:18] + '..') if len(step.actual_response) > 20 else step.actual_response.strip()
        
        print(f"│ {step.name:<8} │ {step_status_emoji} {step.status:<8} │ {expected_clipped:<24} │ {actual_clipped:<20} │")

    print(f"└──────────┴─────────────┴──────────────────────────┴──────────────────────┘")

async def send_telegram_notification(tester: TelegramBotTester, message: str, chat_id: str):
    """Sends a notification message to the user via Telegram using the existing client."""
    logger.info(f"🔔 Sending Telegram notification...")
    try:
        await tester.client.send_message(int(chat_id), message)
        logger.info("✅ Notification sent successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}")
