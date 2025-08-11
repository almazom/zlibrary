#!/usr/bin/env python3
"""
UC11: Account Exhaustion Simulation
Uses real book titles from Podpisnie.ru and Ad Marginem
"""

import json
from datetime import datetime
from typing import List, Dict, Tuple

class ZLibraryAccountSimulator:
    """Simulates Z-Library multi-account system with exhaustion"""
    
    def __init__(self):
        self.accounts = [
            {
                'id': 1,
                'email': 'almazomam@gmail.com',
                'remaining': 8,
                'limit': 8,
                'status': 'active',
                'books_downloaded': []
            },
            {
                'id': 2,
                'email': 'almazomam2@gmail.com',
                'remaining': 4,
                'limit': 4,
                'status': 'active',
                'books_downloaded': []
            },
            {
                'id': 3,
                'email': 'almazomam3@gmail.com',
                'remaining': 10,
                'limit': 10,
                'status': 'active',
                'books_downloaded': []
            }
        ]
        
        self.current_account_index = 0
        self.total_downloads = 0
        self.switches = []
        self.download_log = []
        
    def find_available_account(self) -> Dict:
        """Find next account with downloads remaining"""
        for i, account in enumerate(self.accounts):
            if account['remaining'] > 0:
                if i != self.current_account_index:
                    # Record switch
                    old_id = self.accounts[self.current_account_index]['id']
                    new_id = account['id']
                    self.switches.append({
                        'from': old_id,
                        'to': new_id,
                        'at_download': self.total_downloads + 1
                    })
                    self.current_account_index = i
                    print(f"  ⚡ SWITCH: Account {old_id} → Account {new_id}")
                return account
        return None
    
    def download_book(self, book_title: str) -> Dict:
        """Simulate downloading a book"""
        account = self.find_available_account()
        
        if not account:
            return {
                'status': 'error',
                'message': 'No working accounts found',
                'book': book_title
            }
        
        # Simulate download
        account['remaining'] -= 1
        account['books_downloaded'].append(book_title)
        self.total_downloads += 1
        
        if account['remaining'] == 0:
            account['status'] = 'exhausted'
        
        # Log download
        self.download_log.append({
            'download_num': self.total_downloads,
            'book': book_title,
            'account_id': account['id'],
            'remaining': account['remaining']
        })
        
        return {
            'status': 'success',
            'book': book_title,
            'account_id': account['id'],
            'downloads_remaining': account['remaining']
        }
    
    def get_summary(self) -> Dict:
        """Get test summary"""
        return {
            'total_downloads': self.total_downloads,
            'switches': len(self.switches),
            'accounts': [
                {
                    'id': acc['id'],
                    'used': acc['limit'] - acc['remaining'],
                    'limit': acc['limit'],
                    'status': acc['status'],
                    'books': len(acc['books_downloaded'])
                }
                for acc in self.accounts
            ]
        }

def main():
    """Run UC11 exhaustion test with real books"""
    
    # Real books from Podpisnie.ru and Ad Marginem
    books = [
        # Batch 1: Podpisnie.ru (8 books for Account 1)
        "Семейный лексикон",
        "Ирландские сказки и легенды",
        "Из ничего: искусство создавать искусство",
        "Развод",
        "Курс: Разговоры со студентами",
        "Семь лет в Крестах",
        "Кадавры",
        "Полторы комнаты",
        
        # Batch 2: Philosophy (4 books for Account 2)
        "Невыносимая легкость бытия - Кундера",
        "Средневековое мышление - Ален де Либера",
        "Феноменология восприятия - Мерло-Понти",
        "Бытие и ничто - Сартр",
        
        # Batch 3: More books (10 books for Account 3)
        "Общество спектакля - Ги Дебор",
        "Симулякры и симуляция - Бодрийяр",
        "Капитализм и шизофрения - Делез",
        "Археология знания - Фуко",
        "Различие и повторение - Делез",
        "Логика смысла - Делез",
        "Надзирать и наказывать - Фуко",
        "История сексуальности - Фуко",
        "Чистый код - Роберт Мартин",
        "Прагматичный программист",
        
        # Overflow to test exhaustion
        "Улисс - Джойс",
        "Процесс - Кафка",
        "Замок - Кафка"
    ]
    
    print("=" * 70)
    print("UC11: ACCOUNT EXHAUSTION SIMULATION")
    print("=" * 70)
    print(f"Testing with {len(books)} real books from Podpisnie.ru & Ad Marginem")
    print(f"Expected: 22 successful downloads, 2 account switches")
    print("-" * 70)
    
    sim = ZLibraryAccountSimulator()
    
    # Show initial state
    print("\nINITIAL STATE:")
    for acc in sim.accounts:
        print(f"  Account {acc['id']}: {acc['remaining']}/{acc['limit']} downloads")
    print(f"  Total capacity: 22 downloads")
    print("-" * 70)
    
    # Test each book
    successful_downloads = []
    failed_downloads = []
    
    for i, book in enumerate(books, 1):
        print(f"\n[{i}/{len(books)}] {book[:50]}")
        
        result = sim.download_book(book)
        
        if result['status'] == 'success':
            print(f"  ✅ SUCCESS - Account {result['account_id']} ({result['downloads_remaining']} left)")
            successful_downloads.append(book)
        else:
            print(f"  ❌ FAILED - {result['message']}")
            failed_downloads.append(book)
            if "No working accounts" in result['message']:
                print("  ⛔ ALL ACCOUNTS EXHAUSTED")
                break
    
    # Final report
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    
    summary = sim.get_summary()
    
    print("\nACCOUNT STATUS:")
    for acc in summary['accounts']:
        status_icon = "✅" if acc['status'] == 'active' else "❌"
        print(f"  {status_icon} Account {acc['id']}: {acc['used']}/{acc['limit']} used - {acc['status'].upper()}")
    
    print(f"\nSTATISTICS:")
    print(f"  Books tested: {len(books)}")
    print(f"  Successful downloads: {summary['total_downloads']}")
    print(f"  Failed downloads: {len(failed_downloads)}")
    print(f"  Account switches: {summary['switches']}")
    
    # Show switch points
    if sim.switches:
        print(f"\n⚡ SWITCH POINTS:")
        for switch in sim.switches:
            print(f"  Download #{switch['at_download']}: Account {switch['from']} → Account {switch['to']}")
    
    # Distribution
    print(f"\nDOWNLOAD DISTRIBUTION:")
    for acc in summary['accounts']:
        if acc['books'] > 0:
            percentage = (acc['books'] / summary['total_downloads'] * 100)
            print(f"  Account {acc['id']}: {acc['books']} books ({percentage:.1f}%)")
    
    # Success criteria
    print(f"\n✅ SUCCESS CRITERIA:")
    criteria = {
        "All 22 downloads used": summary['total_downloads'] == 22,
        "2 account switches": summary['switches'] == 2,
        "Account 1 used 8 times": summary['accounts'][0]['used'] == 8,
        "Account 2 used 4 times": summary['accounts'][1]['used'] == 4,
        "Account 3 used 10 times": summary['accounts'][2]['used'] == 10,
        "All accounts exhausted": all(acc['status'] == 'exhausted' for acc in summary['accounts'])
    }
    
    all_passed = True
    for criterion, passed in criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {criterion}")
        if not passed:
            all_passed = False
    
    # Overall result
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ UC11 TEST PASSED: Account exhaustion and switching work correctly")
    else:
        print("❌ UC11 TEST FAILED: Check implementation")
    print("=" * 70)

if __name__ == "__main__":
    main()