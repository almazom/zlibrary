#!/bin/bash
# Search Examples for Z-Library API using curl
#
# These examples demonstrate various search operations using HTTP requests.
# Requires active session (run basic_auth.sh first).

# Configuration
BASE_URL="https://z-library.sk"
COOKIE_JAR="zlibrary_cookies.txt"
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

echo "=== Z-Library Search Examples ==="
echo ""

# Check if we have session cookies
if [ ! -f "$COOKIE_JAR" ]; then
    echo "❌ Cookie file not found. Run basic_auth.sh first to authenticate."
    exit 1
fi

# Example 1: Basic search
echo "1. Basic search for 'python programming'"
echo "========================================"

SEARCH_QUERY="python programming"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY" \
  > search_basic.html

if [ $? -eq 0 ]; then
    echo "✓ Basic search completed"
    echo "Results saved to search_basic.html"
    
    # Extract some basic info if possible
    if command -v grep &> /dev/null; then
        book_count=$(grep -o 'class="bookRow"' search_basic.html | wc -l)
        echo "Found approximately $book_count books on this page"
    fi
else
    echo "❌ Basic search failed"
fi

echo ""

# Example 2: Search with year filter
echo "2. Search with year filter (2020-2024)"
echo "======================================"

SEARCH_QUERY="machine learning"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY?yearFrom=2020&yearTo=2024" \
  > search_year_filter.html

if [ $? -eq 0 ]; then
    echo "✓ Year-filtered search completed"
    echo "Results saved to search_year_filter.html"
else
    echo "❌ Year-filtered search failed"
fi

echo ""

# Example 3: Search with language filter
echo "3. Search with language filter (English)"
echo "========================================"

SEARCH_QUERY="data science"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY?languages%5B%5D=english" \
  > search_language_filter.html

if [ $? -eq 0 ]; then
    echo "✓ Language-filtered search completed"
    echo "Results saved to search_language_filter.html"
else
    echo "❌ Language-filtered search failed"
fi

echo ""

# Example 4: Search with extension filter (PDF only)
echo "4. Search with extension filter (PDF only)"
echo "=========================================="

SEARCH_QUERY="artificial intelligence"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY?extensions%5B%5D=pdf" \
  > search_pdf_filter.html

if [ $? -eq 0 ]; then
    echo "✓ PDF-filtered search completed"
    echo "Results saved to search_pdf_filter.html"
else
    echo "❌ PDF-filtered search failed"
fi

echo ""

# Example 5: Complex search with multiple filters
echo "5. Complex search with multiple filters"
echo "======================================"

SEARCH_QUERY="blockchain"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

# URL with multiple filters: English, PDF, 2020-2024
COMPLEX_URL="$BASE_URL/s/$ENCODED_QUERY?yearFrom=2020&yearTo=2024&languages%5B%5D=english&extensions%5B%5D=pdf"

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$COMPLEX_URL" \
  > search_complex.html

if [ $? -eq 0 ]; then
    echo "✓ Complex search completed"
    echo "Results saved to search_complex.html"
    echo "Filters applied: English language, PDF format, years 2020-2024"
else
    echo "❌ Complex search failed"
fi

echo ""

# Example 6: Exact phrase search
echo "6. Exact phrase search"
echo "====================="

SEARCH_QUERY="neural networks"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY?e=1" \
  > search_exact.html

if [ $? -eq 0 ]; then
    echo "✓ Exact phrase search completed"
    echo "Results saved to search_exact.html"
else
    echo "❌ Exact phrase search failed"
fi

echo ""

# Example 7: Paginated search (page 2)
echo "7. Paginated search (page 2)"
echo "==========================="

SEARCH_QUERY="programming"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY?page=2" \
  > search_page2.html

if [ $? -eq 0 ]; then
    echo "✓ Paginated search (page 2) completed"
    echo "Results saved to search_page2.html"
else
    echo "❌ Paginated search failed"
fi

echo ""

# Example 8: Search with custom result count
echo "8. Search with custom result count (25 per page)"
echo "==============================================="

SEARCH_QUERY="database"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY?count=25" \
  > search_custom_count.html

if [ $? -eq 0 ]; then
    echo "✓ Custom count search completed"
    echo "Results saved to search_custom_count.html"
else
    echo "❌ Custom count search failed"
fi

echo ""

# Example 9: Full-text search
echo "9. Full-text search within book contents"
echo "======================================="

