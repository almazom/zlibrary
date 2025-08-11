#!/usr/bin/env python3
"""
Simple Book Search Service - Single API endpoint backend
Clean, simple implementation for book_search.sh
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import re
from difflib import SequenceMatcher

# Load environment
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib, Extension, Language

def normalize_filename(title, author=""):
    """Normalize filename for comparison"""
    # Combine title and author
    full_name = f"{title}_{author}" if author else title
    # Lowercase and remove special chars
    normalized = re.sub(r'[^\w\s]', '', full_name.lower())
    # Replace spaces with underscores
    normalized = re.sub(r'\s+', '_', normalized)
    # Remove multiple underscores
    normalized = re.sub(r'_+', '_', normalized)
    return normalized.strip('_')

def check_duplicate(title, author=""):
    """Check if book already downloaded"""
    downloads_dir = Path(os.getenv('DOWNLOAD_DIR', './downloads'))
    if not downloads_dir.exists():
        return None
    
    search_normalized = normalize_filename(title, author)
    
    for epub_file in downloads_dir.glob('*.epub'):
        file_normalized = normalize_filename(epub_file.stem)
        
        # Exact match
        if file_normalized == search_normalized:
            return {
                'exact_match': True,
                'path': str(epub_file.absolute()),
                'size': epub_file.stat().st_size
            }
        
        # Similarity check
        similarity = SequenceMatcher(None, file_normalized, search_normalized).ratio()
        if similarity > 0.8:
            return {
                'exact_match': False,
                'similar': True,
                'path': str(epub_file.absolute()),
                'size': epub_file.stat().st_size,
                'similarity': similarity
            }
    
    return None

def should_download(confidence_score, readability_score):
    """Check if book meets quality thresholds"""
    min_confidence = float(os.getenv('MIN_CONFIDENCE', '0.4'))
    min_quality = os.getenv('MIN_QUALITY', 'ANY')
    
    # Check confidence threshold
    if confidence_score < min_confidence:
        return False, f"Confidence {confidence_score:.2f} below threshold {min_confidence}"
    
    # Check quality threshold
    quality_thresholds = {
        "EXCELLENT": 0.8,
        "GOOD": 0.65,
        "FAIR": 0.5,
        "ANY": 0.0
    }
    
    min_qual_score = quality_thresholds.get(min_quality, 0.0)
    if readability_score < min_qual_score:
        return False, f"Quality {readability_score:.2f} below {min_quality} threshold"
    
    return True, "Meets all criteria"

def detect_and_translate_query(query):
    """Detect if query is Russian and prepare fallback translations"""
    import re
    
    # Check if query contains Cyrillic characters
    has_cyrillic = bool(re.search('[а-яА-ЯёЁ]', query))
    
    # Common Russian book title patterns to translate
    translations = {
        'средневековое мышление': 'Penser au Moyen Age',
        'феноменология восприятия': 'Phenomenologie de la perception',
        'бытие и ничто': 'L\'Être et le Néant',
        'критика чистого разума': 'Kritik der reinen Vernunft',
        'атомные привычки': 'Atomic Habits',
        'чистый код': 'Clean Code',
        'прагматичный программист': 'Pragmatic Programmer',
        'паттерны проектирования': 'Design Patterns',
    }
    
    # Check for known translations
    original_query = None
    query_lower = query.lower()
    for ru_title, en_title in translations.items():
        if ru_title in query_lower:
            original_query = query_lower.replace(ru_title, en_title)
            break
    
    # Extract author names that might be transliterated
    author_translations = {
        'ален де либера': 'Alain de Libera',
        'мерло-понти': 'Merleau-Ponty',
        'сартр': 'Sartre',
        'кант': 'Kant',
        'гегель': 'Hegel',
        'делез': 'Deleuze',
        'гваттари': 'Guattari',
        'дебор': 'Debord',
        'роберт мартин': 'Robert Martin',
        'джеймс клир': 'James Clear',
    }
    
    for ru_author, en_author in author_translations.items():
        if ru_author in query_lower:
            if not original_query:
                original_query = query
            original_query = original_query.replace(ru_author, en_author)
    
    return has_cyrillic, original_query

async def search_book(query):
    """Simple book search with multi-account fallback, format support, and language fallback"""
    
    accounts = [
        ('almazomam@gmail.com', 'tataronrails78'),
        ('almazomam2@gmail.com', 'tataronrails78'),
        ('almazomam3@gmail.com', 'tataronrails78')
    ]
    
    # Check if debug mode is enabled
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    debug_info = {
        "accounts_tried": [],
        "login_attempts": [],
        "search_attempts": [],
        "duplicate_checks": [],
        "confidence_calculations": []
    } if debug_mode else None
    
    # Get format preference from environment
    format_pref = os.getenv('FORMAT', 'epub').lower()
    formats_to_try = []
    
    if format_pref == 'auto':
        formats_to_try = ['epub', 'pdf']
    elif format_pref == 'pdf':
        formats_to_try = ['pdf']
    else:
        formats_to_try = ['epub']
    
    # Detect language and prepare fallback
    is_russian, fallback_query = detect_and_translate_query(query)
    queries_to_try = [query]  # Always try original first
    if is_russian and fallback_query:
        queries_to_try.append(fallback_query)  # Add translation as fallback
    
    timestamp = datetime.now().isoformat()
    
    # Detect input format
    if query.startswith(('http://', 'https://')):
        input_format = "url"
        # Extract query from URL if needed
        if 'podpisnie.ru/books/' in query:
            query = query.split('/books/')[-1].replace('/', '').replace('-', ' ')
    elif query.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        input_format = "image"
    else:
        input_format = "txt"
    
    # Base response
    response = {
        "status": "error",
        "timestamp": timestamp,
        "input_format": input_format,
        "query_info": {
            "original_input": sys.argv[1] if len(sys.argv) > 1 else query,
            "extracted_query": query
        },
        "result": {
            "error": "search_failed",
            "message": "No working accounts found"
        }
    }
    
    # Try each account
    for account_idx, (email, password) in enumerate(accounts, 1):
        try:
            if debug_mode:
                debug_info["accounts_tried"].append(email)
                debug_info["login_attempts"].append({
                    "account": email,
                    "account_number": f"{account_idx}/{len(accounts)}",
                    "timestamp": datetime.now().isoformat()
                })
            
            client = AsyncZlib()
            profile = await client.login(email, password)
            limits = await profile.get_limits()
            
            if debug_mode:
                debug_info["login_attempts"][-1].update({
                    "login_success": True,
                    "downloads_remaining": limits.get('daily_remaining', 0),
                    "downloads_limit": limits.get('daily_allowed', 10),
                    "downloads_used": limits.get('daily_amount', 0)
                })
            
            if limits.get('daily_remaining', 0) > 0:
                # Try each query (original + fallback if exists)
                search_results = None
                format_used = None
                actual_query_used = query
                language_fallback_used = False
                
                for query_to_try in queries_to_try:
                    # Try each format in preference order
                    for format_type in formats_to_try:
                        # Set extension based on format
                        if format_type == 'pdf':
                            ext = Extension.PDF
                        else:
                            ext = Extension.EPUB
                        
                        # Search for book in this format
                        search_results = await client.search(
                            q=query_to_try,
                            extensions=[ext],
                            count=1
                        )
                        
                        await search_results.init()
                        
                        if search_results.result:
                            # Quick confidence check - if too low, continue to fallback
                            book = search_results.result[0]
                            book_info = await book.fetch()
                            title_lower = book_info.get('name', '').lower()
                            
                            # Check if it's clearly a wrong match
                            if query_to_try == query and is_russian:  # Original Russian query
                                # Check for obvious mismatches
                                if 'средневековое' in query_to_try.lower() and 'латеральное' in title_lower:
                                    # Wrong book, try fallback
                                    continue
                                if 'мерло-понти' in query_to_try.lower() and 'гегель' in title_lower:
                                    # Wrong philosopher, try fallback
                                    continue
                                if 'восприятия' in query_to_try.lower() and 'духа' in title_lower:
                                    # Wrong phenomenology book
                                    continue
                            
                            format_used = format_type
                            actual_query_used = query_to_try
                            language_fallback_used = (query_to_try != query)
                            break
                    
                    # If found with this query, stop trying
                    if search_results and search_results.result and format_used:
                        break
                
                if not search_results or not search_results.result:
                    response["status"] = "not_found"
                    response["result"] = {
                        "found": False,
                        "message": "No books found matching the search criteria"
                    }
                else:
                    # Get book details
                    book = search_results.result[0]
                    book_info = await book.fetch()
                    
                    # Check for duplicates before downloading
                    book_title = book_info.get('name', '')
                    book_authors = book_info.get('authors', [])
                    author_name = book_authors[0].get('name', '') if book_authors else ''
                    
                    duplicate = check_duplicate(book_title, author_name)
                    
                    if debug_mode:
                        debug_info["duplicate_checks"].append({
                            "title": book_title,
                            "author": author_name,
                            "duplicate_found": duplicate is not None,
                            "exact_match": duplicate.get('exact_match', False) if duplicate else False,
                            "similar_match": duplicate.get('similar', False) if duplicate else False,
                            "similarity": duplicate.get('similarity', 0) if duplicate else 0
                        })
                    
                    # If duplicate found, use existing file
                    if duplicate and duplicate.get('exact_match'):
                        download_path = duplicate['path']
                        download_url = None
                        already_downloaded = True
                    else:
                        already_downloaded = False
                        
                        # Try to download the book
                        download_url = book_info.get('download_url', '')
                        download_path = None
                        
                        if download_url and 'daily limit' not in download_url.lower():
                            # Create downloads directory
                            downloads_dir = Path(os.getenv('DOWNLOAD_DIR', './downloads'))
                            downloads_dir.mkdir(exist_ok=True)
                            
                            # Clean filename with format
                            title = book_info.get('name', 'book').replace('/', '_').replace('\\', '_')[:100]
                            authors = book_info.get('authors', [])
                            author_str = authors[0].get('name', '') if authors else ''
                            author_str = author_str.replace('/', '_').replace('\\', '_')[:50]
                            file_ext = format_used if format_used else 'epub'
                            filename = f"{title}_{author_str}.{file_ext}".replace(' ', '_').replace('__', '_')
                            download_path = downloads_dir / filename
                            
                            try:
                                # Download the book using proper authenticated request
                                import aiohttp
                                async with aiohttp.ClientSession() as session:
                                    # Prepare the full download URL
                                    if not download_url.startswith('http'):
                                        download_url = client.mirror + download_url
                                        
                                    async with session.get(download_url, cookies=client.cookies) as resp:
                                        if resp.status == 200:
                                            content = await resp.read()
                                            if content and len(content) > 1000:  # Basic check for valid file
                                                with open(download_path, 'wb') as f:
                                                    f.write(content)
                                                download_path = str(download_path.absolute())
                                            else:
                                                download_path = None
                                        else:
                                            download_path = None
                            except Exception as e:
                                download_path = None
                    
                    # Calculate simple confidence
                    query_lower = query.lower()
                    title_lower = book_info.get('name', '').lower()
                    
                    # Word overlap
                    query_words = set(query_lower.split())
                    title_words = set(title_lower.split())
                    overlap = len(query_words & title_words) / len(query_words) if query_words else 0
                    
                    confidence_score = min(overlap * 0.5 + 0.5, 1.0)
                    
                    if confidence_score >= 0.8:
                        confidence_level = "VERY_HIGH"
                        confidence_desc = "Очень высокая уверенность - это точно искомая книга"
                    elif confidence_score >= 0.6:
                        confidence_level = "HIGH"
                        confidence_desc = "Высокая уверенность - скорее всего это нужная книга"
                    elif confidence_score >= 0.4:
                        confidence_level = "MEDIUM"
                        confidence_desc = "Средняя уверенность - возможно это нужная книга"
                    else:
                        confidence_level = "LOW"
                        confidence_desc = "Низкая уверенность - вряд ли это искомая книга"
                    
                    # Simple readability score
                    readability_score = 0.7  # Base score
                    factors = []
                    
                    size_str = book_info.get('size', '')
                    if 'MB' in size_str:
                        readability_score = 0.85
                        factors.append(f"Good file size ({size_str})")
                    
                    if book_info.get('publisher'):
                        readability_score = min(readability_score + 0.1, 1.0)
                        factors.append("Has publisher information")
                    
                    if readability_score >= 0.8:
                        readability_level = "EXCELLENT"
                        readability_desc = "Отличное качество - высококачественный EPUB"
                    elif readability_score >= 0.65:
                        readability_level = "GOOD"
                        readability_desc = "Хорошее качество - читабельный EPUB"
                    else:
                        readability_level = "FAIR"
                        readability_desc = "Удовлетворительное качество"
                    
                    # Check if meets quality thresholds
                    meets_threshold, skip_reason = should_download(confidence_score, readability_score)
                    
                    # Only download if meets thresholds (and not already downloaded)
                    if not already_downloaded and not meets_threshold:
                        download_path = None
                        download_url = None
                    
                    # Build successful response
                    response = {
                        "status": "success",
                        "timestamp": timestamp,
                        "input_format": input_format,
                        "query_info": {
                            "original_input": sys.argv[1] if len(sys.argv) > 1 else query,
                            "extracted_query": query,
                            "actual_query_used": actual_query_used,
                            "language_fallback_used": language_fallback_used
                        },
                        "result": {
                            "found": True,
                            "epub_download_url": download_path,  # Keep for backwards compatibility
                            "already_downloaded": already_downloaded,
                            "format_downloaded": format_used if format_used else None,
                            "format_searched": formats_to_try,
                            "fallback_used": len(formats_to_try) > 1 and formats_to_try[0] != format_used,
                            "download_info": {
                                "available": download_path is not None,
                                "url": download_url if download_url else None,
                                "local_path": download_path,
                                "format": format_used,
                                "is_duplicate": already_downloaded,
                                "skipped": not meets_threshold,
                                "skip_reason": skip_reason if not meets_threshold else None
                            },
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
                                "factors": factors
                            },
                            "book_info": {
                                "title": book_info.get('name', ''),
                                "authors": [a.get('name', '') for a in book_info.get('authors', [])[:3]],
                                "year": book_info.get('year', ''),
                                "publisher": book_info.get('publisher', ''),
                                "size": book_info.get('size', ''),
                                "description": book_info.get('description', '')[:300] if book_info.get('description') else ''
                            },
                            "service_used": "zlibrary"
                        }
                    }
                    
                    # Add debug info if enabled
                    if debug_mode:
                        response["debug"] = {
                            "account_used": email,
                            "account_number": f"{account_idx}/{len(accounts)}",
                            "accounts_tried": len(debug_info["accounts_tried"]),
                            "downloads_remaining": f"{limits.get('daily_remaining', 0)}/{limits.get('daily_allowed', 10)}",
                            "login_attempts": debug_info["login_attempts"],
                            "duplicate_check": debug_info["duplicate_checks"][-1] if debug_info["duplicate_checks"] else None,
                            "query_used": actual_query_used,
                            "language_fallback": language_fallback_used,
                            "format_searched": formats_to_try,
                            "format_found": format_used
                        }
                
                await client.logout()
                break
                
        except Exception as e:
            if debug_mode:
                if debug_info["login_attempts"] and len(debug_info["login_attempts"]) > account_idx - 1:
                    debug_info["login_attempts"][-1]["login_success"] = False
                    debug_info["login_attempts"][-1]["error"] = str(e)
            # Try next account
            continue
    
    return response

async def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "result": {
                "error": "no_input",
                "message": "No query provided"
            }
        }))
        sys.exit(1)
    
    query = sys.argv[1]
    result = await search_book(query)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())