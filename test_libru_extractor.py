#!/usr/bin/env python3
"""
Simple test of LibRu extractor for debugging
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.interfaces.extractor import ExtractionRequest
from src.infrastructure.extractors.libru.extractor import LibRuExtractor

async def test_single_extraction():
    """Test single extraction with debug output"""
    async with LibRuExtractor() as extractor:
        request = ExtractionRequest(
            source_id="libru",
            category="RUFANT"
        )
        
        print("Testing LibRu extractor...")
        result = await extractor.extract(request)
        
        if result.is_successful:
            print(f"✅ Success: {result.book.title} by {result.book.author}")
        else:
            print(f"❌ Failed: {result.error}")
        
        return result

if __name__ == "__main__":
    asyncio.run(test_single_extraction())