#!/bin/bash
# Profile Operations Examples for Z-Library API using curl
#
# These examples demonstrate user profile operations including
# download limits, history, and bookmarks management.
# Requires active session (run basic_auth.sh first).

# Configuration
BASE_URL="https://z-library.sk"
COOKIE_JAR="zlibrary_cookies.txt"
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

echo "=== Z-Library Profile Operations Examples ==="
echo ""

# Check if we have session cookies
if [ ! -f "$COOKIE_JAR" ]; then
    echo "❌ Cookie file not found. Run basic_auth.sh first to authenticate."
    exit 1
fi

# Example 1: Get download limits and usage
echo "1. Get download limits and usage information"
echo "==========================================="

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/users/downloads" \
  > profile_downloads.html

if [ $? -eq 0 ]; then
    echo "✓ Download information retrieved"
    echo "Information saved to profile_downloads.html"
    
    # Try to extract download statistics
    if command -v grep &> /dev/null; then
        echo ""
        echo "Download Statistics:"
        echo "-------------------"
        
        # Look for download count information
        daily_info=$(grep -o '[0-9]* downloads' profile_downloads.html | head -3)
        if [ -n "$daily_info" ]; then
            echo "Download info found:"
            echo "$daily_info"
        fi
        
        # Look for reset time
        reset_info=$(grep -o '[0-9]* hours\|[0-9]* minutes' profile_downloads.html | head -1)
        if [ -n "$reset_info" ]; then
            echo "Reset time: $reset_info"
        fi
        
        # Check for download limit warnings
        if grep -q -i "limit\|restriction" profile_downloads.html; then
            echo "⚠️  Download limits or restrictions detected"
        fi
    fi
else
    echo "❌ Failed to get download information"
fi

echo ""

# Example 2: Get download history
echo "2. Get download history"
echo "======================"

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/users/downloads/history" \
  > download_history.html

if [ $? -eq 0 ]; then
    echo "✓ Download history retrieved"
    echo "History saved to download_history.html"
    
    # Try to extract recent downloads
    if command -v grep &> /dev/null; then
        echo ""
        echo "Recent Downloads:"
        echo "----------------"
        
        # Look for book titles in download history
        book_titles=$(grep -o 'title[^>]*>[^<]*<\|href="/book/[^"]*"[^>]*>[^<]*<' download_history.html | sed 's/[^>]*>//;s/<.*$//' | head -5)
        if [ -n "$book_titles" ]; then
            echo "$book_titles" | while read -r title; do
                if [ -n "$title" ]; then
                    echo "  • $title"
                fi
            done
        else
            echo "  No recent downloads found or different HTML structure"
        fi
    fi
else
    echo "❌ Failed to get download history"
fi

echo ""

# Example 3: Get user profile information
echo "3. Get user profile information"
echo "=============================="

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/profile" \
  > user_profile.html

if [ $? -eq 0 ]; then
    echo "✓ User profile retrieved"
    echo "Profile saved to user_profile.html"
    
    # Try to extract profile information
    if command -v grep &> /dev/null; then
        echo ""
        echo "Profile Information:"
        echo "-------------------"
        
        # Look for username/email
        email=$(grep -o '[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]*\.[a-zA-Z][a-zA-Z]*' user_profile.html | head -1)
        if [ -n "$email" ]; then
            echo "Email: $email"
        fi
        
        # Look for account type
        if grep -q -i "premium\|subscription" user_profile.html; then
            echo "Account type: Premium/Subscription detected"
        else
            echo "Account type: Standard/Free"
        fi
        
        # Look for registration date
        reg_date=$(grep -o '[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]\|[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]' user_profile.html | head -1)
        if [ -n "$reg_date" ]; then
            echo "Registration date: $reg_date"
        fi
    fi
else
    echo "❌ Failed to get user profile"
fi

echo ""

# Example 4: Search and manage booklists
echo "4. Search public booklists"
echo "========================="

# Search for programming-related booklists
BOOKLIST_QUERY="programming"
ENCODED_QUERY=$(echo "$BOOKLIST_QUERY" | sed 's/ /%20/g')

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/booklists/search?q=$ENCODED_QUERY" \
  > public_booklists.html

