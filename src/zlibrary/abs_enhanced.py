"""
Enhanced SearchPaginator with bulletproof parsing and cookie fallback
"""
from bs4 import BeautifulSoup as bsoup
from bs4 import Tag
import logging
import json
import os
import time
from .exception import ParseError

logger = logging.getLogger(__name__)

class BookItem(dict):
    """Enhanced BookItem with better field extraction"""
    
    def __init__(self, request_func, mirror):
        super().__init__()
        self.__r = request_func
        self.mirror = mirror
        
    async def fetch(self):
        """Fetch detailed book information"""
        if not self.get("url"):
            raise ValueError("No URL available for this book")
            
        resp = await self.__r(self.get("url"))
        soup = bsoup(resp, features="lxml")
        
        details = {}
        
        # Extract all available metadata
        title = soup.find("h1", itemprop="name")
        if title:
            details["name"] = title.text.strip()
            
        # Author extraction
        authors = []
        author_links = soup.find_all("a", itemprop="author")
        for a in author_links:
            authors.append({"name": a.text.strip(), "url": self.mirror + a.get("href", "")})
        details["authors"] = authors
        
        # Download URL
        download_btn = soup.find("a", class_="dlButton")
        if not download_btn:
            download_btn = soup.find("a", href=lambda x: x and "dl2.php" in x)
        if download_btn:
            dl_url = download_btn.get("href", "")
            if not dl_url.startswith("http"):
                dl_url = self.mirror + dl_url
            details["download_url"] = dl_url
        else:
            details["download_url"] = "Not available"
            
        # Other metadata
        for field in ["year", "publisher", "language", "categories", "isbn", "isbn10", "isbn13"]:
            elem = soup.find(attrs={"itemprop": field})
            if elem:
                details[field] = elem.text.strip()
                
        # File info
        file_info = soup.find("div", class_="property__file")
        if file_info:
            value = file_info.find("div", class_="property_value")
            if value:
                parts = value.text.strip().split(",")
                details["extension"] = parts[0].strip() if parts else "Unknown"
                details["size"] = parts[1].strip() if len(parts) > 1 else "Unknown"
                
        # Description
        desc = soup.find("div", id="bookDescriptionBox")
        if desc:
            details["description"] = desc.text.strip()
            
        # Rating
        rating = soup.find("span", itemprop="ratingValue")
        if rating:
            details["rating"] = rating.text.strip()
            
        return details

