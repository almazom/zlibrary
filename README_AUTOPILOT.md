# 🚀 Autopilot Testing System for URL to EPUB Pipeline

## 🎯 Overview

The autopilot testing system automatically tests the complete URL to EPUB pipeline with various scenarios and optionally sends progress updates via Telegram.

## ✅ Current Status: RUNNING

**Autopilot PID**: 63471  
**Log File**: `logs/autopilot_20250808_121030.log`  
**Started**: 12:10:30  

## 📋 Test Coverage

### 🌐 URL Extraction Tests (5 tests)
1. **Russian Contemporary Fiction** - `Fredrik Backman - Anxious People`
2. **Classic Dystopian** - `George Orwell - 1984`  
3. **Russian Literature** - `Dostoevsky - Crime and Punishment`
4. **Children's Classic** - `Saint-Exupéry - The Little Prince`
5. **Modern Philosophy** - `Yuval Noah Harari - Sapiens`

### 🔍 Direct Search Tests (5 tests)
1. **Fuzzy English** - "Harry Potter Philosopher Stone"
2. **Russian Classic** - "Война и мир Толстой"
3. **Author Title** - "tolkien hobbit"
4. **Russian Fuzzy** - "мастер маргарита булгаков"
5. **English Horror** - "stephen king shining"

### 🧪 Error Handling Tests (3 tests)
1. **Empty Query** - Test error handling for invalid input
2. **Non-existent Book** - Test behavior with unfindable books
3. **Service Forcing** - Test --force-flibusta parameter

## 🎮 Control Commands

```bash
# Monitor current progress
./monitor_autopilot.sh

# View live logs
tail -f logs/autopilot_20250808_121030.log

# Stop testing (if needed)
kill 63471

# Quick demo (single test)
python3 quick_autopilot_demo.py
```

## 📱 Telegram Notifications (Optional)

To receive test progress updates in Telegram:

```bash
./setup_telegram.sh
```

This will guide you through:
1. Creating a Telegram bot with @BotFather
2. Getting your chat ID
3. Adding credentials to `.env`

## 📊 Expected Results

The system will test **13 total scenarios**:
- URL extraction from marketplace URLs
- Direct book searches in multiple languages
- Download capability testing
- Error handling verification
- Service selection (Z-Library vs Flibusta)

**Estimated completion time**: 5-10 minutes

## 🎯 What It Tests

### URL Processing
- Ozon.ru slug parsing
- Title/author extraction
- Language detection
- Query normalization

### Search Pipeline  
- Z-Library integration
- Flibusta fallback
- Service selection parameters
- EPUB format filtering

### Download Testing
- File download capability
- Size validation
- Path resolution
- Error handling

### Error Scenarios
- Invalid inputs
- Network timeouts
- Service unavailability
- Download limits

## 📁 Output Files

Results are saved to:
- `autopilot_results_YYYYMMDD_HHMMSS.json` - Detailed test results
- `logs/autopilot_YYYYMMDD_HHMMSS.log` - Full execution log
- Downloaded EPUBs in `downloads/` folder

## 🔍 Monitoring Progress

The system provides:
- ✅ Real-time console updates (if Telegram disabled)
- 📱 Telegram progress notifications (if configured)  
- 📊 Live log monitoring via `tail -f`
- 📈 Final success rate and timing statistics

## 🏁 Final Report

Upon completion, you'll receive:
- **Success Rate** percentage
- **Individual test results** for each scenario
- **Performance metrics** (timing, download sizes)
- **Error analysis** for any failed tests
- **Recommendations** for improvements

---

**System Status**: 🟢 ACTIVE - Autopilot testing is currently running in background.

Check progress with: `./monitor_autopilot.sh`