# UC3: URL-to-EPUB Pipeline Test Cases

## Feature: Extract Book Info from URLs and Download EPUB
As an external system
I want to provide book URLs from various sources
So that the correct EPUB is automatically found and downloaded

## Supported URL Sources:
- podpisnie.ru (Russian book recommendations)
- goodreads.com (book reviews)
- amazon.com (book listings)
- Generic book blog posts

## Scenario 1: Podpisnie.ru URL Processing
**Given** I have a podpisnie.ru book URL
**When** I run `./scripts/book_search.sh "https://www.podpisnie.ru/books/maniac/"`
**Then** System should:
  - Extract book info from URL slug
  - Search Z-Library for the book
  - Download EPUB if found
  - Return JSON with `input_format: "url"`

### Test Cases:
```bash
# Test 1.1: Direct podpisnie URL
./scripts/book_search.sh "https://www.podpisnie.ru/books/maniac/"
# Expected: Extracts "maniac", finds and downloads book

# Test 1.2: Complex podpisnie URL  
./scripts/book_search.sh "https://www.podpisnie.ru/books/misticheskiy-mir-novalisa/"
# Expected: Extracts proper query, finds book

# Test 1.3: URL with Russian title
./scripts/book_search.sh "https://www.podpisnie.ru/books/eto-nesluchayno-yaponskaya/"
# Expected: Handles transliteration correctly
```

## Scenario 2: Goodreads URL Processing
**Given** I have a Goodreads book URL
**When** I run `./scripts/book_search.sh "https://www.goodreads.com/book/show/3735293-clean-code"`
**Then** System should:
  - Extract book ID and title from URL
  - Search for "Clean Code"
  - Download EPUB with high confidence

### Test Cases:
```bash
# Test 2.1: Standard Goodreads URL
./scripts/book_search.sh "https://www.goodreads.com/book/show/3735293-clean-code"
# Expected: Extracts "clean code", downloads book

# Test 2.2: Goodreads with full title
./scripts/book_search.sh "https://www.goodreads.com/book/show/11084145-steve-jobs"  
# Expected: Extracts "steve jobs", finds biography
```

## Scenario 3: Amazon URL Processing
**Given** I have an Amazon book URL
**When** I run `./scripts/book_search.sh "https://www.amazon.com/dp/B07FZRYBW3/"`
**Then** System should:
  - Extract ASIN/ISBN
  - Look up book metadata
  - Search and download EPUB

### Test Cases:
```bash
# Test 3.1: Amazon product page
./scripts/book_search.sh "https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882"
# Expected: Extracts title from URL, downloads book

# Test 3.2: Amazon short link
./scripts/book_search.sh "https://amzn.to/3xyzabc"
# Expected: Follows redirect, extracts book info
```

## Scenario 4: Generic Blog URL
**Given** I have a blog post about a book
**When** I provide the URL
**Then** System should:
  - Fetch page content
  - Extract book title and author
  - Search and download

## Implementation Requirements:

### URL Pattern Detection
```python
def detect_url_source(url):
    if 'podpisnie.ru' in url:
        return 'podpisnie'
    elif 'goodreads.com' in url:
        return 'goodreads'
    elif 'amazon.' in url:
        return 'amazon'
    else:
        return 'generic'
```

### Extraction Logic
```python
def extract_book_info(url, source):
    if source == 'podpisnie':
        # Extract from /books/[slug]/
        slug = re.search(r'/books/([^/]+)', url)
        return slug.group(1).replace('-', ' ')
    elif source == 'goodreads':
        # Extract from /book/show/ID-title
        title = re.search(r'/book/show/\d+-(.+)', url)
        return title.group(1).replace('-', ' ')
    elif source == 'amazon':
        # Extract from product title
        # Need to fetch page or use ASIN lookup
        pass
```

## Edge Cases:
1. **Dead links** - Return error JSON
2. **Paywall sites** - Skip and return not accessible
3. **Foreign language URLs** - Handle UTF-8 properly
4. **Multiple books on page** - Take first or most prominent
5. **Redirect chains** - Follow up to 3 redirects
6. **URL shorteners** - Expand before processing

## Success Metrics:
- ✅ URL correctly identified as `input_format: "url"`
- ✅ Book query extracted accurately
- ✅ Correct book found >80% of the time
- ✅ EPUB downloaded when available
- ✅ Graceful handling of unsupported URLs