class EnhancedSearchPaginator:
    """Enhanced paginator with multiple parsing strategies"""
    
    def __init__(self, request_func, url, mirror, count=10):
        self.__r = request_func
        self.__url = url
        self.mirror = mirror
        self.count = count
        self.page = 1
        self.total = 0
        self.result = []
        self.storage = {}
        
    def parse_page_strategy_1(self, page):
        """New structure with z-bookcard elements"""
        soup = bsoup(page, features="lxml")
        box = soup.find("div", {"id": "searchResultBox"})
        
        if not box:
            return None
            
        # Check for no results
        check_notfound = soup.find("div", {"class": "notFound"})
        if check_notfound:
            logger.debug("Nothing found.")
            self.storage[self.page] = []
            self.result = []
            return []
            
        # Find book items with new structure
        book_items = box.findAll("div", {"class": ["book-item", "resItemBoxBooks"]})
        if not book_items:
            # Try finding z-bookcard directly
            book_items = soup.findAll("z-bookcard")
            
        results = []
        
        for book in book_items:
            js = BookItem(self.__r, self.mirror)
            
            # Handle z-bookcard element
            if book.name == "z-bookcard":
                card = book
            else:
                card = book.find("z-bookcard")
                
            if card:
                # Extract from z-bookcard attributes
                js["id"] = card.get("id", "")
                js["isbn"] = card.get("isbn", "")
                js["title"] = card.get("title", "Unknown")
                
                book_url = card.get("href", "")
                if book_url:
                    js["url"] = f"{self.mirror}{book_url}" if not book_url.startswith("http") else book_url
                    
                # Try to get additional attributes
                js["publisher"] = card.get("publisher", "")
                js["year"] = card.get("year", "")
                js["language"] = card.get("language", "")
                js["extension"] = card.get("extension", "")
                js["filesize"] = card.get("filesize", "")
                js["rating"] = card.get("rating", "")
                
                # Look for author in slots
                author_slot = card.find("div", {"slot": "author"})
                if author_slot:
                    js["authors"] = author_slot.text.strip()
                    
                title_slot = card.find("div", {"slot": "title"})
                if title_slot:
                    js["title"] = title_slot.text.strip()
                    
            results.append(js)
            
        return results
        
    def parse_page_strategy_2(self, page):
        """Old structure with resItemBox"""
        soup = bsoup(page, features="lxml")
        
        book_list = soup.findAll("div", {"class": "resItemBox"})
        if not book_list:
            return None
            
        results = []
        
        for book in book_list:
            js = BookItem(self.__r, self.mirror)
            
            # Title and URL
            title_elem = book.find("h3", itemprop="name")
            if title_elem:
                js["title"] = title_elem.text.strip()
                link = title_elem.find("a")
                if link:
                    js["url"] = self.mirror + link.get("href", "")
                    
            # Authors
            author_links = book.find_all("a", href=lambda x: x and "/author/" in x)
            authors = [a.text.strip() for a in author_links]
            if authors:
                js["authors"] = ", ".join(authors)
                
            # Year
            year_elem = book.find("div", class_="property_year")
            if year_elem:
                value = year_elem.find("div", class_="property_value")
                if value:
                    js["year"] = value.text.strip()
                    
            # Publisher
            pub_elem = book.find("div", class_="property_publisher")
            if pub_elem:
                value = pub_elem.find("div", class_="property_value")
                if value:
                    js["publisher"] = value.text.strip()
                    
            # File info
            file_elem = book.find("div", class_="property__file")
            if file_elem:
                value = file_elem.find("div", class_="property_value")
                if value:
                    parts = value.text.strip().split(",")
                    js["extension"] = parts[0].strip() if parts else ""
                    js["size"] = parts[1].strip() if len(parts) > 1 else ""
                    
            results.append(js)
            
        return results
        
    def parse_page(self, page):
        """Try multiple parsing strategies"""
        
        # Try strategy 1 (new structure)
        results = self.parse_page_strategy_1(page)
        if results is not None:
            self.storage[self.page] = results
            self.result = results
            return
            
        # Try strategy 2 (old structure)
        results = self.parse_page_strategy_2(page)
        if results is not None:
            self.storage[self.page] = results
            self.result = results
            return
            
        # If both fail, raise error
        raise ParseError("Could not parse book list with any strategy")
        
    async def init(self):
        """Initialize paginator"""
        url = f"{self.__url}&page={self.page}&limit={self.count}"
        resp = await self.__r(url)
        self.parse_page(resp)
        
        # Extract total pages
        soup = bsoup(resp, features="lxml")
        paginator = soup.find("div", class_="paginator")
        if paginator:
            pages = paginator.find_all("a")
            if pages:
                try:
                    self.total = int(pages[-2].text)
                except:
                    self.total = 1
        else:
            self.total = 1
            
    async def next_page(self):
        """Go to next page"""
        if self.page < self.total:
            self.page += 1
            if self.page not in self.storage:
                url = f"{self.__url}&page={self.page}&limit={self.count}"
                resp = await self.__r(url)
                self.parse_page(resp)
            else:
                self.result = self.storage[self.page]
                
    async def prev_page(self):
        """Go to previous page"""
        if self.page > 1:
            self.page -= 1
            if self.page in self.storage:
                self.result = self.storage[self.page]
            else:
                url = f"{self.__url}&page={self.page}&limit={self.count}"
                resp = await self.__r(url)
                self.parse_page(resp)


class SessionCookieManager:
    """Manage session cookies for fallback authentication"""
    
    @staticmethod
    def load_cookies(cookie_file="cookies.txt"):
        """Load cookies from file"""
        cookies = {}
        
        if os.path.exists(cookie_file):
            with open(cookie_file, "r") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.strip().split("\t")
                    if len(parts) >= 7:
                        name = parts[5]
                        value = parts[6]
                        if name in ["remix_userid", "remix_userkey", "selectedSiteMode"]:
                            cookies[name] = value
                            
        return cookies
        
    @staticmethod
    def save_cookies(cookies, cookie_file="cookies.txt"):
        """Save cookies to file in Netscape format"""
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# https://curl.haxx.se/docs/http-cookies.html\n")
            f.write("# This file was generated by zlibrary enhanced API\n\n")
            
            for name, value in cookies.items():
                # domain, flag, path, secure, expiry, name, value
                f.write(f".z-library.sk\tTRUE\t/\tTRUE\t{int(time.time()) + 86400*30}\t{name}\t{value}\n")