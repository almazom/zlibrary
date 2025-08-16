#!/usr/bin/env python3
"""
Test direct Novalis search to show higher confidence
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from url_to_epub_with_confidence import URLtoEPUBWithConfidence

async def test_direct_novalis():
    processor = URLtoEPUBWithConfidence()
    
    # Create mock extraction for direct Novalis search
    extracted_info = {
        "title_keywords": ["генрих", "фон", "офтердинген"],
        "author_keywords": ["новалис"],
        "search_query": "новалис",
        "expected_title": "Генрих фон Офтердинген",
        "expected_author": "Новалис",
        "book_type": "роман",
        "language": "russian"
    }
    
    print("🔍 Testing confidence calculation with direct Novalis search...")
    
    # Mock search result (from our earlier search)
    mock_search_result = {
        "name": "Генрих фон Офтердинген",
        "authors": [
            {"author": "Новалис"},
            {"author": "0 comments"},
            {"author": "Litres"}
        ],
        "year": "2019",
        "extension": "EPUB",
        "size": "500 KB",
        "description": "Роман немецкого поэта-романтика Новалиса..."
    }
    
    confidence = processor.calculate_confidence(extracted_info, mock_search_result)
    
    print("\n🎯 CONFIDENCE CALCULATION RESULT:")
    print("=" * 50)
    print(f"Score: {confidence['score']} ({confidence['percentage']})")
    print(f"Level: {confidence['level']}")
    print(f"Description: {confidence['description']}")
    print("\n📝 Confidence Breakdown:")
    for reason in confidence['reasons']:
        print(f"   • {reason}")
    
    return confidence

if __name__ == "__main__":
    asyncio.run(test_direct_novalis())