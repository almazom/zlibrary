#!/usr/bin/env python3
"""
TDD Test Suite for Z-Library Multi-Account System
Tests account pool, rotation, limit handling with 2 real accounts
"""

import asyncio
import json
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from zlibrary.account_pool import AccountPool, SmartDownloader
from zlibrary.libasync import AsyncZlib

# Import MultiAccountManager from root directory
sys.path.insert(0, str(Path(__file__).parent))
from multi_account_manager import MultiAccountManager

# Load environment variables
load_dotenv()


class TestMultiAccountSystem(unittest.IsolatedAsyncioTestCase):
    """Test suite for multi-account Z-Library system with 2 accounts"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_config_file = "test_accounts_config.json"
        cls.test_accounts_file = "test_accounts.txt"
        
        # Get accounts from environment
        cls.account1 = {
            "email": os.getenv("ZLOGIN"),
            "password": os.getenv("ZPASSW")
        }
        cls.account2 = {
            "email": os.getenv("ZLOGIN1"),
            "password": os.getenv("ZPASSW1")
        }
        
        # Verify both accounts are configured
        if not all([cls.account1["email"], cls.account1["password"],
                   cls.account2["email"], cls.account2["password"]]):
            raise ValueError("Both ZLOGIN/ZPASSW and ZLOGIN1/ZPASSW1 must be set in .env")
    
    async def asyncSetUp(self):
        """Set up each test"""
        # Clean up any existing test files
        for file in [self.test_config_file, self.test_accounts_file]:
            if Path(file).exists():
                Path(file).unlink()
    
    async def asyncTearDown(self):
        """Clean up after each test"""
        # Remove test files
        for file in [self.test_config_file, self.test_accounts_file]:
            if Path(file).exists():
                Path(file).unlink()
    
    # Test 1: Account Pool Initialization
    async def test_account_pool_initialization(self):
        """Test that AccountPool correctly initializes with 2 accounts"""
        print("\n🧪 Test 1: Account Pool Initialization")
        
        pool = AccountPool(self.test_config_file)
        
        # Add both accounts
        pool.add_account(self.account1["email"], self.account1["password"], "Primary account")
        pool.add_account(self.account2["email"], self.account2["password"], "Secondary account")
        
        # Verify accounts were added
        self.assertEqual(len(pool.accounts), 2, "Should have 2 accounts in pool")
        
        # Verify account properties
        account_emails = [acc.email for acc in pool.accounts]
        self.assertIn(self.account1["email"], account_emails)
        self.assertIn(self.account2["email"], account_emails)
        
        # Verify config file was created
        self.assertTrue(Path(self.test_config_file).exists(), "Config file should be created")
        
        # Load and verify config structure
        with open(self.test_config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIn("accounts", config)
        self.assertEqual(len(config["accounts"]), 2)
        print("✅ Account pool initialized with 2 accounts")
    
    # Test 2: Account Authentication
    async def test_account_authentication(self):
        """Test that both accounts can authenticate successfully"""
        print("\n🧪 Test 2: Account Authentication")
        
        pool = AccountPool(self.test_config_file)
        pool.add_account(self.account1["email"], self.account1["password"])
        pool.add_account(self.account2["email"], self.account2["password"])
        
        # Test first account login
        client1, acc1 = await pool.get_available_client()
        self.assertIsNotNone(client1, "First account should authenticate")
        self.assertIsNotNone(client1.profile, "First account should have profile")
        print(f"✅ Account 1 authenticated: {self.account1['email']}")
        
        # Force rotation to second account
        pool.current_index = 1
        client2, acc2 = await pool.get_available_client()
        self.assertIsNotNone(client2, "Second account should authenticate")
        self.assertIsNotNone(client2.profile, "Second account should have profile")
        print(f"✅ Account 2 authenticated: {self.account2['email']}")
    
    # Test 3: Account Limits Checking
    async def test_account_limits_checking(self):
        """Test that limits are correctly retrieved for both accounts"""
        print("\n🧪 Test 3: Account Limits Checking")
        
        pool = AccountPool(self.test_config_file)
        pool.add_account(self.account1["email"], self.account1["password"])
        pool.add_account(self.account2["email"], self.account2["password"])
        
        # Initialize pool
        await pool.initialize()
        
        # Check limits for both accounts
        for i, account in enumerate(pool.accounts):
            self.assertIsNotNone(account.daily_limit, f"Account {i+1} should have daily_limit")
            self.assertIsNotNone(account.daily_remaining, f"Account {i+1} should have daily_remaining")
            self.assertIsNotNone(account.daily_used, f"Account {i+1} should have daily_used")
            
            # Verify limit values are reasonable
            self.assertGreaterEqual(account.daily_limit, 0)
            self.assertGreaterEqual(account.daily_remaining, 0)
            self.assertGreaterEqual(account.daily_used, 0)
            
            print(f"✅ Account {i+1} limits: {account.daily_remaining}/{account.daily_limit} remaining")
    
    # Test 4: Account Rotation Logic
    async def test_account_rotation(self):
        """Test that account rotation works when limits are exhausted"""
        print("\n🧪 Test 4: Account Rotation Logic")
        
        pool = AccountPool(self.test_config_file)
        pool.add_account(self.account1["email"], self.account1["password"])
        pool.add_account(self.account2["email"], self.account2["password"])
        
        await pool.initialize()
        
        # Simulate first account exhausted
        pool.accounts[0].daily_remaining = 0
        pool.accounts[0].is_active = True
        pool.accounts[1].daily_remaining = 5
        pool.accounts[1].is_active = True
        
        # Should rotate to second account
        client, acc = await pool.get_available_client()
        self.assertIsNotNone(client)
        self.assertEqual(pool.current_index, 1, "Should rotate to second account")
        print("✅ Rotated from exhausted account 1 to account 2")
        
        # Simulate both accounts exhausted
        pool.accounts[0].daily_remaining = 0
        pool.accounts[1].daily_remaining = 0
        
        client, acc = await pool.get_available_client()
        self.assertIsNone(client, "Should return None when all accounts exhausted")
        print("✅ Correctly returns None when all accounts exhausted")
    
    # Test 5: Multi-Account Manager Integration
    async def test_multi_account_manager(self):
        """Test MultiAccountManager with 2 accounts from environment"""
        print("\n🧪 Test 5: Multi-Account Manager Integration")
        
        manager = MultiAccountManager(config_file=self.test_config_file)
        
        # Add accounts from environment
        added = await manager.add_accounts_from_env()
        self.assertGreater(added, 0, "Should add accounts from environment")
        print(f"✅ Added {added} accounts from environment")
        
        # Initialize and get statistics
        stats = await manager.initialize()
        self.assertIsNotNone(stats)
        self.assertEqual(stats["total_accounts"], 2, "Should have 2 total accounts")
        self.assertGreaterEqual(stats["active_accounts"], 0)
        
        print(f"✅ Manager initialized: {stats['active_accounts']}/{stats['total_accounts']} active")
        print(f"   Total daily limit: {stats['total_daily_limit']}")
        print(f"   Total remaining: {stats['total_daily_remaining']}")
    
    # Test 6: Search with Account Rotation
    async def test_search_with_rotation(self):
        """Test searching with automatic account rotation"""
        print("\n🧪 Test 6: Search with Account Rotation")
        
        manager = MultiAccountManager(config_file=self.test_config_file)
        await manager.add_accounts_from_env()
        await manager.initialize()
        
        # Perform search
        books = await manager.search_with_rotation(
            query="Python",
            max_results=5,
            extension="pdf"
        )
        
        self.assertIsInstance(books, list)
        print(f"✅ Search completed, found {len(books)} books")
        
        # Verify books have required fields
        if books:
            book = books[0]
            self.assertIn("id", book)
            self.assertIn("name", book)
            self.assertIn("authors", book)
            print(f"✅ First book: {book.get('name', 'Unknown')[:50]}...")
    
    # Test 7: Statistics Tracking
    async def test_statistics_tracking(self):
        """Test that statistics are correctly tracked across accounts"""
        print("\n🧪 Test 7: Statistics Tracking")
        
        pool = AccountPool(self.test_config_file)
        pool.add_account(self.account1["email"], self.account1["password"])
        pool.add_account(self.account2["email"], self.account2["password"])
        
        await pool.initialize()
        stats = pool.get_statistics()
        
        # Verify statistics structure
        self.assertIn("total_accounts", stats)
        self.assertIn("active_accounts", stats)
        self.assertIn("total_daily_limit", stats)
        self.assertIn("total_daily_remaining", stats)
        self.assertIn("total_daily_used", stats)
        
        # Verify calculations
        self.assertEqual(stats["total_accounts"], 2)
        self.assertLessEqual(stats["active_accounts"], 2)
        self.assertEqual(
            stats["total_daily_used"] + stats["total_daily_remaining"],
            stats["total_daily_limit"],
            "Used + Remaining should equal Total Limit"
        )
        
        print(f"✅ Statistics tracking working:")
        print(f"   Total accounts: {stats['total_accounts']}")
        print(f"   Active accounts: {stats['active_accounts']}")
        print(f"   Combined daily limit: {stats['total_daily_limit']}")
    
    # Test 8: Account Persistence
    async def test_account_persistence(self):
        """Test that account state persists across pool instances"""
        print("\n🧪 Test 8: Account Persistence")
        
        # Create first pool instance
        pool1 = AccountPool(self.test_config_file)
        pool1.add_account(self.account1["email"], self.account1["password"], "Test note 1")
        pool1.add_account(self.account2["email"], self.account2["password"], "Test note 2")
        await pool1.initialize()
        
        # Modify some state
        pool1.accounts[0].daily_used = 3
        pool1.save_config()
        
        # Create second pool instance from same config
        pool2 = AccountPool(self.test_config_file)
        
        # Verify state was persisted
        self.assertEqual(len(pool2.accounts), 2, "Should load 2 accounts")
        self.assertEqual(pool2.accounts[0].daily_used, 3, "State should persist")
        self.assertEqual(pool2.accounts[0].notes, "Test note 1", "Notes should persist")
        
        print("✅ Account state correctly persists to disk")
    
    # Test 9: Error Handling
    async def test_error_handling(self):
        """Test error handling for invalid accounts"""
        print("\n🧪 Test 9: Error Handling")
        
        pool = AccountPool(self.test_config_file)
        
        # Add invalid account
        pool.add_account("invalid@email.com", "wrongpassword", "Invalid account")
        pool.add_account(self.account1["email"], self.account1["password"], "Valid account")
        
        # Initialize should handle the error
        await pool.initialize()
        
        # Check that invalid account is marked inactive
        invalid_account = next((acc for acc in pool.accounts if acc.email == "invalid@email.com"), None)
        self.assertIsNotNone(invalid_account)
        self.assertFalse(invalid_account.is_active, "Invalid account should be marked inactive")
        
        # Valid account should still work
        valid_account = next((acc for acc in pool.accounts if acc.email == self.account1["email"]), None)
        self.assertIsNotNone(valid_account)
        self.assertTrue(valid_account.is_active, "Valid account should be active")
        
        print("✅ Error handling works, invalid accounts marked inactive")
    
    # Test 10: Concurrent Operations
    async def test_concurrent_operations(self):
        """Test that pool handles concurrent requests properly"""
        print("\n🧪 Test 10: Concurrent Operations")
        
        pool = AccountPool(self.test_config_file)
        pool.add_account(self.account1["email"], self.account1["password"])
        pool.add_account(self.account2["email"], self.account2["password"])
        await pool.initialize()
        
        # Create multiple concurrent client requests
        tasks = [pool.get_available_client() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        non_none_clients = [c for c, acc in results if c is not None]
        self.assertGreater(len(non_none_clients), 0, "Should get at least some clients")
        
        print(f"✅ Handled 5 concurrent requests, {len(non_none_clients)} succeeded")


class TestSmartDownloader(unittest.IsolatedAsyncioTestCase):
    """Test SmartDownloader functionality with account pool"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_config_file = "test_downloader_config.json"
        cls.account1 = {
            "email": os.getenv("ZLOGIN"),
            "password": os.getenv("ZPASSW")
        }
        cls.account2 = {
            "email": os.getenv("ZLOGIN1"),
            "password": os.getenv("ZPASSW1")
        }
    
    async def asyncSetUp(self):
        """Set up each test"""
        if Path(self.test_config_file).exists():
            Path(self.test_config_file).unlink()
    
    async def asyncTearDown(self):
        """Clean up after each test"""
        if Path(self.test_config_file).exists():
            Path(self.test_config_file).unlink()
    
    async def test_smart_downloader_initialization(self):
        """Test SmartDownloader initialization with account pool"""
        print("\n🧪 Test 11: SmartDownloader Initialization")
        
        pool = AccountPool(self.test_config_file)
        pool.add_account(self.account1["email"], self.account1["password"])
        pool.add_account(self.account2["email"], self.account2["password"])
        
        downloader = SmartDownloader(pool)
        await downloader.initialize()
        
        self.assertIsNotNone(downloader.pool)
        self.assertEqual(len(downloader.pool.accounts), 2)
        print("✅ SmartDownloader initialized with 2-account pool")
    
    async def test_search_with_smart_downloader(self):
        """Test searching through SmartDownloader"""
        print("\n🧪 Test 12: SmartDownloader Search")
        
        pool = AccountPool(self.test_config_file)
        pool.add_account(self.account1["email"], self.account1["password"])
        pool.add_account(self.account2["email"], self.account2["password"])
        
        downloader = SmartDownloader(pool)
        await downloader.initialize()
        
        # Search for books
        books = await downloader.search("Python programming", limit=3)
        
        self.assertIsInstance(books, list)
        self.assertLessEqual(len(books), 3)
        
        if books:
            print(f"✅ Found {len(books)} books through SmartDownloader")
            print(f"   First result: {books[0].get('name', 'Unknown')[:50]}...")


def run_all_tests():
    """Run all tests and generate report"""
    print("="*60)
    print("🚀 Z-LIBRARY MULTI-ACCOUNT SYSTEM TEST SUITE")
    print("="*60)
    print(f"Testing with 2 accounts:")
    print(f"  Account 1: {os.getenv('ZLOGIN')}")
    print(f"  Account 2: {os.getenv('ZLOGIN1')}")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMultiAccountSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSmartDownloader))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚨 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! Multi-account system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)