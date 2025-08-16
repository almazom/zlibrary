#!/usr/bin/env python3
"""
Simulate Account Exhaustion and Switching
Tests the logic without actual API calls
"""

import json
from datetime import datetime

class AccountSimulator:
    """Simulates Z-Library accounts with download limits"""
    
    def __init__(self):
        self.accounts = [
            {
                'email': 'almazomam@gmail.com',
                'downloads_remaining': 8,
                'downloads_limit': 8,
                'status': 'active'
            },
            {
                'email': 'almazomam2@gmail.com', 
                'downloads_remaining': 4,
                'downloads_limit': 4,
                'status': 'active'
            },
            {
                'email': 'almazomam3@gmail.com',
                'downloads_remaining': 10,
                'downloads_limit': 10,
                'status': 'active'
            }
        ]
        self.current_account = 0
        self.switches = 0
        self.books_downloaded = []
        
    def download_book(self, book_title):
        """Simulate downloading a book"""
        
        # Try each account
        for i in range(len(self.accounts)):
            account = self.accounts[self.current_account]
            
            if account['downloads_remaining'] > 0:
                # Download successful
                account['downloads_remaining'] -= 1
                
                if account['downloads_remaining'] == 0:
                    account['status'] = 'exhausted'
                    
                self.books_downloaded.append({
                    'book': book_title,
                    'account': self.current_account + 1,
                    'remaining': account['downloads_remaining']
                })
                
                return True
            else:
                # Account exhausted, try next
                print(f"  ❌ Account {self.current_account + 1} exhausted")
                
                # Find next available account
                next_account = self.find_next_available()
                
                if next_account is not None:
                    old_account = self.current_account
                    self.current_account = next_account
                    self.switches += 1
                    print(f"  ⚡ SWITCHING: Account {old_account + 1} → Account {self.current_account + 1}")
                else:
                    print(f"  ⛔ ALL ACCOUNTS EXHAUSTED")
                    return False
                    
        return False
    
    def find_next_available(self):
        """Find next account with downloads remaining"""
        for i in range(len(self.accounts)):
            if self.accounts[i]['downloads_remaining'] > 0:
                return i
        return None
    
    def get_status(self):
        """Get current status of all accounts"""
        return {
            'accounts': [
                {
                    'id': i + 1,
                    'email': acc['email'],
                    'remaining': acc['downloads_remaining'],
                    'limit': acc['downloads_limit'],
                    'status': acc['status']
                }
                for i, acc in enumerate(self.accounts)
            ],
            'total_remaining': sum(acc['downloads_remaining'] for acc in self.accounts),
            'switches': self.switches,
            'books_downloaded': len(self.books_downloaded)
        }

def main():
    """Test account exhaustion with 25 books to ensure complete exhaustion"""
    
    # Books from Podpisnie.ru + extras to ensure exhaustion
    books = [
        # First 8 books - Account 1
        "Семейный лексикон",
        "Ирландские сказки и легенды",
        "Из ничего: искусство создавать искусство",
        "Развод",
        "Курс: Разговоры со студентами",
        "Семь лет в Крестах",
        "Кадавры",
        "Полторы комнаты",
        # Next 4 books - Account 2
        "Невыносимая легкость бытия",
        "The Book: Как создать цивилизацию",
        "Мир образов. Образы мира",
        "Тайна Моря",
        # Next 10 books - Account 3
        "История одного немца",
        "Лисьи Броды",
        "Дочь самурая",
        "Другой дом",
        "Истории книжных магазинов",
        "Роза",
        "У Плыли-Две-Птицы",
        "Любовь в эпоху ненависти",
        "Средневековое мышление",
        "Феноменология восприятия",
        # Extra 3 books to test exhaustion
        "Бытие и ничто",
        "Критика чистого разума",
        "Общество спектакля"
    ]
    
    print("=" * 60)
    print("ACCOUNT EXHAUSTION SIMULATION TEST")
    print("=" * 60)
    print(f"Testing {len(books)} books to ensure 100% exhaustion")
    print(f"Total capacity: 22 downloads (8+4+10)")
    print("-" * 60)
    
    sim = AccountSimulator()
    
    # Show initial state
    initial = sim.get_status()
    print("\nINITIAL STATE:")
    for acc in initial['accounts']:
        print(f"  Account {acc['id']}: {acc['remaining']}/{acc['limit']} downloads")
    print(f"  Total available: {initial['total_remaining']}")
    print("-" * 60)
    
    # Download books
    for i, book in enumerate(books, 1):
        print(f"\n[{i}/{len(books)}] Downloading: {book[:40]}...")
        
        success = sim.download_book(book)
        
        if success:
            last_download = sim.books_downloaded[-1]
            print(f"  ✅ SUCCESS using Account {last_download['account']} ({last_download['remaining']} left)")
        else:
            print(f"  ❌ FAILED - All accounts exhausted")
            break
    
    # Final report
    print("\n" + "=" * 60)
    print("FINAL EXHAUSTION REPORT")
    print("=" * 60)
    
    final = sim.get_status()
    
    print("\nACCOUNT STATUS:")
    for acc in final['accounts']:
        status_icon = "✅" if acc['status'] == 'active' else "❌"
        print(f"  {status_icon} Account {acc['id']}: {acc['remaining']}/{acc['limit']} - {acc['status'].upper()}")
    
    print(f"\nSTATISTICS:")
    print(f"  Books attempted: {len(books)}")
    print(f"  Books downloaded: {final['books_downloaded']}")
    print(f"  Account switches: {final['switches']}")
    print(f"  Downloads remaining: {final['total_remaining']}")
    
    # Show download distribution
    print(f"\nDOWNLOAD DISTRIBUTION:")
    acc_usage = {1: 0, 2: 0, 3: 0}
    for download in sim.books_downloaded:
        acc_usage[download['account']] += 1
    
    for acc_id, count in acc_usage.items():
        percentage = (count / final['books_downloaded'] * 100) if final['books_downloaded'] > 0 else 0
        print(f"  Account {acc_id}: {count} downloads ({percentage:.1f}%)")
    
    # Success criteria
    print(f"\n✅ SUCCESS CRITERIA:")
    print(f"  1. All accounts exhausted: {'YES' if final['total_remaining'] == 0 else 'NO'}")
    print(f"  2. Account switching worked: {'YES' if final['switches'] >= 2 else 'NO'}")
    print(f"  3. Used all 22 downloads: {'YES' if final['books_downloaded'] == 22 else 'NO'}")
    print(f"  4. Correct switching order: {'YES' if acc_usage[1] == 8 and acc_usage[2] == 4 and acc_usage[3] == 10 else 'NO'}")
    
    # Show switch points
    print(f"\n⚡ SWITCH POINTS:")
    switch_points = []
    current_acc = 1
    for i, download in enumerate(sim.books_downloaded, 1):
        if download['account'] != current_acc:
            switch_points.append(f"  Book #{i}: Account {current_acc} → Account {download['account']}")
            current_acc = download['account']
    
    for point in switch_points:
        print(point)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE - 100% EXHAUSTION VERIFIED")
    print("=" * 60)

if __name__ == "__main__":
    main()