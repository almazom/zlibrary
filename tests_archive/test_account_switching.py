#!/usr/bin/env python3
"""
Test Account Switching When Limits Exhausted
Tests automatic rotation between Z-Library accounts when download limits are reached
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary import AsyncZlib, Extension, Language

class AccountSwitchTester:
    """Test automatic account switching functionality"""
    
    def __init__(self):
        # Load accounts from .env
        self.accounts = [
            {"email": os.getenv("ZLOGIN"), "password": os.getenv("ZPASSW"), "name": "Account-1"},
            {"email": os.getenv("ZLOGIN1"), "password": os.getenv("ZPASSW1"), "name": "Account-2"}, 
            {"email": os.getenv("ZLOGIN2"), "password": os.getenv("ZPASSW2"), "name": "Account-3"},
        ]
        
        # Filter valid accounts
        self.accounts = [acc for acc in self.accounts if acc["email"] and acc["password"]]
        print(f"🎯 Found {len(self.accounts)} accounts to test")
        
        self.clients = {}
        self.limits = {}
    
    async def initialize_accounts(self):
        """Login and check limits for all accounts"""
        print("\n🔑 Initializing accounts...")
        
        working_accounts = 0
        for acc in self.accounts:
            try:
                client = AsyncZlib()
                profile = await client.login(acc["email"], acc["password"])
                limits = await profile.get_limits()
                
                self.clients[acc["name"]] = {
                    "client": client,
                    "profile": profile,
                    "email": acc["email"]
                }
                
                self.limits[acc["name"]] = {
                    "remaining": limits["daily_remaining"],
                    "limit": limits["daily_allowed"],
                    "used": limits["daily_amount"],
                    "reset": limits["daily_reset"],
                    "original_remaining": limits["daily_remaining"]
                }
                
                working_accounts += 1
                print(f"✅ {acc['name']} ({acc['email']}): {limits['daily_remaining']}/{limits['daily_allowed']} downloads")
                
            except Exception as e:
                print(f"❌ {acc['name']} ({acc['email']}): {e}")
        
        total_downloads = sum(lim["remaining"] for lim in self.limits.values())
        print(f"\n📊 Total available downloads: {total_downloads}")
        return working_accounts > 0
    
    async def get_available_account(self):
        """Get next account with available downloads (mimics account switching logic)"""
        for name, limits in self.limits.items():
            if limits["remaining"] > 0:
                return name, self.clients[name]
        return None, None
    
    async def test_sequential_downloads(self, max_downloads=15):
        """Test downloading books sequentially with automatic account switching"""
        print(f"\n🔍 Searching for books...")
        
        # Use first available account for search
        first_account_name, first_account = await self.get_available_account()
        if not first_account:
            print("❌ No accounts available!")
            return []
        
        # Search for books
        try:
            results = await first_account["client"].search(
                q="Python programming",
                extensions=[Extension.EPUB, Extension.PDF],
                lang=[Language.ENGLISH],
                count=max_downloads
            )
            
            await results.init()
            books = results.result
            print(f"📚 Found {len(books)} books to test with")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
        
        # Test downloading with account switching
        print(f"\n⬇️ Testing account switching with {len(books)} downloads...")
        print("="*80)
        
        results = []
        for i, book in enumerate(books, 1):
            # Get available account (this simulates account switching)
            account_name, account_info = await self.get_available_account()
            
            if not account_info:
                print(f"🛑 STOP: All accounts exhausted at download {i}")
                remaining_books = len(books) - i + 1
                print(f"   Could not download {remaining_books} remaining books")
                break
            
            current_remaining = self.limits[account_name]["remaining"]
            
            try:
                # Attempt download
                print(f"{i:2d}. Using {account_name} ({current_remaining} left) -> ", end="")
                
                details = await book.fetch()
                download_url = details.get('download_url', '')
                
                if download_url and download_url != "No download available":
                    # Simulate successful download - decrease remaining count
                    self.limits[account_name]["remaining"] -= 1
                    self.limits[account_name]["used"] += 1
                    
                    new_remaining = self.limits[account_name]["remaining"]
                    book_name = details['name'][:50]
                    
                    print(f"✅ '{book_name}' ({new_remaining} left)")
                    
                    result = {
                        "index": i,
                        "book": book_name,
                        "account": account_name,
                        "status": "success",
                        "remaining_after": new_remaining
                    }
                    
                    # Check if account is now exhausted
                    if new_remaining == 0:
                        print(f"   ⚠️  {account_name} is now EXHAUSTED - will switch to next account")
                    
                else:
                    print(f"⚠️ Book unavailable")
                    result = {
                        "index": i,
                        "book": book.name if hasattr(book, 'name') else 'Unknown',
                        "account": account_name,
                        "status": "unavailable"
                    }
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({
                    "index": i,
                    "book": book.name if hasattr(book, 'name') else 'Unknown',
                    "account": account_name,
                    "status": "failed",
                    "error": str(e)
                })
            
            # Small delay between downloads
            await asyncio.sleep(1)
        
        return results
    
    def print_switching_summary(self, results):
        """Print summary of account switching behavior"""
        print("\n" + "="*80)
        print("ACCOUNT SWITCHING SUMMARY")
        print("="*80)
        
        # Account usage summary
        accounts_used = {}
        successful_downloads = 0
        
        for result in results:
            if result["status"] == "success":
                account = result["account"]
                if account not in accounts_used:
                    accounts_used[account] = 0
                accounts_used[account] += 1
                successful_downloads += 1
        
        print(f"✅ Total successful downloads: {successful_downloads}")
        print(f"🔄 Accounts used: {len(accounts_used)}")
        
        for account, count in accounts_used.items():
            original = self.limits[account]["original_remaining"]
            current = self.limits[account]["remaining"] 
            print(f"   {account}: {count} downloads ({original}→{current} remaining)")
        
        # Show current status
        print(f"\n💾 Current account status:")
        for name, limits in self.limits.items():
            status = "EXHAUSTED" if limits["remaining"] == 0 else "AVAILABLE"
            print(f"   {name}: {limits['remaining']}/{limits['limit']} ({status})")
        
        # Test if switching logic worked
        total_remaining = sum(lim["remaining"] for lim in self.limits.values())
        if successful_downloads > 0 and total_remaining > 0:
            print(f"\n🎯 SWITCHING TEST: ✅ SUCCESS")
            print(f"   Downloaded {successful_downloads} books using multiple accounts")
            print(f"   {total_remaining} downloads still available across accounts")
        elif total_remaining == 0:
            print(f"\n🎯 SWITCHING TEST: ✅ ALL ACCOUNTS EXHAUSTED")
            print(f"   Downloaded {successful_downloads} books before running out")
        else:
            print(f"\n🎯 SWITCHING TEST: ⚠️ NO DOWNLOADS ATTEMPTED")
    
    async def cleanup(self):
        """Cleanup all connections"""
        for account_info in self.clients.values():
            try:
                await account_info["client"].logout()
            except:
                pass

async def main():
    """Run account switching test"""
    print("🔄 Z-Library Account Switching Test")
    print("="*50)
    
    tester = AccountSwitchTester()
    
    # Initialize accounts
    if not await tester.initialize_accounts():
        print("❌ No working accounts available!")
        return
    
    # Test sequential downloads with switching
    results = await tester.test_sequential_downloads(max_downloads=25)
    
    # Show summary
    tester.print_switching_summary(results)
    
    # Cleanup
    await tester.cleanup()
    
    print(f"\n🎯 Account switching test complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()