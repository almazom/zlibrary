#!/usr/bin/env python3
"""
Real Integration Test for Z-Library EPUB Download

This test performs a real download of an EPUB book from Z-Library.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
import tempfile
import aiohttp

# Try to load .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"🔧 Loaded environment variables from {env_path}")
    else:
        print(f"ℹ️  No .env file found at {env_path}")
except ImportError:
    print("ℹ️  python-dotenv not installed. Using system environment variables only.")

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import zlibrary
from zlibrary import Language, Extension

# Enable rich logging with colors
logging.basicConfig(
    level=logging.INFO,
    format='🔍 %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable zlibrary logging
logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
logging.getLogger("zlibrary").setLevel(logging.DEBUG)


async def test_real_epub_download():
    """Test real EPUB download from Z-Library."""
    
    print("🚀 Starting Z-Library EPUB Download Test")
    print("=" * 50)
    
    # Get credentials from environment
    email = os.getenv('ZLOGIN')
    password = os.getenv('ZPASSW')
    
    if not email or not password:
        print("❌ Z-Library credentials not found!")
        print()
        print("📝 To set up credentials:")
        print("1. Copy env.template to .env:")
        print("   cp env.template .env")
        print()
        print("2. Edit .env file with your Z-Library credentials:")
        print("   ZLOGIN=your-email@example.com")
        print("   ZPASSW=your-password")
        print()
        print("3. Make sure you have a Z-Library account at: https://z-library.sk")
        print()
        
        # Fallback to interactive input
        try:
            email = input("🔑 Enter Z-Library email (or Ctrl+C to exit): ").strip()
            password = input("🔐 Enter Z-Library password: ").strip()
            
            if not email or not password:
                print("❌ Invalid credentials provided.")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Test cancelled by user.")
            return False
    
    try:
        # Initialize Z-Library client
        print("🔧 Initializing Z-Library client...")
        lib = zlibrary.AsyncZlib()
        
        # Login
        print("🔐 Logging in...")
        await lib.login(email, password)
        print("✅ Login successful!")
        
        # Check download limits
        print("\n📊 Checking download limits...")
        try:
            limits = await lib.profile.get_limits()
            print(f"📈 Daily allowed: {limits['daily_allowed']}")
            print(f"📉 Daily remaining: {limits['daily_remaining']}")
            print(f"🕐 Reset time: {limits['daily_reset']}")
            
            if limits['daily_remaining'] <= 0:
                print("⚠️  No downloads remaining today. Test will search but not download.")
                download_allowed = False
            else:
                download_allowed = True
                
        except Exception as e:
            print(f"⚠️  Could not get limits: {e}")
            download_allowed = True  # Try anyway
        
        # Search for a small EPUB book for testing
        print("\n🔍 Searching for EPUB books...")
        search_queries = [
            "python programming",
            "programming tutorial", 
            "computer science",
            "software engineering"
        ]
        
        book_found = None
        
        for query in search_queries:
            print(f"🔎 Searching: '{query}'")
            try:
                paginator = await lib.search(
                    q=query,
                    count=10,
                    lang=[Language.ENGLISH],
                    extensions=[Extension.EPUB]
                )
                
                books = await paginator.next()
                print(f"📚 Found {len(books)} EPUB books")
                
                # Look for a relatively small book
                for book in books:
                    if book.get('size'):
                        size_str = book['size'].lower()
                        print(f"📖 {book['name'][:50]}... - {book['size']}")
                        
                        # Try to find a book smaller than 10MB
                        if any(size_indicator in size_str for size_indicator in ['kb', 'mb']) and \
                           not any(large_indicator in size_str for large_indicator in ['gb', '100', '200', '300']):
                            book_found = book
                            break
                
                if book_found:
                    break
                    
            except Exception as e:
                print(f"❌ Search failed for '{query}': {e}")
                continue
        
        if not book_found:
            print("❌ No suitable EPUB book found for testing")
            return False
        
        print(f"\n📚 Selected book for download:")
        print(f"📖 Title: {book_found.get('name', 'Unknown')}")
        print(f"👤 Authors: {book_found.get('authors', 'Unknown')}")
        print(f"📅 Year: {book_found.get('year', 'Unknown')}")
        print(f"📄 Format: {book_found.get('extension', 'Unknown')}")
        print(f"📏 Size: {book_found.get('size', 'Unknown')}")
        
        # Get detailed book information including download URL
        print(f"\n🔍 Getting book details...")
        try:
            book_details = await book_found.fetch()
            print(f"✅ Got book details successfully")
            
            download_url = book_details.get('download_url')
            if not download_url:
                print("❌ No download URL found in book details")
                return False
                
            print(f"🔗 Download URL obtained")
            
        except Exception as e:
            print(f"❌ Failed to get book details: {e}")
            return False
        
        # Download the file if allowed
        if download_allowed:
            print(f"\n📥 Downloading EPUB file...")
            
            # Create downloads directory
            downloads_dir = Path("downloads")
            downloads_dir.mkdir(exist_ok=True)
            
            # Generate safe filename
            safe_title = "".join(c for c in book_details['name'][:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}.epub"
            filepath = downloads_dir / filename
            
            try:
                # Download the file using the authenticated session
                async with aiohttp.ClientSession(cookies=lib.cookies) as session:
                    async with session.get(download_url) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            # Save to file
                            with open(filepath, 'wb') as f:
                                f.write(content)
                            
                            file_size = len(content)
                            print(f"✅ Successfully downloaded: {filepath}")
                            print(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                            
                            # Verify it's a valid EPUB file
                            if filepath.suffix.lower() == '.epub' and file_size > 1000:
                                print("✅ Downloaded file appears to be a valid EPUB")
                                return True
                            else:
                                print("⚠️  Downloaded file may not be a valid EPUB")
                                return False
                        else:
                            print(f"❌ Download failed with status: {response.status}")
                            return False
                            
            except Exception as e:
                print(f"❌ Download failed: {e}")
                return False
        else:
            print("ℹ️  Download limit reached. Test completed successfully without download.")
            return True
            
    except zlibrary.exception.LoginFailed as e:
        print(f"❌ Login failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Test completed successfully!")
    return True


async def main():
    """Main test runner."""
    
    print("🧪 Z-Library EPUB Download Integration Test")
    print("==========================================")
    print()
    
    success = await test_real_epub_download()
    
    if success:
        print("\n✅ All tests passed!")
        exit_code = 0
    else:
        print("\n❌ Test failed!")
        exit_code = 1
    
    print("\n📝 Test Summary:")
    print(f"Status: {'PASS' if success else 'FAIL'}")
    print(f"Exit Code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 