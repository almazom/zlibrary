#!/usr/bin/env python3
"""
Comprehensive Test Suite for TXT to EPUB Service
Tests various scenarios and confidence levels
"""

import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from txt_to_epub_service import TextToEPUBService

class TxtServiceTester:
    """Test the TXT to EPUB service comprehensively"""
    
    def __init__(self):
        self.service = TextToEPUBService()
        self.test_cases = [
            # Expected VERY_HIGH confidence
            {
                "text": "Harry Potter philosopher stone",
                "expectation": "VERY_HIGH",
                "reason": "Exact title match"
            },
            {
                "text": "Clean Code Robert Martin",
                "expectation": "HIGH",
                "reason": "Title + author match"
            },
            {
                "text": "Maniac Benjamin Labatut",
                "expectation": "MEDIUM", 
                "reason": "Good title + author match"
            },
            
            # Expected MEDIUM confidence
            {
                "text": "Python programming machine learning",
                "expectation": "MEDIUM",
                "reason": "General programming topic"
            },
            {
                "text": "Гарри Поттер философский камень",
                "expectation": "HIGH",
                "reason": "Russian Harry Potter title"
            },
            
            # Expected LOW confidence
            {
                "text": "some random book that doesnt exist",
                "expectation": "LOW",
                "reason": "Random text"
            },
            {
                "text": "хьбиуфвбиу некая книга 12345",
                "expectation": "VERY_LOW",
                "reason": "Gibberish text"
            },
            
            # Edge cases
            {
                "text": "a",
                "expectation": "ANY",
                "reason": "Single character"
            },
            {
                "text": "1984 George Orwell dystopia",
                "expectation": "HIGH",
                "reason": "Classic book with author"
            },
            {
                "text": "Новалис мистический мир",
                "expectation": "LOW",
                "reason": "Specific philosophical book"
            }
        ]
    
    async def run_comprehensive_tests(self):
        """Run all test cases and analyze results"""
        
        print("🧪 Comprehensive TXT to EPUB Service Testing")
        print("=" * 70)
        print(f"Running {len(self.test_cases)} test cases...")
        
        results = []
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📝 Test {i}/{len(self.test_cases)}: '{test_case['text']}'")
            print(f"   Expected: {test_case['expectation']} ({test_case['reason']})")
            print("-" * 50)
            
            # Run the test
            result = await self.service.search_book_from_text(test_case['text'])
            
            # Analyze result
            test_result = {
                "test_case": test_case,
                "response": result,
                "analysis": self.analyze_result(result, test_case)
            }
            results.append(test_result)
            
            # Print immediate analysis
            self.print_test_analysis(test_result)
        
        # Final summary
        self.print_final_summary(results)
        return results
    
    def analyze_result(self, result, test_case):
        """Analyze if the result meets expectations"""
        analysis = {
            "status_ok": result["status"] in ["success", "not_found"],
            "schema_valid": self.validate_schema(result),
            "confidence_reasonable": False,
            "expectation_met": False,
            "notes": []
        }
        
        if result["status"] == "success":
            confidence = result["result"]["confidence"]
            confidence_level = confidence["level"]
            
            # Check if confidence is reasonable
            if confidence["score"] >= 0.0 and confidence["score"] <= 1.0:
                analysis["confidence_reasonable"] = True
            
            # Check expectation
            expected = test_case["expectation"]
            if expected == "ANY":
                analysis["expectation_met"] = True
                analysis["notes"].append("Any result acceptable")
            elif expected == confidence_level:
                analysis["expectation_met"] = True
                analysis["notes"].append("Confidence level matches expectation")
            else:
                analysis["notes"].append(f"Expected {expected}, got {confidence_level}")
        
        elif result["status"] == "not_found":
            if test_case["expectation"] in ["VERY_LOW", "LOW"]:
                analysis["expectation_met"] = True
                analysis["notes"].append("Expected low confidence, got not found")
            else:
                analysis["notes"].append("Unexpected not found result")
        
        return analysis
    
    def validate_schema(self, result):
        """Validate that response follows the schema"""
        required_fields = ["status", "timestamp", "input_format", "query_info", "result"]
        
        for field in required_fields:
            if field not in result:
                return False
        
        if result["input_format"] != "txt":
            return False
            
        if "original_input" not in result["query_info"]:
            return False
            
        return True
    
    def print_test_analysis(self, test_result):
        """Print analysis for a single test"""
        result = test_result["response"]
        analysis = test_result["analysis"]
        
        if result["status"] == "success":
            confidence = result["result"]["confidence"]
            book_info = result["result"]["book_info"]
            
            print(f"   📚 FOUND: {book_info['title'][:40]}...")
            print(f"   👥 Authors: {', '.join(book_info['authors'][:2])}")
            print(f"   🎯 Confidence: {confidence['level']} ({confidence['score']:.3f})")
            print(f"   ✅ Recommended: {'YES' if confidence['recommended'] else 'NO'}")
        elif result["status"] == "not_found":
            print(f"   ❌ NOT FOUND: {result['result']['message']}")
        else:
            print(f"   💥 ERROR: {result['result'].get('error', 'Unknown')}")
        
        # Analysis
        status_icon = "✅" if analysis["status_ok"] else "❌"
        schema_icon = "✅" if analysis["schema_valid"] else "❌"
        expect_icon = "✅" if analysis["expectation_met"] else "⚠️"
        
        print(f"   {status_icon} Status OK | {schema_icon} Schema Valid | {expect_icon} Expectation Met")
        
        if analysis["notes"]:
            for note in analysis["notes"]:
                print(f"   📄 {note}")
    
    def print_final_summary(self, results):
        """Print final test summary"""
        print(f"\n{'='*70}")
        print("📊 FINAL TEST SUMMARY")
        print(f"{'='*70}")
        
        total_tests = len(results)
        status_ok = sum(1 for r in results if r["analysis"]["status_ok"])
        schema_valid = sum(1 for r in results if r["analysis"]["schema_valid"])
        expectations_met = sum(1 for r in results if r["analysis"]["expectation_met"])
        confidence_reasonable = sum(1 for r in results if r["analysis"]["confidence_reasonable"])
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Status OK: {status_ok}/{total_tests} ({status_ok/total_tests*100:.1f}%)")
        print(f"📋 Schema Valid: {schema_valid}/{total_tests} ({schema_valid/total_tests*100:.1f}%)")
        print(f"🎯 Expectations Met: {expectations_met}/{total_tests} ({expectations_met/total_tests*100:.1f}%)")
        print(f"🔢 Confidence Reasonable: {confidence_reasonable}/{total_tests} ({confidence_reasonable/total_tests*100:.1f}%)")
        
        # Overall score
        overall_score = (status_ok + schema_valid + expectations_met) / (total_tests * 3) * 100
        print(f"\n🏆 OVERALL SCORE: {overall_score:.1f}%")
        
        if overall_score >= 90:
            print("🌟 EXCELLENT - Service is working very well!")
        elif overall_score >= 75:
            print("👍 GOOD - Service is working well with minor issues")
        elif overall_score >= 60:
            print("⚠️ FAIR - Service has some issues that need attention")
        else:
            print("❌ POOR - Service needs significant improvements")

async def main():
    """Run the comprehensive test suite"""
    tester = TxtServiceTester()
    results = await tester.run_comprehensive_tests()
    
    # Optionally save detailed results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to test_results.json")

if __name__ == "__main__":
    asyncio.run(main())