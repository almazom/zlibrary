#!/usr/bin/env python3
"""
Simple Authorization Test for Z-Library

This test only checks if we can successfully login to Z-Library.
No downloads, just authentication verification.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Try to load .env file
try:
    from dotenv import load_dotenv
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
from zlibrary.exception import LoginFailed

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='🔍 %(asctime)s - %(levelname)s - %(message)s'
)

# Enable zlibrary logging
logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
logging.getLogger("zlibrary").setLevel(logging.INFO)


async def test_authorization():
    """Test Z-Library authorization only."""
    
    print("🔐 Z-Library Authorization Test")
    print("=" * 35)
    
    # Try different variable naming conventions
    email = (os.getenv('ZLOGIN') or 
             os.getenv('ZLIB_EMAIL') or 
             os.getenv('ZLIBRARY_EMAIL'))
    
    password = (os.getenv('ZPASSW') or 
                os.getenv('ZLIB_PASS') or 
                os.getenv('ZLIBRARY_PASSWORD'))
    
    print(f"📧 Email from env: {'✅ Found' if email else '❌ Not found'}")
    print(f"🔑 Password from env: {'✅ Found' if password else '❌ Not found'}")
    
    if not email or not password:
        print("\n❌ Credentials not found in environment variables!")
        print("Expected variables (any of these combinations):")
        print("  ZLOGIN + ZPASSW")
        print("  ZLIB_EMAIL + ZLIB_PASS") 
        print("  ZLIBRARY_EMAIL + ZLIBRARY_PASSWORD")
        print(f"\nFound in .env:")
        
        # Show what we actually found
        env_vars = dict(os.environ)
        zlib_vars = {k: '***' if 'pass' in k.lower() else v 
                    for k, v in env_vars.items() 
                    if 'zlib' in k.lower()}
        
        if zlib_vars:
            for k, v in zlib_vars.items():
                print(f"  {k}={v}")
        else:
            print("  No Z-Library variables found")
            
        return False
    
    try:
        print(f"\n🚀 Initializing Z-Library client...")
        lib = zlibrary.AsyncZlib()
        
        print(f"🔐 Attempting login with email: {email[:3]}***{email[-10:]}")
        await lib.login(email, password)
        
        print("✅ LOGIN SUCCESSFUL! 🎉")
        print(f"🌐 Connected to: {lib.mirror}")
        
        # Test basic profile access
        try:
            print(f"\n📊 Testing profile access...")
            limits = await lib.profile.get_limits()
            print(f"✅ Profile access successful!")
            print(f"📈 Daily downloads allowed: {limits['daily_allowed']}")
            print(f"📉 Daily downloads remaining: {limits['daily_remaining']}")
            print(f"🕐 Reset time: {limits['daily_reset']}")
            
        except Exception as e:
            print(f"⚠️  Profile access failed: {e}")
            print("   (Login was successful, but profile features may be limited)")
        
        # Logout
        await lib.logout()
        print(f"🚪 Logged out successfully")
        
        return True
        
    except LoginFailed as e:
        print(f"❌ LOGIN FAILED: {e}")
        print(f"\n🔍 Troubleshooting tips:")
        print(f"  1. Check that email and password are correct")
        print(f"  2. Make sure your Z-Library account is active")
        print(f"  3. Try logging in manually at https://z-library.sk")
        print(f"  4. Check your internet connection")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner."""
    print("🧪 Quick Z-Library Authorization Test")
    print("=====================================\n")
    
    success = await test_authorization()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 AUTHORIZATION TEST PASSED!")
        print("✅ You can now run full integration tests")
        exit_code = 0
    else:
        print("❌ AUTHORIZATION TEST FAILED!")
        print("🔧 Please check your credentials and try again")
        exit_code = 1
    
    print(f"Exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 