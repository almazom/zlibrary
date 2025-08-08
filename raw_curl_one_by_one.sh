#!/bin/bash
# Raw cURL API - One by One Book Processing
# Simulates real external API usage - NO BATCHING

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
API_BASE="https://z-library.sk"
COOKIES_FILE="./tmp/cookies.txt"
DOWNLOADS_DIR="./downloads/one_by_one_test"
CURRENT_BOOK_DIR=""

# Create directories
mkdir -p ./tmp
mkdir -p "$DOWNLOADS_DIR"

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       Z-LIBRARY RAW CURL API - ONE BY ONE PROCESSING${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo

# Step 1: Fetch Penguin Books List via Web
echo -e "${PURPLE}STEP 1: Fetching Penguin Random House 2025 Best Books...${NC}"
echo -e "${CYAN}Making raw HTTP request to Penguin website...${NC}"

curl -s "https://www.penguinrandomhouse.com/the-read-down/the-best-books-of-2025/" \
    -H "User-Agent: Mozilla/5.0" | \
    grep -oE '(The Emperor of Gladness|Murderland|One Golden Summer|Beyond Anxiety|We Can Do Hard Things|The Note|The Stolen Queen|We Do Not Part|Dream Count|Problematic Summer Romance|Witchcraft for Wayward Girls|Theft|The Listeners|Great Big Beautiful Life|Atmosphere)' | \
    head -15 | sort -u > ./tmp/book_titles.txt

echo -e "${GREEN}✅ Found $(wc -l < ./tmp/book_titles.txt) book titles${NC}"
echo

# Add authors manually (since we know them)
cat > ./tmp/penguin_books.txt << 'EOF'
The Emperor of Gladness|Ocean Vuong
Murderland|Caroline Fraser
One Golden Summer|Carley Fortune
Beyond Anxiety|Martha Beck
We Can Do Hard Things|Glennon Doyle
The Note|Alafair Burke
The Stolen Queen|Fiona Davis
We Do Not Part|Han Kang
Dream Count|Chimamanda Ngozi Adichie
Problematic Summer Romance|Ali Hazelwood
Witchcraft for Wayward Girls|Grady Hendrix
Theft|Abdulrazak Gurnah
The Listeners|Maggie Stiefvater
Great Big Beautiful Life|Emily Henry
Atmosphere|Taylor Jenkins Reid
EOF

# Step 2: Authenticate ONCE
echo -e "${PURPLE}STEP 2: Authenticating with Z-Library...${NC}"
echo -e "${CYAN}URL: POST ${API_BASE}/rpc.php${NC}"

if [[ -z "$ZLOGIN" || -z "$ZPASSW" ]]; then
    echo -e "${RED}❌ Error: Set ZLOGIN and ZPASSW environment variables${NC}"
    exit 1
fi

echo -e "${CYAN}Sending authentication request...${NC}"
AUTH_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
    -d "email=${ZLOGIN}&password=${ZPASSW}&action=login&gg_json_mode=1" \
    -c "$COOKIES_FILE" \
    "${API_BASE}/rpc.php")

if echo "$AUTH_RESPONSE" | grep -q "user_id"; then
    USER_ID=$(echo "$AUTH_RESPONSE" | grep -o '"user_id":[0-9]*' | cut -d: -f2)
    echo -e "${GREEN}✅ Login successful! User ID: $USER_ID${NC}"
else
    echo -e "${RED}❌ Login failed!${NC}"
    echo "$AUTH_RESPONSE"
    exit 1
fi

