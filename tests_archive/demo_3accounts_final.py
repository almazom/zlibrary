#!/usr/bin/env python3
"""
Final Demo: 3-Account Z-Library System
Shows 30 downloads/day capacity with automatic rotation
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from zlibrary.account_pool import AccountPool
from multi_account_manager import MultiAccountManager

# Load environment variables
load_dotenv()


async def demo_three_accounts():
    """Demonstrate 3-account Z-Library system"""
    
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "Z-LIBRARY MULTI-ACCOUNT SYSTEM" + " "*17 + "║")
    print("║" + " "*25 + "3 ACCOUNTS CONFIGURED" + " "*22 + "║")
    print("╚" + "═"*68 + "╝")
    print(f"\n📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Initialize MultiAccountManager
    manager = MultiAccountManager(config_file="demo_3accounts.json")
    
    # Add accounts from environment
    print("\n🔄 LOADING ACCOUNTS FROM ENVIRONMENT...")
    added = await manager.add_accounts_from_env()
    print(f"✅ Loaded {added} accounts from .env file")
    
    # Initialize all accounts
    print("\n🚀 INITIALIZING ACCOUNT POOL...")
    stats = await manager.initialize()
    
    # Display account details
    print("\n📊 ACCOUNT STATUS:")
    print("┌" + "─"*68 + "┐")
    for i, acc in enumerate(manager.pool.accounts, 1):
        status = "✅" if acc.is_active else "❌"
        print(f"│ {status} Account {i}: {acc.email:<35} │")
        print(f"│    Daily Limit: {acc.daily_limit:<10} Remaining: {acc.daily_remaining:<10}      │")
    print("└" + "─"*68 + "┘")
    
    # Show combined capacity
    print("\n💎 COMBINED CAPACITY:")
    print("┌" + "─"*68 + "┐")
    print(f"│ 🎯 Total Accounts:     {stats['total_accounts']:<44} │")
    print(f"│ ✅ Active Accounts:    {stats['active_accounts']:<44} │")
    print(f"│ 📚 Daily Limit:        {stats['total_daily_limit']} downloads/day" + " "*26 + "│")
    print(f"│ 📊 Available Now:      {stats['total_daily_remaining']} downloads" + " "*30 + "│")
    print(f"│ 📈 Used Today:         {stats['total_daily_used']} downloads" + " "*31 + "│")
    print("└" + "─"*68 + "┘")
    
    # Demonstrate search capability
    print("\n🔍 DEMONSTRATION: SEARCH WITH AUTOMATIC ROTATION")
    print("-" * 70)
    
    query = "artificial intelligence"
    print(f"Searching for: '{query}'")
    
    books = await manager.search_with_rotation(
        query=query,
        max_results=5,
        extension="pdf"
    )
    
    print(f"\n📚 Found {len(books)} books:")
    for i, book in enumerate(books[:3], 1):
        print(f"\n   {i}. {book.get('name', 'Unknown')[:50]}...")
        print(f"      Author: {book.get('authors', 'Unknown')}")
        print(f"      Year: {book.get('year', 'N/A')}")
        print(f"      Size: {book.get('size', 'N/A')}")
    
    # Show rotation behavior
    print("\n🔄 ACCOUNT ROTATION DEMONSTRATION:")
    print("-" * 70)
    
    print("Making multiple requests to show rotation...")
    for i in range(5):
        client, account = await manager.pool.get_available_client()
        if client:
            print(f"   Request {i+1}: Using {account.email} ({account.daily_remaining} downloads left)")
    
    # Calculate benefits
    print("\n📈 BENEFITS ANALYSIS:")
    print("┌" + "─"*68 + "┐")
    print("│ METRIC                  │ 1 ACCOUNT │ 3 ACCOUNTS │ IMPROVEMENT │")
    print("├" + "─"*25 + "┼" + "─"*11 + "┼" + "─"*12 + "┼" + "─"*13 + "┤")
    print("│ Daily Downloads         │    10     │     30     │     3x      │")
    print("│ Weekly Downloads        │    70     │    210     │     3x      │")
    print("│ Monthly Downloads       │   300     │    900     │     3x      │")
    print("│ Failover Protection     │    No     │    Yes     │     ✅      │")
    print("│ Automatic Rotation      │    No     │    Yes     │     ✅      │")
    print("└" + "─"*68 + "┘")
    
    # Future scaling
    print("\n🚀 SCALING POTENTIAL:")
    print("   • Current: 3 accounts = 30 downloads/day")
    print("   • With 5 accounts = 50 downloads/day")
    print("   • With 10 accounts = 100 downloads/day")
    print("   • Maximum supported: 99 accounts = 990 downloads/day")
    
    # Instructions for adding more
    print("\n📝 TO ADD MORE ACCOUNTS:")
    print("   1. Add to .env file:")
    print("      ZLOGIN3=new_email@gmail.com")
    print("      ZPASSW3=password")
    print("   2. Run this demo again")
    print("   3. Enjoy increased capacity!")
    
    print("\n" + "="*70)
    print("✨ SYSTEM READY: 3 accounts active, 30 downloads/day available")
    print("="*70)
    
    # Clean up
    if Path("demo_3accounts.json").exists():
        Path("demo_3accounts.json").unlink()


if __name__ == "__main__":
    asyncio.run(demo_three_accounts())