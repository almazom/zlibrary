# 🤖 TELEGRAM ACCOUNTS & BOTS MANIFEST
**Version**: 1.0.0  
**Created**: 2025-08-13 13:24 MSK  
**Purpose**: Definitive reference to prevent confusion between accounts, bots, sessions, and tokens  
**Status**: ✅ VERIFIED WORKING COMBINATIONS  

## 📱 USER ACCOUNTS

### 👤 Клава. Тех поддержка (@ClavaFamily)
- **User ID**: `5282615364`
- **Display Name**: "Клава. Тех поддержка"
- **Username**: @ClavaFamily
- **Role**: Primary test user for IUC integration tests
- **API Credentials**:
  - **API ID**: `29950132`
  - **API Hash**: `e0bf78283481e2341805e3e4e90d289a`
- **String Session**: `1ApWapzMBu4PfiXOaKlWyf87-hEiVPCmh152Zt4x2areHOfSfMNDENrJBepoLDZBGqqwrfPvo4zeDB6M8jZZkgUy8pwU9Ba67fDMlnIkESlhbX_aJFLuzbfbd3IwSYh60pLsa0mk8huWxXwHpVNDBeISwp4uGxqF6R_lxWBv_4l3pU3szXcJPS4kw9cTXZkwazvH28AOteP400dazpNpyEt2MbB56GIl9r5B7vQLcATUSW0rvd5-fWF_u2aw243XIHs7H39e_pJt2u0encXQM2Ca7X992Aad2WuHQDv7rDf1CuOO5s8UDZpvxc7ul4W53-PHyEguqLorV1uURpJH6HDDchK4WiTI=`
- **Status**: ✅ ACTIVE & VERIFIED (2025-08-13)

### 👤 Alternative Test User (if needed)
- **User ID**: `14835038`
- **Role**: Secondary test user
- **Status**: 🔄 STANDBY

---

## 🤖 BOT ACCOUNTS

### 📚 Primary Book Search Bot
- **Bot Name**: `epub_extractor_bot`
- **Username**: `@epub_toc_based_sample_bot`
- **Bot ID**: `7956300223`
- **Token**: `7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls`
- **Purpose**: Main Z-Library book search and EPUB delivery
- **Features**: Enhanced author search, progress messages, file delivery
- **Status**: ✅ ACTIVE & RESPONDING (PID: 4181960)
- **Server Script**: `bot_app.py` (via venv-manager.sh)
- **Enhanced Search**: ✅ IMPLEMENTED (confidence boost 0.0→0.9)

### 🔧 Alternative Bot
- **Bot Name**: `Hey, bro!`  
- **Username**: `@anythingllm_bot`
- **Bot ID**: `7278748318`
- **Token**: `7278748318:AAERbVmfwA5acy6qNYcvYwKWB44ja09cZF8`
- **Purpose**: Testing/development
- **Status**: 🔄 STANDBY

---

## 🔗 VERIFIED WORKING COMBINATIONS

### ✅ Primary Testing Setup (RECOMMENDED)
```bash
# User Session Method (Telethon)
USER_ACCOUNT="Клава. Тех поддержка (@ClavaFamily)"
USER_ID="5282615364"
API_ID="29950132"  
API_HASH="e0bf78283481e2341805e3e4e90d289a"
STRING_SESSION="1ApWapzMBu4PfiXOaKlWyf87-hEiV..." # (full session above)
TARGET_BOT="@epub_toc_based_sample_bot"

# Expected Flow:
# клава техподержка USER → sends message → @epub_toc_based_sample_bot BOT → processes with enhanced search
```

### ✅ Curl API Method (ALTERNATIVE)
```bash
# Bot API Method (curl)
BOT_TOKEN="7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls"
CHAT_ID="5282615364"  # клава техподержка's ID
API_URL="https://api.telegram.org/bot$BOT_TOKEN/sendMessage"

# Command:
curl -s -X POST "$API_URL" -H "Content-Type: application/json" \
  -d '{"chat_id": "5282615364", "text": "Умберто эко"}'

# Expected Flow:
# curl → sends to bot → bot processes as if message came from клава техподержка
```

---

## 📋 IUC INTEGRATION TESTING REFERENCE

