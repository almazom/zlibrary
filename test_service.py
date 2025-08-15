#!/usr/bin/env python3
"""
Test service layer specifically
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.extractors.libru.extractor import LibRuExtractor
from src.application.services.extraction_service import ExtractionService

async def test_service():
    """Test service layer"""
    # Initialize extractors
    extractors = {}
    libru = LibRuExtractor()
    await libru.__aenter__()
    extractors["libru"] = libru
    
    # Create service
    service = ExtractionService(
        extractors=extractors,
        quality_threshold=0.85,
        max_retries=1,  # Reduce retries for faster testing
        enable_fallback=False
    )
    
    print("Testing service extraction...")
    
    # Test extraction
    result = await service.extract_book(
        source="libru",
        category="RUFANT",
        timeout=15.0  # Increase timeout
    )
    
    if result.is_successful:
        print(f"✅ Service success: {result.book.title}")
    else:
        print(f"❌ Service failed: {result.error}")
    
    # Cleanup
    await libru.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(test_service())