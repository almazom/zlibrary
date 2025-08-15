#!/usr/bin/env python3
"""
Extended UC12 Analysis - Deep dive into concurrent operations
"""

import asyncio
import sys
import time
import threading
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))

from UC12_concurrent_test import ConcurrentAccountManager, download_book_concurrent

async def extended_monitoring_test():
    print('🔍 Extended Monitoring Test - Thread Safety & Resource Analysis')
    print('=' * 70)
    
    manager = ConcurrentAccountManager()
    
    # Test with resource monitoring
    print('\n📊 Resource Monitoring During Concurrent Operations:')
    
    # Monitor thread safety with rapid-fire requests
    start_memory = sys.getsizeof(manager.accounts) + sys.getsizeof(manager.download_log)
    start_time = time.time()
    
    # Launch 50 concurrent requests to stress test
    tasks = [download_book_concurrent(manager, f'Stress_{i}') for i in range(50)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    end_memory = sys.getsizeof(manager.accounts) + sys.getsizeof(manager.download_log)
    
    successful = sum(1 for r in results if r.get('status') == 'success')
    
    print(f'  ✅ Successful requests: {successful}/50')
    print(f'  ⏱️ Total execution time: {end_time - start_time:.3f}s')
    print(f'  💾 Memory usage: {start_memory} → {end_memory} bytes ({end_memory - start_memory:+d})')
    print(f'  🔒 Lock acquisitions: {len(manager.download_log)}')
    print(f'  ⚡ Account switches: {manager.switch_count}')
    print(f'  💥 Detected collisions: {manager.collision_count}')
    
    # Verify data consistency
    account_totals = {}
    for log in manager.download_log:
        account_totals[log['account_id']] = account_totals.get(log['account_id'], 0) + 1
    
    print(f'\n  📋 Final Account Usage:')
    expected_limits = {1: 8, 2: 4, 3: 10}
    total_used = 0
    
    for acc_id in sorted(account_totals.keys()):
        used = account_totals[acc_id]
        limit = expected_limits[acc_id]
        total_used += used
        status = '✅' if used <= limit else '❌ OVERUSE!'
        print(f'    {status} Account {acc_id}: {used}/{limit} downloads')
    
    print(f'  📊 Total system usage: {total_used}/22')
    
    # Thread safety validation
    timestamps = [log['timestamp'] for log in manager.download_log]
    concurrent_ops = 0
    for i in range(len(timestamps)):
        for j in range(i+1, len(timestamps)):
            if abs(timestamps[i] - timestamps[j]) < 0.001:  # Within 1ms
                concurrent_ops += 1
    
    print(f'  🧵 Concurrent operations detected: {concurrent_ops}')
    safety_status = 'GOOD' if concurrent_ops <= manager.collision_count else 'NEEDS ATTENTION'
    print(f'  🛡️ Thread safety: {safety_status}')
    
    # Rate limiting compliance test
    print('\n📈 Rate Limiting Analysis:')
    if len(timestamps) > 1:
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        min_interval = min(intervals) * 1000  # Convert to ms
        avg_interval = (sum(intervals) / len(intervals)) * 1000
        print(f'  ⚡ Minimum interval: {min_interval:.1f}ms')
        print(f'  📊 Average interval: {avg_interval:.1f}ms')
        print(f'  🎯 Rate compliance: {"GOOD" if min_interval >= 1 else "TOO FAST"}')
    
    # Performance under load analysis
    print('\n🏋️ Performance Under Load:')
    throughput = successful / (end_time - start_time)
    efficiency = (successful / 22) * 100  # Percentage of total capacity used
    print(f'  🚀 Throughput: {throughput:.1f} requests/second')
    print(f'  📊 Capacity efficiency: {efficiency:.1f}%')
    print(f'  ⚖️ Load handling: {"EXCELLENT" if throughput > 50 else "GOOD" if throughput > 20 else "NEEDS OPTIMIZATION"}')

if __name__ == "__main__":
    asyncio.run(extended_monitoring_test())