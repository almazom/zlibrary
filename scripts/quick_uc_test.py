#!/usr/bin/env python3
"""
Quick UC Test Runner - Simple and Fast
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def run_test(query, name="Test"):
    """Run a single test and return clear YES/NO result"""
    print(f"\n🔍 {name}")
    print(f"   Query: {query}")
    
    try:
        result = subprocess.run(
            f'./scripts/book_search.sh "{query}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=Path(__file__).parent
        )
        
        if result.stdout:
            data = json.loads(result.stdout)
            
            # Determine verdict
            verdict = "ERROR"
            confidence = 0
            
            if data.get("status") == "not_found":
                verdict = "NO"
            elif data.get("status") == "success":
                if data.get("result", {}).get("found"):
                    download_path = data.get("result", {}).get("epub_download_url")
                    if download_path and Path(download_path).exists():
                        verdict = "YES"
                        confidence = data.get("result", {}).get("confidence", {}).get("score", 0)
                    else:
                        verdict = "NO"
                else:
                    verdict = "NO"
            
            # Print result
            if verdict == "YES":
                conf_level = data.get("result", {}).get("confidence", {}).get("level", "?")
                print(f"   ✅ EPUB: YES (Confidence: {conf_level} {confidence:.2f})")
            elif verdict == "NO":
                print(f"   ❌ EPUB: NO (Book not found/available)")
            else:
                print(f"   ⚠️  EPUB: ERROR")
                
            return verdict, data
            
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
        return "ERROR", None

def main():
    print("=" * 60)
    print("🚀 QUICK UC TEST - EPUB AVAILABILITY CHECK")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Define test cases
    tests = [
        # Should find and download
        ("Clean Code Robert Martin", "UC1.1 - Programming Book"),
        ("1984 George Orwell", "UC1.2 - Classic Fiction"),
        ("Atomic Habits James Clear", "UC1.3 - Self-Help"),
        
        # Should NOT find
        ("xyz999 fake book qwerty", "UC2.1 - Non-existent Book"),
        
        # URL input
        ("https://www.podpisnie.ru/books/maniac/", "UC3.1 - URL Input"),
        
        # Edge cases
        ("Ulysses", "UC_Edge - Just Title"),
        ("Python Programming", "UC_Edge - Generic Search"),
        
        # Russian
        ("Война и мир Толстой", "UC_Russian - Russian Book"),
    ]
    
    results = []
    yes_count = 0
    no_count = 0
    error_count = 0
    
    for query, name in tests:
        verdict, data = run_test(query, name)
        results.append({
            "name": name,
            "query": query,
            "verdict": verdict
        })
        
        if verdict == "YES":
            yes_count += 1
        elif verdict == "NO":
            no_count += 1
        else:
            error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ EPUBs Available: {yes_count}")
    print(f"❌ Not Available: {no_count}")
    print(f"⚠️  Errors: {error_count}")
    print(f"📚 Total Tests: {len(tests)}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"test_results/quick_test_{timestamp}.json"
    Path("test_results").mkdir(exist_ok=True)
    
    with open(result_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "yes": yes_count,
                "no": no_count,
                "error": error_count,
                "total": len(tests)
            },
            "tests": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved: {result_file}")
    
    # Clear YES/NO answer
    print("\n" + "=" * 60)
    print("🎯 FINAL VERDICT")
    print("=" * 60)
    
    for result in results:
        status = "✅" if result["verdict"] == "YES" else "❌" if result["verdict"] == "NO" else "⚠️"
        print(f"{status} {result['name']}: {result['verdict']}")

if __name__ == "__main__":
    main()