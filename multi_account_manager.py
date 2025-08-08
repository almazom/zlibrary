#!/usr/bin/env python3
"""
Multi-Account Manager with Rate Limit Handling and Telegram Notifications
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zlibrary.account_pool import AccountPool, SmartDownloader
from zlibrary import AsyncZlib, Extension, Language

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram (placeholder for now)"""
    
    @staticmethod
    async def send_message(message: str):
        """Send message to Telegram"""
        # TODO: Integrate with actual Telegram bot
        logger.info(f"📱 TELEGRAM: {message}")
        
        # For now, also save to a log file
        log_file = Path("notifications.log")
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")


class MultiAccountManager:
    """
    Manager for multiple Z-Library accounts with intelligent rotation
    """
    
    def __init__(self, config_file: str = "accounts_config.json"):
        self.pool = AccountPool(config_file)
        self.notifier = TelegramNotifier()
        self.stats = {
            'total_searches': 0,
            'total_downloads': 0,
            'total_failures': 0
        }
    
    async def add_accounts_from_env(self):
        """
        Add accounts from environment variables or .env file
        Format: ZLOGIN1, ZPASSW1, ZLOGIN2, ZPASSW2, etc.
        """
        added = 0
        
        # First check for primary account (ZLOGIN/ZPASSW)
        email = os.getenv("ZLOGIN")
        password = os.getenv("ZPASSW")
        if email and password:
            self.pool.add_account(email, password, "Primary account")
            added += 1
            logger.info(f"Added primary account: {email}")
        
        # Then check for numbered accounts (ZLOGIN1, ZLOGIN2, etc.)
        for i in range(1, 100):  # Support up to 99 additional accounts
            email = os.getenv(f"ZLOGIN{i}")
            password = os.getenv(f"ZPASSW{i}")
            
            if email and password:
                self.pool.add_account(email, password, f"Account {i}")
                added += 1
                logger.info(f"Added account {i}: {email}")
            else:
                # Stop when we find a gap in numbering
                break
        
        if added > 0:
            await self.notifier.send_message(f"✅ Added {added} accounts to pool")
        
        return added
    
    async def add_accounts_from_file(self, file_path: str):
        """
        Add accounts from a file (one account per line: email:password)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return 0
        
        added = 0
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    email, password = line.split(':', 1)
                    self.pool.add_account(email.strip(), password.strip(), f"From {file_path.name}")
                    added += 1
        
        if added > 0:
            await self.notifier.send_message(f"✅ Added {added} accounts from {file_path}")
        
        return added
    
    async def initialize(self):
        """Initialize all accounts and check their status"""
        logger.info("🚀 Initializing account pool...")
        
        results = await self.pool.initialize_all()
        
        # Get statistics
        stats = self.pool.get_statistics()
        
        # Prepare notification message
        message = f"""
