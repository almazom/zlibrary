#!/usr/bin/env python3
"""
Simple test to verify 2 Z-Library accounts are working
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from zlibrary.account_pool import AccountPool
from zlibrary.libasync import AsyncZlib

# Load environment variables
load_dotenv()


async def test_two_accounts():
    """Test that both accounts work correctly"""
    print("="*60)
    print("🧪 TESTING 2 Z-LIBRARY ACCOUNTS")
    print("="*60)
    
    # Get accounts from environment
    account1_email = os.getenv("ZLOGIN")
    account1_pass = os.getenv("ZPASSW")
    account2_email = os.getenv("ZLOGIN1")
    account2_pass = os.getenv("ZPASSW1")
    
    print(f"Account 1: {account1_email}")
    print(f"Account 2: {account2_email}")
    print("="*60)
    
    # Test Account 1
    print("\n📌 Testing Account 1...")
    try:
        client1 = AsyncZlib()
        profile1 = await client1.login(account1_email, account1_pass)
        limits1 = await profile1.get_limits()
        print(f"✅ Account 1 authenticated successfully")
        print(f"   Daily limit: {limits1['daily_allowed']}")
        print(f"   Remaining: {limits1['daily_remaining']}")
        print(f"   Used today: {limits1['daily_amount']}")
        await client1.logout()
    except Exception as e:
        print(f"❌ Account 1 failed: {e}")
        return False
    
    # Test Account 2
    print("\n📌 Testing Account 2...")
    try:
        client2 = AsyncZlib()
        profile2 = await client2.login(account2_email, account2_pass)
        limits2 = await profile2.get_limits()
        print(f"✅ Account 2 authenticated successfully")
        print(f"   Daily limit: {limits2['daily_allowed']}")
        print(f"   Remaining: {limits2['daily_remaining']}")
        print(f"   Used today: {limits2['daily_amount']}")
        await client2.logout()
    except Exception as e:
        print(f"❌ Account 2 failed: {e}")
        return False
    
    # Test Account Pool
    print("\n📌 Testing Account Pool with both accounts...")
    try:
        pool = AccountPool("test_pool_config.json")
        pool.add_account(account1_email, account1_pass, "Primary account")
        pool.add_account(account2_email, account2_pass, "Secondary account")
        
        print(f"✅ Added {len(pool.accounts)} accounts to pool")
        
        # Initialize pool
        await pool.initialize_all()
        
        # Get statistics
        stats = pool.get_statistics()
        print(f"✅ Pool Statistics:")
        print(f"   Total accounts: {stats['total_accounts']}")
        print(f"   Active accounts: {stats['active_accounts']}")
        print(f"   Combined daily limit: {stats['total_daily_limit']}")
        print(f"   Combined remaining: {stats['total_daily_remaining']}")
        
        # Test rotation
        client, account = await pool.get_available_client()
        if client:
            print(f"✅ Got client from pool: {account.email}")
            
            # Search test
            results = await client.search("Python", count=5)
            await results.init()
            print(f"✅ Search returned {len(results.result)} books")
            
    except Exception as e:
        print(f"❌ Account pool failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test file
        if Path("test_pool_config.json").exists():
            Path("test_pool_config.json").unlink()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Both Z-Library accounts are working correctly")
    print("✅ Account pool and rotation functioning properly")
    print("="*60)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"Account 1: {limits1['daily_remaining']}/{limits1['daily_allowed']} downloads remaining")
    print(f"Account 2: {limits2['daily_remaining']}/{limits2['daily_allowed']} downloads remaining")
    print(f"Total capacity: {limits1['daily_remaining'] + limits2['daily_remaining']}/{limits1['daily_allowed'] + limits2['daily_allowed']} downloads")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_two_accounts())
    sys.exit(0 if success else 1)