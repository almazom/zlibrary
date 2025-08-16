#!/usr/bin/env python3
"""
Quick Test - Send one message and monitor response
"""
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = "14835038"  # From UC3 pattern

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    
    print(f"📤 SENDING: '{text}'")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200 and response.json().get('ok'):
        print(f"✅ MESSAGE SENT")
        return True
    else:
        print(f"❌ SEND FAILED: {response.text}")
        return False

def check_responses(timeout=30):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    print(f"👁️ MONITORING RESPONSES...")
    
    start_time = time.time()
    last_update_id = 0
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, params={"offset": last_update_id + 1, "timeout": 5})
            if response.status_code == 200:
                result = response.json()
                if result.get('ok') and result.get('result'):
                    updates = result['result']
                    for update in updates:
                        last_update_id = max(last_update_id, update['update_id'])
                        message = update.get('message', {})
                        
                        # Skip our own messages
                        if message.get('from', {}).get('id') == int(CHAT_ID):
                            continue
                        
                        # Bot response!
                        text = message.get('text', '')
                        document = message.get('document')
                        
                        if document:
                            print(f"📎 DOCUMENT: {document.get('file_name', 'unknown')}")
                            if document.get('file_name', '').endswith('.epub'):
                                print(f"🎉 EPUB RECEIVED!")
                                return True
                        
                        if text:
                            print(f"💬 BOT RESPONSE: {text[:80]}...")
                            if "🔍" in text:
                                print(f"🔍 PROGRESS MESSAGE!")
                            if "❌" in text:
                                print(f"❌ ERROR MESSAGE!")
                            if "✅" in text:
                                print(f"✅ SUCCESS MESSAGE!")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        time.sleep(2)
    
    print(f"⏰ TIMEOUT ({timeout}s)")
    return False

def main():
    print(f"🤖 QUICK BOT TEST")
    print(f"Token: {BOT_TOKEN[:20]}...")
    print(f"Chat: {CHAT_ID}")
    print("=" * 40)
    
    # Send book query
    if not send_message("Clean Code Robert Martin"):
        return
    
    # Monitor for responses
    success = check_responses(60)
    
    if success:
        print(f"🎉 TEST SUCCESS!")
    else:
        print(f"❌ TEST INCOMPLETE")

if __name__ == "__main__":
    main()