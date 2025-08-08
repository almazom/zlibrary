#!/usr/bin/env python3
"""
Full External Service Usage Simulation
Demonstrates complete API workflow with different book examples
"""

import json
from datetime import datetime

def simulate_service_response(input_text, download=False, book_scenario="found"):
    """Simulate the enhanced service response for different scenarios"""
    
    timestamp = datetime.now().isoformat()
    
    # Detect input format
    if input_text.startswith("http"):
        input_format = "url"
    elif input_text.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        input_format = "image"
    else:
        input_format = "txt"
    
    base_response = {
        "status": "success",
        "timestamp": timestamp,
        "input_format": input_format,
        "query_info": {
            "original_input": input_text,
            "extracted_query": input_text
        }
    }
    
    if book_scenario == "found":
        # Simulate successful book found with different quality levels
        if "1984" in input_text.lower():
            book_data = {
                "title": "1984",
                "authors": ["George Orwell"],
                "year": "1949",
                "publisher": "Penguin Books",
                "size": "2.1 MB",
                "description": "A dystopian social science fiction novel by English novelist George Orwell. It was published on 8 June 1949 by Secker & Warburg as Orwell's ninth and final book completed in his lifetime."
            }
            confidence_score = 0.95
            readability_score = 0.92
            readability_factors = [
                "Good file size (2.1 MB)",
                "Quality publisher: Penguin Books", 
                "Complete title suggests proper metadata",
                "Quality author info: George Orwell",
                "Detailed description available"
            ]
            
        elif "dune" in input_text.lower():
            book_data = {
                "title": "Dune",
                "authors": ["Frank Herbert"],
                "year": "1965",
                "publisher": "Ace Books",
                "size": "3.7 MB",
                "description": "A science fiction novel by American author Frank Herbert, originally published as two separate serials in Analog magazine. It tied with Roger Zelazny's This Immortal for the Hugo Award in 1966."
            }
            confidence_score = 0.88
            readability_score = 0.85
            readability_factors = [
                "Large file (3.7 MB) suggests high quality",
                "Complete title suggests proper metadata",
                "Quality author info: Frank Herbert",
                "Detailed description available"
            ]
            
        elif "sapiens" in input_text.lower():
            book_data = {
                "title": "Sapiens: A Brief History of Humankind",
                "authors": ["Yuval Noah Harari"],
                "year": "2011",
                "publisher": "Random House",
                "size": "4.2 MB", 
                "description": "A book by Israeli author Yuval Noah Harari, first published in Hebrew in Israel in 2011 based on a series of lectures Harari taught at The Hebrew University of Jerusalem."
            }
            confidence_score = 0.92
            readability_score = 0.95
            readability_factors = [
                "Large file (4.2 MB) suggests high quality",
                "Quality publisher: Random House",
                "Recent publication (2011)",
                "Complete title suggests proper metadata",
                "Quality author info: Yuval Noah Harari",
                "Detailed description available"
            ]
        else:
            # Generic book response
            book_data = {
                "title": "Generic Book Title",
                "authors": ["Unknown Author"],
                "year": "2020",
                "publisher": "Generic Publisher",
                "size": "1.5 MB",
                "description": "A generic book description for simulation purposes."
            }
            confidence_score = 0.65
            readability_score = 0.70
            readability_factors = [
                "Good file size (1.5 MB)",
                "Recent publication (2020)",
                "Complete title suggests proper metadata"
            ]
        
        # Download info based on request
        if download:
            filename = f"{book_data['title'].replace(' ', '_').replace(':', '')}.epub"
            download_info = {
                "available": True,
                "url": f"file:///home/almaz/microservices/zlibrary_api_module/downloads/{filename}",
                "local_path": f"/home/almaz/microservices/zlibrary_api_module/downloads/{filename}",
                "filename": filename,
                "file_size": int(float(book_data['size'].split()[0]) * 1024 * 1024)  # Convert MB to bytes
            }
            epub_download_url = download_info["url"]
            readability_factors.append("Successful download verified")
            readability_score = min(readability_score + 0.05, 1.0)  # Bonus for successful download
        else:
            download_info = {
                "available": False,
                "url": None
            }
            epub_download_url = None
        
        # Determine confidence level
        if confidence_score >= 0.8:
            confidence_level = "VERY_HIGH"
            confidence_desc = "Очень высокая уверенность - это точно искомая книга"
        elif confidence_score >= 0.6:
            confidence_level = "HIGH"
            confidence_desc = "Высокая уверенность - скорее всего это нужная книга"
        else:
            confidence_level = "MEDIUM"
            confidence_desc = "Средняя уверенность - возможно это нужная книга"
        
        # Determine readability level
        if readability_score >= 0.8:
            readability_level = "EXCELLENT"
            readability_desc = "Отличное качество - высококачественный EPUB"
        elif readability_score >= 0.65:
            readability_level = "GOOD"
            readability_desc = "Хорошее качество - читабельный EPUB"
        else:
            readability_level = "FAIR"
            readability_desc = "Удовлетворительное качество - может быть читабелен"
        
        base_response["result"] = {
            "found": True,
            "epub_download_url": epub_download_url,
            "download_info": download_info,
            "confidence": {
                "score": round(confidence_score, 3),
                "level": confidence_level,
                "description": confidence_desc,
                "recommended": confidence_score >= 0.4
            },
            "readability": {
                "score": round(readability_score, 3),
                "level": readability_level,
                "description": readability_desc,
                "factors": readability_factors
            },
            "book_info": book_data,
            "service_used": "zlibrary"
        }
        
    elif book_scenario == "not_found":
        base_response["status"] = "not_found"
        base_response["result"] = {
            "found": False,
            "message": "No books found matching the search criteria. Try different keywords or check spelling."
        }
        
    else:  # error
        base_response["status"] = "error"
        base_response["result"] = {
            "error": "search_failed",
            "message": "Search service error: Unable to connect to book database. Please try again later."
        }
    
    return base_response

