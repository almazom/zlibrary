#!/usr/bin/env python3
"""
Book Search API CLI Service
Usage: python3 book_search_api_cli.py "URL"
Always returns standardized JSON to stdout
"""

import asyncio
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from standardized_book_search import StandardizedBookSearch

async def main():
    """CLI interface for book search API"""
    
    # Check arguments
    if len(sys.argv) != 2:
        error_response = {
            "status": "error",
            "timestamp": "2025-08-08T15:45:00Z",
            "query_info": {
                "original_url": "",
                "extracted_query": ""
            },
            "result": {
                "error": "invalid_usage",
                "message": "Usage: python3 book_search_api_cli.py 'URL'"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        # Initialize service and search
        service = StandardizedBookSearch()
        result = await service.search_book(url)
        
        # Output JSON to stdout
        print(json.dumps(result, ensure_ascii=False))
        
        # Exit with appropriate code
        sys.exit(0 if result["status"] in ["success", "not_found"] else 1)
        
    except KeyboardInterrupt:
        error_response = {
            "status": "error",
            "timestamp": "2025-08-08T15:45:00Z",
            "query_info": {
                "original_url": url,
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
            "timestamp": "2025-08-08T15:45:00Z", 
            "query_info": {
                "original_url": url,
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