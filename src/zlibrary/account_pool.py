#!/usr/bin/env python3
"""
Multi-Account Pool Manager for Z-Library
Supports unlimited accounts with automatic rotation and limit tracking
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

from .libasync import AsyncZlib
from .exception import LoginFailed, NoProfileError

logger = logging.getLogger(__name__)


@dataclass
class AccountInfo:
    """Single Z-Library account information"""
    email: str
    password: str
    daily_limit: int = 10
    daily_used: int = 0
    daily_remaining: int = 10
    reset_time: Optional[str] = None
    last_used: Optional[str] = None
    is_active: bool = True
    login_failures: int = 0
    notes: str = ""


class AccountPool:
    """
    Manages multiple Z-Library accounts with automatic rotation
    
    Features:
    - Unlimited account support
    - Automatic failover when limits reached
    - Account health monitoring
    - Persistent state storage
    - Round-robin and smart selection strategies
    """
    
    def __init__(self, config_file: str = "accounts_config.json"):
        self.config_file = Path(config_file)
        self.accounts: List[AccountInfo] = []
        self.clients: Dict[str, AsyncZlib] = {}
        self.current_index = 0
        self.total_daily_limit = 0
        self.total_daily_remaining = 0
        
        # Load existing configuration
        self.load_config()
    
    def add_account(self, email: str, password: str, notes: str = "") -> None:
        """
        Add a new account to the pool
        
        Args:
            email: Z-Library account email
            password: Account password
            notes: Optional notes about the account
        """
        # Check if account already exists
        for acc in self.accounts:
            if acc.email == email:
                logger.warning(f"Account {email} already exists")
                return
        
        account = AccountInfo(
            email=email,
            password=password,
            notes=notes
        )
        self.accounts.append(account)
        logger.info(f"Added account: {email} (Total: {len(self.accounts)})")
        self.save_config()
    
    def remove_account(self, email: str) -> bool:
        """Remove an account from the pool"""
        for i, acc in enumerate(self.accounts):
            if acc.email == email:
                self.accounts.pop(i)
                if email in self.clients:
                    del self.clients[email]
                logger.info(f"Removed account: {email}")
                self.save_config()
                return True
        return False
    
    async def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all accounts and check their status
        
        Returns:
            Dict mapping email to success status
        """
        results = {}
        logger.info(f"Initializing {len(self.accounts)} accounts...")
        
        for account in self.accounts:
            try:
                client = AsyncZlib()
                profile = await client.login(account.email, account.password)
                
                # Update account limits
                limits = await profile.get_limits()
                account.daily_limit = limits.get('daily_allowed', 10)
                account.daily_remaining = limits.get('daily_remaining', 0)
                account.daily_used = limits.get('daily_amount', 0)
                account.reset_time = limits.get('daily_reset', '')
                account.is_active = True
                account.login_failures = 0
                account.last_used = datetime.now().isoformat()
                
                self.clients[account.email] = client
                results[account.email] = True
                
                logger.info(f"✅ {account.email}: {account.daily_remaining}/{account.daily_limit} remaining")
                
            except LoginFailed as e:
                account.is_active = False
                account.login_failures += 1
                results[account.email] = False
                logger.error(f"❌ {account.email}: Login failed - {e}")
                
            except Exception as e:
                account.is_active = False
                results[account.email] = False
                logger.error(f"❌ {account.email}: Error - {e}")
        
        # Calculate totals
        self.update_totals()
        self.save_config()
        
        return results
    
    async def get_available_client(self) -> Tuple[Optional[AsyncZlib], Optional[AccountInfo]]:
        """
        Get an available client with remaining downloads
        
        Returns:
            Tuple of (client, account_info) or (None, None) if no available accounts
        """
        # First try accounts with remaining quota
        for account in self.accounts:
            if account.is_active and account.daily_remaining > 0:
                if account.email not in self.clients:
                    # Re-login if needed
                    try:
                        client = AsyncZlib()
                        await client.login(account.email, account.password)
                        self.clients[account.email] = client
                    except:
                        account.is_active = False
                        continue
                
                account.last_used = datetime.now().isoformat()
                logger.info(f"Using account: {account.email} ({account.daily_remaining} remaining)")
                return self.clients[account.email], account
        
        logger.warning("No accounts with available quota")
        return None, None
    
    async def rotate_to_next(self) -> Tuple[Optional[AsyncZlib], Optional[AccountInfo]]:
        """
        Rotate to next available account using round-robin
        
        Returns:
            Tuple of (client, account_info) or (None, None)
        """
        start_index = self.current_index
        
        while True:
            self.current_index = (self.current_index + 1) % len(self.accounts)
            account = self.accounts[self.current_index]
            
            if account.is_active and account.daily_remaining > 0:
                if account.email not in self.clients:
                    try:
                        client = AsyncZlib()
                        await client.login(account.email, account.password)
                        self.clients[account.email] = client
                    except:
                        account.is_active = False
                        continue
                
                account.last_used = datetime.now().isoformat()
                logger.info(f"Rotated to: {account.email} ({account.daily_remaining} remaining)")
                return self.clients[account.email], account
            
            # Completed full rotation without finding available account
            if self.current_index == start_index:
                break
        
        logger.warning("No available accounts after rotation")
        return None, None
    
    async def update_account_limits(self, email: str) -> bool:
        """
        Update limits for a specific account
        
        Args:
            email: Account email to update
            
        Returns:
            True if successful, False otherwise
        """
        for account in self.accounts:
            if account.email == email:
                if email in self.clients:
                    try:
                        profile = await self.clients[email].profile
                        limits = await profile.get_limits()
                        
                        account.daily_limit = limits.get('daily_allowed', 10)
                        account.daily_remaining = limits.get('daily_remaining', 0)
                        account.daily_used = limits.get('daily_amount', 0)
                        account.reset_time = limits.get('daily_reset', '')
                        
                        self.update_totals()
                        self.save_config()
                        return True
                    except:
                        pass
        return False
    
    async def refresh_all_limits(self) -> Dict[str, Dict]:
        """
        Refresh limits for all active accounts
        
        Returns:
            Dict mapping email to limit info
        """
        results = {}
        
        for account in self.accounts:
            if account.is_active and account.email in self.clients:
                try:
                    profile = self.clients[account.email].profile
                    limits = await profile.get_limits()
                    
                    account.daily_limit = limits.get('daily_allowed', 10)
                    account.daily_remaining = limits.get('daily_remaining', 0)
                    account.daily_used = limits.get('daily_amount', 0)
                    account.reset_time = limits.get('daily_reset', '')
                    
                    results[account.email] = {
                        'limit': account.daily_limit,
                        'remaining': account.daily_remaining,
                        'used': account.daily_used,
                        'reset': account.reset_time
                    }
                    
                except Exception as e:
                    results[account.email] = {'error': str(e)}
        
        self.update_totals()
        self.save_config()
        return results
    
    def update_totals(self) -> None:
        """Update total limits across all accounts"""
        self.total_daily_limit = sum(
            acc.daily_limit for acc in self.accounts if acc.is_active
        )
        self.total_daily_remaining = sum(
            acc.daily_remaining for acc in self.accounts if acc.is_active
        )
    
    def get_statistics(self) -> Dict:
        """
        Get pool statistics
        
        Returns:
            Dictionary with pool stats
        """
        active_accounts = [acc for acc in self.accounts if acc.is_active]
        
        return {
            'total_accounts': len(self.accounts),
            'active_accounts': len(active_accounts),
            'inactive_accounts': len(self.accounts) - len(active_accounts),
            'total_daily_limit': self.total_daily_limit,
            'total_daily_remaining': self.total_daily_remaining,
            'total_daily_used': self.total_daily_limit - self.total_daily_remaining,
            'accounts': [
                {
                    'email': acc.email,
                    'active': acc.is_active,
                    'remaining': acc.daily_remaining,
                    'limit': acc.daily_limit,
                    'reset': acc.reset_time,
                    'notes': acc.notes
                }
                for acc in self.accounts
            ]
        }
    
    def save_config(self) -> None:
        """Save accounts configuration to file"""
        config = {
            'version': '1.0',
            'updated': datetime.now().isoformat(),
            'accounts': [asdict(acc) for acc in self.accounts]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.debug(f"Saved {len(self.accounts)} accounts to {self.config_file}")
    
    def load_config(self) -> None:
        """Load accounts configuration from file"""
        if not self.config_file.exists():
            logger.info("No existing config file found")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.accounts = [
                AccountInfo(**acc) for acc in config.get('accounts', [])
            ]
            
            logger.info(f"Loaded {len(self.accounts)} accounts from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup all client sessions"""
        for email, client in self.clients.items():
            try:
                await client.logout()
            except:
                pass
        self.clients.clear()


class SmartDownloader:
    """
    Smart downloader using account pool for maximum efficiency
    """
    
    def __init__(self, pool: AccountPool):
        self.pool = pool
        self.download_count = 0
        self.failed_count = 0
    
    async def search_and_download(self, query: str, extension: str = "epub", 
                                 max_downloads: int = 5) -> List[Dict]:
        """
        Search and download books using available accounts
        
        Args:
            query: Search query
            extension: File extension filter
            max_downloads: Maximum number of downloads
            
        Returns:
            List of download results
        """
        results = []
        
        # Get available client
        client, account = await self.pool.get_available_client()
        if not client:
            logger.error("No available accounts for search")
            return results
        
        # Perform search
        try:
            from .const import Extension, Language
            
            ext_enum = getattr(Extension, extension.upper(), Extension.EPUB)
            
            search_results = await client.search(
                q=query,
                extensions=[ext_enum],
                count=min(max_downloads, 50)
            )
            
            await search_results.init()
            books = search_results.result[:max_downloads]
            
            logger.info(f"Found {len(books)} books for '{query}'")
            
            # Download books using pool
            for i, book in enumerate(books, 1):
                # Check if we need to rotate accounts
                if account.daily_remaining <= 0:
                    client, account = await self.pool.rotate_to_next()
                    if not client:
                        logger.warning("No more accounts available")
                        break
                
                try:
                    # Fetch book details
                    details = await book.fetch()
                    
                    result = {
                        'index': i,
                        'name': details.get('name'),
                        'authors': details.get('authors'),
                        'download_url': details.get('download_url'),
                        'size': details.get('size'),
                        'account_used': account.email,
                        'status': 'success'
                    }
                    
                    # Update account usage
                    account.daily_remaining -= 1
                    account.daily_used += 1
                    self.download_count += 1
                    
                    results.append(result)
                    logger.info(f"✅ Downloaded {i}/{len(books)}: {result['name'][:50]}")
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.failed_count += 1
                    results.append({
                        'index': i,
                        'name': book.name if hasattr(book, 'name') else 'Unknown',
                        'status': 'failed',
                        'error': str(e)
                    })
                    logger.error(f"❌ Failed {i}/{len(books)}: {e}")
            
            # Save updated limits
            self.pool.save_config()
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return results


# Example usage functions
async def example_setup():
    """Example: Setting up account pool"""
    pool = AccountPool("accounts.json")
    
    # Add accounts (you would add your real accounts)
    pool.add_account("account1@email.com", "password1", "Primary account")
    pool.add_account("account2@email.com", "password2", "Backup account 1")
    pool.add_account("account3@email.com", "password3", "Backup account 2")
    pool.add_account("account4@email.com", "password4", "Backup account 3")
    pool.add_account("account5@email.com", "password5", "Backup account 4")
    
    # Initialize all accounts
    results = await pool.initialize_all()
    
    # Show statistics
    stats = pool.get_statistics()
    print(f"Account Pool Statistics:")
    print(f"  Total accounts: {stats['total_accounts']}")
    print(f"  Active accounts: {stats['active_accounts']}")
    print(f"  Total daily limit: {stats['total_daily_limit']}")
    print(f"  Total remaining: {stats['total_daily_remaining']}")
    
    return pool


async def example_download():
    """Example: Using pool for downloads"""
    pool = AccountPool("accounts.json")
    await pool.initialize_all()
    
    downloader = SmartDownloader(pool)
    
    # Download books
    results = await downloader.search_and_download(
        query="Python programming",
        extension="epub",
        max_downloads=10
    )
    
    print(f"\nDownload Results:")
    for result in results:
        if result['status'] == 'success':
            print(f"✅ {result['name']} - Used: {result['account_used']}")
        else:
            print(f"❌ {result['name']} - Error: {result.get('error')}")
    
    await pool.cleanup()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_setup())