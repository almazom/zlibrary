#!/usr/bin/env python3
"""
INTERACTIVE MANUAL TEST - Type fuzzy book titles and see normalization
"""
import asyncio
import sys
sys.path.insert(0, '.')
from book_normalization_system import UnifiedBookNormalizer

async def interactive_test():
    normalizer = UnifiedBookNormalizer()
    
    print("\n" + "="*60)
    print("📚 INTERACTIVE BOOK NORMALIZATION TEST")
    print("="*60)
    print("\nType fuzzy/misspelled book titles and see how they get fixed!")
    print("\nExamples to try:")
    print("  • hary poter")
    print("  • pyhton programing")
    print("  • gatsby")
    print("  • hp")
    print("  • 1984")
    print("  • jorj orwell")
    print("\nType 'quit' to exit\n")
    
    while True:
        # Get user input
        user_input = input("📖 Enter fuzzy book title: ").strip()
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Process the fuzzy input
        print(f"\n🔍 Processing: '{user_input}'")
        print("-" * 40)
        
        result = await normalizer.normalize_book_query(user_input)
        
        # Get the normalized result
        normalized = result['final_result']['result']
        confidence = result['final_result']['confidence']
        method = result['final_result']['method']
        detected_type = result.get('detected_type', 'unknown')
        
        # Show results
        print(f"✨ Normalized: '{normalized}'")
        print(f"📊 Confidence: {confidence:.0%}")
        print(f"🔧 Method: {method}")
        print(f"🏷️  Type detected: {detected_type}")
        
        # Show the change
        if normalized.lower() != user_input.lower():
            print(f"\n✅ FIXED: '{user_input}' → '{normalized}'")
        else:
            print(f"\n📌 No change needed (or couldn't fix)")
        
        print("\n" + "="*60 + "\n")

# Run the interactive test
asyncio.run(interactive_test())