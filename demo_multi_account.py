#!/usr/bin/env python3
"""
Demo: Multi-Account Z-Library System with 2 Accounts
Shows automatic rotation and increased download capacity
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from zlibrary.account_pool import AccountPool, SmartDownloader

# Load environment variables
load_dotenv()


async def demo_multi_account():
    """Demonstrate multi-account functionality"""
    print("="*70)
    print("🚀 Z-LIBRARY MULTI-ACCOUNT SYSTEM DEMO")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Create account pool
    pool = AccountPool("demo_config.json")
    
    # Add accounts from environment
    account1 = os.getenv("ZLOGIN")
    pass1 = os.getenv("ZPASSW")
    account2 = os.getenv("ZLOGIN1")
    pass2 = os.getenv("ZPASSW1")
    
    pool.add_account(account1, pass1, "Primary Account")
    pool.add_account(account2, pass2, "Secondary Account")
    
    print(f"\n📋 ACCOUNT POOL SETUP")
    print(f"   Account 1: {account1}")
    print(f"   Account 2: {account2}")
    
    # Initialize accounts
    print(f"\n🔄 Initializing accounts...")
    results = await pool.initialize_all()
    
    # Show account status
    print(f"\n📊 ACCOUNT STATUS:")
    for i, acc in enumerate(pool.accounts, 1):
        status = "✅ Active" if acc.is_active else "❌ Inactive"
        print(f"   Account {i}: {status}")
        print(f"      Email: {acc.email}")
        print(f"      Daily Limit: {acc.daily_limit}")
        print(f"      Remaining: {acc.daily_remaining}")
        print(f"      Used Today: {acc.daily_used}")
        if acc.reset_time:
            print(f"      Resets in: {acc.reset_time}")
    
    # Get pool statistics
    stats = pool.get_statistics()
    print(f"\n🎯 COMBINED CAPACITY:")
    print(f"   Total Accounts: {stats['total_accounts']}")
    print(f"   Active Accounts: {stats['active_accounts']}")
    print(f"   Total Daily Limit: {stats['total_daily_limit']} downloads")
    print(f"   Total Remaining: {stats['total_daily_remaining']} downloads")
    print(f"   Total Used Today: {stats['total_daily_used']} downloads")
    
    # Demonstrate search with automatic rotation
    print(f"\n🔍 DEMONSTRATING SEARCH WITH ROTATION:")
    
    # Create SmartDownloader
    downloader = SmartDownloader(pool)
    
    # Search for books (search only, not download)
    query = "machine learning"
    print(f"   Searching for: '{query}'")
    
    # Get a client from pool and search
    client, account = await pool.get_available_client()
    if client:
        print(f"   Using account: {account.email}")
        results = await client.search(query, count=10)
        await results.init()
        books = results.result
        print(f"   ✅ Found {len(books)} books")
    else:
        books = []
        print(f"   ❌ No available accounts")
    
    # Show first 3 results
    if books:
        print(f"\n📚 SAMPLE RESULTS:")
        for i, book in enumerate(books[:3], 1):
            print(f"   {i}. {book.get('name', 'Unknown')[:60]}...")
            if book.get('authors'):
                print(f"      Author: {book['authors']}")
            print(f"      Year: {book.get('year', 'N/A')}")
            print(f"      Extension: {book.get('extension', 'N/A')}")
    
    # Demonstrate account rotation
    print(f"\n🔄 DEMONSTRATING ACCOUNT ROTATION:")
    
    # Get client from pool multiple times
    for i in range(3):
        client, account = await pool.get_available_client()
        if client:
            print(f"   Request {i+1}: Using {account.email} ({account.daily_remaining} remaining)")
        else:
            print(f"   Request {i+1}: No accounts available")
    
    # Final statistics
    print(f"\n📈 FINAL STATISTICS:")
    final_stats = pool.get_statistics()
    print(f"   Active accounts: {final_stats['active_accounts']}/{final_stats['total_accounts']}")
    print(f"   Downloads remaining today: {final_stats['total_daily_remaining']}/{final_stats['total_daily_limit']}")
    
    # Benefits summary
    print(f"\n💡 BENEFITS OF MULTI-ACCOUNT SYSTEM:")
    print(f"   ✅ 2x download capacity (20 downloads/day vs 10)")
    print(f"   ✅ Automatic failover if one account hits limit")
    print(f"   ✅ Seamless rotation between accounts")
    print(f"   ✅ Combined statistics tracking")
    print(f"   ✅ Persistent state across sessions")
    
    print(f"\n" + "="*70)
    print(f"✨ Demo complete! Multi-account system is ready to use.")
    print(f"="*70)
    
    # Clean up
    if Path("demo_config.json").exists():
        Path("demo_config.json").unlink()


if __name__ == "__main__":
    asyncio.run(demo_multi_account())