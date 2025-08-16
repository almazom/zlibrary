#!/usr/bin/env python3
"""
CLAUDE + Z-LIBRARY INTEGRATION - Complete feedback development system
Combines Claude SDK normalization with Z-Library search for real-world validation
"""
import asyncio
import sys
import time
from typing import Dict, Any, List
sys.path.insert(0, '.')
sys.path.insert(0, './src')

from claude_sdk_normalizer import ClaudeSDKNormalizer
from zlibrary.libasync import AsyncZlib
from zlibrary.abs import BookItem

class ClaudeZLibraryIntegration:
    """Integration of Claude SDK normalization with Z-Library search"""
    
    def __init__(self):
        self.claude_normalizer = ClaudeSDKNormalizer()
        self.zlib_client = AsyncZlib()
        self.search_cache = {}
        self.integration_log = []
    
    async def search_with_normalization(self, fuzzy_query: str, test_original: bool = True) -> Dict[str, Any]:
        """
        Search Z-Library with Claude normalization and feedback comparison
        
        Args:
            fuzzy_query: The original fuzzy/incorrect query
            test_original: Whether to test original query for comparison
            
        Returns:
            Complete results with normalization feedback and search effectiveness
        """
        print(f"\n🔍 CLAUDE + Z-LIBRARY SEARCH")
        print("=" * 60)
        print(f"📚 Query: '{fuzzy_query}'")
        
        results = {
            "original_query": fuzzy_query,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "normalization_result": {},
            "original_search": {},
            "normalized_search": {},
            "improvement_analysis": {}
        }
        
        # Step 1: Normalize with Claude SDK
        print(f"\n🤖 STEP 1: Claude Normalization")
        print("-" * 40)
        
        normalization = self.claude_normalizer.normalize_book_title(fuzzy_query)
        results["normalization_result"] = normalization
        
        if normalization["success"]:
            normalized_query = normalization["normalized"]
            print(f"✅ Normalized: '{normalized_query}'")
            print(f"📊 Confidence: {normalization['confidence']:.0%}")
            print(f"🔧 Problems fixed: {', '.join(normalization.get('problems_found', []))}")
        else:
            print(f"❌ Normalization failed: {normalization.get('error', 'Unknown error')}")
            return results
        
        # Step 2: Search with original (if requested)
        if test_original and fuzzy_query.lower() != normalized_query.lower():
            print(f"\n🔎 STEP 2: Original Query Search")
            print("-" * 40)
            
            try:
                original_search_results = await self._search_zlibrary(fuzzy_query)
                results["original_search"] = original_search_results
                print(f"📖 Original query found: {original_search_results['total_found']} books")
            except Exception as e:
                results["original_search"] = {"error": str(e), "total_found": 0}
                print(f"❌ Original search failed: {e}")
        
        # Step 3: Search with normalized query
        print(f"\n🎯 STEP 3: Normalized Query Search")
        print("-" * 40)
        
        try:
            normalized_search_results = await self._search_zlibrary(normalized_query)
            results["normalized_search"] = normalized_search_results
            print(f"📚 Normalized query found: {normalized_search_results['total_found']} books")
            
            # Show sample results
            if normalized_search_results["books"]:
                print("\n📋 Top results:")
                for i, book in enumerate(normalized_search_results["books"][:3], 1):
                    print(f"  {i}. {book.get('name', 'Unknown')} - {book.get('authors', 'Unknown author')}")
        
        except Exception as e:
            results["normalized_search"] = {"error": str(e), "total_found": 0}
            print(f"❌ Normalized search failed: {e}")
        
        # Step 4: Analyze improvement
        results["improvement_analysis"] = self._analyze_search_improvement(results)
        self._log_integration_result(results)
        
        return results
    
    async def _search_zlibrary(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search Z-Library and return structured results"""
        
        if query in self.search_cache:
            return self.search_cache[query]
        
        try:
            # Perform search
            search_results = await self.zlib_client.search(q=query, count=limit)
            await search_results.init()
            
            books = []
            for book_item in search_results.result:
                # Get basic info (don't fetch full details to avoid quota issues)
                book_data = {
                    "name": getattr(book_item, 'name', 'Unknown'),
                    "authors": getattr(book_item, 'authors', 'Unknown'),
                    "year": getattr(book_item, 'year', ''),
                    "extension": getattr(book_item, 'extension', ''),
                    "language": getattr(book_item, 'language', ''),
                    "id": getattr(book_item, 'id', '')
                }
                books.append(book_data)
            
            result = {
                "query": query,
                "total_found": len(books),
                "books": books,
                "has_results": len(books) > 0
            }
            
            self.search_cache[query] = result
            return result
            
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "total_found": 0,
                "books": [],
                "has_results": False
            }
    
    def _analyze_search_improvement(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how much normalization improved search results"""
        
        original_count = results.get("original_search", {}).get("total_found", 0)
        normalized_count = results.get("normalized_search", {}).get("total_found", 0)
        
        improvement = {
            "original_results": original_count,
            "normalized_results": normalized_count,
            "improvement_absolute": normalized_count - original_count,
            "improvement_percentage": 0.0,
            "effectiveness": "unknown"
        }
        
        if original_count > 0:
            improvement["improvement_percentage"] = ((normalized_count - original_count) / original_count) * 100
        
        # Classify effectiveness
        if normalized_count > original_count:
            improvement["effectiveness"] = "improved"
        elif normalized_count == original_count and normalized_count > 0:
            improvement["effectiveness"] = "maintained"
        elif normalized_count < original_count:
            improvement["effectiveness"] = "degraded"
        else:
            improvement["effectiveness"] = "no_results"
        
        return improvement
    
    def _log_integration_result(self, result: Dict[str, Any]):
        """Log integration result for feedback development"""
        
        log_entry = {
            "timestamp": result["timestamp"],
            "original_query": result["original_query"],
            "normalized_query": result["normalization_result"].get("normalized", ""),
            "claude_confidence": result["normalization_result"].get("confidence", 0.0),
            "search_improvement": result["improvement_analysis"]["effectiveness"],
            "original_results": result["improvement_analysis"]["original_results"],
            "normalized_results": result["improvement_analysis"]["normalized_results"]
        }
        
        self.integration_log.append(log_entry)
        
        # Keep last 50 entries
        if len(self.integration_log) > 50:
            self.integration_log = self.integration_log[-50:]
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration effectiveness statistics"""
        
        if not self.integration_log:
            return {"total_tests": 0}
        
        total = len(self.integration_log)
        
        # Count effectiveness categories
        effectiveness_counts = {}
        confidence_sum = 0
        search_improvements = 0
        
        for entry in self.integration_log:
            effectiveness = entry["search_improvement"]
            effectiveness_counts[effectiveness] = effectiveness_counts.get(effectiveness, 0) + 1
            confidence_sum += entry["claude_confidence"]
            
            if entry["normalized_results"] > entry["original_results"]:
                search_improvements += 1
        
        return {
            "total_tests": total,
            "search_improvement_rate": search_improvements / total if total > 0 else 0.0,
            "average_claude_confidence": confidence_sum / total if total > 0 else 0.0,
            "effectiveness_breakdown": effectiveness_counts,
            "recent_tests": self.integration_log[-5:]
        }
    
    async def feedback_development_cycle(self, test_queries: List[str]) -> Dict[str, Any]:
        """Complete feedback development cycle with multiple test queries"""
        
        print("\n🔄 CLAUDE + Z-LIBRARY FEEDBACK DEVELOPMENT CYCLE")
        print("=" * 80)
        
        cycle_results = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 TEST {i}/{len(test_queries)}")
            print("=" * 40)
            
            result = await self.search_with_normalization(query)
            cycle_results.append(result)
            
            # Brief pause between searches
            await asyncio.sleep(1)
        
        # Generate cycle statistics
        stats = self.get_integration_stats()
        
        print(f"\n📊 CYCLE STATISTICS")
        print("=" * 40)
        print(f"Total tests: {stats['total_tests']}")
        print(f"Search improvement rate: {stats['search_improvement_rate']:.0%}")
        print(f"Average Claude confidence: {stats['average_claude_confidence']:.0%}")
        print(f"Effectiveness breakdown: {stats['effectiveness_breakdown']}")
        
        return {
            "cycle_results": cycle_results,
            "statistics": stats,
            "cycle_complete": True
        }


async def test_claude_zlibrary_integration():
    """Test the complete Claude + Z-Library integration"""
    
    # First ensure we're logged in
    integration = ClaudeZLibraryIntegration()
    
    # Login to Z-Library (using credentials from .env)
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        email = os.getenv("ZLOGIN")
        password = os.getenv("ZPASSW")
        
        if not email or not password:
            print("❌ Z-Library credentials not found in .env file")
            return
        
        print("🔐 Logging into Z-Library...")
        profile = await integration.zlib_client.login(email, password)
        print(f"✅ Logged in successfully as user: {profile.id}")
        
    except Exception as e:
        print(f"❌ Z-Library login failed: {e}")
        return
    
    # Test queries with various issues
    test_queries = [
        "ведмак 3 дикая охота",  # Russian with typo
        "hary poter",            # English typo
        "метро2033 глуховски",   # Russian missing space
        "пелевин generation п",  # Mixed language
        "azazel akunin",         # Transliterated Russian
    ]
    
    # Run feedback development cycle
    results = await integration.feedback_development_cycle(test_queries)
    
    await integration.zlib_client.logout()
    print("\n✅ Integration testing complete!")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test single query
        query = ' '.join(sys.argv[1:])
        
        async def single_test():
            integration = ClaudeZLibraryIntegration()
            
            # Quick login
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            try:
                await integration.zlib_client.login(os.getenv("ZLOGIN"), os.getenv("ZPASSW"))
                result = await integration.search_with_normalization(query)
                await integration.zlib_client.logout()
                return result
            except Exception as e:
                print(f"Error: {e}")
        
        asyncio.run(single_test())
    else:
        # Run full test suite
        asyncio.run(test_claude_zlibrary_integration())