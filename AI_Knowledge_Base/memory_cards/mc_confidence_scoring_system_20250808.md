# Confidence Scoring System - Memory Card

## Overview
Advanced confidence calculation system for book search matching.

## Implementation
- **Native Bash**: Word overlap calculation in enhanced script
- **Python Backend**: Advanced scoring in service modules
- **Dual Layer**: Both bash and Python calculate independently

## Confidence Levels
| Level | Score Range | Russian Description | Recommended |
|-------|-------------|-------------------|-------------|
| **VERY_HIGH** | ≥0.8 | Очень высокая уверенность - это точно искомая книга | ✅ Yes |
| **HIGH** | ≥0.6 | Высокая уверенность - скорее всего это нужная книга | ✅ Yes |
| **MEDIUM** | ≥0.4 | Средняя уверенность - возможно это нужная книга | ✅ Yes |
| **LOW** | ≥0.2 | Низкая уверенность - вряд ли это искомая книга | ❌ No |
| **VERY_LOW** | <0.2 | Очень низкая уверенность - это не та книга | ❌ No |

## Calculation Factors

### 1. Word Overlap (50% weight)
```bash
# Count matching words between input and found title
overlap_score = matching_words / total_input_words * 0.5
```

### 2. Exact Phrase Match (+40% bonus)
```bash
# Boost if exact input phrase found in title
if input_text in book_title: score += 0.4
```

### 3. Author Detection (+30% bonus)
```bash
# Boost if author names appear in input text
if author_name in input_text: score += 0.3
```

### 4. Language Consistency (+10% bonus)
```bash
# Bonus for matching Cyrillic/Latin patterns
if both_cyrillic OR both_latin: score += 0.1
```

## JSON Output Format
```json
{
  "confidence": {
    "score": 0.750,
    "level": "HIGH",
    "description": "Высокая уверенность - скорее всего это нужная книга",
    "recommended": true
  }
}
```

## Implementation Files
- `scripts/zlib_search_enhanced.sh` - Native bash calculation
- `txt_to_epub_service.py` - Python implementation
- `standardized_book_search.py` - URL-based confidence

## Test Results
- **Harry Potter philosopher stone** → VERY_HIGH (1.0)
- **Clean Code Robert Martin** → HIGH (0.6-0.8)
- **Maniac Benjamin Labatut** → MEDIUM (0.4-0.6)
- **Random nonsense text** → VERY_LOW (<0.2)

## Usage
```bash
# Automatic in enhanced script
./scripts/zlib_search_enhanced.sh "book title"

# Manual disable
./scripts/zlib_search_enhanced.sh --no-confidence "book title"
```

**Confidence scoring provides intelligent book matching assessment for all search types.**