def main():
    """Run full service simulation with different scenarios"""
    
    print("🚀 FULL EXTERNAL SERVICE USAGE SIMULATION")
    print("=" * 60)
    print()
    
    test_cases = [
        {
            "name": "1984 by George Orwell (with download)",
            "input": "1984 George Orwell",
            "download": True,
            "scenario": "found"
        },
        {
            "name": "Dune by Frank Herbert (no download)",
            "input": "Dune Frank Herbert science fiction",
            "download": False,
            "scenario": "found"
        },
        {
            "name": "Sapiens by Yuval Harari (with download)",
            "input": "Sapiens brief history humankind Harari",
            "download": True,
            "scenario": "found"
        },
        {
            "name": "URL Input Example",
            "input": "https://www.example.com/books/atomic-habits/",
            "download": False,
            "scenario": "found"
        },
        {
            "name": "Book Not Found",
            "input": "Very Obscure Book That Does Not Exist Anywhere",
            "download": False,
            "scenario": "not_found"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"📝 Test Case {i}: {case['name']}")
        print("-" * 50)
        
        # Show raw request
        request_data = {
            "input": case['input'],
            "download": case['download']
        }
        
        print("🌐 Raw HTTP Request:")
        print(f"POST /api/v1/search-enhanced")
        print(f"Content-Type: application/json")
        print(f"Body: {json.dumps(request_data, indent=2)}")
        print()
        
        # Show bash command equivalent
        download_flag = "--download" if case['download'] else ""
        print("💻 Bash Command Equivalent:")
        print(f"./scripts/zlib_search_enhanced.sh {download_flag} \"{case['input']}\"")
        print()
        
        # Generate response
        response = simulate_service_response(
            case['input'], 
            case['download'], 
            case['scenario']
        )
        
        print("📋 Expected JSON Response:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Highlight key fields
        if response["status"] == "success":
            result = response["result"]
            print()
            print("🔍 Key Response Fields:")
            print(f"   ✅ Status: {response['status']}")
            print(f"   📥 Input Format: {response['input_format']}")
            print(f"   📚 Found: {result['found']}")
            print(f"   📁 Download URL: {result['epub_download_url'] or 'Not available'}")
            print(f"   🎯 Confidence: {result['confidence']['level']} ({result['confidence']['score']})")
            print(f"   📖 Readability: {result['readability']['level']} ({result['readability']['score']})")
            print(f"   🏷️  Title: {result['book_info']['title']}")
            print(f"   👤 Author: {', '.join(result['book_info']['authors'])}")
            print(f"   🔧 Service: {result['service_used']}")
        
        print()
        print("=" * 60)
        print()

if __name__ == "__main__":
    main()