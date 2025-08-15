#!/usr/bin/env python3
"""
Check Z-Library account limits and reset times
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib

async def check_account_limits(email, password, account_num):
    """Check account limits and reset time"""
    print(f"\n📋 Account {account_num}: {email}")
    print("-"*40)
    
    try:
        client = AsyncZlib()
        profile = await client.login(email, password)
        limits = await profile.get_limits()
        
        print(f"Daily used: {limits['daily_amount']}")
        print(f"Daily allowed: {limits['daily_allowed']}")
        print(f"Daily remaining: {limits['daily_remaining']}")
        print(f"Reset time: {limits.get('daily_reset', 'Unknown')}")
        
        return limits
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return None

async def main():
    """Check all account limits"""
    accounts = [
        ('almazomam@gmail.com', 'tataronrails78'),
        ('almazomam2@gmail.com', 'tataronrails78'),
        ('almazomam3@gmail.com', 'tataronrails78')
    ]
    
    print("📊 Z-Library Account Limits Check")
    print("="*50)
    
    total_remaining = 0
    
    for i, (email, password) in enumerate(accounts, 1):
        limits = await check_account_limits(email, password, i)
        if limits:
            total_remaining += limits['daily_remaining']
    
    print(f"\n🎯 SUMMARY")
    print("="*50)
    print(f"Total downloads remaining across all accounts: {total_remaining}")
    
    if total_remaining == 0:
        print("❌ NO DOWNLOADS AVAILABLE - All accounts exhausted")
        print("💡 Need to either:")
        print("   - Wait for daily reset")
        print("   - Add more accounts")
        print("   - Use different Z-Library accounts")
    else:
        print(f"✅ {total_remaining} downloads available")

if __name__ == "__main__":
    asyncio.run(main())