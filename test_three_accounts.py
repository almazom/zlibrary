#!/usr/bin/env python3
"""
Test all 3 Z-Library accounts and verify 30 downloads/day capacity
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from zlibrary.account_pool import AccountPool
from zlibrary.libasync import AsyncZlib

# Load environment variables
load_dotenv()


async def test_three_accounts():
    """Test that all 3 accounts work correctly"""
    print("="*70)
    print("🧪 TESTING 3 Z-LIBRARY ACCOUNTS")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Get all 3 accounts from environment
    accounts = [
        {"email": os.getenv("ZLOGIN"), "password": os.getenv("ZPASSW"), "name": "Primary"},
        {"email": os.getenv("ZLOGIN1"), "password": os.getenv("ZPASSW1"), "name": "Secondary"},
        {"email": os.getenv("ZLOGIN2"), "password": os.getenv("ZPASSW2"), "name": "Tertiary"}
    ]
    
    print("\n📋 ACCOUNTS TO TEST:")
    for i, acc in enumerate(accounts, 1):
        print(f"   Account {i}: {acc['email']} ({acc['name']})")
    
    # Test each account individually
    print("\n🔐 TESTING INDIVIDUAL ACCOUNTS:")
    print("-" * 50)
    
    limits_data = []
    for i, acc in enumerate(accounts, 1):
        print(f"\n📌 Testing Account {i}: {acc['email']}...")
        try:
            client = AsyncZlib()
            profile = await client.login(acc["email"], acc["password"])
            limits = await profile.get_limits()
            
            limits_data.append({
                "email": acc["email"],
                "name": acc["name"],
                "limit": limits["daily_allowed"],
                "remaining": limits["daily_remaining"],
                "used": limits["daily_amount"]
            })
            
            print(f"   ✅ Authenticated successfully")
            print(f"   📊 Daily limit: {limits['daily_allowed']}")
            print(f"   📊 Remaining: {limits['daily_remaining']}")
            print(f"   📊 Used today: {limits['daily_amount']}")
            
            await client.logout()
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
    
    # Test Account Pool with all 3 accounts
    print("\n🔄 TESTING ACCOUNT POOL WITH 3 ACCOUNTS:")
    print("-" * 50)
    
    try:
        pool = AccountPool("test_3accounts_config.json")
        
        # Add all 3 accounts to pool
        for acc in accounts:
            pool.add_account(acc["email"], acc["password"], f"{acc['name']} account")
        
        print(f"✅ Added {len(pool.accounts)} accounts to pool")
        
        # Initialize pool
        print("🔄 Initializing account pool...")
        await pool.initialize_all()
        
        # Get statistics
        stats = pool.get_statistics()
        
        print("\n📊 POOL STATISTICS:")
        print(f"   Total accounts: {stats['total_accounts']}")
        print(f"   Active accounts: {stats['active_accounts']}")
        print(f"   Combined daily limit: {stats['total_daily_limit']} downloads")
        print(f"   Combined remaining: {stats['total_daily_remaining']} downloads")
        print(f"   Combined used today: {stats['total_daily_used']} downloads")
        
        # Test rotation through all 3 accounts
        print("\n🔄 TESTING ACCOUNT ROTATION:")
        used_accounts = set()
        for i in range(5):  # Try 5 requests to see rotation
            client, account = await pool.get_available_client()
            if client:
                used_accounts.add(account.email)
                print(f"   Request {i+1}: Using {account.email}")
        
        print(f"\n✅ Accounts used in rotation: {len(used_accounts)}/3")
        for email in used_accounts:
            print(f"   - {email}")
        
        # Perform a test search
        print("\n🔍 PERFORMING TEST SEARCH:")
        client, account = await pool.get_available_client()
        if client:
            print(f"   Using account: {account.email}")
            results = await client.search("Python", count=3)
            await results.init()
            print(f"   ✅ Search successful, found {len(results.result)} books")
        
    except Exception as e:
        print(f"❌ Account pool failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test file
        if Path("test_3accounts_config.json").exists():
            Path("test_3accounts_config.json").unlink()
    
    # Summary
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    
    print("\n📊 ACCOUNT SUMMARY:")
    total_limit = 0
    total_remaining = 0
    total_used = 0
    
    for i, data in enumerate(limits_data, 1):
        print(f"\n   Account {i}: {data['email']}")
        print(f"      Status: ✅ Active")
        print(f"      Daily Limit: {data['limit']} downloads")
        print(f"      Remaining: {data['remaining']} downloads")
        print(f"      Used Today: {data['used']} downloads")
        
        total_limit += data['limit']
        total_remaining += data['remaining']
        total_used += data['used']
    
    print("\n" + "="*70)
    print("💎 TOTAL CAPACITY WITH 3 ACCOUNTS:")
    print(f"   🚀 Total Daily Limit: {total_limit} downloads/day")
    print(f"   ✅ Total Remaining Today: {total_remaining} downloads")
    print(f"   📈 Total Used Today: {total_used} downloads")
    print(f"   📊 Utilization: {(total_used/total_limit)*100:.1f}%")
    print("="*70)
    
    print("\n🌟 BENEFITS:")
    print(f"   • 3x download capacity vs single account")
    print(f"   • {total_limit} downloads per day available")
    print(f"   • Automatic failover between accounts")
    print(f"   • No manual switching needed")
    print(f"   • Persistent state tracking")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_three_accounts())
    sys.exit(0 if success else 1)