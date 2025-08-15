#!/usr/bin/env python3
"""
Z-Library Account Status Tracker
Tracks which accounts are registered and working
"""

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
    """Check if account is registered and working"""
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
        print(f"\n🔍 Testing {i:2d}: {email}")
        
        is_working, result = await check_account_status(email, password)
        
        if is_working:
            working += 1
            total_downloads += result
            print(f"    ✅ Working - {result} downloads remaining")
        else:
            print(f"    ❌ Failed - {result}")
    
    print(f"\n📈 SUMMARY")
    print("="*60)
    print(f"Working accounts: {working}/{len(ACCOUNTS)}")
    print(f"Total downloads available: {total_downloads}")
    print(f"Failed accounts: {len(ACCOUNTS) - working}")
    
    if working < len(ACCOUNTS):
        print(f"\n💡 TO-DO: Register {len(ACCOUNTS) - working} additional accounts")

if __name__ == "__main__":
    asyncio.run(main())
