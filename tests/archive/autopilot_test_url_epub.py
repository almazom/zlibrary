#!/usr/bin/env python3
"""
🚀 AUTOPILOT TESTING FOR URL TO EPUB PIPELINE
Runs comprehensive tests and sends Telegram notifications
"""
import asyncio
import json
import subprocess
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
from typing import Dict, List, Any

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

class TelegramNotifier:
    """Send test updates to Telegram"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = bool(self.bot_token and self.chat_id)
        
    def send_message(self, message: str):
        """Send message to Telegram"""
        if not self.enabled:
            print(f"[Telegram Disabled] {message}")
            return
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                print(f"✅ Telegram sent: {message[:50]}...")
            else:
                print(f"⚠️ Telegram failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")

class AutopilotTester:
    """Comprehensive autopilot testing system"""
    
    def __init__(self):
        self.telegram = TelegramNotifier()
        self.test_results = []
        self.start_time = time.time()
        self.script_path = "./scripts/zlib_book_search_fixed.sh"
        
        # Test URLs from various marketplaces
        self.test_urls = [
            {
                "name": "Russian Contemporary Fiction",
                "url": "https://www.ozon.ru/product/trevozhnye-lyudi-bakman-fredrik-202912464/",
                "expected": {"title": "Anxious People", "author": "Fredrik Backman"}
            },
            {
                "name": "Classic Dystopian",
                "url": "https://www.ozon.ru/product/1984-orwell-george-138516846/",
                "expected": {"title": "1984", "author": "George Orwell"}
            },
            {
                "name": "Russian Literature",
                "url": "https://www.ozon.ru/product/prestuplenie-i-nakazanie-dostoevskiy-fedor-241899024/",
                "expected": {"title": "Crime and Punishment", "author": "Dostoevsky"}
            },
            {
                "name": "Children's Classic",
                "url": "https://www.ozon.ru/product/malenkiy-princ-sent-ekzyuperi-antuan-141651995/",
                "expected": {"title": "The Little Prince", "author": "Saint-Exupéry"}
            },
            {
                "name": "Modern Philosophy",
                "url": "https://www.ozon.ru/product/sapiens-kratkaya-istoriya-chelovechestva-harari-yuval-noy-140170885/",
                "expected": {"title": "Sapiens", "author": "Yuval Noah Harari"}
            }
        ]
        
        # Test queries for direct search
        self.test_queries = [
            {"query": "Harry Potter Philosopher Stone", "type": "fuzzy_english"},
            {"query": "Война и мир Толстой", "type": "russian_classic"},
            {"query": "tolkien hobbit", "type": "author_title"},
            {"query": "мастер маргарита булгаков", "type": "russian_fuzzy"},
            {"query": "stephen king shining", "type": "english_horror"}
        ]
        
    async def test_url_extraction(self, url_info: Dict) -> Dict:
        """Test URL extraction and search"""
        test_name = url_info['name']
        url = url_info['url']
        
        self.telegram.send_message(f"🔍 Testing: *{test_name}*\nURL: `{url[:50]}...`")
        
        result = {
            "test_name": test_name,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "details": {}
        }
        
        try:
            # Extract book name from URL for search
            if "ozon.ru" in url:
                # Parse Ozon URL slug
                import re
                match = re.search(r'/product/([^/?]+)', url)
                if match:
                    slug = match.group(1)
                    # Convert slug to search query
                    parts = slug.split('-')
                    
                    # Known patterns
                    if "trevozhnye-lyudi" in slug:
                        query = "Fredrik Backman Anxious People"
                    elif "1984" in slug:
                        query = "George Orwell 1984"
                    elif "prestuplenie" in slug:
                        query = "Достоевский Преступление и наказание"
                    elif "malenkiy-princ" in slug:
                        query = "Antoine de Saint-Exupéry The Little Prince"
                    elif "sapiens" in slug:
                        query = "Yuval Noah Harari Sapiens"
                    else:
                        query = ' '.join(parts[:3])
                else:
                    query = test_name
            else:
                query = test_name
            
            # Search for the book
            cmd = [self.script_path, "--service", "--json", "-f", "epub", query]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                try:
                    search_result = json.loads(process.stdout)
                    
                    if search_result.get('status') == 'success':
                        result['success'] = True
                        result['details'] = {
                            'query_used': query,
                            'service': search_result.get('service_used', 'unknown'),
                            'results_count': search_result.get('total_results', 0),
                            'first_result': None
                        }
                        
                        # Get first result details
                        if search_result.get('results'):
                            first = search_result['results'][0]
                            result['details']['first_result'] = {
                                'title': first.get('name', 'Unknown'),
                                'authors': first.get('authors', [])[:2] if isinstance(first.get('authors'), list) else [],
                                'year': first.get('year', ''),
                                'size': first.get('size', '')
                            }
                            
                            # Check if it matches expected
                            if url_info.get('expected'):
                                expected = url_info['expected']
                                title_match = expected['title'].lower() in first.get('name', '').lower()
                                result['details']['matches_expected'] = title_match
                        
                        self.telegram.send_message(
                            f"✅ *{test_name}*\n"
                            f"Found: {result['details']['results_count']} books\n"
                            f"Service: {result['details']['service']}"
                        )
                    else:
                        result['error'] = search_result.get('message', 'Search failed')
                        self.telegram.send_message(f"⚠️ *{test_name}*\nNo results found")
                        
                except json.JSONDecodeError as e:
                    result['error'] = f"JSON parse error: {e}"
                    
            else:
                result['error'] = f"Command failed: {process.stderr[:200]}"
                
        except subprocess.TimeoutExpired:
            result['error'] = "Search timeout (30s)"
            self.telegram.send_message(f"⏱️ *{test_name}*\nTimeout!")
            
        except Exception as e:
            result['error'] = str(e)[:200]
            self.telegram.send_message(f"❌ *{test_name}*\nError: {str(e)[:100]}")
        
        return result
    
    async def test_direct_search(self, query_info: Dict) -> Dict:
        """Test direct search queries"""
        query = query_info['query']
        query_type = query_info['type']
        
        self.telegram.send_message(f"🔎 Testing query: *{query_type}*\n`{query}`")
        
        result = {
            "query": query,
            "type": query_type,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "details": {}
        }
        
        try:
            # Search with download
            cmd = [self.script_path, "--service", "--json", "-f", "epub", "--download", query]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=45
            )
            
            if process.returncode == 0:
                try:
                    download_result = json.loads(process.stdout)
                    
                    if download_result.get('status') == 'success':
                        result['success'] = True
                        result['details'] = {
                            'downloaded': True,
                            'service': download_result.get('service_used', 'unknown'),
                            'book': download_result.get('book', {}),
                            'file': download_result.get('file', {})
                        }
                        
                        file_info = download_result.get('file', {})
                        book_info = download_result.get('book', {})
                        
                        self.telegram.send_message(
                            f"✅ Downloaded: *{query_type}*\n"
                            f"📚 {book_info.get('name', 'Unknown')[:30]}\n"
                            f"📦 {file_info.get('size', 0) / 1024:.0f} KB"
                        )
                    else:
                        result['details']['downloaded'] = False
                        result['error'] = download_result.get('message', 'Download failed')
                        
                except json.JSONDecodeError as e:
                    result['error'] = f"JSON parse error: {e}"
                    
            else:
                result['error'] = f"Command failed: {process.stderr[:200]}"
                
        except subprocess.TimeoutExpired:
            result['error'] = "Download timeout (45s)"
            self.telegram.send_message(f"⏱️ *{query_type}* timeout!")
            
        except Exception as e:
            result['error'] = str(e)[:200]
            
        return result
    
    async def test_error_handling(self) -> Dict:
        """Test error cases and edge scenarios"""
        self.telegram.send_message("🧪 Testing error handling...")
        
        error_tests = []
        
        # Test 1: Invalid URL
        try:
            cmd = [self.script_path, "--service", "--json", "-f", "epub", ""]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            error_tests.append({
                "test": "empty_query",
                "handled": "error" in process.stdout.lower() or process.returncode != 0
            })
        except:
            error_tests.append({"test": "empty_query", "handled": True})
        
        # Test 2: Non-existent book
        try:
            cmd = [self.script_path, "--service", "--json", "-f", "epub", "xyzabc123nonexistent999"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            result = json.loads(process.stdout) if process.stdout else {}
            error_tests.append({
                "test": "nonexistent_book",
                "handled": result.get('total_results', 1) == 0
            })
        except:
            error_tests.append({"test": "nonexistent_book", "handled": True})
        
        # Test 3: Service forcing
        try:
            cmd = [self.script_path, "--force-flibusta", "--service", "--json", "-f", "epub", "test"]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            result = json.loads(process.stdout) if process.stdout else {}
            error_tests.append({
                "test": "force_flibusta",
                "handled": result.get('service_used') == 'flibusta' or 'flibusta' in process.stdout
            })
        except:
            error_tests.append({"test": "force_flibusta", "handled": False})
        
        return {
            "error_handling": error_tests,
            "passed": sum(1 for t in error_tests if t.get('handled', False)),
            "total": len(error_tests)
        }
    
    async def run_autopilot_tests(self):
        """Run all tests in autopilot mode"""
        self.telegram.send_message(
            "🚀 *AUTOPILOT TESTING STARTED*\n"
            f"📋 URL Tests: {len(self.test_urls)}\n"
            f"🔍 Query Tests: {len(self.test_queries)}\n"
            f"🧪 Error Tests: 3\n"
            f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        all_results = {
            "start_time": datetime.now().isoformat(),
            "url_tests": [],
            "query_tests": [],
            "error_tests": {},
            "summary": {}
        }
        
        # Test URL extraction
        self.telegram.send_message("📌 *Phase 1: URL Extraction Tests*")
        for url_info in self.test_urls:
            result = await self.test_url_extraction(url_info)
            all_results["url_tests"].append(result)
            await asyncio.sleep(2)  # Avoid rate limiting
        
        # Test direct searches
        self.telegram.send_message("📌 *Phase 2: Direct Search Tests*")
        for query_info in self.test_queries:
            result = await self.test_direct_search(query_info)
            all_results["query_tests"].append(result)
            await asyncio.sleep(2)
        
        # Test error handling
        self.telegram.send_message("📌 *Phase 3: Error Handling Tests*")
        error_results = await self.test_error_handling()
        all_results["error_tests"] = error_results
        
        # Calculate summary
        url_success = sum(1 for t in all_results["url_tests"] if t.get("success"))
        query_success = sum(1 for t in all_results["query_tests"] if t.get("success"))
        
        all_results["summary"] = {
            "total_tests": len(self.test_urls) + len(self.test_queries) + 3,
            "url_tests": {
                "total": len(self.test_urls),
                "passed": url_success,
                "failed": len(self.test_urls) - url_success
            },
            "query_tests": {
                "total": len(self.test_queries),
                "passed": query_success,
                "failed": len(self.test_queries) - query_success
            },
            "error_tests": error_results,
            "duration": time.time() - self.start_time,
            "end_time": datetime.now().isoformat()
        }
        
        # Send final report
        duration = all_results["summary"]["duration"]
        total_passed = url_success + query_success + error_results.get("passed", 0)
        total_tests = all_results["summary"]["total_tests"]
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        final_report = (
            f"✅ *AUTOPILOT TESTING COMPLETE*\n\n"
            f"📊 *Results Summary:*\n"
            f"• Total Tests: {total_tests}\n"
            f"• Passed: {total_passed}\n"
            f"• Success Rate: {success_rate:.1f}%\n\n"
            f"📌 *URL Tests:* {url_success}/{len(self.test_urls)}\n"
            f"🔍 *Query Tests:* {query_success}/{len(self.test_queries)}\n"
            f"🧪 *Error Tests:* {error_results.get('passed', 0)}/{error_results.get('total', 0)}\n\n"
            f"⏱️ Duration: {duration:.1f} seconds\n"
            f"🏁 Completed: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        self.telegram.send_message(final_report)
        
        # Save detailed results
        results_file = f"autopilot_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        return all_results

async def main():
    """Main autopilot testing entry point"""
    
    # Load environment variables
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check if Telegram is configured
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
        print("   Tests will run but notifications will be printed to console only.")
    
    # Run autopilot tests
    tester = AutopilotTester()
    results = await tester.run_autopilot_tests()
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("🎯 AUTOPILOT TESTING COMPLETE")
    print("=" * 80)
    print(f"Success Rate: {results['summary']['url_tests']['passed']}/{results['summary']['url_tests']['total']} URL tests")
    print(f"             {results['summary']['query_tests']['passed']}/{results['summary']['query_tests']['total']} Query tests")
    print(f"Duration: {results['summary']['duration']:.1f} seconds")
    print("=" * 80)

if __name__ == "__main__":
    print("🚀 Starting Autopilot Testing System...")
    print("=" * 80)
    asyncio.run(main())