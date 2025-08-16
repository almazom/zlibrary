#!/usr/bin/env python3
"""
Test fast cognitive validation speed
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, '/home/almaz/microservices/zlibrary_api_module/src')
from pipeline.cognitive_validator import CognitiveValidator

# Test cases
test_cases = [
    ("Stephen King It", "downloads/Zagovor_protiv_russkoy_istorii.epub"),
    ("Заговор против русской истории", "downloads/Zagovor_protiv_russkoy_istorii.epub"),
    ("Алехин Календарь", "downloads/II trattato.epub"),
]

validator = CognitiveValidator(verbose=False)

print("Testing Fast Cognitive Validation Speed")
print("=" * 50)

for user_request, epub_file in test_cases:
    epub_path = Path(epub_file)
    if not epub_path.exists():
        print(f"⚠️ File not found: {epub_file}")
        continue
    
    print(f"\n📚 Request: {user_request}")
    print(f"📄 File: {epub_path.name}")
    
    # Time the validation
    start = time.time()
    result = validator.validate_and_report(user_request, str(epub_path))
    duration = time.time() - start
    
    # Show results
    print(f"⏱️  Time: {duration:.2f}s")
    print(f"🎯 Confidence: {result.get('confidence', 0):.0%}")
    print(f"📊 Quality: {result.get('match_quality', 'unknown')}")
    print(f"🧠 Method: {'AI-assisted' if result.get('intelligent_match') else 'Fast pattern matching'}")
    print(f"💬 Feedback: {result.get('feedback', 'N/A')}")

print("\n" + "=" * 50)
print("✅ Speed test complete!")