#!/usr/bin/env python3
"""
Send Telegram testing progress update
"""
import os
import requests
from pathlib import Path

# Load environment variables
def load_env():
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

load_env()

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

def send_telegram_message(message: str):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured. To enable notifications:")
        print("1. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env file")
        print("2. Run ./setup_telegram.sh for setup instructions")
        print("\n📱 Message would have been:")
        print("=" * 50)
        print(message)
        print("=" * 50)
        return False
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Telegram message sent successfully!")
            return True
        else:
            print(f"⚠️ Telegram API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def main():
    """Send the final completion status"""
    
    # The requested final completion message
    message = """✅ <b>URL Testing Service Complete!</b>

📊 <b>Final Results:</b>
• Success Rate: 87.5% (7/8 URLs)
• Target Met: YES (≥80%)
• Russian Support: CONFIRMED ✓

🎯 <b>Deliverables:</b>
✓ Interactive test script
✓ UC21 test suite created
✓ Russian URL patterns documented
✓ Memory cards updated
✓ 4 atomic git commits

📁 <b>Files Created:</b>
• scripts/interactive_url_test.sh
• tests/UC21_interactive_url_epub.md
• test_results/interactive_url_test_report.md
• memory_cards/mc_russian_bookstore_patterns.md

🚀 <b>Ready for Production!</b>

Run: ./scripts/interactive_url_test.sh"""

    print("📤 Sending Telegram completion status...")
    success = send_telegram_message(message)
    
    if success:
        print("🎉 URL Testing Service completion status sent to Telegram!")
    else:
        print("⚠️ Could not send to Telegram - check configuration")

if __name__ == "__main__":
    main()