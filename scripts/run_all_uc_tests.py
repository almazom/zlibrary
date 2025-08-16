#!/usr/bin/env python3
"""
Comprehensive UC Test Runner with Feedback Loop
Runs all Use Case tests and provides clear YES/NO EPUB availability results
"""

import asyncio
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import time

class UCTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.downloads_dir = self.project_root / "downloads"
        self.results_dir = self.project_root / "test_results"
        self.results_dir.mkdir(exist_ok=True)
        self.test_results = []
        self.start_time = datetime.now()
        
    def run_book_search(self, query: str, options: str = "") -> Dict[str, Any]:
        """Run book_search.sh and return JSON result"""
        cmd = f"./scripts/book_search.sh {options} \"{query}\""
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            if result.stdout:
                return json.loads(result.stdout)
            else:
                return {
                    "status": "error",
                    "result": {
                        "error": "no_output",
                        "message": "No output from command"
                    }
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "result": {
                    "error": "timeout",
                    "message": "Command timed out after 30 seconds"
                }
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error", 
                "result": {
                    "error": "json_parse_error",
                    "message": str(e),
                    "output": result.stdout if result else ""
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "result": {
                    "error": "execution_error",
                    "message": str(e)
                }
            }
    
    def verify_epub_download(self, result: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Verify EPUB was actually downloaded
        Returns: (success: bool, verdict: YES/NO/ERROR, file_path: Optional[str])
        """
        if result.get("status") == "error":
            return False, "ERROR", None
            
        if result.get("status") == "not_found":
            return True, "NO", None
            
        epub_path = result.get("result", {}).get("epub_download_url")
        download_info = result.get("result", {}).get("download_info", {})
        
        # Check if book was found
        if not result.get("result", {}).get("found"):
            return True, "NO", None
        
        # Check if download was available
        if not download_info.get("available"):
            # Book found but not downloadable (e.g., limit reached)
            return True, "NO", None
            
        # Check if file exists
        if epub_path and Path(epub_path).exists():
            file_size = Path(epub_path).stat().st_size
            if file_size > 10000:  # At least 10KB
                return True, "YES", epub_path
            else:
                return False, "ERROR", f"File too small: {file_size} bytes"
        else:
            return False, "NO", None
    
    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case and return result"""
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"   Query: {test_case['query']}")
        
        # Run the search
        result = self.run_book_search(test_case['query'], test_case.get('options', ''))
        
        # Verify download
        success, verdict, file_path = self.verify_epub_download(result)
        
        # Get confidence and quality scores
        confidence_score = result.get("result", {}).get("confidence", {}).get("score", 0)
        confidence_level = result.get("result", {}).get("confidence", {}).get("level", "UNKNOWN")
        readability_score = result.get("result", {}).get("readability", {}).get("score", 0)
        readability_level = result.get("result", {}).get("readability", {}).get("level", "UNKNOWN")
        
        # Check if result matches expectation
        expected_verdict = test_case.get("expected_verdict", "YES")
        test_passed = verdict == expected_verdict
        
        # Build test result
        test_result = {
            "test_name": test_case['name'],
            "test_category": test_case.get('category', 'general'),
            "query": test_case['query'],
            "expected_verdict": expected_verdict,
            "actual_verdict": verdict,
            "test_passed": test_passed,
            "success": success,
            "confidence": {
                "score": confidence_score,
                "level": confidence_level
            },
            "readability": {
                "score": readability_score,
                "level": readability_level
            },
            "file_path": file_path,
            "book_info": result.get("result", {}).get("book_info", {}),
            "timestamp": datetime.now().isoformat(),
            "raw_result": result
        }
        
        # Print result
        status_icon = "✅" if test_passed else "❌"
        print(f"   {status_icon} Verdict: {verdict} (expected: {expected_verdict})")
        
        if verdict == "YES":
            print(f"   📚 Downloaded: {Path(file_path).name if file_path else 'N/A'}")
            print(f"   🎯 Confidence: {confidence_level} ({confidence_score:.2f})")
            print(f"   📖 Quality: {readability_level} ({readability_score:.2f})")
        elif verdict == "NO":
            print(f"   ℹ️  Book not available/found")
        else:
            print(f"   ⚠️  Error occurred")
            
        return test_result
    
    def run_all_tests(self, test_cases: List[Dict[str, Any]]) -> None:
        """Run all test cases with feedback loop"""
        print("=" * 60)
        print("🚀 UC TEST RUNNER - COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"📅 Started: {self.start_time.isoformat()}")
        print(f"📊 Total tests: {len(test_cases)}")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}]", end="")
            result = self.run_test_case(test_case)
            self.test_results.append(result)
            
            # Small delay between tests
            time.sleep(1)
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
    
    def generate_summary(self) -> None:
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['test_passed'])
        failed = total - passed
        
        yes_count = sum(1 for r in self.test_results if r['actual_verdict'] == 'YES')
        no_count = sum(1 for r in self.test_results if r['actual_verdict'] == 'NO')
        error_count = sum(1 for r in self.test_results if r['actual_verdict'] == 'ERROR')
        
        print(f"✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        print(f"❌ Failed: {failed}/{total} ({failed/total*100:.1f}%)")
        print()
        print(f"📚 EPUBs downloaded: {yes_count}")
        print(f"🚫 Books not found/available: {no_count}")
        print(f"⚠️  Errors: {error_count}")
        
        # Group by category
        categories = {}
        for result in self.test_results:
            cat = result['test_category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'failed': 0, 'total': 0}
            categories[cat]['total'] += 1
            if result['test_passed']:
                categories[cat]['passed'] += 1
            else:
                categories[cat]['failed'] += 1
        
        print("\n📂 By Category:")
        for cat, stats in categories.items():
            print(f"   {cat}: {stats['passed']}/{stats['total']} passed")
        
        # Failed tests details
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['test_passed']:
                    print(f"   - {result['test_name']}")
                    print(f"     Expected: {result['expected_verdict']}, Got: {result['actual_verdict']}")
    
    def save_results(self) -> None:
        """Save test results to JSON file"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        result_file = self.results_dir / f"uc_test_results_{timestamp}.json"
        
        summary = {
            "test_run": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.start_time).total_seconds()
            },
            "statistics": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r['test_passed']),
                "failed": sum(1 for r in self.test_results if not r['test_passed']),
                "epub_downloads": sum(1 for r in self.test_results if r['actual_verdict'] == 'YES'),
                "not_found": sum(1 for r in self.test_results if r['actual_verdict'] == 'NO'),
                "errors": sum(1 for r in self.test_results if r['actual_verdict'] == 'ERROR')
            },
            "test_results": self.test_results
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Results saved: {result_file}")
        
        # Also save a simple verdict file
        verdict_file = self.results_dir / f"uc_verdicts_{timestamp}.txt"
        with open(verdict_file, 'w') as f:
            f.write("UC TEST VERDICTS\n")
            f.write("=" * 60 + "\n\n")
            for result in self.test_results:
                verdict_symbol = "✅" if result['actual_verdict'] == "YES" else "❌"
                f.write(f"{verdict_symbol} {result['test_name']}: {result['actual_verdict']}\n")
                if result['actual_verdict'] == "YES":
                    f.write(f"   Confidence: {result['confidence']['level']} ({result['confidence']['score']:.2f})\n")
                    f.write(f"   Quality: {result['readability']['level']} ({result['readability']['score']:.2f})\n")
                f.write("\n")
        
        print(f"📝 Verdicts saved: {verdict_file}")


def get_test_cases() -> List[Dict[str, Any]]:
    """Define all UC test cases"""
    return [
        # UC1: Successful downloads (should find and download)
        {
            "name": "UC1.1 - Clean Code",
            "category": "UC1_successful",
            "query": "Clean Code Robert Martin",
            "expected_verdict": "YES"
        },
        {
            "name": "UC1.2 - 1984",
            "category": "UC1_successful",
            "query": "1984 George Orwell",
            "expected_verdict": "YES"
        },
        {
            "name": "UC1.3 - Atomic Habits",
            "category": "UC1_successful",
            "query": "Atomic Habits James Clear",
            "expected_verdict": "YES"
        },
        {
            "name": "UC1.4 - Python Crash Course",
            "category": "UC1_successful", 
            "query": "Python Crash Course Eric Matthes",
            "expected_verdict": "YES"
        },
        
        # UC2: Not found (should return NO)
        {
            "name": "UC2.1 - Gibberish",
            "category": "UC2_not_found",
            "query": "qwerty12345 fake book xyz999",
            "expected_verdict": "NO"
        },
        {
            "name": "UC2.2 - Random chars",
            "category": "UC2_not_found",
            "query": "zzzz9999 imaginary title nonexistent",
            "expected_verdict": "NO"
        },
        
        # UC3: URL to EPUB
        {
            "name": "UC3.1 - Podpisnie URL",
            "category": "UC3_url_input",
            "query": "https://www.podpisnie.ru/books/maniac/",
            "expected_verdict": "YES"
        },
        
        # UC4: Duplicate detection (run same book twice)
        {
            "name": "UC4.1 - First download",
            "category": "UC4_duplicate",
            "query": "The Pragmatic Programmer",
            "expected_verdict": "YES"
        },
        {
            "name": "UC4.2 - Duplicate check",
            "category": "UC4_duplicate",
            "query": "The Pragmatic Programmer",
            "expected_verdict": "YES"  # Should still say YES but use cached
        },
        
        # UC5: Quality filtering with strict mode
        {
            "name": "UC5.1 - High quality book",
            "category": "UC5_quality",
            "query": "Design Patterns Gang of Four",
            "options": "--strict",
            "expected_verdict": "YES"
        },
        
        # UC6: PDF fallback
        {
            "name": "UC6.1 - PDF format",
            "category": "UC6_pdf",
            "query": "Introduction to Algorithms Cormen",
            "options": "--format pdf",
            "expected_verdict": "YES"
        },
        
        # Edge cases
        {
            "name": "UC_Edge.1 - Unicode",
            "category": "edge_cases",
            "query": "最危险的书 Ulysses Joyce",
            "expected_verdict": "YES"
        },
        {
            "name": "UC_Edge.2 - C++ book",
            "category": "edge_cases",
            "query": "C++ Programming Language Stroustrup",
            "expected_verdict": "YES"
        },
        {
            "name": "UC_Edge.3 - Just title",
            "category": "edge_cases",
            "query": "Ulysses",
            "expected_verdict": "YES"
        },
        
        # Russian books
        {
            "name": "UC_Russian.1",
            "category": "russian",
            "query": "Мастер и Маргарита Булгаков",
            "expected_verdict": "YES"
        },
        {
            "name": "UC_Russian.2",
            "category": "russian",
            "query": "Война и мир Толстой",
            "expected_verdict": "YES"
        },
        
        # Popular modern books
        {
            "name": "UC_Popular.1",
            "category": "popular",
            "query": "Harry Potter philosopher stone",
            "expected_verdict": "YES"
        },
        {
            "name": "UC_Popular.2",
            "category": "popular",
            "query": "Sapiens Yuval Noah Harari",
            "expected_verdict": "YES"
        },
        {
            "name": "UC_Popular.3",
            "category": "popular",
            "query": "Thinking Fast and Slow Kahneman",
            "expected_verdict": "YES"
        }
    ]


def main():
    """Main entry point"""
    runner = UCTestRunner()
    test_cases = get_test_cases()
    
    # Add option to run specific category
    if len(sys.argv) > 1:
        category = sys.argv[1]
        test_cases = [tc for tc in test_cases if tc.get('category') == category]
        if not test_cases:
            print(f"No tests found for category: {category}")
            print("Available categories:", set(tc.get('category') for tc in get_test_cases()))
            sys.exit(1)
    
    runner.run_all_tests(test_cases)
    
    # Return exit code based on test results
    failed = sum(1 for r in runner.test_results if not r['test_passed'])
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()