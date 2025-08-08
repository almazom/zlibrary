#!/usr/bin/env python3
"""
RUSSIAN BOOK TITLES - Fuzzy Input Testing
Testing Cyrillic fuzzy inputs and common Russian book misspellings
"""
import asyncio
import sys
sys.path.insert(0, '.')
from book_normalization_system import UnifiedBookNormalizer

# Russian fuzzy examples
RUSSIAN_FUZZY_EXAMPLES = [
    # Война и мир (War and Peace)
    ("вайна и мир", "война и мир"),  # Common phonetic mistake
    ("война имир", "война и мир"),    # Missing space
    ("воина и мир", "война и мир"),   # Typo
    
    # Преступление и наказание (Crime and Punishment)
    ("преступление и наказанье", "преступление и наказание"),
    ("приступление и наказание", "преступление и наказание"),
    ("преступлене и наказание", "преступление и наказание"),
    
    # Мастер и Маргарита (Master and Margarita)
    ("мастер и маргорита", "мастер и маргарита"),
    ("мастер имаргарита", "мастер и маргарита"),
    ("мастир и маргарита", "мастер и маргарита"),
    
    # Евгений Онегин (Eugene Onegin)
    ("евгений анегин", "евгений онегин"),
    ("евгени онегин", "евгений онегин"),
    ("евгений онигин", "евгений онегин"),
    
    # Братья Карамазовы (Brothers Karamazov)
    ("братья карамазови", "братья карамазовы"),
    ("братя карамазовы", "братья карамазовы"),
    ("братья коромазовы", "братья карамазовы"),
    
    # Mixed Latin/Cyrillic (common typing error)
    ("вoйна и мир", "война и мир"),  # 'o' is Latin, not Cyrillic
    ("мacтep и маргарита", "мастер и маргарита"),  # 'a' and 'c' are Latin
    
    # Abbreviations
    ("вим", "война и мир"),
    ("пин", "преступление и наказание"),
    ("мим", "мастер и маргарита"),
    
    # Author + partial title
    ("толстой война", "война и мир толстой"),
    ("достоевский преступление", "преступление и наказание достоевский"),
    ("булгаков мастер", "мастер и маргарита булгаков"),
    
    # Phonetic in Latin
    ("voyna i mir", "война и мир"),
    ("master i margarita", "мастер и маргарита"),
    ("prestuplenie i nakazanie", "преступление и наказание"),
]

async def test_russian_fuzzy(fuzzy_text, expected=None):
    """Test Russian fuzzy input"""
    normalizer = UnifiedBookNormalizer()
    
    print(f"\n{'='*60}")
    print(f"📖 RUSSIAN INPUT: '{fuzzy_text}'")
    if expected:
        print(f"📋 EXPECTED: '{expected}'")
    print('='*60)
    
    # Process it
    result = await normalizer.normalize_book_query(fuzzy_text)
    
    # Extract results
    normalized = result['final_result']['result']
    confidence = result['final_result']['confidence']
    method = result['final_result']['method']
    detected_type = result.get('detected_type', 'unknown')
    
    print(f"\n🔍 ANALYSIS:")
    print(f"  • Problem detected: {detected_type}")
    print(f"  • Confidence: {confidence:.0%}")
    
    print(f"\n✨ RESULT:")
    print(f"  Input:  '{fuzzy_text}'")
    print(f"  Output: '{normalized}'")
    
    if normalized != fuzzy_text:
        print(f"\n✅ Changed: '{fuzzy_text}' → '{normalized}'")
    else:
        print(f"\n📌 No change (might need Russian-specific rules)")
    
    return normalized

async def test_all_russian_examples():
    """Test all Russian examples"""
    print("\n🇷🇺 TESTING RUSSIAN FUZZY BOOK TITLES")
    print("="*70)
    
    success = 0
    total = len(RUSSIAN_FUZZY_EXAMPLES)
    
    for fuzzy, expected in RUSSIAN_FUZZY_EXAMPLES[:5]:  # Test first 5
        result = await test_russian_fuzzy(fuzzy, expected)
        if result.lower() == expected.lower():
            success += 1
        print("-"*60)
    
    print(f"\n📊 Results: {success}/{5} corrected successfully")
    print("\nNOTE: Full Russian support would need:")
    print("  • Russian-specific typo rules")
    print("  • Cyrillic keyboard layout error patterns")
    print("  • Common Russian book abbreviations")
    print("  • Transliteration support (Latin ↔ Cyrillic)")

# Examples to try manually
MANUAL_TEST_EXAMPLES = [
    "вайна и мир",           # Война и мир with phonetic error
    "мастер имаргарита",     # Мастер и Маргарита without space
    "достоевский братя",     # Dostoevsky + Brothers (typo)
    "prestuplenie",          # Crime and Punishment in Latin
    "толстой вим",          # Tolstoy + abbreviation
    "евгени анегин пушкин",  # Eugene Onegin by Pushkin with typos
]

if __name__ == "__main__":
    print("\n🚀 RUSSIAN FUZZY INPUT TEST")
    print("\nChoose test mode:")
    print("1. Test one specific input")
    print("2. Test all examples")
    print("3. Show manual examples")
    
    # For Claude Code, we'll test one specific example
    TEST_INPUT = "вайна и мир"  # <-- CHANGE THIS TO YOUR RUSSIAN FUZZY INPUT
    
    print(f"\nTesting: '{TEST_INPUT}'")
    asyncio.run(test_russian_fuzzy(TEST_INPUT, "война и мир"))
    
    print("\n" + "="*60)
    print("📝 More Russian fuzzy examples to try:")
    for i, example in enumerate(MANUAL_TEST_EXAMPLES, 1):
        print(f"  {i}. '{example}'")
    print("\nChange TEST_INPUT in the file to test different ones!")