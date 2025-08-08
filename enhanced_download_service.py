#!/usr/bin/env python3
"""
Enhanced Download Service with EPUB URL and Readability Confidence
Adds actual download functionality and quality assessment
"""

import asyncio
import json
import subprocess
import os
import re
from datetime import datetime
from pathlib import Path

class EnhancedDownloadService:
    """Service that provides actual EPUB downloads with readability confidence"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent / "scripts" / "archived" / "zlib_book_search_fixed.sh"
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
    
    def calculate_readability_confidence(self, book_info, download_success=None):
        """Calculate how readable/quality this EPUB is likely to be"""
        
        readability_score = 0.5  # Base score
        factors = []
        
        # 1. File size analysis (30% weight)
        size_str = book_info.get("size", "")
        if size_str:
            size_kb = self._parse_size_to_kb(size_str)
            if size_kb > 0:
                if size_kb > 5000:  # > 5MB - likely high quality with images
                    readability_score += 0.3
                    factors.append(f"Large file ({size_str}) suggests high quality")
                elif size_kb > 1000:  # > 1MB - good quality
                    readability_score += 0.2
                    factors.append(f"Good file size ({size_str})")
                elif size_kb < 100:  # < 100KB - likely poor quality
                    readability_score -= 0.2
                    factors.append(f"Small file ({size_str}) may be low quality")
        
        # 2. Publisher quality (20% weight)
        publisher = book_info.get("publisher", "").lower()
        quality_publishers = [
            "penguin", "harper", "macmillan", "random house", "simon", "scholastic",
            "oxford", "cambridge", "pearson", "wiley", "springer", "elsevier",
            "pottermore", "bloomsbury", "tor", "bantam"
        ]
        
        if any(pub in publisher for pub in quality_publishers):
            readability_score += 0.2
            factors.append(f"Quality publisher: {book_info.get('publisher', '')}")
        elif "unknown" in publisher or not publisher:
            readability_score -= 0.1
            factors.append("Unknown publisher may affect quality")
        
        # 3. Year/recency (15% weight)
        year = book_info.get("year", "")
        if year and year.isdigit():
            year_int = int(year)
            current_year = datetime.now().year
            if year_int >= current_year - 5:  # Recent books
                readability_score += 0.15
                factors.append(f"Recent publication ({year})")
            elif year_int < 1950:  # Very old books might have scanning issues
                readability_score -= 0.1
                factors.append(f"Old publication ({year}) may have scan quality issues")
        
        # 4. Title completeness (10% weight)
        title = book_info.get("title", "")
        if len(title) > 20 and not "..." in title:
            readability_score += 0.1
            factors.append("Complete title suggests proper metadata")
        elif "..." in title:
            readability_score -= 0.05
            factors.append("Truncated title may indicate incomplete record")
        
        # 5. Author information quality (10% weight)
        authors = book_info.get("authors", [])
        clean_authors = [a for a in authors if not any(skip in a.lower() for skip in ["comment", "support", "amazon", "litres"])]
        
        if len(clean_authors) >= 1 and all(len(a) > 3 for a in clean_authors):
            readability_score += 0.1
            factors.append(f"Quality author info: {', '.join(clean_authors[:2])}")
        
        # 6. Description quality (10% weight)
        description = book_info.get("description", "")
        if description and len(description) > 100:
            readability_score += 0.1
            factors.append("Detailed description available")
        
        # 7. Download success bonus (5% weight)
        if download_success is True:
            readability_score += 0.05
            factors.append("Successful download verified")
        elif download_success is False:
            readability_score -= 0.1
            factors.append("Download failed - may indicate quality issues")
        
        # Normalize score to 0-1 range
        readability_score = max(0.0, min(1.0, readability_score))
        
        # Determine readability level
        if readability_score >= 0.8:
            level = "EXCELLENT"
            desc = "Отличное качество - высококачественный EPUB"
        elif readability_score >= 0.65:
            level = "GOOD" 
            desc = "Хорошее качество - читабельный EPUB"
        elif readability_score >= 0.5:
            level = "FAIR"
            desc = "Удовлетворительное качество - может быть читабелен"
        elif readability_score >= 0.3:
            level = "POOR"
            desc = "Плохое качество - могут быть проблемы с чтением"
        else:
            level = "VERY_POOR"
            desc = "Очень плохое качество - скорее всего нечитабелен"
        
        return {
            "score": round(readability_score, 3),
            "level": level,
            "description": desc,
            "factors": factors
        }
    
    def _parse_size_to_kb(self, size_str):
        """Convert size string to KB"""
        if not size_str:
            return 0
            
        try:
            # Parse formats like "1.5 MB", "500 KB", etc.
            match = re.search(r'([\d.]+)\s*(KB|MB|GB)', size_str.upper())
            if match:
                value = float(match.group(1))
                unit = match.group(2)
                
                if unit == "KB":
                    return value
                elif unit == "MB":
                    return value * 1024
                elif unit == "GB":
                    return value * 1024 * 1024
        except:
            pass
            
        return 0
    
    async def get_actual_download_url(self, book_info, search_query):
        """Get actual EPUB download URL using the download script"""
        
        try:
            # Use the zlib script with download flag
            cmd = [
                str(self.script_path),
                "--json", "--service", "--download",
                "-f", "epub",
                "-o", str(self.download_dir),
                search_query
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                
                if response_data.get("status") == "success":
                    # Check if file was actually downloaded
                    file_info = response_data.get("file", {})
                    file_path = file_info.get("path", "")
                    
                    if file_path and Path(file_path).exists():
                        # Convert to absolute path or URL
                        abs_path = Path(file_path).resolve()
                        return {
                            "success": True,
                            "download_url": f"file://{abs_path}",
                            "local_path": str(abs_path),
                            "file_size": file_info.get("size", 0),
                            "filename": file_info.get("filename", "")
                        }
            
            return {
                "success": False,
                "reason": "Download failed or file not found",
                "download_url": None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "reason": "Download timeout (60s exceeded)", 
                "download_url": None
            }
        except Exception as e:
            return {
                "success": False,
                "reason": f"Download error: {str(e)[:100]}",
                "download_url": None
            }
    
    async def enhanced_search_with_download(self, input_text, enable_download=True):
        """Enhanced search that includes actual download URLs and readability confidence"""
        
        timestamp = datetime.now().isoformat()
        
        # Detect input format
        if input_text.startswith("http"):
            input_format = "url"
        elif input_text.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            input_format = "image"
        else:
            input_format = "txt"
        
        # Base response
        response = {
            "status": "error",
            "timestamp": timestamp,
            "input_format": input_format,
            "query_info": {
                "original_input": input_text,
                "extracted_query": input_text
            },
            "result": {
                "error": "unknown_error",
                "message": "An unknown error occurred"
            }
        }
        
        try:
            # First, do regular search to get book info
            if input_format == "url":
                from standardized_book_search import StandardizedBookSearch
                service = StandardizedBookSearch()
                search_result = await service.search_book(input_text)
            else:
                from txt_to_epub_service import TextToEPUBService
                service = TextToEPUBService()
                search_result = await service.search_book_from_text(input_text)
            
            if search_result["status"] == "success":
                book_info = search_result["result"]["book_info"]
                confidence = search_result["result"]["confidence"]
                service_used = search_result["result"]["service_used"]
                
                # Calculate readability confidence
                readability = self.calculate_readability_confidence(book_info)
                
                # Get actual download URL if enabled
                download_info = {"available": False, "url": None}
                if enable_download:
                    download_result = await self.get_actual_download_url(
                        book_info, 
                        search_result["query_info"]["extracted_query"]
                    )
                    
                    if download_result["success"]:
                        download_info = {
                            "available": True,
                            "url": download_result["download_url"],
                            "local_path": download_result["local_path"],
                            "filename": download_result["filename"],
                            "file_size": download_result["file_size"]
                        }
                        # Update readability with download success
                        readability = self.calculate_readability_confidence(book_info, True)
                    else:
                        download_info = {
                            "available": False,
                            "url": None,
                            "reason": download_result["reason"]
                        }
                        # Update readability with download failure
                        readability = self.calculate_readability_confidence(book_info, False)
                
                # Build enhanced response
                response.update({
                    "status": "success",
                    "query_info": search_result["query_info"],
                    "result": {
                        "found": True,
                        "epub_download_url": download_info.get("url"),
                        "download_info": download_info,
                        "confidence": confidence,
                        "readability": readability,
                        "book_info": book_info,
                        "service_used": service_used
                    }
                })
            else:
                # Pass through the original error
                response = search_result
                
        except Exception as e:
            response.update({
                "status": "error",
                "result": {
                    "error": "enhanced_service_error",
                    "message": f"Enhanced service error: {str(e)[:200]}"
                }
            })
        
        return response

async def main():
    """Test the enhanced download service"""
    
    service = EnhancedDownloadService()
    
    test_cases = [
        "Harry Potter philosopher stone",
        "Clean Code Robert Martin",
        "https://www.podpisnie.ru/books/maniac/"
    ]
    
    print("🚀 Enhanced Download Service with Readability Testing")
    print("=" * 70)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_input}")
        print("-" * 50)
        
        result = await service.enhanced_search_with_download(test_input, enable_download=False)  # Disable actual download for testing
        
        if result["status"] == "success":
            book_info = result["result"]["book_info"]
            confidence = result["result"]["confidence"] 
            readability = result["result"]["readability"]
            
            print(f"✅ Found: {book_info['title'][:50]}")
            print(f"🎯 Match Confidence: {confidence['level']} ({confidence['score']:.3f})")
            print(f"📖 Readability: {readability['level']} ({readability['score']:.3f})")
            print(f"📋 Quality factors:")
            for factor in readability['factors']:
                print(f"   • {factor}")
        else:
            print(f"❌ {result['result']['error']}: {result['result']['message']}")

if __name__ == "__main__":
    asyncio.run(main())