# 🤖 Memory Card: Telegram Bot Project Specification

**Created**: 2025-08-12  
**Type**: Project Specification  
**Status**: ✅ Complete Requirements Captured

## 🎯 Core Requirements Captured

### **Primary Functionality**
- **Multi-modal input:** URLs + text searches (v1.0)
- **Future extensibility:** Image covers, message extraction (v1.1+)
- **Interface language:** Russian with smart messaging
- **Outcome:** Binary - EPUB download OR clear "не найдена"

### **Input Processing Flow**
```
Input → Extract/Parse → Show Progress → Search → Result
URL   → Claude WebFetch → "📖 Найдено: Title" → Z-Library → EPUB/NotFound
Text  → Direct Parse   → "✍️ Автор: Author"  → Z-Library → EPUB/NotFound
```

## 📱 UX Message Flow (Russian)

### **Success Flow**
```
User: https://alpinabook.ru/catalog/book-pishi-sokrashchay-2025/

Bot: 📚 Ищу книгу...
     📖 Найдено: "Пиши, сокращай"
     ✍️ Автор: Максим Ильяхов
     🔍 Поиск в библиотеке...
     📥 [book.epub] - Уверенность: 67% (HIGH)
```

### **Failure Flow**
```
User: https://invalid-url.com/book/

Bot: 📚 Ищу книгу...
     ❌ Не удалось извлечь информацию о книге
     💡 Попробуйте отправить название книги текстом
```

## ⚙️ Technical Integration Points

### **Backend Integration**
- **Core Engine:** Existing `book_search.sh` + Claude WebFetch
- **Confidence Threshold:** 60%+ = download, <60% = "не найдена"
- **File Handling:** EPUB upload (max 50MB) or download link
- **Error Handling:** 3 scenarios with fallback suggestions

### **Architecture**
```
Telegram Bot (Python) 
    ↓
book_search.sh --claude-extract
    ↓  
Claude WebFetch + Z-Library
    ↓
EPUB File → Telegram Upload
```

## ✅ Success Criteria (6 Critical Tests)

### **MUST PASS for v1.0 Release**
1. **URL Processing:** alpinabook.ru URL → correct EPUB in <60s
2. **Text Search:** "Война и мир" → Tolstoy book with 60%+ confidence
3. **Error Handling:** Invalid URL → clear error + fallback suggestion
4. **Concurrent Load:** 5+ users simultaneously → all respond within 90s
5. **Russian Support:** "Гарри Поттер и философский камень" → correct book
6. **Safety:** Never send wrong book silently (confidence validation)

### **Quality Standards**
- **Response Time:** <60 seconds per request
- **Accuracy:** 60%+ confidence required for auto-download
- **Language:** Perfect Russian/Cyrillic handling
- **Reliability:** No crashes under concurrent load

## 🔧 Production Requirements

### **Logging & Monitoring (Required)**
- **Usage tracking:** All requests, responses, confidence scores
- **Error logging:** Failed extractions, timeouts, Z-Library issues
- **Debug info:** Extraction results, search queries, file paths

### **Error Handling Matrix**
| Scenario | Response | Action |
|----------|----------|---------|
| URL extraction fails | "❌ Не удалось извлечь" + "💡 Попробуйте текстом" | Fallback to text |
| Z-Library down | "🔧 Библиотека недоступна" + "⏳ Повторите позже" | Retry suggestion |
| File >50MB | "📁 Слишком большой" + "🔗 Скачать: [link]" | Download link |

## 📋 Implementation Phases

### **Phase 1: v1.0 - Core Bot**
- Russian message flow implementation
- Integration with existing book_search.sh
- File upload to Telegram
- Usage logging
- All 6 success criteria passing

### **Phase 2: v1.1 - Enhanced Features**
- Image cover recognition
- Message extraction from forwards
- Confidence-based confirmations (45-59% range)

### **Phase 3: v1.2 - Production Scale**
- Rate limiting per user
- Admin monitoring commands
- Performance optimization
- Analytics dashboard

## 🚀 Ready for Implementation

**Next Steps:**
1. Choose Python framework (aiogram/python-telegram-bot)
2. Create bot structure + Telegram API integration
3. Implement Russian message flow
4. Connect to existing book_search.sh pipeline
5. Test all 6 critical success criteria

**Definition of Done:** All success criteria pass + Russian UX flow works flawlessly + concurrent user support + production logging implemented