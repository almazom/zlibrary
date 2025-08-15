#!/usr/bin/env python3
"""
Performance Benchmark Script for Eksmo Extractors
Compares original vs optimized implementations
"""

import asyncio
import time
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List
import statistics

class ExtractionBenchmark:
    """Benchmark tool for comparing extraction performance"""
    
    def __init__(self):
        self.results = {
            'original': [],
            'optimized': []
        }
        self.script_dir = Path(__file__).parent
    
    async def run_original_extractor(self) -> Dict:
        """Run the original ekstractor and measure time"""
        start_time = time.time()
        
        try:
            # Run original extractor
            result = subprocess.run(
                ["python3", str(self.script_dir / "eksmo_random_extractor.py")],
                capture_output=True,
                text=True,
                timeout=90  # Allow up to 90 seconds
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return {
                        'success': True,
                        'duration': duration,
                        'data': data
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'duration': duration,
                        'error': 'JSON parse error'
                    }
            else:
                return {
                    'success': False,
                    'duration': duration,
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': 90,
                'error': 'Timeout (>90s)'
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def run_optimized_extractor(self) -> Dict:
        """Run the optimized extractor and measure time"""
        start_time = time.time()
        
        try:
            # Run optimized extractor
            result = subprocess.run(
                ["python3", str(self.script_dir / "optimized_eksmo_extractor.py")],
                capture_output=True,
                text=True,
                timeout=30  # Stricter timeout for optimized version
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    # Parse the JSON output
                    lines = result.stdout.split('\n')
                    json_str = ''
                    in_json = False
                    for line in lines:
                        if line.strip().startswith('{'):
                            in_json = True
                        if in_json:
                            json_str += line + '\n'
                        if line.strip().endswith('}') and in_json:
                            break
                    
                    data = json.loads(json_str)
                    return {
                        'success': True,
                        'duration': duration,
                        'data': data
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'duration': duration,
                        'error': 'JSON parse error'
                    }
            else:
                return {
                    'success': False,
                    'duration': duration,
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': 30,
                'error': 'Timeout (>30s)'
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def run_benchmark(self, num_runs: int = 3):
        """Run benchmark comparison"""
        print("=" * 60)
        print("📊 EKSMO EXTRACTOR PERFORMANCE BENCHMARK")
        print("=" * 60)
        print(f"Running {num_runs} iterations for each implementation...")
        print()
        
        # Test original implementation
        print("🔵 Testing ORIGINAL implementation...")
        print("-" * 40)
        for i in range(num_runs):
            print(f"  Run {i+1}/{num_runs}: ", end="", flush=True)
            result = await self.run_original_extractor()
            self.results['original'].append(result)
            
            if result['success']:
                print(f"✅ {result['duration']:.2f}s")
            else:
                print(f"❌ {result['duration']:.2f}s - {result.get('error', 'Unknown error')}")
        
        print()
        
        # Test optimized implementation
        print("🟢 Testing OPTIMIZED implementation...")
        print("-" * 40)
        for i in range(num_runs):
            print(f"  Run {i+1}/{num_runs}: ", end="", flush=True)
            result = await self.run_optimized_extractor()
            self.results['optimized'].append(result)
            
            if result['success']:
                print(f"✅ {result['duration']:.2f}s")
            else:
                print(f"❌ {result['duration']:.2f}s - {result.get('error', 'Unknown error')}")
        
        print()
        self.print_results()
    
    def calculate_stats(self, results: List[Dict]) -> Dict:
        """Calculate statistics for a set of results"""
        successful_runs = [r for r in results if r['success']]
        all_durations = [r['duration'] for r in results]
        successful_durations = [r['duration'] for r in successful_runs]
        
        if not successful_durations:
            return {
                'success_rate': 0,
                'avg_duration': statistics.mean(all_durations) if all_durations else 0,
                'min_duration': 0,
                'max_duration': 0,
                'median_duration': 0,
                'stdev_duration': 0
            }
        
        return {
            'success_rate': len(successful_runs) / len(results) * 100,
            'avg_duration': statistics.mean(successful_durations),
            'min_duration': min(successful_durations),
            'max_duration': max(successful_durations),
            'median_duration': statistics.median(successful_durations),
            'stdev_duration': statistics.stdev(successful_durations) if len(successful_durations) > 1 else 0
        }
    
    def print_results(self):
        """Print benchmark results and comparison"""
        print("=" * 60)
        print("📈 BENCHMARK RESULTS")
        print("=" * 60)
        
        original_stats = self.calculate_stats(self.results['original'])
        optimized_stats = self.calculate_stats(self.results['optimized'])
        
        # Original implementation stats
        print("\n🔵 ORIGINAL IMPLEMENTATION:")
        print(f"  Success Rate:     {original_stats['success_rate']:.1f}%")
        print(f"  Average Duration: {original_stats['avg_duration']:.2f}s")
        print(f"  Min Duration:     {original_stats['min_duration']:.2f}s")
        print(f"  Max Duration:     {original_stats['max_duration']:.2f}s")
        print(f"  Median Duration:  {original_stats['median_duration']:.2f}s")
        if original_stats['stdev_duration'] > 0:
            print(f"  Std Deviation:    {original_stats['stdev_duration']:.2f}s")
        
        # Optimized implementation stats
        print("\n🟢 OPTIMIZED IMPLEMENTATION:")
        print(f"  Success Rate:     {optimized_stats['success_rate']:.1f}%")
        print(f"  Average Duration: {optimized_stats['avg_duration']:.2f}s")
        print(f"  Min Duration:     {optimized_stats['min_duration']:.2f}s")
        print(f"  Max Duration:     {optimized_stats['max_duration']:.2f}s")
        print(f"  Median Duration:  {optimized_stats['median_duration']:.2f}s")
        if optimized_stats['stdev_duration'] > 0:
            print(f"  Std Deviation:    {optimized_stats['stdev_duration']:.2f}s")
        
        # Performance comparison
        print("\n" + "=" * 60)
        print("🎯 PERFORMANCE IMPROVEMENT")
        print("=" * 60)
        
        if original_stats['avg_duration'] > 0 and optimized_stats['avg_duration'] > 0:
            improvement = (original_stats['avg_duration'] - optimized_stats['avg_duration']) / original_stats['avg_duration'] * 100
            speedup = original_stats['avg_duration'] / optimized_stats['avg_duration']
            
            print(f"\n  Speed Improvement: {improvement:.1f}%")
            print(f"  Speedup Factor:    {speedup:.1f}x faster")
            print(f"  Time Saved:        {original_stats['avg_duration'] - optimized_stats['avg_duration']:.2f}s per extraction")
            
            # Target evaluation
            print("\n📋 TARGET EVALUATION:")
            if optimized_stats['avg_duration'] < 15:
                print(f"  ✅ SUCCESS: Average {optimized_stats['avg_duration']:.2f}s < 15s target")
            elif optimized_stats['avg_duration'] < 30:
                print(f"  ⚠️  PARTIAL: Average {optimized_stats['avg_duration']:.2f}s (target: <15s)")
            else:
                print(f"  ❌ FAILED: Average {optimized_stats['avg_duration']:.2f}s (target: <15s)")
            
            # Success rate comparison
            if optimized_stats['success_rate'] >= original_stats['success_rate']:
                print(f"  ✅ Reliability maintained or improved")
            else:
                print(f"  ⚠️  Reliability decreased by {original_stats['success_rate'] - optimized_stats['success_rate']:.1f}%")
        else:
            print("  ⚠️  Insufficient data for comparison")
        
        print("\n" + "=" * 60)
        
        # Save detailed results to file
        self.save_results()
    
    def save_results(self):
        """Save detailed benchmark results to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = self.script_dir / f"benchmark_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'results': self.results,
                'stats': {
                    'original': self.calculate_stats(self.results['original']),
                    'optimized': self.calculate_stats(self.results['optimized'])
                }
            }, f, indent=2, default=str)
        
        print(f"\n📁 Detailed results saved to: {results_file}")

async def main():
    """Main entry point"""
    # Parse command line arguments
    num_runs = 3  # Default
    if len(sys.argv) > 1:
        try:
            num_runs = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [num_runs]")
            print(f"  num_runs: Number of benchmark iterations (default: 3)")
            sys.exit(1)
    
    # Check if both implementations exist
    script_dir = Path(__file__).parent
    original_script = script_dir / "eksmo_random_extractor.py"
    optimized_script = script_dir / "optimized_eksmo_extractor.py"
    
    if not original_script.exists():
        print(f"❌ Original implementation not found: {original_script}")
        sys.exit(1)
    
    if not optimized_script.exists():
        print(f"❌ Optimized implementation not found: {optimized_script}")
        sys.exit(1)
    
    # Run benchmark
    benchmark = ExtractionBenchmark()
    await benchmark.run_benchmark(num_runs)

if __name__ == "__main__":
    asyncio.run(main())