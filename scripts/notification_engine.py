#!/usr/bin/env python3
"""
Notification Engine
Reads a JSON object from stdin and sends a formatted notification via Telegram.
"""

import sys
import json
import os
import subprocess
from dotenv import load_dotenv

def send_notification(data: dict):
    """Formats and sends the notification."""
    
    telegram_script_path = os.getenv("TELEGRAM_SCRIPT_PATH")
    if not telegram_script_path:
        print("⚠️ TELEGRAM_SCRIPT_PATH not set in .env, cannot send notification.", file=sys.stderr)
        sys.exit(1)

    try:
        book_info = data.get("book", {})
        if not book_info:
            print("⚠️ No 'book' information in JSON, cannot send notification.", file=sys.stderr)
            return

        # Format the message
        message = f"""📚 NEW BOOK EXTRACTED!

📖 Title: {book_info.get("title", "N/A")}
✍️ Author: {book_info.get("author", "N/A")}
📂 Category: lib.ru/{book_info.get("category", "N/A")}
⏱️ Time: {data.get("performance", {}).get("total_time", 0):.1f}s
🎯 Confidence: {book_info.get("confidence", "N/A")}

🔗 URL: {book_info.get("source_url", "N/A")}"""

        # Execute the telegram script
        result = subprocess.run(
            [telegram_script_path, "send", message],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("📱 Telegram notification sent successfully.")
        else:
            print(f"⚠️ Telegram notification failed: {result.stderr}", file=sys.stderr)

    except Exception as e:
        print(f"❌ An unexpected error occurred in the notification engine: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to read from stdin and trigger notification."""
    try:
        # Read all data from stdin
        input_data = sys.stdin.read()
        
        if not input_data:
            print("⚠️ Stdin is empty, no data to process.", file=sys.stderr)
            sys.exit(1)
            
        # Parse the JSON data
        data = json.loads(input_data)
        
        # Send the notification
        send_notification(data)

    except json.JSONDecodeError:
        print("❌ Failed to decode JSON from stdin.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    load_dotenv()
    main()
