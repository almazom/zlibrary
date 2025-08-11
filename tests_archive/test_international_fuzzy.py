#!/usr/bin/env python3
"""
INTERNATIONAL FUZZY INPUT TESTS
Testing Claude SDK normalizer with books from Japan, France, Italy, and Russian fuzzy inputs
"""
import asyncio
import sys
sys.path.insert(0, '.')
from claude_sdk_normalizer import ClaudeSDKNormalizer

# International fuzzy test cases
INTERNATIONAL_FUZZY_CASES = [
    # Russian fuzzy inputs
    ("пелевин чапаев и пустата", "Russian", "typo in 'пустота'"),
    ("достоевский преступление и наказанье", "Russian", "old spelling 'наказанье'"),
    ("солженицин один ден ивана денисовича", "Russian", "typos and missing letters"),
    ("булгаков мастер и маргорита", "Russian", "typo in 'маргарита'"),
    
    # Japanese books (romanized with errors)
    ("norvegski les murakam", "Japanese", "Norwegian Wood by Murakami with typos"),
    ("kafk na beragy hakidzi murakam", "Japanese", "Kafka on the Shore with multiple typos"),
    ("kolorit tseles yoshigar banan", "Japanese", "Colorless Tsukuru by Haruki Murakami"),
    ("batalii roial kosigun takam", "Japanese", "Battle Royale by Koushun Takami"),
    
    # French books with errors
    ("malenkiy prinz sent eksyuper", "French", "Le Petit Prince with Russian/French mix"),
    ("graff monte kristo duma", "French", "The Count of Monte Cristo"),
    ("chuzhoy kamyu", "French", "L'Étranger by Camus in Russian"),
    ("madamm bovar flober", "French", "Madame Bovary with typos"),
    
    # Italian books with errors
    ("bozhestvenna komedia dant", "Italian", "Divine Comedy in Russian"),
    ("imea roza umbert eko", "Italian", "Name of the Rose by Umberto Eco"),
    ("dekameron bokachi", "Italian", "Decameron by Boccaccio"),
    ("leopard lampeduza", "Italian", "Il Gattopardo"),
    
    # German books
    ("metamorfoza kafka", "German", "Die Verwandlung by Kafka"),
    ("faist gete", "German", "Faust by Goethe"),
    ("buddenbroki man", "German", "Buddenbrooks by Thomas Mann"),
    
    # Mixed language confusion
    ("master margarita bulgakov", "Russian", "mixed English-Russian"),
    ("war peace tolstoi", "Russian", "English title with author"),
    ("crime punishment dostoevsky", "Russian", "English title"),
]

async def test_international_fuzzy():
    """Test international fuzzy inputs with enhanced Claude SDK"""
    
    normalizer = ClaudeSDKNormalizer()
    
    print("\n🌍 INTERNATIONAL FUZZY INPUT TEST")
    print("=" * 80)
    print("Testing books from Japan, France, Italy, Germany with fuzzy Russian inputs")
    
    results = []
    
    for i, (fuzzy_input, origin_language, description) in enumerate(INTERNATIONAL_FUZZY_CASES[:8], 1):
        print(f"\n📚 TEST {i}/8: {description}")
        print("=" * 60)
        print(f"🔍 Input: '{fuzzy_input}' (Expected origin: {origin_language})")
        
        result = normalizer.normalize_book_title(fuzzy_input, origin_language.lower())
        
        if result['success']:
            print(f"✅ Success! Confidence: {result['confidence']:.0%}")
            
            # Show original language version
            orig_lang = result.get('original_language_version', {})
            if orig_lang.get('title'):
                title = orig_lang['title']
                author = orig_lang.get('author', 'Unknown')
                lang_code = orig_lang.get('language_code', 'unknown')
                
                # Show romanized version if available
                romanized_title = orig_lang.get('title_romanized', '')
                romanized_author = orig_lang.get('author_romanized', '')
                
                print(f"🌍 Original ({lang_code}): {title} - {author}")
                if romanized_title or romanized_author:
                    print(f"🔤 Romanized: {romanized_title or title} - {romanized_author or author}")
            
            # Show Russian version
            rus_lang = result.get('russian_language_version', {})
            if rus_lang.get('title'):
                rus_title = rus_lang['title']
                rus_author = rus_lang.get('author', 'Unknown')
                translator = rus_lang.get('translator', '')
                print(f"🇷🇺 Russian: {rus_title} - {rus_author}")
                if translator:
                    print(f"📖 Translator: {translator}")
            
            # Show what was fixed
            problems = result.get('problems_found', [])
            if problems:
                print(f"🔧 Fixed: {', '.join(problems[:3])}")
            
            # Internet research info
            research = result.get('internet_research', {})
            if research.get('found_book'):
                print(f"🔍 Found: {research.get('original_language', 'unknown')} book")
                if research.get('original_country'):
                    print(f"🏴 Origin: {research['original_country']}")
        
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        results.append(result)
        
        print("-" * 60)
        await asyncio.sleep(1)  # Brief pause
    
    # Summary statistics
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\n📊 SUMMARY: {successful}/{len(results)} successful normalizations")
    
    return results

if __name__ == "__main__":
    # Test specific case or run all
    if len(sys.argv) > 1:
        test_input = ' '.join(sys.argv[1:])
        normalizer = ClaudeSDKNormalizer()
        
        print(f"\n🧪 Testing: '{test_input}'")
        result = normalizer.normalize_book_title(test_input)
        
        print("\n📋 Full Result:")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        asyncio.run(test_international_fuzzy())