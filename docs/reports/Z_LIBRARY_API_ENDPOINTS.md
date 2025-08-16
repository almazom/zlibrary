# 📚 Z-Library API Endpoints Documentation

## 🌐 Base URLs
- **Clearnet**: `https://z-library.sk`
- **Tor/Onion**: `http://bookszlibb74ugqojhzhg2a63w5i2atv5bqarulgczawnbmsb6s6qead.onion`
- **Login Onion**: `http://loginzlib2vrak5zzpcocc3ouizykn6k5qecgj2tzlnab5wcbqhembyd.onion`

## 🔐 Authentication Endpoints

### Login
**Endpoint**: `POST /rpc.php`

**Headers**:
```
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
```

**Body Parameters**:
- `email`: User email address
- `password`: User password  
- `action`: "login"
- `gg_json_mode`: 1 (for JSON response)

**Response** (JSON):
```json
{
  "errors": [],
  "response": {
    "params": "",
    "priorityRedirectUrl": "/?remix_userid=ID&remix_userkey=KEY",
    "forceRedirection": "/?remix_userid=ID&remix_userkey=KEY",
    "user_id": 42838870,
    "user_key": "3738509343d5697c26273dfc2e05b2ec"
  }
}
```

**Cookies Set**:
- `remix_userid`: User ID
- `remix_userkey`: Session key
- `selectedSiteMode`: "books"

---

## 🔍 Search Endpoints

### Standard Search
**Endpoint**: `GET /s/{query}`

**Query Parameters**:
- `page`: Page number (default: 1)
- `yearFrom`: Start year filter
- `yearTo`: End year filter
- `languages`: Language codes (comma-separated)
- `extensions`: File extensions (comma-separated)

**Example**:
```
GET /s/python%20programming?page=1&yearFrom=2020&extensions=pdf,epub
```

### Full-Text Search
**Endpoint**: `GET /fulltext/{query}`

**Query Parameters**:
- `phrase`: 1 for exact phrase search
- `words`: 1 for word-based search
- Other parameters same as standard search

---

## 📖 Book Detail Endpoints

### Get Book Information
**Endpoint**: `GET /book/{book_id}/{hash}/{slug}.html`

**Example**:
```
GET /book/117550122/47896b/the-emperor-of-gladness.html
```

**Response**: HTML containing:
- Book metadata (title, author, year, publisher)
- Cover image URL
- Download link
- File information (size, format)
- Rating and quality scores

---

## 📥 Download Endpoints

### Direct Download
**Endpoint**: `GET /dl/{book_id}/{hash}`

**Headers Required**:
```
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
Cookie: remix_userid=ID; remix_userkey=KEY
```

**Example**:
```
GET /dl/117550122/577cf9
```

**Response**: 
- Binary file download (EPUB/PDF/MOBI)
- Follows redirects (use `-L` with curl)

### Download with Mirror
For personalized mirrors, the download URL pattern is:
```
https://[user-mirror].z-library.sk/dl/{book_id}/{hash}
```

---

## 👤 User Profile Endpoints

### Get Download Limits
**Endpoint**: `GET /users/downloads`

**Response** (HTML parsed to):
```json
{
  "daily_amount": 10,
  "daily_allowed": 10,
  "daily_remaining": 8,
  "daily_reset": "2h 30m"
}
```

### Download History
**Endpoint**: `GET /users/downloads-history`

**Query Parameters**:
- `page`: Page number
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)

---

## 📚 Booklist Endpoints

### Public Booklists Search
**Endpoint**: `GET /booklists`

**Query Parameters**:
- `searchQuery`: Search query
- `order`: Sorting (popular/newest/recent)

### Private Booklists
**Endpoint**: `GET /booklists/my`

**Query Parameters**:
- `searchQuery`: Search query
- `order`: Sorting option

---

## 🔧 Python API Usage

### Authentication
```python
from zlibrary import AsyncZlib

client = AsyncZlib()
await client.login("email@example.com", "password")
```

