#!/usr/bin/env python3
"""
Test Account Switching Strategy on Exhaustion
Tests with 20 books from Podpisnie.ru
"""

import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib

# Books from Podpisnie.ru
BOOKS_TO_TEST = [
    "Семейный лексикон",
    "Ирландские сказки и легенды", 
    "Из ничего искусство создавать искусство",
    "Развод",
    "Курс Разговоры со студентами",
    "Семь лет в Крестах",
    "Кадавры",
    "Полторы комнаты",
    "Невыносимая легкость бытия Кундера",
    "The Book Как создать цивилизацию заново",
    "Мир образов Образы мира",
    "Тайна Моря",
    "История одного немца",
    "Лисьи Броды",
    "Дочь самурая",
    "Другой дом",
    "Истории книжных магазинов",
    "Роза",
    "У Плыли-Две-Птицы",
    "Любовь в эпоху ненависти"
]

async def test_account_switching():
    """Test account switching on exhaustion"""
    
    accounts = [
        ('almazomam@gmail.com', 'tataronrails78'),
        ('almazomam2@gmail.com', 'tataronrails78'),
        ('almazomam3@gmail.com', 'tataronrails78')
    ]
    
    print("=== ACCOUNT SWITCHING TEST ===")
    print(f"Testing {len(BOOKS_TO_TEST)} books from Podpisnie.ru")
    print(f"Accounts available: {len(accounts)}")
    print("-" * 50)
    
    results = {
        'books_tested': 0,
        'books_found': 0,
        'account_switches': 0,
        'current_account': 0,
        'account_usage': {0: 0, 1: 0, 2: 0},
        'exhausted_accounts': []
    }
    
    for book_num, book_query in enumerate(BOOKS_TO_TEST, 1):
        print(f"\n[{book_num}/{len(BOOKS_TO_TEST)}] Searching: {book_query}")
        
        book_found = False
        
        # Try each account until one works
        for acc_index, (email, password) in enumerate(accounts):
            if acc_index in results['exhausted_accounts']:
                print(f"  ⏭️  Account {acc_index+1} already exhausted, skipping")
                continue
                
            try:
                print(f"  🔄 Trying account {acc_index+1}: {email.split('@')[0]}@...")
                
                client = AsyncZlib()
                profile = await client.login(email, password)
                limits = await profile.get_limits()
                
                remaining = limits.get('daily_remaining', 0)
                print(f"     Downloads remaining: {remaining}")
                
                if remaining > 0:
                    # Account switch if different from current
                    if acc_index != results['current_account']:
                        results['account_switches'] += 1
                        print(f"  ⚡ ACCOUNT SWITCH: #{results['current_account']+1} → #{acc_index+1}")
                        results['current_account'] = acc_index
                    
                    # Search for book
                    search_results = await client.search(
                        q=book_query,
                        extensions=['epub'],
                        count=1
                    )
                    
                    await search_results.init()
                    
                    if search_results.result:
                        book = search_results.result[0]
                        book_info = await book.fetch()
                        title = book_info.get('name', 'Unknown')
                        
                        print(f"  ✅ FOUND: {title[:50]}...")
                        results['books_found'] += 1
                        results['account_usage'][acc_index] += 1
                        book_found = True
                        
                        # Check if account now exhausted
                        new_limits = await profile.get_limits()
                        if new_limits.get('daily_remaining', 0) == 0:
                            print(f"  ⚠️  Account {acc_index+1} now EXHAUSTED")
                            results['exhausted_accounts'].append(acc_index)
                        
                        break
                    else:
                        print(f"  ❌ Book not found in Z-Library")
                        break
                        
                else:
                    print(f"  ❌ Account exhausted (0 downloads)")
                    if acc_index not in results['exhausted_accounts']:
                        results['exhausted_accounts'].append(acc_index)
                    continue
                    
            except Exception as e:
                print(f"  ❌ Account error: {str(e)[:50]}")
                if acc_index not in results['exhausted_accounts']:
                    results['exhausted_accounts'].append(acc_index)
                continue
            
            finally:
                try:
                    await client.logout()
                except:
                    pass
        
        results['books_tested'] += 1
        
        if not book_found:
            print(f"  ⛔ Could not find book with any account")
        
        # Stop if all accounts exhausted
        if len(results['exhausted_accounts']) == len(accounts):
            print("\n🛑 ALL ACCOUNTS EXHAUSTED - Stopping test")
            break
    
    # Print final report
    print("\n" + "=" * 50)
    print("FINAL ACCOUNT SWITCHING REPORT")
    print("=" * 50)
    print(f"Books tested: {results['books_tested']}/{len(BOOKS_TO_TEST)}")
    print(f"Books found: {results['books_found']}")
    print(f"Account switches: {results['account_switches']}")
    print(f"Exhausted accounts: {len(results['exhausted_accounts'])}/{len(accounts)}")
    print("\nAccount usage breakdown:")
    for acc_id, usage in results['account_usage'].items():
        status = "EXHAUSTED" if acc_id in results['exhausted_accounts'] else "ACTIVE"
        print(f"  Account {acc_id+1}: {usage} downloads [{status}]")
    
    # Success criteria
    print("\n✅ SUCCESS CRITERIA:")
    print(f"  1. Account switching works: {'YES' if results['account_switches'] > 0 else 'NO'}")
    print(f"  2. Fallback on exhaustion: {'YES' if results['account_switches'] > 0 else 'UNTESTED'}")
    print(f"  3. Multiple accounts used: {'YES' if sum(1 for u in results['account_usage'].values() if u > 0) > 1 else 'NO'}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_account_switching())