# UC16: Multi-Language Search Support

## Feature: Intelligent Multi-Language Search
As a global user
I want to search in any language or script
So that language barriers don't limit book discovery

## Background
Given the search system supports multiple languages
And Unicode normalization is available

## Scenario 1: Cyrillic Search
```gherkin
Given a book title in Cyrillic: "Война и мир"
When I search for the book
Then the system should:
  - Preserve Cyrillic characters
  - Find Russian edition
  - Also suggest transliterated versions
  - Show results: "War and Peace" as alternative
```

## Scenario 2: Mixed Script Search
```gherkin
Given a query with mixed scripts: "1984 Джордж Оруэлл"
When I search
Then the system should:
  - Parse both Latin and Cyrillic
  - Search for "1984" AND "George Orwell"
  - Handle author transliteration
  - Return relevant results
```

## Scenario 3: Unicode Normalization
```gherkin
Given different Unicode representations:
  | Input | Normalized |
  | café | cafe |
  | naïve | naive |
  | Björk | Bjork |
  | 北京 | 北京 |
When searching
Then all variants should find the same book
```

## Scenario 4: Transliteration Fallback
```gherkin
Given a Russian title: "Преступление и наказание"
When no Russian edition exists
Then the system should:
  - Transliterate to "Prestuplenie i nakazanie"
  - Search for "Crime and Punishment"
  - Return English/French editions
  - Mark as fallback result
```

## Implementation Requirements

### 1. Character Set Support
```python
SUPPORTED_SCRIPTS = {
    'latin': string.ascii_letters,
    'cyrillic': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
    'arabic': 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي',
    'chinese': 'CJK unified ideographs',
    'japanese': 'hiragana + katakana + kanji'
}
```

### 2. Transliteration Map
```python
CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g',
    'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
    'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
    'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '',
    'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
}
```

### 3. Language Detection
```python
def detect_language(text: str) -> List[str]:
    """Detect languages present in text"""
    languages = []
    if re.search(r'[а-яА-Я]', text):
        languages.append('russian')
    if re.search(r'[a-zA-Z]', text):
        languages.append('english')
    if re.search(r'[\u4e00-\u9fff]', text):
        languages.append('chinese')
    return languages
```

### 4. Search Strategy
```python
async def multi_language_search(query: str):
    # 1. Detect languages
    languages = detect_language(query)
    
    # 2. Normalize Unicode
    normalized = unicodedata.normalize('NFKD', query)
    
    # 3. Generate variants
    variants = [
        query,  # Original
        normalized,  # Normalized
        transliterate(query),  # Transliterated
        remove_accents(query)  # Without accents
    ]
    
    # 4. Search all variants
    results = []
    for variant in variants:
        results.extend(await search(variant))
    
    # 5. Deduplicate and rank
    return rank_results(deduplicate(results))
```

## Test Cases

### Cyrillic Tests
- "Война и мир" → War and Peace
- "Братья Карамазовы" → Brothers Karamazov
- "Мастер и Маргарита" → Master and Margarita

### Mixed Script Tests
- "1984 Оруэлл" → 1984 by Orwell
- "Гарри Поттер Harry Potter" → Harry Potter series
- "アキラ AKIRA" → Akira manga

### Unicode Edge Cases
- "Naïve Café" → Naive Cafe
- "Zürich" → Zurich
- "São Paulo" → Sao Paulo

## Success Criteria
- ✅ All major scripts supported
- ✅ Transliteration accuracy >90%
- ✅ Unicode normalization works
- ✅ Mixed script queries handled
- ✅ Language fallback functional

## Performance Metrics
- Language detection: <10ms
- Transliteration: <5ms
- Unicode normalization: <2ms
- Multi-variant search: <500ms