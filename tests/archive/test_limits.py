#!/usr/bin/env python3
"""Test download limits for all 3 Z-Library accounts"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from zlibrary import AsyncZlib
import json

load_dotenv()

async def check_account_limits(email: str, password: str, account_num: int):
    """Check download limits for a single account"""
    print(f"\n{'='*60}")
    print(f"Account #{account_num}: {email}")
    print(f"{'='*60}")
    
    client = AsyncZlib()
    result = {
        "account": account_num,
        "email": email,
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "limits": None,
        "error": None
    }
    
    try:
        # Login
        print(f"Logging in...")
        profile = await client.login(email, password)
        print(f"✓ Login successful")
        
        # Get limits
        print(f"Fetching download limits...")
        limits = await profile.get_limits()
        
        result["status"] = "success"
        result["limits"] = limits
        
        # Display limits
        print(f"\nDownload Limits:")
        print(f"  Daily Downloads Used:      {limits['daily_amount']}")
        print(f"  Daily Downloads Allowed:   {limits['daily_allowed']}")
        print(f"  Daily Downloads Remaining: {limits['daily_remaining']}")
        print(f"  Limit Reset Time:          {limits['daily_reset']}")
        
        # Calculate percentage used
        if limits['daily_allowed'] > 0:
            percent_used = (limits['daily_amount'] / limits['daily_allowed']) * 100
            print(f"  Usage Percentage:          {percent_used:.1f}%")
            result["limits"]["usage_percentage"] = percent_used
        
        # Logout
        await client.logout()
        print(f"\n✓ Logged out successfully")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

async def main():
    """Test all 3 accounts"""
    print("Z-Library Account Limits Tester")
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Account credentials
    accounts = [
        (os.getenv("ZLOGIN"), os.getenv("ZPASSW"), 1),
        (os.getenv("ZLOGIN1"), os.getenv("ZPASSW1"), 2),
        (os.getenv("ZLOGIN2"), os.getenv("ZPASSW2"), 3),
    ]
    
    # Check all accounts
    results = []
    total_remaining = 0
    total_allowed = 0
    
    for email, password, num in accounts:
        if email and password:
            result = await check_account_limits(email, password, num)
            results.append(result)
            
            if result["status"] == "success" and result["limits"]:
                total_remaining += result["limits"]["daily_remaining"]
                total_allowed += result["limits"]["daily_allowed"]
        else:
            print(f"\n✗ Account #{num} credentials not found in .env")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total Accounts Tested:     {len(results)}")
    print(f"Successful Logins:         {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed Logins:             {sum(1 for r in results if r['status'] == 'error')}")
    print(f"Total Downloads Remaining: {total_remaining}")
    print(f"Total Downloads Allowed:   {total_allowed}")
    
    # Save results to JSON
    output_file = f"limits_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "summary": {
                "accounts_tested": len(results),
                "successful": sum(1 for r in results if r['status'] == 'success'),
                "failed": sum(1 for r in results if r['status'] == 'error'),
                "total_remaining": total_remaining,
                "total_allowed": total_allowed
            },
            "accounts": results
        }, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())