if [ $? -eq 0 ]; then
    echo "✓ Public booklists search completed"
    echo "Results saved to public_booklists.html"
    
    # Try to extract booklist information
    if command -v grep &> /dev/null; then
        echo ""
        echo "Public Booklists Found:"
        echo "----------------------"
        
        # Look for booklist names and URLs
        booklist_info=$(grep -o 'href="/booklist/[^"]*"[^>]*>[^<]*<' public_booklists.html | head -5)
        if [ -n "$booklist_info" ]; then
            echo "$booklist_info" | while read -r info; do
                url=$(echo "$info" | grep -o 'href="[^"]*"' | sed 's/href="//;s/"$//')
                name=$(echo "$info" | sed 's/[^>]*>//;s/<.*$//')
                if [ -n "$name" ] && [ -n "$url" ]; then
                    echo "  • $name"
                    echo "    URL: $BASE_URL$url"
                fi
            done
        else
            echo "  No booklists found or different HTML structure"
        fi
    fi
else
    echo "❌ Failed to search public booklists"
fi

echo ""

# Example 5: Get personal booklists
echo "5. Get personal booklists"
echo "========================"

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/profile/booklists" \
  > personal_booklists.html

if [ $? -eq 0 ]; then
    echo "✓ Personal booklists retrieved"
    echo "Lists saved to personal_booklists.html"
    
    # Try to extract personal booklist information
    if command -v grep &> /dev/null; then
        echo ""
        echo "Personal Booklists:"
        echo "------------------"
        
        booklist_count=$(grep -o 'booklist' personal_booklists.html | wc -l)
        echo "Found references to $booklist_count booklist items"
        
        # Look for specific booklist names
        personal_lists=$(grep -o 'My [^<]*\|Favorites[^<]*\|Reading List[^<]*' personal_booklists.html | head -5)
        if [ -n "$personal_lists" ]; then
            echo "$personal_lists" | while read -r list; do
                if [ -n "$list" ]; then
                    echo "  • $list"
                fi
            done
        fi
    fi
else
    echo "❌ Failed to get personal booklists"
fi

echo ""

# Example 6: Get account statistics
echo "6. Get account statistics"
echo "========================"

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/profile/stats" \
  > account_stats.html

if [ $? -eq 0 ]; then
    echo "✓ Account statistics retrieved"
    echo "Stats saved to account_stats.html"
    
    # Try to extract statistics
    if command -v grep &> /dev/null; then
        echo ""
        echo "Account Statistics:"
        echo "------------------"
        
        # Look for download counts
        total_downloads=$(grep -o '[0-9]* total downloads\|[0-9]* books downloaded' account_stats.html | head -1)
        if [ -n "$total_downloads" ]; then
            echo "Total downloads: $total_downloads"
        fi
        
        # Look for favorite counts
        favorites=$(grep -o '[0-9]* favorites\|[0-9]* saved books' account_stats.html | head -1)
        if [ -n "$favorites" ]; then
            echo "Favorites: $favorites"
        fi
        
        # Look for recent activity
        if grep -q -i "last login\|recent activity" account_stats.html; then
            echo "✓ Recent activity information available"
        fi
    fi
else
    echo "❌ Failed to get account statistics (may not be available)"
fi

echo ""

# Example 7: Check notification settings
echo "7. Check notification settings"
echo "============================="

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/profile/settings" \
  > profile_settings.html

if [ $? -eq 0 ]; then
    echo "✓ Profile settings retrieved"
    echo "Settings saved to profile_settings.html"
    
    # Check for various settings
    if command -v grep &> /dev/null; then
        echo ""
        echo "Settings Information:"
        echo "--------------------"
        
        if grep -q -i "notification" profile_settings.html; then
            echo "✓ Notification settings found"
        fi
        
        if grep -q -i "privacy" profile_settings.html; then
            echo "✓ Privacy settings found"
        fi
        
        if grep -q -i "language" profile_settings.html; then
            echo "✓ Language preferences found"
        fi
        
        if grep -q -i "theme\|dark mode" profile_settings.html; then
            echo "✓ Theme settings found"
        fi
    fi
