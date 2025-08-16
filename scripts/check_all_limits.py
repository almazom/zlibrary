#!/usr/bin/env python3
"""
Check download limits for all configured Z-Library accounts
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
sys.path.insert(0, '/home/almaz/microservices/zlibrary_api_module/src')
from zlibrary import AsyncZlib

async def check_account(email, password, account_name):
    """Check limits for a single account"""
    if not email or not password:
        return f"{account_name}: Not configured"
    
    try:
        lib = AsyncZlib()
        await lib.login(email, password)
        limits = await lib.profile.get_limits()
        
        daily_allowed = limits.get('daily_allowed', 0)
        daily_remaining = limits.get('daily_remaining', 0)
        daily_amount = limits.get('daily_amount', 0)
        
        status = "✅" if daily_remaining > 0 else "❌"
        return f"{status} {account_name}: {daily_remaining}/{daily_allowed} remaining (used: {daily_amount})"
    
    except Exception as e:
        return f"⚠️ {account_name}: Error - {str(e)[:50]}"

async def main():
    # Load environment
    load_dotenv('/home/almaz/microservices/zlibrary_api_module/.env')
    
    print("🔍 Checking Z-Library Account Limits")
    print("=" * 50)
    
    # Get accounts from environment
    accounts = [
        (os.getenv('ZLOGIN'), os.getenv('ZPASSW'), "Account 1 (Primary)"),
        (os.getenv('ZLOGIN1'), os.getenv('ZPASSW1'), "Account 2"),
        (os.getenv('ZLOGIN2'), os.getenv('ZPASSW2'), "Account 3"),
    ]
    
    # Check all accounts
    tasks = [check_account(email, password, name) for email, password, name in accounts]
    results = await asyncio.gather(*tasks)
    
    # Display results
    for result in results:
        print(result)
    
    # Summary
    print("\n📊 Summary:")
    total_remaining = 0
    working_accounts = 0
    
    for result in results:
        if "remaining" in result and "✅" in result:
            # Extract remaining downloads
            parts = result.split(":")
            if len(parts) > 1:
                remaining_part = parts[1].split("/")[0].strip()
                try:
                    remaining = int(remaining_part)
                    total_remaining += remaining
                    if remaining > 0:
                        working_accounts += 1
                except:
                    pass
    
    print(f"Total downloads available: {total_remaining}")
    print(f"Working accounts: {working_accounts}/3")
    
    if total_remaining == 0:
        print("\n⚠️ All accounts have reached their daily limits!")
        print("Solutions:")
        print("1. Wait for limit reset (usually midnight server time)")
        print("2. Add more Z-Library accounts to .env")
        print("3. Consider using Flibusta for Russian books")

if __name__ == "__main__":
    asyncio.run(main())