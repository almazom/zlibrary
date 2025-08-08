#!/usr/bin/env python3
"""
MODERN/LESS OBVIOUS RUSSIAN BOOKS - Fuzzy Input Testing
Testing contemporary and less classical Russian titles
"""
import asyncio
import sys
sys.path.insert(0, '.')
from book_normalization_system import UnifiedBookNormalizer

# Modern/Less obvious Russian books with fuzzy versions
MODERN_RUSSIAN_FUZZY = [
    # Современная литература (Contemporary Literature)
    ("метро 2033 глуховски", "метро 2033 глуховский"),  # Metro 2033 by Glukhovsky
    ("метро2033", "метро 2033"),  # Missing space
    ("митро 2033", "метро 2033"),  # Typo
    
    # Пелевин - современный автор
    ("пелевин чапаев и пустата", "чапаев и пустота пелевин"),  # Typo in "пустота"
    ("generation п пелевин", "generation п пелевин"),  # Mixed Latin/Cyrillic
    ("ампир в", "empire v"),  # Phonetic Russian of "Empire V"
    
    # Акунин - детективы
    ("азазел акунин", "азазель акунин"),  # Missing soft sign
    ("турецкий гамбет", "турецкий гамбит"),  # Typo
    ("статски советник", "статский советник"),  # Missing letter
    
    # Улицкая - современная проза
    ("зелёный шатер улицкая", "зелёный шатёр улицкая"),  # Common typo
    ("казус кукоцкого", "казус кукоцкого"),
    ("медея и её дети", "медея и ее дети"),  # ё vs е
    
    # Прилепин - новейшая литература
    ("санкья прилепин", "санькя прилепин"),  # Typo
    ("обител прилепин", "обитель прилепин"),  # Missing soft sign
    ("чёрная обезяна", "чёрная обезьяна"),  # Missing soft sign
    
    # Бизнес и саморазвитие на русском
    ("тонкое искуство пофигизма", "тонкое искусство пофигизма"),  # Typo
    ("7 навыков высокоэфективных людей", "7 навыков высокоэффективных людей"),  # Missing letter
    ("подсознание может всё", "подсознание может все"),  # ё vs е
    
    # IT книги на русском
    ("грокаем алгоритмы", "грокаем алгоритмы"),
    ("чистый код мартин", "чистый код роберт мартин"),
    ("совершенный код макконел", "совершенный код макконнелл"),  # Typo in author
    
    # Популярная психология
    ("игры в которые играют люди", "игры, в которые играют люди"),  # Missing comma
    ("красная таблетка", "красная таблетка"),
    ("нлп практическое руководство", "нлп: практическое руководство"),  # Missing colon
    
    # Фантастика и фэнтези
    ("ведмак сапковский", "ведьмак сапковский"),  # Common typo
    ("дозоры лукяненко", "дозоры лукьяненко"),  # Typo in author
    ("лабиринт отражений", "лабиринт отражений"),
    
    # Сокращения и сленг
    ("гп", "гарри поттер"),  # Harry Potter in Russian
    ("вк", "война и мир"),  # Unlikely but possible
    ("зс", "зелёный шатёр"),  # Abbreviation
    
    # Транслит (Translit)
    ("metro 2033", "метро 2033"),
    ("vedmak", "ведьмак"),
    ("master i margarita", "мастер и маргарита"),
    
    # Опечатки в популярных запросах
    ("python для начинающих", "питон для начинающих"),  # Mixed languages
    ("java script подробное руководство", "javascript подробное руководство"),
    ("c++ для чайников", "с++ для чайников"),  # Latin C vs Cyrillic С
]

async def test_modern_russian(fuzzy_text):
    """Test modern Russian fuzzy input"""
    normalizer = UnifiedBookNormalizer()
    
    print(f"\n{'='*60}")
    print(f"📚 MODERN RUSSIAN BOOK: '{fuzzy_text}'")
    print('='*60)
    
    # Process it
    result = await normalizer.normalize_book_query(fuzzy_text)
    
    # Extract results
    normalized = result['final_result']['result']
    confidence = result['final_result']['confidence']
    method = result['final_result']['method']
    detected_type = result.get('detected_type', 'unknown')
    
    print(f"\n🔍 ANALYSIS:")
    print(f"  • Problem type: {detected_type}")
    print(f"  • Confidence: {confidence:.0%}")
    print(f"  • Method: {method}")
    
    print(f"\n✨ RESULT:")
    print(f"  Input:  '{fuzzy_text}'")
    print(f"  Output: '{normalized}'")
    
    if normalized.lower() != fuzzy_text.lower():
        print(f"\n✅ Normalized!")
    else:
        print(f"\n📌 No change applied")
    
    return normalized

# Real examples from Z-Library (современные книги)
REAL_ZLIBRARY_RUSSIAN = [
    # Actual popular searches
    "метро 2033",
    "ведьмак последнее желание",
    "python програмирование",  # With typo
    "1с програмирование",      # With typo
    "нейросети с нуля",
    "блокчейн технологии",
    "криптовалюты для начинающих",
    "инвестиции в акции",
    "психология влияния чалдини",
    "sapiens краткая история человечества",
    
    # Technical books in Russian
    "джанго для начинающих",
    "реакт разработка",
    "машинное обучение",
    "глубокое обучение",
    "kubernetes на практике",
    "докер для разработчиков",
    
    # Business books
    "от нуля к единице",
    "бережливый стартап",
    "стратегия голубого океана",
    "7 навыков",
    
    # Modern fiction
    "цветы для элджернона",
    "марсианин",
    "дюна",
    "благие знамения",
]

if __name__ == "__main__":
    print("\n🚀 MODERN RUSSIAN BOOKS - FUZZY TEST")
    print("="*60)
    
    # Examples with typos/fuzzy input
    test_examples = [
        "метро2033 глуховски",      # Metro 2033 - missing space, typo in author
        "ведмак сапковский",        # Witcher - common typo (м instead of ь)
        "питон програмирование",    # Python programming - typo
        "докер для разработчиков",  # Docker for developers
        "generation п пелевин",     # Mixed Latin/Cyrillic
        "санкья прилепин",         # Modern Russian lit with typo
        "чистый код мартин",       # Clean Code
        "машинное обучение",       # Machine Learning
    ]
    
    print("\n📚 Testing modern/non-classical Russian books:\n")
    
    # Test one specific
    TEST_INPUT = "ведмак 3 дикая ахота"  # <-- With typo in "охота"
    
    print(f"Testing: '{TEST_INPUT}'")
    asyncio.run(test_modern_russian(TEST_INPUT))
    
    print("\n" + "="*60)
    print("\n📝 More modern Russian books to test (with typos):")
    for i, example in enumerate(test_examples, 1):
        print(f"  {i}. '{example}'")
    
    print("\n💡 These are actual books available in Z-Library!")
    print("   Change TEST_INPUT to try different ones.")