else
    echo "❌ Failed to get profile settings"
fi

echo ""

# Example 8: Monitor account limits and generate report
echo "8. Generate account status report"
echo "================================"

echo "Generating comprehensive account report..."

REPORT_FILE="account_report_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "Z-Library Account Status Report"
    echo "Generated: $(date)"
    echo "==============================="
    echo ""
    
    echo "DOWNLOAD INFORMATION:"
    echo "--------------------"
    if [ -f "profile_downloads.html" ]; then
        # Extract download info
        daily_info=$(grep -o '[0-9]* downloads' profile_downloads.html)
        if [ -n "$daily_info" ]; then
            echo "$daily_info"
        else
            echo "Download information not parsed successfully"
        fi
        
        reset_info=$(grep -o '[0-9]* hours\|[0-9]* minutes' profile_downloads.html | head -1)
        if [ -n "$reset_info" ]; then
            echo "Reset time: $reset_info"
        fi
    else
        echo "Download information not available"
    fi
    
    echo ""
    echo "RECENT DOWNLOADS:"
    echo "----------------"
    if [ -f "download_history.html" ]; then
        book_titles=$(grep -o 'title[^>]*>[^<]*<\|href="/book/[^"]*"[^>]*>[^<]*<' download_history.html | sed 's/[^>]*>//;s/<.*$//' | head -5)
        if [ -n "$book_titles" ]; then
            echo "$book_titles" | while read -r title; do
                if [ -n "$title" ]; then
                    echo "• $title"
                fi
            done
        else
            echo "No recent downloads or unable to parse"
        fi
    else
        echo "Download history not available"
    fi
    
    echo ""
    echo "ACCOUNT STATUS:"
    echo "--------------"
    if [ -f "user_profile.html" ]; then
        email=$(grep -o '[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]*\.[a-zA-Z][a-zA-Z]*' user_profile.html | head -1)
        if [ -n "$email" ]; then
            echo "Email: $email"
        fi
        
        if grep -q -i "premium\|subscription" user_profile.html; then
            echo "Account type: Premium/Subscription"
        else
            echo "Account type: Standard/Free"
        fi
    else
        echo "Profile information not available"
    fi
    
    echo ""
    echo "COOKIES STATUS:"
    echo "--------------"
    if [ -f "$COOKIE_JAR" ]; then
        cookie_count=$(wc -l < "$COOKIE_JAR")
        echo "Total cookies: $cookie_count"
        
        if grep -q "remix_userkey" "$COOKIE_JAR"; then
            echo "✓ User authentication cookies present"
        else
            echo "⚠ Authentication cookies missing"
        fi
        
        if grep -q "singlelogin" "$COOKIE_JAR"; then
            echo "✓ Single login session active"
        fi
    else
        echo "No cookie file found"
    fi
    
} > "$REPORT_FILE"

echo "✓ Account report generated: $REPORT_FILE"

echo ""
echo "=== Profile Operations Examples Complete ==="
echo ""
echo "Files created:"
echo "- profile_downloads.html (download limits and usage)"
echo "- download_history.html (download history)"
echo "- user_profile.html (user profile information)"
echo "- public_booklists.html (public booklist search results)"
echo "- personal_booklists.html (personal booklist information)"
echo "- account_stats.html (account statistics)"
echo "- profile_settings.html (profile settings)"
echo "- $REPORT_FILE (comprehensive account report)"
echo ""
echo "Key information extracted:"
echo "- Download limits and remaining quota"
echo "- Recent download history"
echo "- Account type and status"
echo "- Booklist information"
echo "- Profile settings and preferences"
echo ""
echo "Next steps:"
echo "1. Parse HTML files for structured data extraction"
echo "2. Set up monitoring scripts for download limits"
echo "3. Use booklist URLs for specific collection management"
echo "4. Implement automated reporting for account status"
echo ""
echo "Note: Some profile features may require:"
echo "- Premium account access"
echo "- Specific permission levels"
echo "- Recent Z-Library interface updates"