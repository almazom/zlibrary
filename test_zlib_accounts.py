#!/usr/bin/env python3
"""
Test Z-Library accounts individually to diagnose authentication issues
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib

async def test_account(email, password, account_num):
    """Test a single Z-Library account"""
    print(f"\n🧪 Testing Account {account_num}: {email}")
    print("="*50)
    
    try:
        client = AsyncZlib()
        print(f"📝 Attempting login...")
        
        profile = await client.login(email, password)
        print(f"✅ Login successful!")
        
        # Get limits
        limits = await profile.get_limits()
        print(f"📊 Download limits: {limits['daily_remaining']}/{limits['daily_allowed']} remaining")
        
        # Try a simple search
        print(f"🔍 Testing search...")
        results = await client.search(q="test", count=1)
        await results.init()
        
        if results.result:
            print(f"✅ Search successful! Found {len(results.result)} result(s)")
            return True
        else:
            print(f"⚠️ Search returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Account failed: {str(e)}")
        return False

async def main():
    """Test all Z-Library accounts"""
    accounts = [
        ('almazomam@gmail.com', 'tataronrails78'),
        ('almazomam2@gmail.com', 'tataronrails78'),
        ('almazomam3@gmail.com', 'tataronrails78')
    ]
    
    print("🔍 Z-Library Multi-Account Authentication Test")
    print("="*60)
    
    working_accounts = 0
    
    for i, (email, password) in enumerate(accounts, 1):
        if await test_account(email, password, i):
            working_accounts += 1
    
    print(f"\n📊 FINAL RESULTS")
    print("="*60)
    print(f"Total accounts tested: {len(accounts)}")
    print(f"Working accounts: {working_accounts}")
    print(f"Failed accounts: {len(accounts) - working_accounts}")
    
    if working_accounts == 0:
        print("❌ NO WORKING ACCOUNTS - Need to update credentials!")
        return 1
    elif working_accounts < len(accounts):
        print("⚠️ SOME ACCOUNTS FAILING - Consider updating failed credentials")
        return 0
    else:
        print("✅ ALL ACCOUNTS WORKING")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)