# 🏗️ Memory Card: Telegram Bot Technical Architecture

**Created**: 2025-08-12  
**Type**: Technical Implementation  
**Status**: ✅ Architecture Defined

## 🔧 Technical Stack Decision

### **Python Framework: aiogram 3.x**
```python
# Why aiogram over python-telegram-bot:
# - Modern async/await support
# - Better webhook handling 
# - Rich middleware system
# - Excellent Russian community
# - Built-in FSM for conversations
```

### **Integration Architecture**
```
Telegram User
    ↓ (webhook/polling)
aiogram Bot Handler
    ↓ (subprocess call)
book_search.sh --claude-extract "$input"
    ↓ (Claude WebFetch)
Claude AI → Website Extraction
    ↓ (JSON response)
Z-Library Search & Download
    ↓ (EPUB file)
Telegram File Upload
```

## 📂 Project Structure

```
telegram_bot/
├── bot.py              # Main bot application
├── handlers/           # Message handlers
│   ├── __init__.py
│   ├── url_handler.py  # URL input processing
│   ├── text_handler.py # Text search processing
│   └── error_handler.py # Error handling
├── utils/              # Helper functions
│   ├── __init__.py
│   ├── book_search.py  # Integration with book_search.sh
│   ├── russian_msgs.py # Russian message templates
│   └── file_handler.py # File upload/download logic
├── config/             # Configuration
│   ├── __init__.py
│   ├── settings.py     # Bot settings
│   └── logging.py      # Logging configuration
├── requirements.txt    # Dependencies
└── README.md          # Quick start guide
```

## 🔌 Integration Points

### **book_search.sh Integration**
```python
import subprocess
import json

async def search_book(input_text: str, input_type: str) -> dict:
    """Call existing book_search.sh with Claude integration"""
    
    cmd = [
        "./scripts/book_search.sh",
        "--claude-extract" if input_type == "url" else "",
        "--download",
        "--json",
        input_text
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    return json.loads(result.stdout)
```

### **Russian Message Templates**
```python
MESSAGES = {
    "searching": "📚 Ищу книгу...",
    "found_title": "📖 Найдено: \"{title}\"",
    "found_author": "✍️ Автор: {author}",
    "searching_library": "🔍 Поиск в библиотеке...",
    "success": "📥 Уверенность: {confidence}% ({level})",
    "not_found": "📚 Книга не найдена в библиотеке",
    "url_extract_failed": "❌ Не удалось извлечь информацию о книге\n💡 Попробуйте отправить название книги текстом",
    "library_down": "🔧 Библиотека временно недоступна\n⏳ Повторите попытку через несколько минут",
    "file_too_large": "📁 Файл слишком большой для Telegram ({size}MB)\n🔗 Скачать: {url}"
}
```

## ⚡ Handler Flow Implementation

### **URL Handler Logic**
```python
@router.message(F.text.regexp(r'https?://'))
async def handle_url(message: Message):
    # Step 1: Show searching message
    search_msg = await message.answer(MESSAGES["searching"])
    
    # Step 2: Call book_search.sh with URL
    try:
        result = await search_book(message.text, "url")
        
        # Step 3: Show extracted info
        if result.get("query_info", {}).get("extracted_query"):
            extracted = result["query_info"]["extracted_query"]
            # Parse title/author from extracted query
            await search_msg.edit_text(
                f"{MESSAGES['searching']}\n"
                f"{MESSAGES['found_title'].format(title=title)}\n"
                f"{MESSAGES['found_author'].format(author=author)}\n"
                f"{MESSAGES['searching_library']}"
            )
        
        # Step 4: Handle result
        if result["status"] == "success" and result["result"]["found"]:
            confidence = result["result"]["confidence"]["score"]
            if confidence >= 0.6:  # 60% threshold
                await send_epub_file(message, result)
            else:
                await search_msg.edit_text(MESSAGES["not_found"])
        else:
            await search_msg.edit_text(MESSAGES["not_found"])
            
    except Exception as e:
        await handle_error(message, e, search_msg)
```

### **File Upload Logic**
```python
async def send_epub_file(message: Message, result: dict):
    """Send EPUB file to user with confidence info"""
    
    file_path = result["result"]["epub_download_url"]
    confidence = result["result"]["confidence"]["score"]
    level = result["result"]["confidence"]["level"]
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > 50 * 1024 * 1024:  # 50MB Telegram limit
        await message.answer(MESSAGES["file_too_large"].format(
            size=file_size // (1024*1024),
            url=f"file://{file_path}"
        ))
        return
    
    # Upload file
    document = FSInputFile(file_path)
    await message.answer_document(
        document,
        caption=MESSAGES["success"].format(
            confidence=int(confidence*100),
            level=level
        )
    )
```

## 📊 Logging & Monitoring

### **Usage Logging Structure**
```python
import logging
import json

# Configure structured logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot_usage.log'),
        logging.StreamHandler()
    ]
)

async def log_request(user_id: int, input_text: str, result: dict):
    """Log all bot interactions for debugging"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "input": input_text[:100],  # Truncate long inputs
        "input_type": detect_input_type(input_text),
        "success": result.get("status") == "success",
        "confidence": result.get("result", {}).get("confidence", {}).get("score"),
        "found": result.get("result", {}).get("found", False),
        "error": result.get("result", {}).get("error") if result.get("status") == "error" else None
    }
    
    logger.info(f"BOT_REQUEST: {json.dumps(log_data)}")
```

## 🔒 Security & Performance

### **Input Validation**
```python
def validate_input(text: str) -> bool:
    """Validate user input for security"""
    # Length limits
    if len(text) > 1000:
        return False
    
    # Basic injection prevention
    dangerous_chars = [';', '|', '&', '$', '`']
    if any(char in text for char in dangerous_chars):
        return False
    
    return True
```

### **Rate Limiting (Future v1.2)**
```python
from aiogram.utils.decorator import rate_limit

@rate_limit(limit=3, key="user")  # 3 requests per minute per user
async def handle_message(message: Message):
    # Handler logic
    pass
```

## 🧪 Testing Strategy

### **Unit Tests**
- Message handler logic
- Book search integration
- Russian message formatting
- Error handling scenarios

### **Integration Tests**
- Full pipeline: URL → Claude → Z-Library → Telegram
- Concurrent user scenarios
- File upload edge cases
- All 6 success criteria validation

### **Load Testing**
- 5+ concurrent users
- Response time under load
- Memory usage monitoring
- Error rate tracking

## 🚀 Deployment Configuration

### **Environment Variables**
```bash
# .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOOK_SEARCH_SCRIPT_PATH=./scripts/book_search.sh
DOWNLOAD_DIR=./downloads
MAX_FILE_SIZE_MB=50
LOG_LEVEL=INFO
CLAUDE_EXTRACT_TIMEOUT=90
```

### **Docker Support (Future)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## 📈 Success Metrics

### **Technical KPIs**
- **Response Time:** <60 seconds (95th percentile)
- **Success Rate:** >90% for valid inputs
- **Concurrent Users:** 5+ without degradation
- **Error Rate:** <5% for normal operations
- **File Upload Success:** >95% for files <50MB

### **Ready for Implementation**
Architecture defined, integration points clear, all technical decisions made. Ready to proceed with bot.py implementation.