### 🧪 Test Message Examples
- **Author Search**: `"Умберто эко"` → Should return "Имя розы" with ✅ HIGH confidence  
- **Book + Author**: `"Имя розы, Эко"` → Should work with ✅ MEDIUM confidence
- **English Author**: `"Robert Martin"` → Should find programming books
- **Start Command**: `"/start"` → Should return welcome message

### 🔧 Quick Commands
```bash
# Check bot status
cd /home/almaz/microservices/zlibrary_api_module
./scripts/venv-manager.sh status

# Send test message (User Session)
python3 -c "from telethon.sync import TelegramClient; from telethon.sessions import StringSession; TelegramClient(StringSession('1ApWapzMBu4PfiXOaKlWyf87-hEiV...'), 29950132, 'e0bf78283481e2341805e3e4e90d289a').send_message('@epub_toc_based_sample_bot', 'Умберто эко')"

# Send test message (Curl)
curl -s -X POST "https://api.telegram.org/bot7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls/sendMessage" -H "Content-Type: application/json" -d '{"chat_id": "5282615364", "text": "Умберто эко"}'

# Watch logs
./scripts/venv-manager.sh logs --follow
```

---

## ⚠️ COMMON CONFUSION POINTS (RESOLVED)

### ❌ Wrong Bot Combinations
- ~~Sending to @anythingllm_bot expecting book search~~ → Use @epub_toc_based_sample_bot
- ~~Using old tokens from logs~~ → Use current tokens from this manifest
- ~~Mixed up user/chat IDs~~ → клава техподержка = 5282615364

### ❌ Wrong Session/Token Pairs  
- ~~String session + bot token~~ → Use string session for USER, bot token for BOT API
- ~~Wrong API credentials~~ → Always use API_ID=29950132, API_HASH=e0bf78283481e2341805e3e4e90d289a for клава техподержка

### ✅ Correct Understanding
- **USER SESSION** (Telethon): клава техподержка sends message AS USER to bot
- **BOT API** (curl): Bot sends message TO клава техподержка's chat
- **Both methods** trigger the same bot processing pipeline

---

## 🗂️ FILE LOCATIONS

### Session Files
- **Active Session**: `/home/almaz/microservices/zlibrary_api_module/tests/IUC/sessions/klava_teh_podderzhka.session`
- **String Session**: Stored in IUC lib/iuc_patterns.sh as DEFAULT_STRING_SESSION
- **Backup**: Multiple .session files in telegram_bot/ directory

### Configuration Files  
- **IUC Patterns**: `/home/almaz/microservices/zlibrary_api_module/tests/IUC/lib/iuc_patterns.sh`
- **Bot App**: `/home/almaz/microservices/zlibrary_api_module/telegram_bot/bot_app.py`
- **Enhanced Search**: `/home/almaz/microservices/zlibrary_api_module/scripts/enhanced_author_search.py`
- **Environment**: `/home/almaz/microservices/zlibrary_api_module/.env`

### Log Files
- **Bot Logs**: `/home/almaz/microservices/zlibrary_api_module/telegram_bot/logs/venv_bot.log`
- **IUC Logs**: Generated per test execution

---

## 🚀 SUCCESS VERIFICATION CHECKLIST

Before any testing session, verify:

- [ ] Bot status: `./scripts/venv-manager.sh status` → Should show "RUNNING"
- [ ] Correct bot: @epub_toc_based_sample_bot (ID: 7956300223)  
- [ ] User account: клава техподержка (ID: 5282615364)
- [ ] Enhanced search: Available in book_search_engine.py
- [ ] Session string: Valid and not corrupted
- [ ] Message flow: USER → BOT → Enhanced search → EPUB delivery

## 🎯 ENHANCED AUTHOR SEARCH VERIFICATION

**Test Query**: `"Умберто эко"`  
**Expected Results**:
- ✅ Message accepted by bot
- ✅ Progress message: "🔍 Searching for book..."  
- ✅ Author detection: TRUE (author-only query)
- ✅ Confidence boost: 0.0 → 0.9 (VERY_HIGH)
- ✅ Book found: "Имя розы" by Умберто Эко
- ✅ EPUB delivery: Success

---

**Last Updated**: 2025-08-13 13:24 MSK  
**Verified By**: Claude Code Assistant  
**Status**: 🟢 ALL SYSTEMS OPERATIONAL