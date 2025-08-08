#!/usr/bin/env python3
"""
CLI wrapper for Enhanced Download Service
Provides actual EPUB downloads with readability confidence
"""

import asyncio
import sys
import json
from enhanced_download_service import EnhancedDownloadService

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error", 
            "result": {
                "error": "no_input",
                "message": "No input provided"
            }
        }))
        sys.exit(1)
    
    input_text = sys.argv[1]
    enable_download = "--download" in sys.argv
    
    service = EnhancedDownloadService()
    result = await service.enhanced_search_with_download(input_text, enable_download)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())