SEARCH_QUERY="deep learning algorithms"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

# Full-text search URL (may vary based on Z-Library version)
curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/s/$ENCODED_QUERY?fulltext=1" \
  > search_fulltext.html

if [ $? -eq 0 ]; then
    echo "✓ Full-text search completed"
    echo "Results saved to search_fulltext.html"
else
    echo "❌ Full-text search failed"
fi

echo ""

# Example 10: Extract book IDs and URLs from search results
echo "10. Extract book information from search results"
echo "==============================================="

if [ -f "search_basic.html" ]; then
    echo "Extracting book information from basic search results..."
    
    # Extract book URLs (this is a simple approach - real parsing would be more complex)
    if command -v grep &> /dev/null; then
        echo "Book URLs found:"
        grep -o 'href="/book/[^"]*"' search_basic.html | head -5 | sed 's/href="//;s/"$//'
        
        echo ""
        echo "Book IDs found:"
        grep -o '/book/[0-9]*/[a-f0-9]*' search_basic.html | head -5 | sed 's|/book/||'
    fi
    
    # Save extracted URLs for use in other scripts
    grep -o 'href="/book/[^"]*"' search_basic.html | sed 's/href="//;s/"$//' > book_urls.txt
    echo "Book URLs saved to book_urls.txt"
else
    echo "⚠️  No basic search results found. Run basic search first."
fi

echo ""

# Example 11: Search different file formats
echo "11. Search different file formats"
echo "================================"

SEARCH_QUERY="javascript"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

formats=("pdf" "epub" "mobi" "txt")

for format in "${formats[@]}"; do
    echo "Searching for $format files..."
    
    curl -X GET \
      -H "User-Agent: $USER_AGENT" \
      -b "$COOKIE_JAR" \
      "$BASE_URL/s/$ENCODED_QUERY?extensions%5B%5D=$format" \
      > "search_${format}.html"
    
    if [ $? -eq 0 ]; then
        if command -v grep &> /dev/null; then
            count=$(grep -o 'class="bookRow"' "search_${format}.html" | wc -l)
            echo "  ✓ Found ~$count books in $format format"
        else
            echo "  ✓ Search completed for $format"
        fi
    else
        echo "  ❌ Search failed for $format"
    fi
done

echo ""

# Example 12: International search (multiple languages)
echo "12. International search (multiple languages)"
echo "============================================"

SEARCH_QUERY="mathematics"
ENCODED_QUERY=$(echo "$SEARCH_QUERY" | sed 's/ /%20/g')

languages=("english" "spanish" "french" "german" "russian")

for lang in "${languages[@]}"; do
    echo "Searching in $lang..."
    
    curl -X GET \
      -H "User-Agent: $USER_AGENT" \
      -b "$COOKIE_JAR" \
      "$BASE_URL/s/$ENCODED_QUERY?languages%5B%5D=$lang" \
      > "search_${lang}.html"
    
    if [ $? -eq 0 ]; then
        echo "  ✓ Search completed in $lang"
    else
        echo "  ❌ Search failed in $lang"
    fi
done

echo ""
echo "=== Search Examples Complete ==="
echo ""
echo "Files created:"
echo "- search_basic.html (basic search results)"
echo "- search_year_filter.html (year-filtered results)"
echo "- search_language_filter.html (language-filtered results)"
echo "- search_pdf_filter.html (PDF-only results)"
echo "- search_complex.html (multiple filters)"
echo "- search_exact.html (exact phrase search)"
echo "- search_page2.html (second page of results)"
echo "- search_custom_count.html (custom result count)"
echo "- search_fulltext.html (full-text search)"
echo "- search_[format].html (format-specific searches)"
echo "- search_[language].html (language-specific searches)"
echo "- book_urls.txt (extracted book URLs)"
echo ""
echo "Next steps:"
echo "1. Parse HTML files to extract structured data"
echo "2. Use book URLs with book_details.sh for detailed information"
echo "3. Use book IDs with download_examples.sh for downloads"
echo ""
echo "Common URL parameters:"
echo "- yearFrom/yearTo: Filter by publication year"
echo "- languages[]: Filter by language (english, spanish, etc.)"
echo "- extensions[]: Filter by format (pdf, epub, mobi, txt, etc.)"
echo "- e=1: Exact phrase search"
echo "- page=N: Get specific page of results"
echo "- count=N: Number of results per page"
echo "- fulltext=1: Search within book contents"