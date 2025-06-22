#!/bin/bash
# Basic Authentication Examples for Z-Library API using curl
#
# These examples demonstrate how to interact with Z-Library using raw HTTP requests.
# Note: This requires understanding the internal API structure.

# Configuration
EMAIL="${ZLOGIN:-your-email@example.com}"
PASSWORD="${ZPASSW:-your-password}"
BASE_URL="https://z-library.sk"
LOGIN_URL="https://z-library.sk/rpc.php"
COOKIE_JAR="zlibrary_cookies.txt"

# User-Agent string (important for avoiding blocks)
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

echo "=== Z-Library Authentication Examples ==="
echo ""

# Example 1: Login and get session cookies
echo "1. Login and get session cookies"
echo "================================"

# Clean up any existing cookies
rm -f "$COOKIE_JAR"

# Login request
echo "Logging in as: $EMAIL"
curl -X POST \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -c "$COOKIE_JAR" \
  -d "isModal=true" \
  -d "email=$EMAIL" \
  -d "password=$PASSWORD" \
  -d "site_mode=books" \
  -d "action=login" \
  -d "isSingleLogin=1" \
  -d "redirectUrl=" \
  -d "gg_json_mode=1" \
  "$LOGIN_URL" > login_response.json

# Check login response
if [ $? -eq 0 ]; then
    echo "✓ Login request sent"
    
    # Parse response to check for errors
    if command -v jq &> /dev/null; then
        validation_error=$(jq -r '.response.validationError // "none"' login_response.json)
        if [ "$validation_error" != "none" ] && [ "$validation_error" != "null" ]; then
            echo "❌ Login failed: $validation_error"
            exit 1
        else
            echo "✓ Login successful"
            
            # Extract useful information
            user_id=$(jq -r '.response.user.id // "unknown"' login_response.json)
            echo "User ID: $user_id"
        fi
    else
        echo "ℹ️  Install jq to parse JSON responses"
        echo "Response saved to login_response.json"
    fi
else
    echo "❌ Login request failed"
    exit 1
fi

echo ""

# Example 2: Test authenticated request
echo "2. Test authenticated request (get main page)"
echo "============================================="

curl -X GET \
  -H "User-Agent: $USER_AGENT" \
  -b "$COOKIE_JAR" \
  "$BASE_URL/" > main_page.html

if [ $? -eq 0 ]; then
    echo "✓ Authenticated request successful"
    
    # Check if we're logged in by looking for logout link
    if grep -q "logout" main_page.html; then
        echo "✓ Session is active (found logout link)"
    else
        echo "⚠️  Session might not be active"
    fi
    
    echo "Main page saved to main_page.html"
else
    echo "❌ Authenticated request failed"
fi

echo ""

# Example 3: Extract user mirror domain (for personalized access)
echo "3. Extract user mirror domain"
echo "============================="

# Look for remix_userkey in cookies
if [ -f "$COOKIE_JAR" ]; then
    remix_userkey=$(grep "remix_userkey" "$COOKIE_JAR" | cut -f7)
    remix_userid=$(grep "remix_userid" "$COOKIE_JAR" | cut -f7)
    
    if [ -n "$remix_userkey" ] && [ -n "$remix_userid" ]; then
        echo "✓ Found user credentials in cookies"
        echo "User Key: $remix_userkey"
        echo "User ID: $remix_userid"
        
        # Try to get personalized domain (this might redirect)
        echo "Testing personalized domain access..."
        
        curl -X GET \
          -H "User-Agent: $USER_AGENT" \
          -b "$COOKIE_JAR" \
          -L \
          -w "Final URL: %{url_effective}\n" \
          "$BASE_URL/?remix_userkey=$remix_userkey&remix_userid=$remix_userid" \
          > personalized_page.html
        
        echo "Personalized page saved to personalized_page.html"
    else
        echo "⚠️  Could not find user credentials in cookies"
    fi
else
    echo "❌ Cookie file not found"
fi

echo ""

# Example 4: Show cookie contents
echo "4. Show cookie contents"
echo "======================="

if [ -f "$COOKIE_JAR" ]; then
    echo "Cookies saved in $COOKIE_JAR:"
    echo "-----------------------------"
    cat "$COOKIE_JAR"
    echo ""
    
    echo "Important cookies:"
    echo "- remix_userkey: $(grep "remix_userkey" "$COOKIE_JAR" | cut -f7)"
    echo "- remix_userid: $(grep "remix_userid" "$COOKIE_JAR" | cut -f7)"
    echo "- singlelogin: $(grep "singlelogin" "$COOKIE_JAR" | cut -f7)"
else
    echo "❌ No cookie file found"
fi

echo ""

# Example 5: Test with proxy (if available)
echo "5. Test with proxy (optional)"
echo "============================="

# Check if PROXY_URL environment variable is set
if [ -n "$PROXY_URL" ]; then
    echo "Testing with proxy: $PROXY_URL"
    
    curl -X GET \
      -H "User-Agent: $USER_AGENT" \
      -b "$COOKIE_JAR" \
      --proxy "$PROXY_URL" \
      "$BASE_URL/" > proxy_test.html
    
    if [ $? -eq 0 ]; then
        echo "✓ Proxy request successful"
        echo "Response saved to proxy_test.html"
    else
        echo "❌ Proxy request failed"
    fi
else
    echo "ℹ️  Set PROXY_URL environment variable to test proxy functionality"
    echo "   Example: export PROXY_URL='socks5://127.0.0.1:9050'"
fi

echo ""

# Example 6: Logout
echo "6. Logout"
echo "========="

curl -X POST \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -b "$COOKIE_JAR" \
  -d "action=logout" \
  "$LOGIN_URL" > logout_response.json

if [ $? -eq 0 ]; then
    echo "✓ Logout request sent"
    echo "Response saved to logout_response.json"
else
    echo "❌ Logout request failed"
fi

echo ""
echo "=== Authentication Examples Complete ==="
echo ""
echo "Files created:"
echo "- $COOKIE_JAR (session cookies)"
echo "- login_response.json (login API response)"
echo "- main_page.html (authenticated main page)"
echo "- personalized_page.html (user-specific domain)"
echo "- logout_response.json (logout API response)"
echo ""
echo "Next steps:"
echo "1. Use the session cookies for authenticated requests"
echo "2. Check search_examples.sh for search functionality"
echo "3. See download_examples.sh for download operations"