### Search and Download
```python
# Search
results = await client.search("python programming", count=10)
await results.init()

# Get first book
book = results.result[0]
details = await book.fetch()

# Download URL is in details
download_url = details['download_url']
print(f"Download: {download_url}")
```

### Direct Book Access
```python
# Get book by ID
book = await client.get_by_id("117550122/47896b")
print(f"Download URL: {book['download_url']}")
```

---

## 🌐 Raw cURL Examples

### 1. Authenticate
```bash
curl -X POST https://z-library.sk/rpc.php \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=user@example.com&password=pass&action=login&gg_json_mode=1" \
  -c cookies.txt
```

### 2. Search
```bash
curl -X GET "https://z-library.sk/s/python%20programming?page=1" \
  -H "User-Agent: Mozilla/5.0" \
  -b cookies.txt
```

### 3. Get Book Details
```bash
curl -X GET "https://z-library.sk/book/117550122/47896b/book.html" \
  -H "User-Agent: Mozilla/5.0" \
  -b cookies.txt
```

### 4. Download Book
```bash
curl -L "https://z-library.sk/dl/117550122/577cf9" \
  -H "User-Agent: Mozilla/5.0" \
  -b cookies.txt \
  -o book.epub
```

---

## 📊 Response Formats

### Search Results (HTML)
- Contains `<div class="book-item">` elements
- Each book has `<z-bookcard>` custom element with attributes:
  - `id`: Book ID
  - `isbn`: ISBN number
  - `href`: Book detail URL
  - `download`: Download path
  - `extension`: File format
  - `filesize`: File size
  - `year`: Publication year
  - `rating`: User rating

### Book Details (HTML)
- Download link in: `<a class="dlButton" href="/dl/...">` 
- Metadata in various `<div>` elements
- Cover image in: `<img class="cover">`

---

## ⚠️ Rate Limiting

- **Concurrent Requests**: Limited to 64 (handled by AsyncZlib semaphore)
- **Daily Download Limit**: Varies by account type (typically 10/day for free accounts)
- **Session Duration**: Cookies valid for ~24 hours

---

## 🔒 Security Notes

1. **Always use HTTPS** for clearnet connections
2. **Store cookies securely** - they contain session tokens
3. **Use Tor/proxies** for enhanced privacy
4. **Don't share session keys** - they provide full account access
5. **Respect rate limits** to avoid account suspension

---

## 📝 Error Codes

- **LoginFailed**: Invalid credentials or banned account
- **ParseError**: HTML structure changed or site update
- **NoProfileError**: Not logged in
- **Download Unavailable**: Book requires Tor or premium account
- **Rate Limited**: Too many requests

---

## 🚀 Complete Download Workflow

1. **Authenticate** → Get session cookies
2. **Search** → Find book URLs
3. **Get Details** → Extract download link
4. **Download** → Save file using cookies
5. **Validate** → Check file integrity

```bash
# Complete example
BOOK="python programming"

# 1. Login
curl -X POST https://z-library.sk/rpc.php \
  -d "email=$EMAIL&password=$PASS&action=login&gg_json_mode=1" \
  -c cookies.txt

# 2. Search
BOOK_URL=$(curl -s "https://z-library.sk/s/$BOOK" -b cookies.txt | \
  grep -o 'href="/book/[^"]*"' | head -1 | sed 's/href="//;s/"//')

# 3. Get download link
DL_URL=$(curl -s "https://z-library.sk$BOOK_URL" -b cookies.txt | \
  grep -o 'href="/dl/[^"]*"' | head -1 | sed 's/href="//;s/"//')

# 4. Download
curl -L "https://z-library.sk$DL_URL" -b cookies.txt -o book.epub
```

---

## 📚 Additional Resources

- **Source Code**: `/src/zlibrary/` - Python implementation
- **Examples**: `/examples/` - Usage examples
- **Tests**: `/tests/` - Test implementations
- **Scripts**: `/scripts/` - Shell script interfaces