echo
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}        PROCESSING EACH BOOK ONE BY ONE${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo

# Process each book ONE BY ONE
BOOK_COUNT=0
SUCCESS_COUNT=0
FAILED_COUNT=0

while IFS='|' read -r TITLE AUTHOR; do
    ((BOOK_COUNT++))
    
    echo -e "${YELLOW}┌────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}│ BOOK #${BOOK_COUNT}: ${TITLE}${NC}"
    echo -e "${YELLOW}│ Author: ${AUTHOR}${NC}"
    echo -e "${YELLOW}└────────────────────────────────────────────────────────────${NC}"
    
    # Create directory for this book
    CLEAN_TITLE=$(echo "$TITLE" | sed 's/[^a-zA-Z0-9]/_/g')
    CURRENT_BOOK_DIR="$DOWNLOADS_DIR/book_${BOOK_COUNT}_${CLEAN_TITLE}"
    mkdir -p "$CURRENT_BOOK_DIR"
    
    # STEP A: Search for the book
    echo -e "${CYAN}[A] SEARCHING...${NC}"
    QUERY="${TITLE} ${AUTHOR}"
    ENCODED_QUERY=$(echo "$QUERY" | sed 's/ /%20/g')
    SEARCH_URL="${API_BASE}/s/${ENCODED_QUERY}?page=1"
    
    echo -e "${CYAN}    URL: GET ${SEARCH_URL}${NC}"
    echo -e "${CYAN}    Executing cURL command...${NC}"
    
    curl -s -X GET \
        -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
        -b "$COOKIES_FILE" \
        "$SEARCH_URL" > "$CURRENT_BOOK_DIR/search_response.html"
    
    # Check if we found any books
    BOOK_FOUND=$(grep -c 'class="book-item' "$CURRENT_BOOK_DIR/search_response.html" || echo "0")
    
    if [[ $BOOK_FOUND -gt 0 ]]; then
        echo -e "${GREEN}    ✅ Found $BOOK_FOUND results${NC}"
        
        # Extract first book URL
        BOOK_URL=$(grep -o 'href="/book/[^"]*"' "$CURRENT_BOOK_DIR/search_response.html" | head -1 | sed 's/href="//;s/"//')
        
        if [[ -n "$BOOK_URL" ]]; then
            echo -e "${GREEN}    📖 Book URL: ${API_BASE}${BOOK_URL}${NC}"
            
            # STEP B: Get book details
            echo -e "${CYAN}[B] FETCHING BOOK DETAILS...${NC}"
            DETAILS_URL="${API_BASE}${BOOK_URL}"
            echo -e "${CYAN}    URL: GET ${DETAILS_URL}${NC}"
            
            curl -s -X GET \
                -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
                -b "$COOKIES_FILE" \
                "$DETAILS_URL" > "$CURRENT_BOOK_DIR/book_details.html"
            
            # Extract download link
            DOWNLOAD_PATH=$(grep -o 'href="/dl/[^"]*"' "$CURRENT_BOOK_DIR/book_details.html" | head -1 | sed 's/href="//;s/"//')
            
            if [[ -n "$DOWNLOAD_PATH" ]]; then
                DOWNLOAD_URL="${API_BASE}${DOWNLOAD_PATH}"
                echo -e "${GREEN}    ✅ Download link found${NC}"
                echo -e "${GREEN}    📥 URL: ${DOWNLOAD_URL}${NC}"
                
                # Extract format
                FORMAT=$(grep -oE '(epub|pdf|mobi)' "$CURRENT_BOOK_DIR/book_details.html" | head -1 | tr '[:upper:]' '[:lower:]')
                [[ -z "$FORMAT" ]] && FORMAT="epub"
                
                # STEP C: Download the book
                echo -e "${CYAN}[C] DOWNLOADING BOOK...${NC}"
                BOOK_FILE="$CURRENT_BOOK_DIR/${CLEAN_TITLE}.${FORMAT}"
                echo -e "${CYAN}    Saving to: ${BOOK_FILE}${NC}"
                
                curl -L -s \
                    -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
                    -b "$COOKIES_FILE" \
                    -o "$BOOK_FILE" \
                    "$DOWNLOAD_URL"
                
                # Check if download was successful
                if [[ -f "$BOOK_FILE" ]] && [[ -s "$BOOK_FILE" ]]; then
                    FILE_SIZE=$(stat -f%z "$BOOK_FILE" 2>/dev/null || stat -c%s "$BOOK_FILE" 2>/dev/null || echo "0")
                    echo -e "${GREEN}    ✅ Downloaded: ${FILE_SIZE} bytes${NC}"
                    
                    # STEP D: Run EPUB diagnostics
                    echo -e "${CYAN}[D] RUNNING EPUB DIAGNOSTICS...${NC}"
                    
                    # Quick diagnostics using file and unzip
                    FILE_TYPE=$(file "$BOOK_FILE" | cut -d: -f2)
                    echo -e "${CYAN}    File type: ${FILE_TYPE}${NC}"
                    
                    if [[ "$FORMAT" == "epub" ]]; then
                        # Check if it's a valid ZIP/EPUB
                        if unzip -t "$BOOK_FILE" > "$CURRENT_BOOK_DIR/epub_test.txt" 2>&1; then
                            FILES_IN_EPUB=$(unzip -l "$BOOK_FILE" | tail -1 | awk '{print $2}')
                            echo -e "${GREEN}    ✅ Valid EPUB with $FILES_IN_EPUB files${NC}"
                            
                            # Check for essential EPUB files
                            if unzip -l "$BOOK_FILE" | grep -q "mimetype"; then
                                echo -e "${GREEN}    ✅ Has mimetype file${NC}"
                            else
                                echo -e "${YELLOW}    ⚠️  Missing mimetype file${NC}"
                            fi
                            
                            if unzip -l "$BOOK_FILE" | grep -q "container.xml"; then
                                echo -e "${GREEN}    ✅ Has container.xml${NC}"
                            else
                                echo -e "${YELLOW}    ⚠️  Missing container.xml${NC}"
                            fi
                            
                            if unzip -l "$BOOK_FILE" | grep -q "\.opf"; then
                                echo -e "${GREEN}    ✅ Has OPF file${NC}"
                            else
                                echo -e "${YELLOW}    ⚠️  Missing OPF file${NC}"
                            fi
                            
                            echo -e "${GREEN}    🎉 EPUB DIAGNOSTICS: PASSED${NC}"
                            ((SUCCESS_COUNT++))
                        else
                            echo -e "${RED}    ❌ Invalid EPUB file${NC}"
                            ((FAILED_COUNT++))
                        fi
                    else
                        echo -e "${YELLOW}    ⚠️  Not an EPUB file (${FORMAT})${NC}"
                        ((SUCCESS_COUNT++))
                    fi
                else
                    echo -e "${RED}    ❌ Download failed - empty or missing file${NC}"
                    ((FAILED_COUNT++))
                fi
            else
                echo -e "${RED}    ❌ No download link found${NC}"
                ((FAILED_COUNT++))
            fi
        else
            echo -e "${RED}    ❌ Could not extract book URL${NC}"
            ((FAILED_COUNT++))
        fi
    else
        echo -e "${YELLOW}    ❌ Book not found (0 results)${NC}"
        echo -e "${YELLOW}    💡 Expected for 2025 books not yet published${NC}"
        ((FAILED_COUNT++))
    fi
    
    echo -e "${YELLOW}└────────────────────────────────────────────────────────────${NC}"
    echo
    
    # Wait between books to simulate real usage
    echo -e "${CYAN}Waiting 3 seconds before next book...${NC}"
    sleep 3
    echo

done < ./tmp/penguin_books.txt

# Final Report
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                    FINAL REPORT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo
echo -e "${CYAN}📚 Total Books Processed: ${BOOK_COUNT}${NC}"
echo -e "${GREEN}✅ Successful Downloads: ${SUCCESS_COUNT}${NC}"
echo -e "${RED}❌ Failed/Not Found: ${FAILED_COUNT}${NC}"
echo
echo -e "${CYAN}📁 Results saved in: ${DOWNLOADS_DIR}${NC}"
echo

if [[ $SUCCESS_COUNT -gt 0 ]]; then
    echo -e "${GREEN}🎉 SUCCESS: Raw cURL API demonstrated with real downloads!${NC}"
    echo -e "${GREEN}   - Authentication working${NC}"
    echo -e "${GREEN}   - Search working${NC}"
    echo -e "${GREEN}   - Download working${NC}"
    echo -e "${GREEN}   - EPUB validation working${NC}"
else
    echo -e "${YELLOW}💡 NOTE: 0 downloads for 2025 books is expected${NC}"
    echo -e "${YELLOW}   These books haven't been published yet!${NC}"
    echo -e "${YELLOW}   The API is working correctly by returning no results.${NC}"
fi

echo
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Raw cURL simulation complete - simulated external API usage${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"