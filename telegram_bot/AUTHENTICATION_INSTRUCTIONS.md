# 🔐 USER SESSION AUTHENTICATION INSTRUCTIONS

## 📱 STEP-BY-STEP AUTHENTICATION:

### 1. Open Terminal in Current Directory
```bash
cd /home/almaz/microservices/zlibrary_api_module/telegram_bot
```

### 2. Run Authentication Script
```bash
python3 setup_session.py
```

### 3. Follow Prompts:
- Script connects to Telegram
- SMS code sent to +79163708898
- Enter the code when prompted
- Session gets authenticated and saved

### 4. Expected Output:
```
🔐 Setting up Telegram user session...
📱 You'll get SMS code, enter it when prompted
Please enter the code you received: [ENTER YOUR CODE]
✅ Authenticated as: Almaz
📤 Test message sent! ID: 1234
🎯 Check your Telegram for bot response!
📁 Session saved for reuse!
```

### 5. Verification:
- Check your Telegram for bot response to "Session Test - Programming Pearls"
- Bot should send progress message and EPUB file
- This proves user session triggers identical pipeline as manual

## 🎯 AFTER AUTHENTICATION:

Once authenticated, you can run:
```python
from telethon.sync import TelegramClient

with TelegramClient('user_session_final', 29950132, 'e0bf78283481e2341805e3e4e90d289a') as client:
    # Send any book search - triggers IDENTICAL pipeline as manual
    client.send_message('@epub_toc_based_sample_bot', 'Clean Code Robert Martin')
```

## 🚀 RESULT:
- User session creates SAME logs as manual: "📝 Text message from user 14835038"
- Triggers identical pipeline: search → progress → EPUB delivery
- 100% automated equivalent to manual typing

---
**🎯 Run `python3 setup_session.py` in terminal to complete authentication!**