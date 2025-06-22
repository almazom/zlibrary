#!/bin/bash
# Book Details Examples for Z-Library API using curl
#
# These examples demonstrate how to get detailed book information
# Requires active session (run basic_auth.sh first).

# Configuration
BASE_URL="https://z-library.sk"
COOKIE_JAR="zlibrary_cookies.txt"
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

echo "=== Z-Library Book Details Examples ==="
echo ""

# Check if we have session cookies
if [ ! -f "$COOKIE_JAR" ]; then
    echo "❌ Cookie file not found. Run basic_auth.sh first to authenticate."
    exit 1
fi

# Example 1: Get details for a specific book ID
echo "1. Get book details by ID"
echo "========================"

# Example book ID (you'll need to replace with actual IDs from search results)
BOOK_ID="5393918/a28f0c"  # This is from the test.py file

echo "Getting details for book ID: $BOOK_ID"

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/book/$BOOK_ID" \
  > book_details_${BOOK_ID//\//_}.html

if [ $? -eq 0 ]; then
    echo "✓ Book details retrieved"
    echo "Details saved to book_details_${BOOK_ID//\//_}.html"
    
    # Try to extract basic information
    if command -v grep &> /dev/null; then
        echo ""
        echo "Basic information extracted:"
        echo "----------------------------"
        
        # Extract title (this is a basic approach - real parsing would be more robust)
        title=$(grep -o '<h1[^>]*>[^<]*</h1>' "book_details_${BOOK_ID//\//_}.html" | sed 's/<[^>]*>//g' | head -1)
        if [ -n "$title" ]; then
            echo "Title: $title"
        fi
        
        # Look for download button/link
        if grep -q "download" "book_details_${BOOK_ID//\//_}.html"; then
            echo "✓ Download link appears to be available"
        else
            echo "⚠️  Download link not found (may require higher access level)"
        fi
        
        # Look for book metadata
        if grep -q "Publisher" "book_details_${BOOK_ID//\//_}.html"; then
            echo "✓ Publisher information found"
        fi
        
        if grep -q "Year" "book_details_${BOOK_ID//\//_}.html"; then
            echo "✓ Publication year found"
        fi
        
        if grep -q "Language" "book_details_${BOOK_ID//\//_}.html"; then
            echo "✓ Language information found"
        fi
    fi
else
    echo "❌ Failed to get book details"
fi

echo ""

# Example 2: Get details for multiple books from search results
echo "2. Get details for multiple books from search results"
echo "====================================================="

if [ -f "book_urls.txt" ]; then
    echo "Using book URLs from previous search..."
    
    count=0
    while IFS= read -r book_url && [ $count -lt 3 ]; do
        if [ -n "$book_url" ]; then
            echo "Getting details for: $book_url"
            
            # Extract book ID from URL for filename
            book_id=$(echo "$book_url" | sed 's|.*/book/||')
            
            curl -X GET \
              -H "User-Agent: $USER_AGENT" \
              -b "$COOKIE_JAR" \
              "$BASE_URL$book_url" \
              > "book_details_${book_id//\//_}.html"
            
            if [ $? -eq 0 ]; then
                echo "  ✓ Details saved to book_details_${book_id//\//_}.html"
            else
                echo "  ❌ Failed to get details"
            fi
            
            # Small delay to be respectful
            sleep 1
            count=$((count + 1))
        fi
    done < book_urls.txt
    
    echo "Retrieved details for $count books"
else
    echo "⚠️  book_urls.txt not found. Run search_examples.sh first."
fi

echo ""

# Example 3: Extract download URLs (if available)
echo "3. Extract download URLs from book details"
echo "=========================================="

for html_file in book_details_*.html; do
    if [ -f "$html_file" ]; then
        echo "Checking $html_file for download links..."
        
        # Look for download URLs (this is a simplified approach)
        if command -v grep &> /dev/null; then
            # Common patterns for download links
            download_links=$(grep -o 'href="[^"]*dl[^"]*"' "$html_file" | sed 's/href="//;s/"$//')
            
            if [ -n "$download_links" ]; then
                echo "  ✓ Found potential download links:"
                echo "$download_links" | while read -r link; do
                    echo "    $BASE_URL$link"
                done
            else
                # Try alternative patterns
                alternative_links=$(grep -o 'href="/[^"]*download[^"]*"' "$html_file" | sed 's/href="//;s/"$//')
                if [ -n "$alternative_links" ]; then
                    echo "  ✓ Found alternative download patterns:"
                    echo "$alternative_links" | while read -r link; do
                        echo "    $BASE_URL$link"
                    done
                else
                    echo "  ⚠️  No download links found"
                fi
            fi
        fi
    fi
done

echo ""

# Example 4: Extract book metadata as JSON-like format
echo "4. Extract book metadata"
echo "======================="

