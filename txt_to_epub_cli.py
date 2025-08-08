#!/usr/bin/env python3
"""
Text to EPUB CLI Service
Usage: python3 txt_to_epub_cli.py "book title author etc"
Always returns standardized JSON to stdout
"""

import asyncio
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from txt_to_epub_service import TextToEPUBService

async def main():
    """CLI interface for text to EPUB search"""
    
    # Check arguments
    if len(sys.argv) != 2:
        error_response = {
            "status": "error",
            "timestamp": "2025-08-08T15:46:00Z",
            "input_format": "txt",
            "query_info": {
                "original_input": "",
                "extracted_query": ""
            },
            "result": {
                "error": "invalid_usage",
                "message": "Usage: python3 txt_to_epub_cli.py 'text to search'"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)
    
    text_input = sys.argv[1]
    
    try:
        # Initialize service and search
        service = TextToEPUBService()
        result = await service.search_book_from_text(text_input)
        
        # Output JSON to stdout
        print(json.dumps(result, ensure_ascii=False))
        
        # Exit with appropriate code
        sys.exit(0 if result["status"] in ["success", "not_found"] else 1)
        
    except KeyboardInterrupt:
        error_response = {
            "status": "error",
            "timestamp": "2025-08-08T15:46:00Z",
            "input_format": "txt",
            "query_info": {
                "original_input": text_input,
                "extracted_query": ""
            },
            "result": {
                "error": "interrupted",
                "message": "Search was interrupted by user"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(130)
        
    except Exception as e:
        error_response = {
            "status": "error",
            "timestamp": "2025-08-08T15:46:00Z",
            "input_format": "txt", 
            "query_info": {
                "original_input": text_input,
                "extracted_query": ""
            },
            "result": {
                "error": "cli_error",
                "message": f"CLI error: {str(e)[:200]}"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())