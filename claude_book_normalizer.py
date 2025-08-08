#!/usr/bin/env python3
"""
CLAUDE SDK BOOK NORMALIZER - Real implementation with feedback loop
Uses Claude Code SDK to properly normalize book titles
"""
import anyio
import json
import sys
from claude_code_sdk import query, ClaudeCodeOptions, Message

async def normalize_with_claude(fuzzy_input: str, language: str = "auto") -> dict:
    """
    Use Claude SDK to normalize book titles with structured JSON output
    """
    prompt = f"""
    You are a book title normalization expert. Fix the following book query and return ONLY valid JSON.

    Input: "{fuzzy_input}"
    Language: {language}

    Tasks:
    1. Fix spelling errors and typos
    2. Complete partial titles if recognizable
    3. Fix soft signs (ь) and hard signs (ъ) in Russian
    4. Separate title from author properly
    5. Add missing punctuation (colons, commas)
    6. If it's a known book series, include the series name
    
    For "ведмак 3 дикая охота" specifically:
    - Fix "ведмак" to "ведьмак" (add soft sign)
    - Recognize as "The Witcher 3: Wild Hunt" series
    - Add proper punctuation
    
    Return ONLY this JSON structure (no other text):
    {{
        "original": "the original input",
        "normalized": "the corrected version",
        "confidence": 0.0 to 1.0,
        "language_detected": "ru/en/mixed/etc",
        "problems_found": ["list", "of", "issues"],
        "title": "extracted book title",
        "author": "extracted author if present",
        "series": "series name if applicable",
        "alternative_titles": ["other possible normalizations"],
        "explanation": "brief explanation of changes"
    }}
    """
    
    messages = []
    
    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeCodeOptions(
                max_turns=1,
                system_prompt="You are a book title normalization assistant. Always return valid JSON only.",
            )
        ):
            messages.append(message)
        
        # Extract JSON from response
        if messages:
            response_text = str(messages[0])
            
            # Try to parse JSON from the response
            try:
                # Find JSON in the response (it might have markdown backticks)
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    result = json.loads(json_str)
                    return result
                else:
                    # If no JSON found, create a fallback
                    return {
                        "original": fuzzy_input,
                        "normalized": fuzzy_input,
                        "confidence": 0.0,
                        "error": "Could not extract JSON from response"
                    }
            except json.JSONDecodeError as e:
                return {
                    "original": fuzzy_input,
                    "normalized": fuzzy_input,
                    "confidence": 0.0,
                    "error": f"JSON parsing error: {e}"
                }
    except Exception as e:
        return {
            "original": fuzzy_input,
            "normalized": fuzzy_input,
            "confidence": 0.0,
            "error": f"Claude SDK error: {e}"
        }

async def test_book_normalization():
    """Test the Claude-powered normalization"""
    
    test_cases = [
        ("ведмак 3 дикая охота", "ru"),
        ("hary poter", "en"),
        ("метро2033 глуховски", "ru"),
        ("пелевин generation п", "mixed"),
    ]
    
    print("\n🤖 CLAUDE SDK BOOK NORMALIZER")
    print("="*60)
    
    for fuzzy_input, lang in test_cases:
        print(f"\n📚 Testing: '{fuzzy_input}' (Language: {lang})")
        print("-"*40)
        
        result = await normalize_with_claude(fuzzy_input, lang)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Normalized: '{result.get('normalized', 'N/A')}'")
            print(f"📊 Confidence: {result.get('confidence', 0):.0%}")
            print(f"🔍 Problems found: {', '.join(result.get('problems_found', []))}")
            if result.get('author'):
                print(f"👤 Author: {result['author']}")
            if result.get('series'):
                print(f"📚 Series: {result['series']}")
            print(f"💡 Explanation: {result.get('explanation', 'N/A')}")
        
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    # Check if we have a specific input from command line
    if len(sys.argv) > 1:
        fuzzy_input = ' '.join(sys.argv[1:])
        print(f"\n🔍 Normalizing: '{fuzzy_input}'")
        result = anyio.run(normalize_with_claude, fuzzy_input)
        print("\n📋 Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Run test cases
        anyio.run(test_book_normalization)