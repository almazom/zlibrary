#!/usr/bin/env python3
"""
IUC05 Diagnostics Runner - Clean Architecture
Run multiple extractions and collect detailed diagnostics
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Any

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.extractors.libru.extractor import LibRuExtractor
from src.application.services.extraction_service import ExtractionService

class IUC05Diagnostics:
    """Collect detailed diagnostics from IUC05 system"""
    
    def __init__(self):
        self.results = []
        self.stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_time": 0,
            "min_time": float('inf'),
            "max_time": 0,
            "categories_used": {},
            "authors_extracted": set(),
            "unique_books": set()
        }
    
    async def run_diagnostics(self, num_runs: int = 10):
        """Run multiple extractions and collect diagnostics"""
        print(f"🚀 Starting IUC05 Diagnostics - {num_runs} runs")
        print("=" * 60)
        
        # Initialize extractor and service
        extractors = {}
        libru = LibRuExtractor()
        await libru.__aenter__()
        extractors["libru"] = libru
        
        service = ExtractionService(
            extractors=extractors,
            quality_threshold=0.85,
            max_retries=1,
            enable_fallback=False
        )
        
        start_time = time.time()
        
        for i in range(1, num_runs + 1):
            print(f"\n🔄 Run {i}/{num_runs}")
            
            run_start = time.time()
            
            try:
                # Test both direct extractor and service layer
                if i % 2 == 1:
                    # Direct extractor test
                    result = await libru.extract(
                        libru.ExtractionRequest(
                            source_id="libru",
                            category=self._select_random_category(),
                            session_id=f"diagnostic_run_{i}"
                        )
                    )
                    test_type = "direct_extractor"
                else:
                    # Service layer test
                    result = await service.extract_book(
                        source="libru",
                        category=self._select_random_category(),
                        session_id=f"diagnostic_service_{i}",
                        timeout=15.0
                    )
                    test_type = "service_layer"
                
                run_time = time.time() - run_start
                
                # Record result
                run_data = {
                    "run_id": i,
                    "test_type": test_type,
                    "timestamp": datetime.now().isoformat(),
                    "success": result.is_successful,
                    "extraction_time": run_time,
                    "confidence": result.confidence if result.is_successful else 0.0,
                    "source": result.source,
                    "error": result.error if not result.is_successful else None
                }
                
                if result.is_successful:
                    run_data.update({
                        "book_title": result.book.title,
                        "book_author": result.book.author,
                        "book_url": result.book.source_url,
                        "category": result.book.metadata.get("category", "unknown")
                    })
                    
                    print(f"   ✅ Success: {result.book.title} by {result.book.author}")
                    print(f"   ⏱️  Time: {run_time:.2f}s | Confidence: {result.confidence:.1%}")
                    
                    # Update stats
                    self.stats["successful_runs"] += 1
                    self.stats["authors_extracted"].add(result.book.author)
                    book_key = f"{result.book.title}|{result.book.author}"
                    self.stats["unique_books"].add(book_key)
                    
                    category = result.book.metadata.get("category", "unknown")
                    self.stats["categories_used"][category] = self.stats["categories_used"].get(category, 0) + 1
                    
                else:
                    print(f"   ❌ Failed: {result.error}")
                    self.stats["failed_runs"] += 1
                
                # Update timing stats
                self.stats["total_time"] += run_time
                self.stats["min_time"] = min(self.stats["min_time"], run_time)
                self.stats["max_time"] = max(self.stats["max_time"], run_time)
                
                self.results.append(run_data)
                self.stats["total_runs"] += 1
                
            except Exception as e:
                run_time = time.time() - run_start
                print(f"   ❌ Exception: {str(e)}")
                
                self.results.append({
                    "run_id": i,
                    "test_type": test_type if 'test_type' in locals() else "unknown",
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "extraction_time": run_time,
                    "error": f"Exception: {str(e)}"
                })
                
                self.stats["failed_runs"] += 1
                self.stats["total_runs"] += 1
        
        total_diagnostic_time = time.time() - start_time
        
        # Cleanup
        await libru.__aexit__(None, None, None)
        
        # Generate final report
        await self._generate_report(total_diagnostic_time)
    
    def _select_random_category(self) -> str:
        """Select random category for variety"""
        import random
        categories = ["RUFANT", "INOFANT", "RAZNOE"]
        return random.choice(categories)
    
    async def _generate_report(self, total_time: float):
        """Generate comprehensive diagnostics report"""
        print("\n" + "=" * 60)
        print("📊 IUC05 DIAGNOSTICS REPORT")
        print("=" * 60)
        
        # Calculate final stats
        success_rate = (self.stats["successful_runs"] / max(self.stats["total_runs"], 1)) * 100
        avg_time = self.stats["total_time"] / max(self.stats["successful_runs"], 1)
        
        # Performance metrics
        print(f"\n🎯 PERFORMANCE METRICS")
        print(f"   Total runs: {self.stats['total_runs']}")
        print(f"   Successful: {self.stats['successful_runs']}")
        print(f"   Failed: {self.stats['failed_runs']}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Average time: {avg_time:.2f}s")
        print(f"   Min time: {self.stats['min_time']:.2f}s")
        print(f"   Max time: {self.stats['max_time']:.2f}s")
        print(f"   Total diagnostic time: {total_time:.2f}s")
        
        # Variety metrics
        print(f"\n📚 VARIETY METRICS")
        print(f"   Unique books: {len(self.stats['unique_books'])}")
        print(f"   Unique authors: {len(self.stats['authors_extracted'])}")
        print(f"   Categories used: {dict(self.stats['categories_used'])}")
        
        # Architecture quality
        print(f"\n🏗️  ARCHITECTURE QUALITY")
        direct_successes = sum(1 for r in self.results if r.get('test_type') == 'direct_extractor' and r.get('success'))
        service_successes = sum(1 for r in self.results if r.get('test_type') == 'service_layer' and r.get('success'))
        direct_total = sum(1 for r in self.results if r.get('test_type') == 'direct_extractor')
        service_total = sum(1 for r in self.results if r.get('test_type') == 'service_layer')
        
        print(f"   Direct extractor success: {direct_successes}/{direct_total} ({direct_successes/max(direct_total,1)*100:.1f}%)")
        print(f"   Service layer success: {service_successes}/{service_total} ({service_successes/max(service_total,1)*100:.1f}%)")
        
        # Save detailed results
        diagnostic_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_runs": self.stats["total_runs"],
                "diagnostic_duration": total_time,
                "architecture": "clean_architecture_v1"
            },
            "summary": {
                "success_rate": success_rate,
                "avg_extraction_time": avg_time,
                "min_extraction_time": self.stats["min_time"],
                "max_extraction_time": self.stats["max_time"],
                "unique_books": len(self.stats["unique_books"]),
                "unique_authors": len(self.stats["authors_extracted"]),
                "categories_distribution": dict(self.stats["categories_used"])
            },
            "detailed_results": self.results
        }
        
        # Save to file
        filename = f"iuc05_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(diagnostic_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
        # Quality assessment
        print(f"\n🎯 QUALITY ASSESSMENT")
        if success_rate >= 95:
            print("   ✅ EXCELLENT: Success rate exceeds 95%")
        elif success_rate >= 90:
            print("   ✅ GOOD: Success rate above 90%")
        elif success_rate >= 80:
            print("   ⚠️  ACCEPTABLE: Success rate above 80%")
        else:
            print("   ❌ POOR: Success rate below 80%")
        
        if avg_time <= 5:
            print("   ✅ EXCELLENT: Average time under 5s")
        elif avg_time <= 8:
            print("   ✅ GOOD: Average time under 8s")
        elif avg_time <= 10:
            print("   ⚠️  ACCEPTABLE: Average time under 10s")
        else:
            print("   ❌ SLOW: Average time exceeds 10s")
        
        if len(self.stats["unique_books"]) >= self.stats["successful_runs"] * 0.8:
            print("   ✅ EXCELLENT: High book variety (>80% unique)")
        elif len(self.stats["unique_books"]) >= self.stats["successful_runs"] * 0.6:
            print("   ✅ GOOD: Good book variety (>60% unique)")
        else:
            print("   ⚠️  LOW: Low book variety (<60% unique)")

async def main():
    """Run IUC05 diagnostics"""
    diagnostics = IUC05Diagnostics()
    await diagnostics.run_diagnostics(10)

if __name__ == "__main__":
    # Fix import issue
    from src.core.interfaces.extractor import ExtractionRequest
    LibRuExtractor.ExtractionRequest = ExtractionRequest
    
    asyncio.run(main())