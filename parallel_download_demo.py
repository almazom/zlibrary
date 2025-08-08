#!/usr/bin/env python3
"""
Parallel Download Demo with Account Switching
Shows concurrent downloads across multiple Z-Library accounts
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib, Extension, Language

class ParallelDownloadManager:
    """Download books in parallel across multiple accounts"""
    
    def __init__(self):
        # Load account credentials from .env
        self.accounts = [
            (os.getenv("ZLOGIN"), os.getenv("ZPASSW"), "Account-1"),
            (os.getenv("ZLOGIN1"), os.getenv("ZPASSW1"), "Account-2"), 
            (os.getenv("ZLOGIN2"), os.getenv("ZPASSW2"), "Account-3"),
        ]
        
        # Filter out None accounts
        self.accounts = [(e, p, n) for e, p, n in self.accounts if e and p]
        print(f"📋 Found {len(self.accounts)} accounts")
        
        self.clients = {}
        self.account_limits = {}
    
    async def initialize_accounts(self):
        """Login to all accounts and check limits"""
        print("\n🔑 Initializing accounts...")
        
        successful = 0
        for email, password, name in self.accounts:
            try:
                client = AsyncZlib()
                profile = await client.login(email, password)
                limits = await profile.get_limits()
                
                self.clients[email] = client
                self.account_limits[email] = {
                    'name': name,
                    'remaining': limits['daily_remaining'],
                    'limit': limits['daily_allowed'],
                    'used': limits['daily_amount'],
                    'reset': limits['daily_reset']
                }
                
                successful += 1
                print(f"✅ {name} ({email}): {limits['daily_remaining']}/{limits['daily_allowed']} downloads")
                
            except Exception as e:
                print(f"❌ {name} ({email}): {e}")
        
        print(f"\n🎯 {successful}/{len(self.accounts)} accounts ready")
        return successful > 0
    
    async def search_books(self, query: str, max_results: int = 20):
        """Search for books using first available account"""
        print(f"\n🔍 Searching: '{query}'...")
        
        # Use first available account for search
        for email, client in self.clients.items():
            try:
                results = await client.search(
                    q=query,
                    extensions=[Extension.EPUB, Extension.PDF],
                    lang=[Language.ENGLISH],
                    count=max_results
                )
                
                await results.init()
                books = results.result
                print(f"📚 Found {len(books)} books")
                return books
                
            except Exception as e:
                print(f"❌ Search failed with {email}: {e}")
                continue
        
        print("❌ All search attempts failed")
        return []
    
    async def download_single_book(self, book, account_email, semaphore):
        """Download a single book using specific account"""
        async with semaphore:  # Limit concurrent downloads
            try:
                client = self.clients[account_email]
                account_info = self.account_limits[account_email]
                
                # Check if account has quota
                if account_info['remaining'] <= 0:
                    return {
                        'book': book.name,
                        'account': account_info['name'],
                        'status': 'quota_exhausted',
                        'error': 'No downloads remaining'
                    }
                
                # Fetch book details
                details = await book.fetch()
                download_url = details.get('download_url', '')
                
                # Update account usage
                account_info['remaining'] -= 1
                account_info['used'] += 1
                
                if download_url and download_url != "No download available":
                    # Save metadata
                    metadata = {
                        'name': details['name'],
                        'authors': details.get('authors', []),
                        'size': details.get('size'),
                        'year': details.get('year'),
                        'language': details.get('language'),
                        'download_url': download_url,
                        'downloaded_at': datetime.now().isoformat(),
                        'account_used': account_info['name']
                    }
                    
                    # Save to file  
                    safe_name = "".join(c for c in details['name'][:50] if c.isalnum() or c in (' ', '-', '_')).strip()
                    book_id = book.get('id', f"book_{hash(book.get('name', 'unknown'))}")
                    filename = f"downloads/{safe_name}_{book_id}.json"
                    Path("downloads").mkdir(exist_ok=True)
                    
                    with open(filename, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    return {
                        'book': details['name'],
                        'account': account_info['name'],
                        'status': 'success',
                        'size': details.get('size'),
                        'file': filename,
                        'remaining': account_info['remaining']
                    }
                else:
                    return {
                        'book': book.name,
                        'account': account_info['name'],
                        'status': 'unavailable',
                        'error': 'No download URL available'
                    }
                    
            except Exception as e:
                return {
                    'book': book.name if hasattr(book, 'name') else 'Unknown',
                    'account': account_info['name'] if account_email in self.account_limits else 'Unknown',
                    'status': 'failed',
                    'error': str(e)
                }
    
    async def parallel_download(self, books, max_concurrent=3):
        """Download books in parallel with smart account distribution"""
        print(f"\n⬇️ Starting parallel downloads ({max_concurrent} concurrent)...")
        
        # Create semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Distribute books across available accounts
        available_accounts = [
            email for email, limits in self.account_limits.items() 
            if limits['remaining'] > 0
        ]
        
        if not available_accounts:
            print("❌ No accounts with available quota!")
            return []
        
        print(f"🎯 Using {len(available_accounts)} accounts with quota")
        
        # Create download tasks
        tasks = []
        for i, book in enumerate(books):
            # Round-robin account selection
            account_email = available_accounts[i % len(available_accounts)]
            
            task = self.download_single_book(book, account_email, semaphore)
            tasks.append(task)
        
        # Execute all downloads in parallel
        print(f"🚀 Launching {len(tasks)} download tasks...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        success_count = 0
        failed_count = 0
        unavailable_count = 0
        quota_exhausted_count = 0
        
        print(f"\n📊 Download Results:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"{i:2d}. ❌ Exception: {result}")
                failed_count += 1
            else:
                status = result['status']
                book_name = result['book'][:60]
                account = result['account']
                
                if status == 'success':
                    remaining = result['remaining']
                    size = result.get('size', 'Unknown')
                    print(f"{i:2d}. ✅ {book_name} | {account} ({remaining} left) | {size}")
                    success_count += 1
                elif status == 'unavailable':
                    print(f"{i:2d}. ⚠️  {book_name} | {account} | Not available")
                    unavailable_count += 1
                elif status == 'quota_exhausted':
                    print(f"{i:2d}. 💤 {book_name} | {account} | Quota exhausted")
                    quota_exhausted_count += 1
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"{i:2d}. ❌ {book_name} | {account} | {error}")
                    failed_count += 1
        
        print("=" * 80)
        print(f"📈 Summary: {success_count} success, {unavailable_count} unavailable, {failed_count} failed, {quota_exhausted_count} quota exhausted")
        
        # Show remaining quotas
        print(f"\n💾 Remaining Quotas:")
        for email, limits in self.account_limits.items():
            print(f"   {limits['name']}: {limits['remaining']}/{limits['limit']} downloads")
        
        return results
    
    async def cleanup(self):
        """Logout from all accounts"""
        print("\n👋 Cleaning up...")
        for client in self.clients.values():
            try:
                await client.logout()
            except:
                pass

async def main():
    """Demo the parallel download system"""
    print("🚀 Z-Library Parallel Download Demo")
    print("=" * 50)
    
    manager = ParallelDownloadManager()
    
    # Initialize accounts
    if not await manager.initialize_accounts():
        print("❌ No accounts available!")
        return
    
    # Search for books
    query = "Python programming machine learning"
    books = await manager.search_books(query, max_results=15)
    
    if not books:
        print("❌ No books found!")
        return
    
    # Download in parallel
    results = await manager.parallel_download(books, max_concurrent=5)
    
    # Cleanup
    await manager.cleanup()
    
    print(f"\n🎯 Demo complete! Check the 'downloads/' folder for results.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()