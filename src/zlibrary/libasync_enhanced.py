"""
Enhanced AsyncZlib with bulletproof authentication and parsing
"""
import json
import logging
import os
from typing import Optional, Dict, List
from .libasync import AsyncZlib
from .abs_enhanced import EnhancedSearchPaginator, SessionCookieManager, BookItem
from .profile import ZlibProfile
from .exception import LoginFailed, NoDomainError
from .util import GET_request, POST_request

logger = logging.getLogger(__name__)

class EnhancedAsyncZlib(AsyncZlib):
    """Enhanced Z-Library client with fallback mechanisms"""
    
    def __init__(self, onion: bool = False, proxy_list: Optional[list] = None, 
                 cookie_file: str = "cookies.txt", use_cookie_fallback: bool = True):
        super().__init__(onion, proxy_list)
        self.cookie_file = cookie_file
        self.use_cookie_fallback = use_cookie_fallback
        self._authenticated = False
        
    async def login(self, email: str = None, password: str = None) -> Optional[ZlibProfile]:
        """Enhanced login with cookie fallback"""
        
        # First try regular login if credentials provided
        if email and password:
            try:
                logger.info(f"Attempting login with email: {email}")
                profile = await super().login(email, password)
                self._authenticated = True
                
                # Save successful cookies
                if self.cookies:
                    SessionCookieManager.save_cookies(self.cookies, self.cookie_file)
                    logger.info(f"Saved session cookies to {self.cookie_file}")
                    
                return profile
                
            except (LoginFailed, AttributeError) as e:
                logger.warning(f"Login failed: {e}")
                
                if not self.use_cookie_fallback:
                    raise
                    
        # Try cookie fallback
        if self.use_cookie_fallback:
            logger.info("Attempting cookie-based authentication...")
            cookies = SessionCookieManager.load_cookies(self.cookie_file)
            
            if cookies and "remix_userid" in cookies and "remix_userkey" in cookies:
                logger.info(f"Found session cookies for user ID: {cookies['remix_userid']}")
                
                # Set cookies and mirror
                self.cookies = cookies
                self.mirror = "https://z-library.sk"
                
                # Create mock profile
                profile = ZlibProfile(
                    GET_request,
                    self.cookies,
                    self.mirror,
                    self.mirror
                )
                
                # Verify cookies are valid by making a test request
                try:
                    test_url = f"{self.mirror}/users/downloads"
                    resp = await GET_request(test_url, cookies=self.cookies)
                    
                    if "You are not logged in" in resp:
                        logger.warning("Session cookies are expired")
                        if email and password:
                            raise LoginFailed("Both login and cookie authentication failed")
                    else:
                        logger.info("✓ Cookie authentication successful")
                        self._authenticated = True
                        self.profile = profile
                        return profile
                        
                except Exception as e:
                    logger.error(f"Cookie validation failed: {e}")
                    
        raise LoginFailed("All authentication methods failed")
        
    async def search(self, q: str, count: int = 10, **kwargs) -> EnhancedSearchPaginator:
        """Enhanced search with better parsing"""
        
        if not self._authenticated and not self.cookies:
            # Try to authenticate with cookies
            await self.login()
            
        if not self.mirror:
            self.mirror = "https://z-library.sk"
            
        # Build search URL
        search_url = f"{self.mirror}/s/{q}"
        
        # Create enhanced paginator
        paginator = EnhancedSearchPaginator(
            lambda url: GET_request(url, cookies=self.cookies),
            search_url,
            self.mirror,
            count
        )
        
        return paginator
        
    async def search_with_fallback(self, q: str, count: int = 10, **kwargs) -> Dict:
        """Search with automatic fallback and structured response"""
        
        try:
            # Try to search
            paginator = await self.search(q, count, **kwargs)
            await paginator.init()
            
            # Build response
            results = []
            for book in paginator.result:
                # Ensure all fields are present
                book_data = {
                    "id": book.get("id", ""),
                    "title": book.get("title", book.get("name", "Unknown")),
                    "authors": book.get("authors", "Unknown"),
                    "year": book.get("year", ""),
                    "publisher": book.get("publisher", ""),
                    "extension": book.get("extension", ""),
                    "size": book.get("size", book.get("filesize", "")),
                    "language": book.get("language", ""),
                    "isbn": book.get("isbn", ""),
                    "url": book.get("url", ""),
                    "rating": book.get("rating", "")
                }
                results.append(book_data)
                
            response = {
                "status": "success",
                "query": q,
                "total_results": len(results),
                "page": paginator.page,
                "total_pages": paginator.total,
                "results": results
            }
            
            # Add account info if available
            if self.cookies:
                response["account_info"] = {
                    "user_id": self.cookies.get("remix_userid", "Unknown"),
                    "authenticated": self._authenticated
                }
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            response = {
                "status": "error",
                "query": q,
                "error": str(e),
                "message": "Search failed. Please check your authentication."
            }
            
        return response
        
    async def download_book(self, book_id: str) -> Dict:
        """Download a book by ID with structured response"""
        
        if not self._authenticated and not self.cookies:
            await self.login()
            
        try:
            # Get book details
            book_url = f"{self.mirror}/book/{book_id}"
            resp = await GET_request(book_url, cookies=self.cookies)
            
            # Parse book page
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp, "lxml")
            
            # Extract download URL
            download_btn = soup.find("a", class_="dlButton")
            if not download_btn:
                download_btn = soup.find("a", href=lambda x: x and "dl2.php" in x)
                
            if download_btn:
                download_url = download_btn.get("href", "")
                if not download_url.startswith("http"):
                    download_url = self.mirror + download_url
                    
                # Get book metadata
                title = soup.find("h1", itemprop="name")
                title_text = title.text.strip() if title else f"Book_{book_id}"
                
                response = {
                    "status": "success",
                    "book_id": book_id,
                    "title": title_text,
                    "download_url": download_url,
                    "message": "Download URL retrieved successfully"
                }
            else:
                response = {
                    "status": "error",
                    "book_id": book_id,
                    "message": "Download not available (daily limit may be reached)"
                }
                
        except Exception as e:
            response = {
                "status": "error",
                "book_id": book_id,
                "error": str(e),
                "message": "Failed to get download URL"
            }
            
        return response


# Convenience function for quick searches
async def quick_search(query: str, use_cookies: bool = True) -> Dict:
    """Quick search function with automatic authentication"""
    
    client = EnhancedAsyncZlib(use_cookie_fallback=use_cookies)
    
    try:
        # Try to authenticate (will use cookies if available)
        await client.login()
    except:
        logger.warning("Authentication failed, attempting anonymous search")
        
    return await client.search_with_fallback(query)