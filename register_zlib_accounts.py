#!/usr/bin/env python3
"""
Guide for registering additional Z-Library accounts
"""

def generate_account_registration_script():
    """Generate a script for semi-automated account registration"""
    
    accounts_to_create = [
        "almazomam4@gmail.com",
        "almazomam5@gmail.com", 
        "almazomam6@gmail.com",
        "almazomam7@gmail.com",
        "almazomam8@gmail.com",
        "almazomam9@gmail.com",
        "almazomam10@gmail.com",
    ]
    
    print("📝 Z-Library Account Registration Guide")
    print("="*60)
    
    print("\n🎯 MANUAL REGISTRATION REQUIRED")
    print("Z-Library requires manual registration for each account.")
    print("Follow these steps for each email:")
    
    for i, email in enumerate(accounts_to_create, 4):
        print(f"\n📧 Account {i}: {email}")
        print(f"   1. Go to https://z-library.sk")
        print(f"   2. Click 'Sign Up'")
        print(f"   3. Email: {email}")
        print(f"   4. Password: tataronrails78")
        print(f"   5. Verify email if required")
    
    print(f"\n✅ Once registered, test with:")
    print(f"   python3 test_zlib_accounts.py")

def create_account_status_tracker():
    """Create a simple account status tracker"""
    
    tracker_content = """#!/usr/bin/env python3
\"\"\"
Z-Library Account Status Tracker
Tracks which accounts are registered and working
\"\"\"

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib

ACCOUNTS = [
    ('almazomam@gmail.com', 'tataronrails78'),       # ✅ Registered
    ('almazomam2@gmail.com', 'tataronrails78'),      # ✅ Registered  
    ('almazomam3@gmail.com', 'tataronrails78'),      # ✅ Registered
    ('almazomam4@gmail.com', 'tataronrails78'),      # ❌ Need to register
    ('almazomam5@gmail.com', 'tataronrails78'),      # ❌ Need to register
    ('almazomam6@gmail.com', 'tataronrails78'),      # ❌ Need to register
    ('almazomam7@gmail.com', 'tataronrails78'),      # ❌ Need to register
    ('almazomam8@gmail.com', 'tataronrails78'),      # ❌ Need to register
    ('almazomam9@gmail.com', 'tataronrails78'),      # ❌ Need to register
    ('almazomam10@gmail.com', 'tataronrails78'),     # ❌ Need to register
]

async def check_account_status(email, password):
    \"\"\"Check if account is registered and working\"\"\"
    try:
        client = AsyncZlib()
        profile = await client.login(email, password)
        limits = await profile.get_limits()
        return True, limits['daily_remaining']
    except Exception as e:
        return False, str(e)

async def main():
    print("📊 Z-Library Account Status Report")
    print("="*60)
    
    working = 0
    total_downloads = 0
    
    for i, (email, password) in enumerate(ACCOUNTS, 1):
        print(f"\\n🔍 Testing {i:2d}: {email}")
        
        is_working, result = await check_account_status(email, password)
        
        if is_working:
            working += 1
            total_downloads += result
            print(f"    ✅ Working - {result} downloads remaining")
        else:
            print(f"    ❌ Failed - {result}")
    
    print(f"\\n📈 SUMMARY")
    print("="*60)
    print(f"Working accounts: {working}/{len(ACCOUNTS)}")
    print(f"Total downloads available: {total_downloads}")
    print(f"Failed accounts: {len(ACCOUNTS) - working}")
    
    if working < len(ACCOUNTS):
        print(f"\\n💡 TO-DO: Register {len(ACCOUNTS) - working} additional accounts")

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    with open("account_status_tracker.py", "w") as f:
        f.write(tracker_content)
    
    print("✅ Created account_status_tracker.py")

def show_quick_fix_options():
    """Show immediate options to get book search working"""
    
    print("\n🚀 IMMEDIATE OPTIONS TO FIX BOOK SEARCH")
    print("="*60)
    
    print("1. ⏰ WAIT FOR RESET (4 hours)")
    print("   - Current accounts will reset automatically")
    print("   - 30 total downloads will be available (3 accounts × 10)")
    
    print("\n2. 📧 REGISTER NEW ACCOUNTS (recommended)")
    print("   - Follow the manual registration guide above")
    print("   - Each new account adds 10 more downloads")
    print("   - 7 additional accounts = 70 more downloads")
    
    print("\n3. 🔄 USE EXISTING PREMIUM ACCOUNTS")
    print("   - If you have other Z-Library accounts")
    print("   - Add them to the accounts list in book_search_engine.py")
    
    print("\n🎯 BEST APPROACH:")
    print("   Register 2-3 accounts now for immediate use")
    print("   Register remaining accounts over time for 24/7 availability")

if __name__ == "__main__":
    generate_account_registration_script()
    create_account_status_tracker()
    show_quick_fix_options()