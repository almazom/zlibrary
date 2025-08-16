#!/usr/bin/env python3
"""
GUIDED MANUAL TEST - Test specific fuzzy inputs one at a time
"""
import asyncio
import sys
sys.path.insert(0, '.')
from book_normalization_system import UnifiedBookNormalizer

async def test_fuzzy_input(fuzzy_text):
    """Test a single fuzzy input and show detailed results"""
    normalizer = UnifiedBookNormalizer()
    
    print("\n" + "="*60)
    print(f"📖 YOUR INPUT: '{fuzzy_text}'")
    print("="*60)
    
    # Process it
    result = await normalizer.normalize_book_query(fuzzy_text)
    
    # Extract results
    normalized = result['final_result']['result']
    confidence = result['final_result']['confidence']
    method = result['final_result']['method']
    detected_type = result.get('detected_type', 'unknown')
    
    # Show what happened
    print(f"\n🔍 ANALYSIS:")
    print(f"  • Problem detected: {detected_type}")
    print(f"  • Fix method used: {method}")
    print(f"  • Confidence level: {confidence:.0%}")
    
    print(f"\n✨ RESULT:")
    print(f"  Before: '{fuzzy_text}'")
    print(f"  After:  '{normalized}'")
    
    if normalized.lower() != fuzzy_text.lower():
        print(f"\n✅ SUCCESS! Fixed the fuzzy input!")
    else:
        print(f"\n⚠️  Could not fix (might be correct already)")
    
    # Show all attempts made
    if len(result.get('all_attempts', [])) > 1:
        print(f"\n📋 All strategies tried:")
        for attempt in result['all_attempts']:
            print(f"  • {attempt['method']}: '{attempt['result']}' (confidence: {attempt['confidence']})")
    
    return normalized

# Test list - we'll go through these one by one
test_cases = [
    "hary poter and the filosofer stone",  # Typos
    "pyhton for data scince",              # Technical typos
    "hp",                                   # Abbreviation
    "gatsby",                               # Partial title
    "1984",                                 # Book that needs author
    "rowling harry potter",                # Author first
    "jorj orwell",                         # Phonetic spelling
    "the grat gatsbee",                    # Classic with typos
]

async def run_guided_test():
    print("\n🎯 GUIDED MANUAL TEST - We'll test fuzzy inputs one by one")
    print("="*60)
    
    # Test each case
    for i, test in enumerate(test_cases, 1):
        print(f"\n📌 TEST {i}/{len(test_cases)}")
        result = await test_fuzzy_input(test)
        print("\n" + "-"*60)
        
        # Ask to continue (in Claude Code, just show the prompt)
        print("\n➡️  Ready for next test? (In Claude Code, run the script again for next)")
        print("="*60)
        
        # Add a small delay so output is readable
        await asyncio.sleep(0.1)

# Run the first test
if __name__ == "__main__":
    # You can change this to test any fuzzy input you want!
    TEST_YOUR_INPUT = "hary poter"  # <-- CHANGE THIS TO YOUR FUZZY INPUT
    
    print(f"\n🚀 Testing YOUR fuzzy input: '{TEST_YOUR_INPUT}'")
    asyncio.run(test_fuzzy_input(TEST_YOUR_INPUT))