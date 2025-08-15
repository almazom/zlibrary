#!/usr/bin/env python3
"""
Clean Architecture Demonstration
Shows how the refactored extraction system works with proper separation of concerns
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import core interfaces
from src.core.interfaces.extractor import ExtractionRequest, ExtractionStatus

# Import infrastructure
from src.infrastructure.extractors.libru.extractor import LibRuExtractor

# Import application services
from src.application.services.extraction_service import ExtractionService


async def demonstrate_single_extraction():
    """Demonstrate single book extraction with the new architecture"""
    print("\n" + "="*60)
    print("SINGLE EXTRACTION DEMONSTRATION")
    print("="*60)
    
    # Initialize extractor with context manager
    async with LibRuExtractor() as libru_extractor:
        # Create extraction request
        request = ExtractionRequest(
            source_id="libru",
            category="RUFANT",
            session_id="demo_session_001"
        )
        
        print(f"\n📚 Extracting from {request.source_id}...")
        print(f"   Category: {request.category}")
        print(f"   Session: {request.session_id}")
        
        # Perform extraction
        result = await libru_extractor.extract(request)
        
        # Display results
        if result.is_successful:
            print(f"\n✅ Extraction successful!")
            print(f"   Title: {result.book.title}")
            print(f"   Author: {result.book.author}")
            print(f"   Source URL: {result.book.source_url}")
            print(f"   Confidence: {result.confidence:.2%}")
            print(f"   Time: {result.extraction_time:.2f}s")
        else:
            print(f"\n❌ Extraction failed: {result.error}")


async def demonstrate_service_orchestration():
    """Demonstrate service layer orchestration with multiple extractors"""
    print("\n" + "="*60)
    print("SERVICE ORCHESTRATION DEMONSTRATION")
    print("="*60)
    
    # Initialize multiple extractors
    extractors = {}
    
    # Add LibRu extractor
    libru = LibRuExtractor()
    await libru.__aenter__()  # Initialize HTTP client
    extractors["libru"] = libru
    
    # Future: Add more extractors here
    # extractors["eksmo"] = EksmoExtractor()
    # extractors["gutenberg"] = GutenbergExtractor()
    
    # Create extraction service
    service = ExtractionService(
        extractors=extractors,
        quality_threshold=0.85,
        max_retries=2,
        enable_fallback=True
    )
    
    print("\n📊 Service Configuration:")
    print(f"   Available sources: {list(extractors.keys())}")
    print(f"   Quality threshold: 0.85")
    print(f"   Fallback enabled: True")
    
    # Test extraction with auto-selection
    print("\n🔄 Testing auto-source selection...")
    result = await service.extract_book(
        source="libru",  # Specify source instead of auto
        category="INOFANT",
        session_id="demo_service_001",
        timeout=15.0  # Increase timeout
    )
    
    if result.is_successful:
        print(f"\n✅ Book extracted successfully!")
        print(f"   Source used: {result.source}")
        print(f"   Title: {result.book.title}")
        print(f"   Author: {result.book.author}")
        print(f"   Time: {result.extraction_time:.2f}s")
    else:
        print(f"\n❌ Extraction failed: {result.error}")
    
    # Display metrics
    metrics = service.get_metrics()
    print("\n📈 Service Metrics:")
    print(f"   Total extractions: {metrics['total_extractions']}")
    print(f"   Success rate: {metrics['success_rate']:.1%}")
    print(f"   Source stats: {json.dumps(metrics['source_stats'], indent=6)}")
    
    # Cleanup
    await libru.__aexit__(None, None, None)


async def demonstrate_batch_extraction():
    """Demonstrate concurrent batch extraction"""
    print("\n" + "="*60)
    print("BATCH EXTRACTION DEMONSTRATION")
    print("="*60)
    
    # Initialize service
    extractors = {}
    libru = LibRuExtractor()
    await libru.__aenter__()
    extractors["libru"] = libru
    
    service = ExtractionService(extractors=extractors)
    
    # Create batch requests
    batch_requests = [
        {"source": "libru", "category": "RUFANT", "session_id": f"batch_{i}", "timeout": 15.0}
        for i in range(3)
    ]
    
    print(f"\n🚀 Extracting {len(batch_requests)} books concurrently...")
    start_time = datetime.now()
    
    # Perform batch extraction
    results = await service.extract_batch(
        requests=batch_requests,
        concurrency=3
    )
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    # Display results
    successful = sum(1 for r in results if r.is_successful)
    print(f"\n📊 Batch Results:")
    print(f"   Total books: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(results) - successful}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Avg time per book: {total_time/len(results):.2f}s")
    
    # Show individual results
    print("\n📚 Extracted Books:")
    for i, result in enumerate(results, 1):
        if result.is_successful:
            print(f"   {i}. {result.book.title} by {result.book.author}")
        else:
            print(f"   {i}. ❌ Failed: {result.error}")
    
    # Cleanup
    await libru.__aexit__(None, None, None)


async def demonstrate_health_checks():
    """Demonstrate health checking capabilities"""
    print("\n" + "="*60)
    print("HEALTH CHECK DEMONSTRATION")
    print("="*60)
    
    # Initialize extractors
    extractors = {}
    libru = LibRuExtractor()
    await libru.__aenter__()
    extractors["libru"] = libru
    
    service = ExtractionService(extractors=extractors)
    
    print("\n🏥 Checking source health...")
    health_status = await service.health_check()
    
    print("\n📊 Health Status:")
    for source, is_healthy in health_status.items():
        status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
        print(f"   {source}: {status}")
    
    # Get source info
    print("\n📋 Source Information:")
    for source_id, extractor in extractors.items():
        info = extractor.get_source_info()
        print(f"\n   {source_id}:")
        print(f"     Name: {info['name']}")
        print(f"     URL: {info['url']}")
        print(f"     Categories: {', '.join(info['categories'])}")
        print(f"     Rate limit: {info['rate_limit']} req/s")
        print(f"     Capabilities: {json.dumps(info['capabilities'], indent=8)}")
    
    # Cleanup
    await libru.__aexit__(None, None, None)


async def main():
    """Run all demonstrations"""
    print("\n" + "#"*60)
    print("#" + " "*18 + "CLEAN ARCHITECTURE DEMO" + " "*18 + "#")
    print("#"*60)
    print("\nThis demonstration shows the refactored IUC05 system")
    print("with proper separation of concerns and clean architecture.")
    
    # Run demonstrations
    await demonstrate_single_extraction()
    await demonstrate_service_orchestration()
    await demonstrate_batch_extraction()
    await demonstrate_health_checks()
    
    print("\n" + "#"*60)
    print("#" + " "*20 + "DEMO COMPLETE" + " "*21 + "#")
    print("#"*60)
    print("\n✨ The new architecture provides:")
    print("   • Clear separation of concerns")
    print("   • Dependency injection")
    print("   • Plugin architecture for extensibility")
    print("   • Service orchestration layer")
    print("   • Concurrent batch processing")
    print("   • Health monitoring")
    print("   • Metrics collection")
    print("\n🚀 Ready for production!\n")


if __name__ == "__main__":
    asyncio.run(main())