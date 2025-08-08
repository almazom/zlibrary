#!/usr/bin/env python3
"""
Test Suite for Enhanced Bash Script
Tests all input types and functionality
"""

import subprocess
import json
import time
from pathlib import Path

class EnhancedScriptTester:
    """Test the enhanced bash script comprehensively"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent / "scripts" / "zlib_search_enhanced.sh"
        self.test_cases = [
            # URL inputs
            {
                "input": "https://www.podpisnie.ru/books/maniac/",
                "expected_format": "url",
                "expectation": "HIGH",
                "description": "Maniac URL from podpisnie.ru"
            },
            {
                "input": "https://www.podpisnie.ru/books/misticheskiy-mir-novalisa-filosofiya-traditsiya-poetika-poetika-monografiya/",
                "expected_format": "url", 
                "expectation": "LOW",
                "description": "Complex Novalis URL"
            },
            
            # Text inputs
            {
                "input": "Harry Potter philosopher stone",
                "expected_format": "txt",
                "expectation": "VERY_HIGH",
                "description": "Popular book with exact title"
            },
            {
                "input": "Clean Code Robert Martin programming",
                "expected_format": "txt",
                "expectation": "HIGH", 
                "description": "Programming book with author"
            },
            {
                "input": "Гарри Поттер философский камень",
                "expected_format": "txt",
                "expectation": "HIGH",
                "description": "Russian Harry Potter title"
            },
            
            # Edge cases
            {
                "input": "a",
                "expected_format": "txt",
                "expectation": "ANY",
                "description": "Single character"
            },
            {
                "input": "some very random book that probably doesnt exist in any library",
                "expected_format": "txt",
                "expectation": "LOW",
                "description": "Long random text"
            },
            
            # Image placeholder (will fail gracefully)
            {
                "input": "/path/to/book/cover.jpg",
                "expected_format": "image",
                "expectation": "ERROR",
                "description": "Image input (not implemented)"
            }
        ]
    
    def run_script(self, input_text, extra_args=None):
        """Run the enhanced script with given input"""
        cmd = [str(self.script_path)]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(input_text)
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "parsed_json": json.loads(result.stdout) if result.stdout.strip() else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout",
                "stdout": "",
                "stderr": "Command timed out after 60 seconds"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": "invalid_json",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "json_error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "execution_error",
                "exception": str(e)
            }
    
    def validate_response_schema(self, response):
        """Validate that response follows our standardized schema"""
        required_fields = ["status", "timestamp", "input_format", "query_info", "result"]
        
        for field in required_fields:
            if field not in response:
                return False, f"Missing required field: {field}"
        
        # Validate query_info
        query_info = response["query_info"]
        if "original_input" not in query_info or "extracted_query" not in query_info:
            return False, "Missing fields in query_info"
        
        # Validate result based on status
        result = response["result"]
        if response["status"] == "success":
            success_fields = ["found", "epub_download_url", "confidence", "book_info", "service_used"]
            for field in success_fields:
                if field not in result:
                    return False, f"Missing field in success result: {field}"
        
        return True, "Schema valid"
    
    def analyze_confidence(self, response, expected_level):
        """Analyze confidence level against expectations"""
        if response["status"] != "success":
            return "N/A", "Response not successful"
        
        confidence = response["result"]["confidence"]
        actual_level = confidence["level"]
        actual_score = confidence["score"]
        
        if expected_level == "ANY":
            return "MATCH", f"Any level acceptable, got {actual_level}"
        elif expected_level == actual_level:
            return "EXACT_MATCH", f"Expected {expected_level}, got {actual_level}"
        elif expected_level == "ERROR":
            return "MISMATCH", f"Expected error, got {actual_level}"
        else:
            return "MISMATCH", f"Expected {expected_level}, got {actual_level}"
    
    def run_comprehensive_tests(self):
        """Run all test cases"""
        print("🚀 Enhanced Script Comprehensive Testing")
        print("=" * 70)
        print(f"Testing {len(self.test_cases)} cases...")
        
        results = []
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📝 Test {i}/{len(self.test_cases)}: {test_case['description']}")
            print(f"   Input: '{test_case['input']}'")
            print(f"   Expected: {test_case['expected_format']} format, {test_case['expectation']} confidence")
            print("-" * 50)
            
            start_time = time.time()
            result = self.run_script(test_case['input'])
            execution_time = time.time() - start_time
            
            analysis = {
                "test_case": test_case,
                "execution_result": result,
                "execution_time": execution_time,
                "schema_valid": False,
                "format_correct": False,
                "confidence_analysis": "N/A",
                "overall_status": "FAIL"
            }
            
            if result["success"] and result["parsed_json"]:
                response = result["parsed_json"]
                
                # Validate schema
                schema_valid, schema_msg = self.validate_response_schema(response)
                analysis["schema_valid"] = schema_valid
                analysis["schema_message"] = schema_msg
                
                # Check input format
                actual_format = response.get("input_format", "unknown")
                analysis["format_correct"] = actual_format == test_case["expected_format"]
                
                # Analyze confidence
                conf_status, conf_msg = self.analyze_confidence(response, test_case["expectation"])
                analysis["confidence_analysis"] = conf_status
                analysis["confidence_message"] = conf_msg
                
                # Overall status
                if schema_valid and analysis["format_correct"] and conf_status in ["MATCH", "EXACT_MATCH"]:
                    analysis["overall_status"] = "PASS"
                elif schema_valid and response["status"] in ["success", "not_found"]:
                    analysis["overall_status"] = "PARTIAL"
                
                # Print results
                print(f"   📊 Status: {response['status'].upper()}")
                if response["status"] == "success":
                    book_info = response["result"]["book_info"]
                    confidence = response["result"]["confidence"]
                    print(f"   📚 Found: {book_info['title'][:50]}")
                    print(f"   🎯 Confidence: {confidence['level']} ({confidence['score']:.3f})")
                    print(f"   ✅ Recommended: {'YES' if confidence['recommended'] else 'NO'}")
                elif response["status"] == "error":
                    print(f"   💥 Error: {response['result']['error']}")
                
            else:
                print(f"   ❌ Execution failed: {result.get('error', 'Unknown error')}")
            
            # Analysis summary
            status_icon = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}[analysis["overall_status"]]
            format_icon = "✅" if analysis["format_correct"] else "❌"
            schema_icon = "✅" if analysis["schema_valid"] else "❌"
            
            print(f"   {status_icon} Overall | {format_icon} Format | {schema_icon} Schema | ⏱️ {execution_time:.1f}s")
            
            results.append(analysis)
        
        # Final summary
        self.print_final_summary(results)
        return results
    
    def print_final_summary(self, results):
        """Print comprehensive test summary"""
        print(f"\n{'='*70}")
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*70}")
        
        total_tests = len(results)
        passed = sum(1 for r in results if r["overall_status"] == "PASS")
        partial = sum(1 for r in results if r["overall_status"] == "PARTIAL")
        failed = sum(1 for r in results if r["overall_status"] == "FAIL")
        
        schema_valid = sum(1 for r in results if r["schema_valid"])
        format_correct = sum(1 for r in results if r["format_correct"])
        avg_time = sum(r["execution_time"] for r in results) / total_tests
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
        print(f"⚠️ Partial: {partial} ({partial/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
        print(f"📋 Schema Valid: {schema_valid}/{total_tests} ({schema_valid/total_tests*100:.1f}%)")
        print(f"🎯 Format Detection: {format_correct}/{total_tests} ({format_correct/total_tests*100:.1f}%)")
        print(f"⏱️ Average Time: {avg_time:.2f}s")
        
        # Overall score
        success_rate = (passed + partial * 0.5) / total_tests * 100
        
        print(f"\n🏆 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🌟 EXCELLENT - Enhanced script working exceptionally well!")
        elif success_rate >= 75:
            print("👍 GOOD - Enhanced script working well with minor issues")
        elif success_rate >= 60:
            print("⚠️ FAIR - Enhanced script has some issues that need attention")
        else:
            print("❌ POOR - Enhanced script needs significant improvements")

def main():
    """Run the comprehensive test suite"""
    tester = EnhancedScriptTester()
    results = tester.run_comprehensive_tests()
    
    # Save detailed results
    with open("enhanced_script_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to enhanced_script_test_results.json")

if __name__ == "__main__":
    main()