extract_metadata() {
    local html_file="$1"
    local book_id="$2"
    
    echo "Extracting metadata from $html_file..."
    
    # Create a simple metadata file
    metadata_file="metadata_${book_id//\//_}.txt"
    
    echo "Book ID: $book_id" > "$metadata_file"
    echo "Extraction Date: $(date)" >> "$metadata_file"
    echo "Source File: $html_file" >> "$metadata_file"
    echo "---" >> "$metadata_file"
    
    if command -v grep &> /dev/null; then
        # Extract title
        title=$(grep -o '<h1[^>]*>[^<]*</h1>' "$html_file" | sed 's/<[^>]*>//g' | head -1)
        if [ -n "$title" ]; then
            echo "Title: $title" >> "$metadata_file"
        fi
        
        # Extract author information
        authors=$(grep -o 'author[^>]*>[^<]*<' "$html_file" | sed 's/author[^>]*>//;s/<$//' | head -3)
        if [ -n "$authors" ]; then
            echo "Authors:" >> "$metadata_file"
            echo "$authors" | while read -r author; do
                echo "  - $author" >> "$metadata_file"
            done
        fi
        
        # Extract year
        year=$(grep -o '[12][0-9][0-9][0-9]' "$html_file" | head -1)
        if [ -n "$year" ]; then
            echo "Year: $year" >> "$metadata_file"
        fi
        
        # Extract file size
        size=$(grep -o '[0-9.]*\s*MB\|[0-9.]*\s*KB\|[0-9.]*\s*GB' "$html_file" | head -1)
        if [ -n "$size" ]; then
            echo "File Size: $size" >> "$metadata_file"
        fi
        
        # Extract language
        language=$(grep -i -o 'language[^>]*>[^<]*<\|lang[^>]*>[^<]*<' "$html_file" | sed 's/[^>]*>//;s/<$//' | head -1)
        if [ -n "$language" ]; then
            echo "Language: $language" >> "$metadata_file"
        fi
        
        # Extract format/extension
        format=$(grep -o -i 'pdf\|epub\|mobi\|txt\|doc\|rtf' "$html_file" | head -1)
        if [ -n "$format" ]; then
            echo "Format: $format" >> "$metadata_file"
        fi
        
        echo "  ✓ Metadata saved to $metadata_file"
    fi
}

# Extract metadata for all downloaded book details
for html_file in book_details_*.html; do
    if [ -f "$html_file" ]; then
        # Extract book ID from filename
        book_id=$(echo "$html_file" | sed 's/book_details_//;s/\.html$//;s/_/\//')
        extract_metadata "$html_file" "$book_id"
    fi
done

echo ""

# Example 5: Get book cover images
echo "5. Download book cover images"
echo "============================"

for html_file in book_details_*.html; do
    if [ -f "$html_file" ]; then
        echo "Looking for cover image in $html_file..."
        
        # Extract cover image URLs
        if command -v grep &> /dev/null; then
            cover_urls=$(grep -o 'src="[^"]*cover[^"]*\|src="[^"]*\.jpg[^"]*\|src="[^"]*\.png[^"]*' "$html_file" | sed 's/src="//;s/".*$//' | head -1)
            
            if [ -n "$cover_urls" ]; then
                echo "  Found cover URL: $cover_urls"
                
                # Extract book ID for filename
                book_id=$(echo "$html_file" | sed 's/book_details_//;s/\.html$//')
                
                # Download cover image
                if [[ "$cover_urls" == http* ]]; then
                    cover_url="$cover_urls"
                else
                    cover_url="$BASE_URL$cover_urls"
                fi
                
                # Determine file extension
                if [[ "$cover_url" == *.jpg* ]]; then
                    ext=".jpg"
                elif [[ "$cover_url" == *.png* ]]; then
                    ext=".png"
                else
                    ext=".jpg"  # default
                fi
                
                curl -X GET \
                  -H "User-Agent: $USER_AGENT" \
                  -b "$COOKIE_JAR" \
                  "$cover_url" \
                  > "cover_${book_id}${ext}"
                
                if [ $? -eq 0 ]; then
                    echo "  ✓ Cover downloaded as cover_${book_id}${ext}"
                else
                    echo "  ❌ Failed to download cover"
                fi
            else
                echo "  ⚠️  No cover image found"
            fi
        fi
    fi
done

echo ""

# Example 6: Check book availability and access level
echo "6. Check book availability and access level"
echo "=========================================="

for html_file in book_details_*.html; do
    if [ -f "$html_file" ]; then
        book_id=$(echo "$html_file" | sed 's/book_details_//;s/\.html$//;s/_/\//')
        
        echo "Checking availability for book $book_id..."
        
        if command -v grep &> /dev/null; then
            # Check for download button
            if grep -q -i "download" "$html_file"; then
                echo "  ✓ Download appears available"
            else
                echo "  ⚠️  Download not available"
            fi
            
            # Check for access restrictions
            if grep -q -i "limit\|restriction\|premium" "$html_file"; then
                echo "  ⚠️  May have access restrictions"
            fi
            
            # Check for file format availability
            formats=$(grep -o -i 'pdf\|epub\|mobi\|txt\|doc\|rtf\|fb2\|azw' "$html_file" | sort | uniq)
            if [ -n "$formats" ]; then
                echo "  Available formats: $(echo $formats | tr '\n' ' ')"
            fi
        fi
    fi
done

echo ""
echo "=== Book Details Examples Complete ==="
echo ""
echo "Files created:"
echo "- book_details_*.html (detailed book pages)"
echo "- metadata_*.txt (extracted metadata)"
echo "- cover_*.jpg/png (book cover images)"
echo ""
echo "Summary of extracted information:"
echo "- Book titles, authors, and publication details"
echo "- Download availability and formats"
echo "- Cover images where available"
echo "- File sizes and languages"
echo ""
echo "Next steps:"
echo "1. Use download URLs with download_examples.sh"
echo "2. Parse metadata files for structured data processing"
echo "3. Use book IDs for profile operations (favorites, etc.)"
echo ""
echo "Note: Actual download availability depends on:"
echo "- Your account access level"
echo "- Daily download limits"
echo "- Book licensing restrictions"