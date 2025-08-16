# 🎨 Search Runners - Visual Pipeline Tools

Beautiful terminal visualization runners for the multi-source book search pipeline.

## 🚀 Quick Start

```bash
# Make scripts executable
chmod +x search/*.sh

# Visual search with real-time pipeline display
./search/visual_search.sh "hary poter filosofer stone"

# Quick fuzzy input demonstration  
./search/fuzzy_search.sh english_fuzzy

# Fast search without visualization
./search/quick_search.sh --json "1984 orwell"
```

## 📁 Search Runners

### 🎨 `visual_search.sh` - Full Pipeline Visualization
Beautiful terminal UI showing all pipeline layers in real-time.

**Features:**
- 🔍 Step-by-step pipeline visualization
- 🤖 Claude AI normalization display
- 🌍 Language-aware routing indicators
- ⚡ Z-Library → 🇷🇺 Flibusta fallback visualization
- 📊 Real-time performance metrics
- 🎨 Rich terminal UI with emojis and colors

**Usage:**
```bash
# Visual search
./search/visual_search.sh "your fuzzy query"

# Interactive mode for multiple searches
./search/visual_search.sh --interactive

# Quick demo
./search/visual_search.sh --demo

# Minimal UI mode
./search/visual_search.sh --quick "fast search"
```

### 🌟 `fuzzy_search.sh` - Specialized Fuzzy Input Demos
Preset demonstrations showcasing AI normalization capabilities.

**Preset Fuzzy Queries:**
- `english_fuzzy` - "hary poter filosofer stone"
- `russian_transliteration` - "malenkiy prinz" 
- `mixed_language` - "dostoevsky преступление punishment"
- `war_peace` - "voyna i mir tolstoy"
- `misspelled_classic` - "shakesbeer hamlet"
- `author_fuzzy` - "tolken lord rings"
- `russian_fuzzy` - "chekhov вишневый sad"
- `numbers_fuzzy` - "orwell 1984 nineteen eighty four"

**Usage:**
```bash
# Run preset fuzzy query
./search/fuzzy_search.sh english_fuzzy

# Run all preset demonstrations
./search/fuzzy_search.sh --all

# Custom fuzzy query
./search/fuzzy_search.sh "your fuzzy input"
```

### ⚡ `quick_search.sh` - Fast Minimal Search
Rapid pipeline search without full visualization.

**Features:**
- ⚡ Fast execution
- 📊 JSON output support
- 📥 Optional download functionality
- 🎯 Format selection (epub, pdf, mobi)
- ⏱️ Configurable timeouts

**Usage:**
```bash
# Quick search
./search/quick_search.sh "book title"

# JSON output for scripts
./search/quick_search.sh --json "query" > result.json

# Search and download
./search/quick_search.sh --download --format epub "book"

# Custom timeout
./search/quick_search.sh --timeout 60 "slow query"
```

## 🎯 Pipeline Layers Visualized

All runners show these pipeline stages:

1. **🔍 Input Validation** - Query sanitization and validation
2. **🤖 Claude Normalization** - AI-powered fuzzy input correction
3. **🎯 Chain Optimization** - Language-aware source routing
4. **⚡ Z-Library Search** - Primary source (fast, comprehensive)
5. **🇷🇺 Flibusta Search** - Fallback source (Russian focus, AI-enhanced)
6. **📊 Result Compilation** - Final results and statistics

## 🌟 Fuzzy Input Examples

### English Misspellings
- "hary poter" → "Harry Potter"
- "shakesbeer hamlet" → "Shakespeare Hamlet"
- "tolken lord rings" → "Tolkien Lord of the Rings"

### Russian Transliteration
- "malenkiy prinz" → "Маленький принц" (The Little Prince)
- "voyna i mir tolstoy" → "Война и мир" (War and Peace)
- "dostoevsky prestuplenie" → "Преступление и наказание"

### Mixed Language
- "dostoevsky преступление punishment" → Context-aware search
- "chekhov вишневый sad" → "Cherry Orchard" recognition
- "tolstoy анна karenina" → "Anna Karenina"

### Number Variations
- "1984 nineteen eighty four" → "1984" normalization
- "451 fahrenheit bradbury" → "Fahrenheit 451"
- "2001 space odyssey" → "2001: A Space Odyssey"

## 📊 Output Formats

### Visual Mode (Default)
```
🎨 MULTI-SOURCE BOOK SEARCH PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔎 Query: "hary poter"
🌟 Fuzzy input detected - AI normalization active

🔄 Pipeline Steps
├── 🔍 Input Validation ✅ Query validated ✓
├── 🤖 Query Normalization ✅ Generated 3 variants: Harry Potter, Гарри Поттер...
├── 🎯 Chain Optimization ✅ 🇬🇧 Latin text → Chain: zlibrary → flibusta
├── ⚡ Z-Library Search ✅ Found: Harry Potter and the Philosopher's Stone...
├── 🇷🇺 Flibusta Search ⏭️ Skipped (already found)
└── 📊 Result Compilation ✅ Results compiled successfully

🎉 SUCCESS! Found via ZLIBRARY
📚 Title: Harry Potter and the Philosopher's Stone
👤 Author: J.K. Rowling
📥 Download: Available
⏱️ Response time: 3.42s
```

### JSON Mode
```json
{
  "found": true,
  "query": "hary poter",
  "source": "zlibrary",
  "response_time": 3.42,
  "title": "Harry Potter and the Philosopher's Stone",
  "author": "J.K. Rowling",
  "download_url": "https://...",
  "file_id": "12345",
  "confidence": 0.95,
  "metadata": {
    "normalized_queries": ["Harry Potter", "Гарри Поттер"],
    "sources_tried": ["zlibrary"],
    "ai_processed": true
  }
}
```

## 🔧 Configuration

### Environment Variables
- `BOOK_DOWNLOAD_DIR` - Default download directory
- `ZLOGIN` - Z-Library username
- `ZPASSW` - Z-Library password
- `FLIBUSTA_API_KEY` - Flibusta API key

### Script Options
- Output directory: `-o, --output <dir>`
- Search timeout: `-t, --timeout <seconds>`
- Format selection: `-f, --format <epub|pdf|mobi>`
- JSON output: `-j, --json`
- Download mode: `-d, --download`

## 🎨 Visual Features

- **🌈 Color-coded status** (green=success, red=failed, yellow=running)
- **📊 Live progress bars** and spinners
- **🎯 Language detection** indicators  
- **⏱️ Real-time timing** for each step
- **📈 Performance statistics** display
- **🎨 Rich terminal formatting** with panels and tables
- **🔄 Interactive modes** for multiple searches

## 📦 Dependencies

All runners require:
- **Python 3.8+**
- **rich** library for beautiful terminal UI

Install with:
```bash
pip install rich>=13.0.0
# Or use the project installer
./install_viz.sh
```

## 🎯 Use Cases

### Development & Testing
- **Debug fuzzy input** handling
- **Visualize pipeline performance** 
- **Test language routing** logic
- **Monitor source availability**

### Demonstrations
- **Showcase AI normalization** capabilities
- **Present multi-source fallback** strategy
- **Display language-aware** routing
- **Highlight search transparency**

### Production Scripts
- **JSON output** for automation
- **Fast search** without visualization
- **Batch processing** with quick_search.sh
- **Monitoring** pipeline health

---

*Built with ❤️ for transparent book search pipeline visualization*