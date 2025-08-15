# MC: Telegram Accounts & Bots Mapping
**Type**: Memory Card  
**Created**: 2025-08-13 13:26 MSK  
**Purpose**: Prevent confusion between telegram accounts, bots, sessions, tokens  
**Priority**: 🔴 CRITICAL - Always reference before telegram testing  

## 🎯 QUICK REFERENCE - NEVER GET THIS WRONG AGAIN

### 👤 PRIMARY TEST USER: Клава. Тех поддержка
```
User ID: 5282615364
Username: @ClavaFamily  
API_ID: 29950132
API_HASH: e0bf78283481e2341805e3e4e90d289a
String Session: 1ApWapzMBu4PfiXOa... (see full manifest)
Status: ✅ ACTIVE
```

### 🤖 PRIMARY BOT: epub_extractor_bot
```
Bot Username: @epub_toc_based_sample_bot
Bot ID: 7956300223  
Token: 7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls
Purpose: Z-Library book search with enhanced author search
Status: ✅ ACTIVE (enhanced search implemented)
```

## 💡 TESTED WORKING COMBINATIONS

### ✅ Method 1: User Session (Telethon) 
```python
# клава техподержка sends AS USER to bot
TelegramClient(StringSession('1ApWapzMBu4PfiXO...'), 29950132, 'e0bf78283...').send_message('@epub_toc_based_sample_bot', 'Умберто эко')
```

### ✅ Method 2: Bot API (curl)
```bash
# Bot API sends TO клава техподержка's chat  
curl -X POST "https://api.telegram.org/bot7956300223:AAHsFCu-4djOAy5G_1eBSZMVR1Zb0U3DCls/sendMessage" \
  -d '{"chat_id": "5282615364", "text": "Умберто эко"}'
```

## 🧪 ENHANCED AUTHOR SEARCH TEST

**Query**: `"Умберто эко"` (author-only)  
**Expected**: Confidence 0.0 → 0.9, returns "Имя розы"  
**Files**: Enhanced in `scripts/enhanced_author_search.py` + `book_search_engine.py`  

## 🚨 COMMON MISTAKES TO AVOID

- ❌ Using @anythingllm_bot for book search → Use @epub_toc_based_sample_bot  
- ❌ Wrong user ID (14835038) → Use 5282615364 (клава техподержка)
- ❌ Mixed credentials → Each account has specific API_ID/Hash/Session
- ❌ Assuming bot is running → Always check: `./scripts/venv-manager.sh status`

## 📁 KEY FILES REFERENCE

- **Full Manifest**: `/TELEGRAM_ACCOUNTS_BOTS_MANIFEST.md`
- **IUC Patterns**: `/tests/IUC/lib/iuc_patterns.sh` 
- **Session Files**: `/tests/IUC/sessions/` (to be created)
- **Bot Manager**: `./scripts/venv-manager.sh`

## 🔧 EMERGENCY COMMANDS

```bash
# Check bot status
./scripts/venv-manager.sh status

# Restart bot if needed  
./scripts/venv-manager.sh restart

# Test message (replace ... with full session)
python3 -c "from telethon.sync import TelegramClient; from telethon.sessions import StringSession; TelegramClient(StringSession('1ApWapz...'), 29950132, 'e0bf78...').send_message('@epub_toc_based_sample_bot', 'test')"
```

---
**⚠️ ALWAYS CONSULT THIS BEFORE TELEGRAM TESTING TO AVOID CONFUSION**