🎯 Account Pool Initialized
━━━━━━━━━━━━━━━━━━━━━
Total accounts: {stats['total_accounts']}
Active: {stats['active_accounts']}
Failed: {stats['inactive_accounts']}
━━━━━━━━━━━━━━━━━━━━━
Total daily limit: {stats['total_daily_limit']}
Total remaining: {stats['total_daily_remaining']}
Total used today: {stats['total_daily_used']}
        """
        
        await self.notifier.send_message(message.strip())
        
        # Show individual account status
        for acc in stats['accounts']:
            if acc['active']:
                logger.info(f"✅ {acc['email']}: {acc['remaining']}/{acc['limit']} remaining")
            else:
                logger.warning(f"❌ {acc['email']}: Inactive")
        
        return stats
    
    async def search_with_rotation(self, query: str, max_results: int = 10, 
                                  extension: str = "epub", language: str = "english"):
        """
        Search for books with automatic account rotation
        """
        self.stats['total_searches'] += 1
        
        logger.info(f"🔍 Searching: '{query}' (max: {max_results})")
        
        # Get available client
        client, account = await self.pool.get_available_client()
        
        if not client:
            message = "❌ No accounts available for search!"
            logger.error(message)
            await self.notifier.send_message(message)
            return []
        
        try:
            # Perform search
            ext_enum = getattr(Extension, extension.upper(), Extension.EPUB)
            lang_enum = getattr(Language, language.upper(), Language.ENGLISH)
            
            results = await client.search(
                q=query,
                extensions=[ext_enum],
                lang=[lang_enum],
                count=max_results
            )
            
            await results.init()
            
            logger.info(f"📚 Found {results.total} pages of results")
            
            # Return book list
            return results.result
            
        except Exception as e:
            error_msg = f"Search failed: {e}"
            logger.error(error_msg)
            await self.notifier.send_message(f"❌ {error_msg}")
            return []
    
    async def download_with_rotation(self, books, output_dir: str = "downloads"):
        """
        Download books with automatic account rotation when limits are reached
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = []
        downloaded = 0
        failed = 0
        
        for i, book in enumerate(books, 1):
            # Get available account
            client, account = await self.pool.get_available_client()
            
            if not client:
                # No more accounts available
                message = f"⚠️ Download stopped at {i}/{len(books)} - No accounts with quota remaining"
                logger.warning(message)
                await self.notifier.send_message(message)
                
                # Show when limits will reset
                reset_info = self._get_reset_times()
                await self.notifier.send_message(reset_info)
                break
            
            try:
                # Fetch book details
                logger.info(f"📥 Downloading {i}/{len(books)}: {book.name[:60]}")
                details = await book.fetch()
                
                download_url = details.get('download_url', '')
                
                if download_url and download_url != "No download available":
                    # Success
                    result = {
                        'name': details['name'],
                        'authors': details.get('authors', []),
                        'download_url': download_url,
                        'account_used': account.email,
                        'status': 'success'
                    }
                    
                    # Update account usage
                    account.daily_remaining -= 1
                    account.daily_used += 1
                    downloaded += 1
                    self.stats['total_downloads'] += 1
                    
                    logger.info(f"✅ Success using {account.email} ({account.daily_remaining} left)")
                    
                    # Save metadata
                    metadata_file = output_path / f"{book.id}_metadata.json"
                    with open(metadata_file, 'w') as f:
                        json.dump(details, f, indent=2)
                    
                else:
                    # Book not available
                    result = {
                        'name': book.name,
                        'status': 'unavailable',
                        'reason': 'No download URL'
                    }
                    failed += 1
                    logger.warning(f"⚠️ Book unavailable: {book.name[:60]}")
                
                results.append(result)
                
            except Exception as e:
                # Download failed
                failed += 1
                self.stats['total_failures'] += 1
                
                result = {
                    'name': book.name if hasattr(book, 'name') else 'Unknown',
                    'status': 'failed',
                    'error': str(e)
                }
                results.append(result)
                
                logger.error(f"❌ Failed: {e}")
                
                # Check if it's a rate limit error
                if "limit" in str(e).lower():
                    # Mark account as exhausted
                    account.daily_remaining = 0
                    
                    # Try to rotate to next account
                    logger.info("Rotating to next account due to limit...")
                    continue
            
            # Rate limiting between downloads
            if i < len(books):
                await asyncio.sleep(2)
        
        # Send summary notification
        summary = f"""
📊 Download Summary
━━━━━━━━━━━━━━━━━━━━━
Total: {len(books)}
Downloaded: {downloaded}
Failed: {failed}
Remaining: {len(books) - downloaded - failed}
━━━━━━━━━━━━━━━━━━━━━
Accounts used: {len(set(r.get('account_used', '') for r in results if r.get('account_used')))}
        """
        
        await self.notifier.send_message(summary.strip())
        
        # Update pool config
        self.pool.save_config()
        
        return results
    
    def _get_reset_times(self) -> str:
        """Get reset times for all accounts"""
        lines = ["⏰ Account Reset Times:"]
        
        for acc in self.pool.accounts:
            if acc.is_active:
                status = f"{acc.daily_remaining}/{acc.daily_limit} left"
                reset = acc.reset_time or "Unknown"
                lines.append(f"  {acc.email}: {status}, resets in {reset}")
        
        return "\n".join(lines)
    
    async def monitor_limits(self):
        """
        Monitor account limits and send notifications
        """
        while True:
            # Refresh all limits
            await self.pool.refresh_all_limits()
            
            stats = self.pool.get_statistics()
            
            # Check if running low
            if stats['total_daily_remaining'] < 5:
                message = f"⚠️ Low quota warning! Only {stats['total_daily_remaining']} downloads remaining across all accounts"
                await self.notifier.send_message(message)
            
            # Check for exhausted accounts
            exhausted = [acc for acc in self.pool.accounts if acc.is_active and acc.daily_remaining == 0]
            if exhausted:
                message = f"💤 {len(exhausted)} accounts exhausted. Will reset in: {exhausted[0].reset_time if exhausted else 'Unknown'}"
                await self.notifier.send_message(message)
            
            # Wait before next check (5 minutes)
            await asyncio.sleep(300)
    
    async def cleanup(self):
        """Cleanup all connections"""
        await self.pool.cleanup()
        logger.info("👋 Cleanup complete")


async def main():
    """Main function demonstrating multi-account usage"""
    
    manager = MultiAccountManager()
    
    # Add accounts from environment or file
    print("🔑 Setting up accounts...")
    
    # Method 1: From environment variables
    added = await manager.add_accounts_from_env()
    
    # Method 2: From file (create accounts.txt with email:password per line)
    accounts_file = Path("accounts.txt")
    if accounts_file.exists():
        added += await manager.add_accounts_from_file("accounts.txt")
    
    if added == 0:
        print("❌ No accounts configured!")
        print("\nTo add accounts, use one of these methods:")
        print("1. Set environment variables: ZLOGIN1, ZPASSW1, ZLOGIN2, ZPASSW2, etc.")
        print("2. Create accounts.txt with email:password per line")
        return
    
    # Initialize all accounts
    stats = await manager.initialize()
    
    if stats['active_accounts'] == 0:
        print("❌ No active accounts available!")
        return
    
    print(f"\n✅ Ready with {stats['active_accounts']} active accounts")
    print(f"📊 Total daily limit: {stats['total_daily_limit']}")
    print(f"📊 Total remaining: {stats['total_daily_remaining']}")
    
    # Example: Search and download
    print("\n📚 Searching for books...")
    books = await manager.search_with_rotation(
        query="Python machine learning",
        max_results=15,
        extension="epub",
        language="english"
    )
    
    if books:
        print(f"Found {len(books)} books")
        
        # Download with automatic rotation
        print("\n⬇️ Starting downloads with account rotation...")
        results = await manager.download_with_rotation(books, "downloads/multi_account")
        
        # Show results
        print("\n📋 Download Results:")
        for r in results:
            if r['status'] == 'success':
                print(f"  ✅ {r['name'][:60]} - Account: {r['account_used']}")
            elif r['status'] == 'unavailable':
                print(f"  ⚠️ {r['name'][:60]} - Unavailable")
            else:
                print(f"  ❌ {r['name'][:60]} - Failed: {r.get('error', 'Unknown')}")
    
    # Cleanup
    await manager.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()