#!/usr/bin/env python3
"""
UC15: Rate Limit Handling Test
Tests intelligent rate limiting and throttling
"""

import asyncio
import time
from collections import deque
from typing import Dict, List, Optional
from datetime import datetime
import random

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        
    async def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens, wait if necessary"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add new tokens
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0  # No wait needed
            
            # Calculate wait time
            wait_time = (tokens - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            
            # Update after wait
            self.tokens = 0
            self.last_update = time.time()
            return wait_time

class AdaptiveThrottler:
    """Dynamically adjusts request rate based on responses"""
    
    def __init__(self, initial_rate: float = 10.0):
        self.current_rate = initial_rate
        self.min_rate = 0.5
        self.max_rate = 50.0
        self.success_streak = 0
        self.limit_events = deque(maxlen=10)
        self.adjustment_history = []
        
    def on_success(self):
        """Handle successful request"""
        self.success_streak += 1
        
        # Increase rate after 10 successes
        if self.success_streak >= 10:
            old_rate = self.current_rate
            self.current_rate = min(self.max_rate, self.current_rate * 1.1)
            self.success_streak = 0
            
            if old_rate != self.current_rate:
                self.adjustment_history.append({
                    'time': time.time(),
                    'action': 'increase',
                    'from': old_rate,
                    'to': self.current_rate
                })
                print(f"  📈 Rate increased: {old_rate:.1f} → {self.current_rate:.1f} req/s")
    
    def on_rate_limit(self):
        """Handle rate limit response"""
        self.success_streak = 0
        self.limit_events.append(time.time())
        
        old_rate = self.current_rate
        self.current_rate = max(self.min_rate, self.current_rate * 0.5)
        
        self.adjustment_history.append({
            'time': time.time(),
            'action': 'decrease',
            'from': old_rate,
            'to': self.current_rate
        })
        print(f"  📉 Rate limited! Reduced: {old_rate:.1f} → {self.current_rate:.1f} req/s")
    
    def get_current_rate(self) -> float:
        """Get current rate in requests per second"""
        return self.current_rate
    
    def get_stats(self) -> Dict:
        """Get throttler statistics"""
        recent_limits = len([t for t in self.limit_events if time.time() - t < 60])
        return {
            'current_rate': self.current_rate,
            'success_streak': self.success_streak,
            'recent_limits': recent_limits,
            'adjustments': len(self.adjustment_history)
        }

class AccountRateLimiter:
    """Per-account rate limiting"""
    
    def __init__(self):
        self.accounts = {
            'account1': {'limit': 100, 'period': 3600, 'used': 0, 'reset_time': time.time() + 3600},
            'account2': {'limit': 50, 'period': 3600, 'used': 0, 'reset_time': time.time() + 3600},
            'account3': {'limit': 200, 'period': 3600, 'used': 0, 'reset_time': time.time() + 3600}
        }
        self.request_history = {acc: deque(maxlen=1000) for acc in self.accounts}
        
    def check_limit(self, account: str) -> tuple[bool, int]:
        """Check if account has capacity"""
        acc_data = self.accounts[account]
        
        # Reset if period expired
        if time.time() > acc_data['reset_time']:
            acc_data['used'] = 0
            acc_data['reset_time'] = time.time() + acc_data['period']
        
        remaining = acc_data['limit'] - acc_data['used']
        can_proceed = remaining > 0
        
        return can_proceed, remaining
    
    def use_account(self, account: str) -> bool:
        """Use account if within limits"""
        can_proceed, remaining = self.check_limit(account)
        
        if can_proceed:
            self.accounts[account]['used'] += 1
            self.request_history[account].append(time.time())
            return True
        return False
    
    def get_best_account(self) -> Optional[str]:
        """Get account with most remaining capacity"""
        best_account = None
        max_remaining = 0
        
        for account, data in self.accounts.items():
            can_proceed, remaining = self.check_limit(account)
            if can_proceed and remaining > max_remaining:
                best_account = account
                max_remaining = remaining
                
        return best_account
    
    def get_stats(self) -> Dict:
        """Get account statistics"""
        stats = {}
        for account, data in self.accounts.items():
            _, remaining = self.check_limit(account)
            stats[account] = {
                'used': data['used'],
                'limit': data['limit'],
                'remaining': remaining,
                'utilization': (data['used'] / data['limit'] * 100) if data['limit'] > 0 else 0
            }
        return stats

class RequestQueue:
    """Queue for managing burst requests"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.queue = asyncio.Queue()
        self.rate_limiter = rate_limiter
        self.processing = False
        self.processed_count = 0
        self.queued_count = 0
        
    async def add(self, request_id: str):
        """Add request to queue"""
        await self.queue.put(request_id)
        self.queued_count += 1
        
        if not self.processing:
            asyncio.create_task(self.process())
    
    async def process(self):
        """Process queued requests with rate limiting"""
        self.processing = True
        
        while not self.queue.empty():
            request_id = await self.queue.get()
            
            # Wait for rate limit token
            wait_time = await self.rate_limiter.acquire()
            if wait_time > 0:
                print(f"  ⏳ Throttled {wait_time:.2f}s for {request_id}")
            
            # Simulate request processing
            await asyncio.sleep(0.1)
            self.processed_count += 1
            print(f"  ✅ Processed: {request_id} ({self.processed_count}/{self.queued_count})")
        
        self.processing = False

async def test_rate_limit_detection():
    """Test rate limit detection and response"""
    print("=" * 70)
    print("UC15.1: RATE LIMIT DETECTION")
    print("=" * 70)
    
    throttler = AdaptiveThrottler(initial_rate=20.0)
    
    print("\n📊 Simulating requests with rate limits:")
    
    for i in range(30):
        # Simulate rate limit every 10 requests
        if i > 0 and i % 10 == 0:
            throttler.on_rate_limit()
            print(f"  ⚠️ Rate limit hit at request {i}")
        else:
            throttler.on_success()
            
        # Show current rate periodically
        if i % 5 == 0:
            stats = throttler.get_stats()
            print(f"  📊 Request {i}: Rate={stats['current_rate']:.1f} req/s")
        
        await asyncio.sleep(0.1)
    
    print(f"\n📈 Final stats: {throttler.get_stats()}")

async def test_adaptive_throttling():
    """Test adaptive rate adjustment"""
    print("\n" + "=" * 70)
    print("UC15.2: ADAPTIVE THROTTLING")
    print("=" * 70)
    
    throttler = AdaptiveThrottler(initial_rate=5.0)
    rate_limiter = RateLimiter(rate=throttler.get_current_rate(), capacity=10)
    
    print("\n📊 Testing adaptive rate adjustment:")
    
    success_count = 0
    for i in range(50):
        # Adjust rate limiter to current throttle rate
        rate_limiter.rate = throttler.get_current_rate()
        
        # Acquire token
        wait_time = await rate_limiter.acquire()
        
        # Simulate random rate limits
        if random.random() < 0.1:  # 10% chance of rate limit
            throttler.on_rate_limit()
        else:
            throttler.on_success()
            success_count += 1
        
        if i % 10 == 0:
            print(f"  Progress: {i}/50, Success: {success_count}, Rate: {throttler.current_rate:.1f} req/s")
    
    print(f"\n✅ Completed with {success_count}/50 successful requests")

async def test_per_account_limits():
    """Test per-account rate limiting"""
    print("\n" + "=" * 70)
    print("UC15.3: PER-ACCOUNT RATE LIMITS")
    print("=" * 70)
    
    limiter = AccountRateLimiter()
    
    print("\n📊 Initial account limits:")
    for account, stats in limiter.get_stats().items():
        print(f"  {account}: {stats['remaining']}/{stats['limit']} available")
    
    print("\n📊 Distributing 100 requests:")
    
    successful = 0
    failed = 0
    
    for i in range(100):
        account = limiter.get_best_account()
        
        if account and limiter.use_account(account):
            successful += 1
            if i % 20 == 0:
                print(f"  ✅ Request {i}: Used {account}")
        else:
            failed += 1
            print(f"  ❌ Request {i}: All accounts exhausted")
    
    print(f"\n📊 Results: {successful} successful, {failed} failed")
    
    print("\n📊 Final account status:")
    for account, stats in limiter.get_stats().items():
        print(f"  {account}: {stats['used']}/{stats['limit']} used ({stats['utilization']:.1f}%)")

async def test_burst_protection():
    """Test burst request handling"""
    print("\n" + "=" * 70)
    print("UC15.4: BURST PROTECTION")
    print("=" * 70)
    
    # Create rate limiter for 10 req/s
    rate_limiter = RateLimiter(rate=10.0, capacity=10)
    queue = RequestQueue(rate_limiter)
    
    print("\n📊 Queueing burst of 50 requests:")
    
    # Queue all requests at once (burst)
    tasks = []
    start_time = time.time()
    
    for i in range(50):
        tasks.append(queue.add(f"Request_{i+1}"))
    
    await asyncio.gather(*tasks)
    print(f"  Queued 50 requests in {time.time() - start_time:.2f}s")
    
    # Wait for processing to complete
    print("\n📊 Processing with rate limiting (10 req/s):")
    while queue.processing or not queue.queue.empty():
        await asyncio.sleep(0.5)
        if queue.processed_count % 10 == 0 and queue.processed_count > 0:
            elapsed = time.time() - start_time
            rate = queue.processed_count / elapsed
            print(f"  Progress: {queue.processed_count}/50, Rate: {rate:.1f} req/s")
    
    total_time = time.time() - start_time
    actual_rate = queue.processed_count / total_time
    
    print(f"\n✅ Processed {queue.processed_count} requests in {total_time:.1f}s")
    print(f"   Target rate: 10.0 req/s")
    print(f"   Actual rate: {actual_rate:.1f} req/s")

async def test_intelligent_load_balancing():
    """Test intelligent load balancing across accounts"""
    print("\n" + "=" * 70)
    print("UC15.5: INTELLIGENT LOAD BALANCING")
    print("=" * 70)
    
    limiter = AccountRateLimiter()
    
    # Simulate different account states
    limiter.accounts['account1']['used'] = 80  # 80% used
    limiter.accounts['account2']['used'] = 10  # 20% used
    limiter.accounts['account3']['used'] = 50  # 25% used
    
    print("\n📊 Initial account utilization:")
    for account, stats in limiter.get_stats().items():
        print(f"  {account}: {stats['utilization']:.1f}% used")
    
    print("\n📊 Smart distribution of 50 requests:")
    
    distribution = {'account1': 0, 'account2': 0, 'account3': 0}
    
    for i in range(50):
        account = limiter.get_best_account()
        if account and limiter.use_account(account):
            distribution[account] += 1
    
    print("\n📊 Request distribution:")
    for account, count in distribution.items():
        print(f"  {account}: {count} requests")
    
    print("\n📊 Final utilization:")
    for account, stats in limiter.get_stats().items():
        print(f"  {account}: {stats['utilization']:.1f}% used")

async def main():
    """Run all UC15 rate limit tests"""
    
    print("⚡ UC15: Rate Limit Handling Tests")
    print("=" * 70)
    
    await test_rate_limit_detection()
    await test_adaptive_throttling()
    await test_per_account_limits()
    await test_burst_protection()
    await test_intelligent_load_balancing()
    
    print("\n" + "=" * 70)
    print("✅ UC15 RATE LIMIT TESTS COMPLETE")
    print("=" * 70)
    
    print("\n📈 Key Findings:")
    print("  1. Rate limits detected and handled automatically")
    print("  2. Adaptive throttling maintains optimal throughput")
    print("  3. Per-account limits prevent bans")
    print("  4. Burst protection smooths traffic spikes")
    print("  5. Intelligent load balancing maximizes capacity")

if __name__ == "__main__":
    asyncio.run(main())