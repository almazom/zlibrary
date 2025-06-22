# Z-Library API - curl Examples

This directory contains comprehensive examples of using Z-Library's web interface through direct HTTP requests using curl. These examples demonstrate the underlying API calls that the Python library makes.

## Overview

The curl examples are organized into several scripts that demonstrate different aspects of the Z-Library API:

1. **`basic_auth.sh`** - Authentication and session management
2. **`search_examples.sh`** - Various search operations
3. **`book_details.sh`** - Getting detailed book information
4. **`profile_operations.sh`** - User profile and account management

## Prerequisites

- `curl` command-line tool
- Valid Z-Library account credentials
- Basic understanding of HTTP requests and cookies
- Optional: `jq` for JSON parsing, `grep` for text extraction

## Setup

1. Set your credentials as environment variables:
```bash
export ZLOGIN="your-email@example.com"
export ZPASSW="your-password"
```

2. Make scripts executable:
```bash
chmod +x *.sh
```

3. Optional proxy setup (for Tor):
```bash
export PROXY_URL="socks5://127.0.0.1:9050"
```

## Usage

### Basic Authentication

Start with authentication to establish a session:

```bash
./basic_auth.sh
```

This script will:
- Log in to Z-Library
- Save session cookies to `zlibrary_cookies.txt`
- Test authenticated requests
- Extract user-specific domain information

### Search Operations

After authentication, perform various searches:

```bash
./search_examples.sh
```

This demonstrates:
- Basic text search
- Advanced filtering (year, language, format)
- Pagination
- Full-text search
- Multiple search strategies

### Book Details

Get detailed information about specific books:

```bash
./book_details.sh
```

Features:
- Fetch complete book metadata
- Extract download URLs
- Download cover images
- Generate metadata summaries

### Profile Management

Access user profile and account information:

```bash
./profile_operations.sh
```

Includes:
- Download limits and usage
- Download history
- Booklist management
- Account statistics
- Settings access

## API Endpoints

### Authentication
- **POST** `/rpc.php` - Login endpoint
- **GET** `/?remix_userkey=X&remix_userid=Y` - Session validation

### Search
- **GET** `/s/{query}` - Basic search
- **GET** `/s/{query}?parameters` - Advanced search with filters

### Book Access
- **GET** `/book/{id}` - Book details page
- **GET** `/dl/{id}` - Download endpoint (authenticated)

### Profile
- **GET** `/profile` - User profile
- **GET** `/users/downloads` - Download limits
- **GET** `/users/downloads/history` - Download history
- **GET** `/booklists/search` - Public booklist search

## Search Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `yearFrom` | Start year filter | `yearFrom=2020` |
| `yearTo` | End year filter | `yearTo=2024` |
| `languages[]` | Language filter | `languages[]=english` |
| `extensions[]` | Format filter | `extensions[]=pdf` |
| `e` | Exact phrase search | `e=1` |
| `page` | Page number | `page=2` |
| `count` | Results per page | `count=25` |
| `fulltext` | Full-text search | `fulltext=1` |

## Cookie Management

The scripts use `zlibrary_cookies.txt` to maintain session state. Important cookies include:

- `remix_userkey` - User authentication key
- `remix_userid` - User ID
- `singlelogin` - Single login session token

## Output Files

The scripts generate various output files:

### Authentication
- `zlibrary_cookies.txt` - Session cookies
- `login_response.json` - Login API response
- `main_page.html` - Authenticated main page

### Search Results
- `search_*.html` - Search result pages
- `book_urls.txt` - Extracted book URLs

### Book Information
- `book_details_*.html` - Book detail pages
- `metadata_*.txt` - Extracted metadata
- `cover_*.jpg` - Book cover images

### Profile Data
- `profile_*.html` - Profile information pages
- `account_report_*.txt` - Comprehensive account reports

## Error Handling

Common issues and solutions:

### Authentication Failures
- Verify credentials are correct
- Check for account lockouts
- Ensure cookies are being saved/loaded

### Rate Limiting
- Add delays between requests
- Reduce concurrent operations
- Use appropriate User-Agent headers

### Access Restrictions
- Some content requires premium accounts
- Download limits may apply
- Geographic restrictions possible

## Security Considerations

- Store credentials in environment variables
- Use HTTPS for all requests
- Consider using Tor for privacy
- Don't commit cookies or credentials to version control
- Respect rate limits and terms of service

## Proxy Support

For enhanced privacy, use with Tor:

```bash
# Start Tor service
sudo systemctl start tor

# Set proxy environment variable
export PROXY_URL="socks5://127.0.0.1:9050"

# Use onion domain
BASE_URL="http://bookszlibb74ugqojhzhg2a63w5i2atv5bqarulgczawnbmsb6s6qead.onion"
```

## Advanced Usage

### Automated Monitoring

Create a cron job to monitor download limits:

```bash
# Add to crontab: check limits every hour
0 * * * * /path/to/profile_operations.sh > /var/log/zlibrary_status.log
```

### Bulk Operations

Process multiple books:

```bash
# Extract all book IDs from search results
grep -o '/book/[0-9]*/[a-f0-9]*' search_*.html | sort -u > all_book_ids.txt

# Process each book
while read -r book_id; do
    curl -b zlibrary_cookies.txt "$BASE_URL$book_id" > "details_${book_id//\//_}.html"
    sleep 1  # Rate limiting
done < all_book_ids.txt
```

### Data Extraction

Use tools like `jq`, `htmlq`, or custom scripts to extract structured data:

```bash
# Extract book titles using htmlq
htmlq -t 'h1' book_details_*.html

# Extract metadata using grep and sed
grep -o 'Publisher: [^<]*' book_details_*.html | sed 's/Publisher: //'
```

## Troubleshooting

### Common Issues

1. **Login failures**: Check credentials and account status
2. **Missing cookies**: Ensure cookie jar is writable and persistent
3. **Parse errors**: Z-Library may change HTML structure
4. **Access denied**: May need premium account or be rate limited

### Debug Mode

Enable verbose curl output:

```bash
# Add -v flag for verbose output
curl -v -X GET -b zlibrary_cookies.txt "$BASE_URL/"
```

### Manual Testing

Test individual endpoints:

```bash
# Test login
curl -X POST -d "email=$ZLOGIN&password=$ZPASSW&action=login" https://z-library.sk/rpc.php

# Test search
curl -b zlibrary_cookies.txt "https://z-library.sk/s/python%20programming"
```

## Integration

These curl examples can be integrated into:
- Shell scripts for automation
- CI/CD pipelines for content validation
- Monitoring systems for service availability
- Custom applications requiring HTTP-level control

## Legal Notice

These examples are for educational purposes. Users must:
- Comply with Z-Library's terms of service
- Respect copyright laws in their jurisdiction
- Use the service responsibly and ethically
- Not abuse rate limits or overload servers

## See Also

- [Python API examples](../python/) - Higher-level Python interface
- [Z-Library API documentation](../../doc/) - Complete API reference
- [Installation guide](../../doc/installation.md) - Setup instructions